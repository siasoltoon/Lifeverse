from __future__ import annotations

import json
import logging
import re
import time
from collections.abc import Callable
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from math import isfinite
from threading import Event, Lock, Thread

from sqlalchemy import DateTime, String, Text, delete, select, text
from sqlalchemy.dialects.postgresql import insert as postgresql_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base

logger = logging.getLogger("lifeverse.observability")


class Metrics:
    """Thread-safe, process-local operational counters and request timings."""

    def __init__(self):
        self._values = {
            "jobs_completed": 0,
            "jobs_failed": 0,
            "jobs_dead": 0,
            "requests": 0,
            "requests_4xx": 0,
            "requests_5xx": 0,
            "request_duration_ms_total": 0.0,
            "request_duration_ms_max": 0.0,
        }
        self._lock = Lock()

    def inc(self, name: str, amount: int = 1) -> None:
        if not isinstance(name, str) or not name:
            raise ValueError("metric name is required")
        if not isinstance(amount, int) or isinstance(amount, bool) or amount < 0:
            raise ValueError("metric increment must be a non-negative integer")
        with self._lock:
            self._values[name] = self._values.get(name, 0) + amount

    def record_request(self, status_code: int, duration_seconds: float) -> None:
        if (
            not isinstance(status_code, int)
            or isinstance(status_code, bool)
            or not 100 <= status_code <= 599
        ):
            raise ValueError("invalid HTTP status code")
        if (
            not isinstance(duration_seconds, (int, float))
            or isinstance(duration_seconds, bool)
            or not isfinite(duration_seconds)
            or duration_seconds < 0
        ):
            raise ValueError("request duration must be a finite non-negative number")
        duration_ms = duration_seconds * 1000
        with self._lock:
            self._values["requests"] += 1
            if 400 <= status_code < 500:
                self._values["requests_4xx"] += 1
            elif status_code >= 500:
                self._values["requests_5xx"] += 1
            self._values["request_duration_ms_total"] += duration_ms
            self._values["request_duration_ms_max"] = max(
                self._values["request_duration_ms_max"], duration_ms
            )

    def snapshot(self) -> dict[str, int | float]:
        with self._lock:
            return dict(self._values)


metrics = Metrics()


class MetricsSnapshotRecord(Base):
    __tablename__ = "operational_metric_snapshots"

    instance_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    service_name: Mapped[str] = mapped_column(String(16), index=True)
    metrics_json: Mapped[str] = mapped_column(Text)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


