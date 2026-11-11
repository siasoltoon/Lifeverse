from __future__ import annotations

import json
import logging
import secrets
from datetime import UTC, datetime, timedelta
from threading import Event, Lock, Thread
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, select, update
from sqlalchemy.dialects.postgresql import insert as postgresql_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base
from .observability import metrics

logger = logging.getLogger(__name__)


class JobRecord(Base):
    __tablename__ = "background_jobs"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    job_type: Mapped[str] = mapped_column(String(96), index=True)
    status: Mapped[str] = mapped_column(String(24), index=True, default="queued")
    payload: Mapped[str] = mapped_column(Text, default="{}")
    run_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, default=5)
    locked_by: Mapped[str | None] = mapped_column(String(128))
    locked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    idempotency_key: Mapped[str] = mapped_column(String(160), unique=True)
    last_error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    __table_args__ = (
        Index("ix_background_jobs_claim", "status", "run_at"),
        Index("ix_background_jobs_lock", "status", "locked_at"),
    )


class WorkerHeartbeat(Base):
    __tablename__ = "worker_heartbeats"

    worker_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    status: Mapped[str] = mapped_column(String(24), default="running")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    stopped_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    current_job_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("background_jobs.id", ondelete="SET NULL")
    )


class WorkerHeartbeatService:
    def heartbeat(self, session, worker_id: str, current_job_id: UUID | None = None, now=None):
        if not isinstance(worker_id, str) or not worker_id or len(worker_id) > 128:
            raise ValueError("worker_id must contain 1-128 characters")

        now = now or datetime.now(UTC)
        values = {
            "worker_id": worker_id,
            "status": "running",
            "started_at": now,
            "last_seen_at": now,
            "stopped_at": None,
            "current_job_id": current_job_id,
        }
        dialect = session.get_bind().dialect.name
        if dialect == "postgresql":
            statement = postgresql_insert(WorkerHeartbeat).values(**values)
        elif dialect == "sqlite":
            statement = sqlite_insert(WorkerHeartbeat).values(**values)
        else:
            raise RuntimeError(f"unsupported heartbeat database dialect: {dialect}")

        statement = statement.on_conflict_do_update(
            index_elements=[WorkerHeartbeat.worker_id],
            set_={
                "status": "running",
                "last_seen_at": now,
                "stopped_at": None,
                "current_job_id": current_job_id,
            },
        )
        session.execute(statement)
        session.commit()
        session.expire_all()
        return session.get(WorkerHeartbeat, worker_id)

    def stop(self, session, worker_id: str, now=None):
        now = now or datetime.now(UTC)
        row = self.heartbeat(session, worker_id, now=now)
        row.status = "stopped"
        row.stopped_at = now
        row.current_job_id = None
        session.commit()
        return row

    def list_stale(self, session, stale_after_seconds: int = 60, now=None):
        if stale_after_seconds < 1:
            raise ValueError("stale_after_seconds must be positive")
        now = now or datetime.now(UTC)
        cutoff = now - timedelta(seconds=stale_after_seconds)
        return list(
            session.scalars(
                select(WorkerHeartbeat).where(
                    WorkerHeartbeat.status == "running",
                    WorkerHeartbeat.last_seen_at < cutoff,
                )
            )
        )