class MetricsSnapshotService:
    """Persists per-process counter snapshots for cross-process scraping."""

    INSTANCE_PATTERN = re.compile(r"[A-Za-z0-9_.:-]{1,128}")
    METRIC_PATTERN = re.compile(r"[a-z][a-z0-9_]{0,63}")

    def publish(self, session, instance_id: str, service_name: str, snapshot: dict, now=None):
        if not isinstance(instance_id, str) or not self.INSTANCE_PATTERN.fullmatch(instance_id):
            raise ValueError("invalid metrics instance id")
        if service_name not in {"api", "worker"}:
            raise ValueError("service_name must be api or worker")
        if not isinstance(snapshot, dict):
            raise ValueError("metrics snapshot must be a dictionary")
        validated = {}
        for name, value in snapshot.items():
            if not isinstance(name, str) or not self.METRIC_PATTERN.fullmatch(name):
                raise ValueError("invalid metric name")
            if (
                not isinstance(value, (int, float))
                or isinstance(value, bool)
                or not isfinite(value)
                or value < 0
            ):
                raise ValueError(f"invalid metric value for {name}")
            validated[name] = value

        now = now or datetime.now(UTC)
        values = {
            "instance_id": instance_id,
            "service_name": service_name,
            "metrics_json": json.dumps(validated, sort_keys=True, allow_nan=False),
            "last_seen_at": now,
        }
        dialect = session.get_bind().dialect.name
        if dialect == "postgresql":
            statement = postgresql_insert(MetricsSnapshotRecord).values(**values)
        elif dialect == "sqlite":
            statement = sqlite_insert(MetricsSnapshotRecord).values(**values)
        else:
            raise RuntimeError(f"unsupported metrics snapshot database dialect: {dialect}")
        statement = statement.on_conflict_do_update(
            index_elements=[MetricsSnapshotRecord.instance_id],
            set_={
                "service_name": service_name,
                "metrics_json": values["metrics_json"],
                "last_seen_at": now,
            },
        )
        session.execute(statement)
        session.execute(
            delete(MetricsSnapshotRecord).where(
                MetricsSnapshotRecord.last_seen_at < now - timedelta(days=7)
            )
        )
        session.commit()
        session.expire_all()
        return session.get(MetricsSnapshotRecord, instance_id)

    def list_active(self, session, stale_after_seconds: int = 60, now=None):
        if (
            not isinstance(stale_after_seconds, int)
            or isinstance(stale_after_seconds, bool)
            or stale_after_seconds < 1
        ):
            raise ValueError("stale_after_seconds must be a positive integer")
        now = now or datetime.now(UTC)
        cutoff = now - timedelta(seconds=stale_after_seconds)
        return list(
            session.scalars(
                select(MetricsSnapshotRecord)
                .where(MetricsSnapshotRecord.last_seen_at >= cutoff)
                .order_by(MetricsSnapshotRecord.service_name, MetricsSnapshotRecord.instance_id)
            )
        )


class MetricsSnapshotReporter:
    """Publishes process-local counters periodically using independent DB sessions."""

    def __init__(
        self,
        session_factory,
        instance_id: str,
        service_name: str,
        snapshot_provider: Callable[[], dict],
        interval_seconds: float = 15.0,
        service: MetricsSnapshotService | None = None,
    ):
        if interval_seconds <= 0:
            raise ValueError("metrics publish interval must be positive")
        self.session_factory = session_factory
        self.instance_id = instance_id
        self.service_name = service_name
        self.snapshot_provider = snapshot_provider
        self.interval_seconds = interval_seconds
        self.service = service or MetricsSnapshotService()
        self._stop_event = Event()
        self._thread: Thread | None = None

    def _publish(self):
        snapshot = self.snapshot_provider()
        with self.session_factory() as session:
            self.service.publish(session, self.instance_id, self.service_name, snapshot)

    def _run(self):
        while not self._stop_event.wait(self.interval_seconds):
            try:
                self._publish()
            except Exception:
                logger.exception(
                    "metrics_snapshot_publish_failed instance_id=%s service=%s",
                    self.instance_id,
                    self.service_name,
                )

    def start(self):
        if self._thread and self._thread.is_alive():
            raise RuntimeError("metrics snapshot reporter is already running")
        self._stop_event.clear()
        self._publish()
        self._thread = Thread(
            target=self._run,
            name=f"metrics-{self.instance_id}",
            daemon=True,
        )
        self._thread.start()

    def stop(self):
        if not self._thread:
            return
        self._stop_event.set()
        self._thread.join(timeout=max(self.interval_seconds + 5, 10))
        if self._thread.is_alive():
            logger.error("metrics_snapshot_shutdown_timeout instance_id=%s", self.instance_id)
            return
        try:
            self._publish()
        except Exception:
            logger.exception(
                "metrics_snapshot_final_publish_failed instance_id=%s service=%s",
                self.instance_id,
                self.service_name,
            )
        self._thread = None


@contextmanager
def timed(operation):
    started = time.perf_counter()
    try:
        yield
    finally:
        logger.info(
            "operation=%s duration_ms=%.2f", operation, (time.perf_counter() - started) * 1000
        )


def readiness(session):
    session.execute(text("SELECT 1"))
    return {"status": "ready", "database": "ok"}