class JobService:
    VALID_STATES = {"queued", "running", "completed", "failed", "dead"}

    def enqueue(
        self, session, job_type, payload=None, run_at=None, idempotency_key=None, max_attempts=5
    ):
        if not job_type or len(job_type) > 96:
            raise ValueError("invalid job type")
        if max_attempts < 1 or max_attempts > 20:
            raise ValueError("max_attempts must be 1-20")
        now = datetime.now(UTC)
        key = idempotency_key or f"job:{job_type}:{secrets.token_urlsafe(18)}"
        existing = session.scalar(select(JobRecord).where(JobRecord.idempotency_key == key))
        if existing:
            return existing
        row = JobRecord(
            job_type=job_type,
            payload=json.dumps(payload or {}, sort_keys=True),
            run_at=run_at or now,
            max_attempts=max_attempts,
            idempotency_key=key,
            updated_at=now,
        )
        session.add(row)
        session.commit()
        session.refresh(row)
        return row

    def recover_expired(self, session, lease_seconds=300, now=None):
        if lease_seconds < 1:
            raise ValueError("lease_seconds must be positive")
        now = now or datetime.now(UTC)
        cutoff = now - timedelta(seconds=lease_seconds)
        rows = list(
            session.scalars(
                select(JobRecord).where(JobRecord.status == "running", JobRecord.locked_at < cutoff)
            )
        )
        for row in rows:
            row.status = "queued"
            row.locked_by = None
            row.locked_at = None
            row.updated_at = now
        session.commit()
        return rows

    def claim(self, session, worker_id, lease_seconds=300, now=None):
        if not worker_id:
            raise ValueError("worker_id is required")
        now = now or datetime.now(UTC)
        self.recover_expired(session, lease_seconds, now)
        candidate = session.scalar(
            select(JobRecord.id)
            .where(JobRecord.status == "queued", JobRecord.run_at <= now)
            .order_by(JobRecord.run_at, JobRecord.created_at)
            .limit(1)
        )
        if not candidate:
            return None
        claim = (
            update(JobRecord)
            .where(JobRecord.id == candidate, JobRecord.status == "queued")
            .values(
                status="running",
                locked_by=worker_id,
                locked_at=now,
                attempts=JobRecord.attempts + 1,
                updated_at=now,
            )
        )
        result = session.execute(claim)
        if result.rowcount != 1:
            session.rollback()
            return None
        session.commit()
        return session.get(JobRecord, candidate)

    def complete(self, session, job_id, worker_id):
        row = session.get(JobRecord, job_id)
        if not row or row.status != "running" or row.locked_by != worker_id:
            raise ValueError("job lease is not owned by worker")
        row.status = "completed"
        row.locked_by = None
        row.locked_at = None
        row.updated_at = datetime.now(UTC)
        session.commit()
        return row

    def fail(self, session, job_id, worker_id, error, retry_delay_seconds=30):
        row = session.get(JobRecord, job_id)
        if not row or row.status != "running" or row.locked_by != worker_id:
            raise ValueError("job lease is not owned by worker")
        now = datetime.now(UTC)
        row.last_error = str(error)[:4000]
        row.locked_by = None
        row.locked_at = None
        row.updated_at = now
        if row.attempts < row.max_attempts:
            row.status = "queued"
            delay = max(0, retry_delay_seconds) * (2 ** max(0, row.attempts - 1))
            row.run_at = now + timedelta(seconds=delay)
        else:
            row.status = "dead"
        session.commit()
        return row


class Worker:
    def __init__(self, service=None, worker_id=None):
        self.service = service or JobService()
        self.worker_id = worker_id or f"worker-{secrets.token_hex(8)}"
        self._current_job_id: UUID | None = None
        self._current_job_lock = Lock()

    @property
    def current_job_id(self) -> UUID | None:
        with self._current_job_lock:
            return self._current_job_id

    def _set_current_job(self, job_id: UUID | None) -> None:
        with self._current_job_lock:
            self._current_job_id = job_id

    def run_once(self, session, handlers):
        job = self.service.claim(session, self.worker_id)
        if not job:
            return None
        self._set_current_job(job.id)
        try:
            payload = json.loads(job.payload)
            handler = handlers.get(job.job_type)
            if handler is None:
                raise ValueError(f"no handler registered for {job.job_type}")
            result = handler(session, payload)
            self.service.complete(session, job.id, self.worker_id)
            metrics.inc("jobs_completed")
            logger.info("background_job_completed job_id=%s type=%s", job.id, job.job_type)
            return result
        except Exception as exc:
            failed = self.service.fail(session, job.id, self.worker_id, exc)
            metrics.inc("jobs_failed")
            if failed.status == "dead":
                metrics.inc("jobs_dead")
            logger.exception("background_job_failed job_id=%s type=%s", job.id, job.job_type)
            return None
        finally:
            self._set_current_job(None)


class WorkerHeartbeatReporter:
    def __init__(
        self,
        session_factory,
        worker_id: str,
        current_job_id,
        interval_seconds: float = 15.0,
        service: WorkerHeartbeatService | None = None,
    ):
        if interval_seconds <= 0:
            raise ValueError("heartbeat interval must be positive")
        self.session_factory = session_factory
        self.worker_id = worker_id
        self.current_job_id = current_job_id
        self.interval_seconds = interval_seconds
        self.service = service or WorkerHeartbeatService()
        self._stop_event = Event()
        self._thread: Thread | None = None

    def _write_heartbeat(self):
        with self.session_factory() as session:
            self.service.heartbeat(
                session, self.worker_id, current_job_id=self.current_job_id()
            )

    def _run(self):
        while not self._stop_event.wait(self.interval_seconds):
            try:
                self._write_heartbeat()
            except Exception:
                logger.exception("worker_heartbeat_failed worker_id=%s", self.worker_id)

    def start(self):
        if self._thread and self._thread.is_alive():
            raise RuntimeError("worker heartbeat reporter is already running")
        self._stop_event.clear()
        self._write_heartbeat()
        self._thread = Thread(
            target=self._run,
            name=f"heartbeat-{self.worker_id}",
            daemon=True,
        )
        self._thread.start()

    def stop(self):
        if not self._thread:
            return
        self._stop_event.set()
        self._thread.join(timeout=max(self.interval_seconds + 5, 10))
        if self._thread.is_alive():
            logger.error("worker_heartbeat_shutdown_timeout worker_id=%s", self.worker_id)
            return
        try:
            with self.session_factory() as session:
                self.service.stop(session, self.worker_id)
        except Exception:
            logger.exception("worker_heartbeat_stop_failed worker_id=%s", self.worker_id)
        self._thread = None
