from datetime import UTC, datetime, timedelta
from time import sleep

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from lifeverse.db import Base
from lifeverse.jobs import (
    JobService,
    Worker,
    WorkerHeartbeat,
    WorkerHeartbeatReporter,
    WorkerHeartbeatService,
)


def test_worker_heartbeat_upsert_and_stale_detection(session):
    service = WorkerHeartbeatService()
    started = datetime(2026, 11, 12, 10, 0, tzinfo=UTC)

    first = service.heartbeat(session, "worker-test", now=started)
    second = service.heartbeat(
        session,
        "worker-test",
        now=started + timedelta(seconds=30),
    )

    assert first.worker_id == second.worker_id == "worker-test"
    assert second.status == "running"
    assert second.started_at.replace(tzinfo=UTC) == started
    assert second.last_seen_at.replace(tzinfo=UTC) == started + timedelta(seconds=30)

    stale = service.list_stale(
        session,
        stale_after_seconds=20,
        now=started + timedelta(seconds=60),
    )
    assert [worker.worker_id for worker in stale] == ["worker-test"]

    stopped = service.stop(session, "worker-test", now=started + timedelta(seconds=61))
    assert stopped.status == "stopped"
    assert stopped.stopped_at.replace(tzinfo=UTC) == started + timedelta(seconds=61)
    assert service.list_stale(
        session,
        stale_after_seconds=20,
        now=started + timedelta(minutes=5),
    ) == []


def test_worker_exposes_current_job_only_while_handler_runs(session):
    service = JobService()
    job = service.enqueue(
        session,
        "test.observe-current-job",
        {"value": "ok"},
        idempotency_key="heartbeat-current-job",
    )
    worker = Worker(service=service, worker_id="worker-current-job")

    def handler(current_session, payload):
        assert worker.current_job_id == job.id
        return payload["value"]

    assert worker.run_once(session, {"test.observe-current-job": handler}) == "ok"
    assert worker.current_job_id is None


def test_heartbeat_reporter_persists_and_marks_clean_shutdown(tmp_path):
    database_path = tmp_path / "worker-heartbeat.db"
    engine = create_engine(f"sqlite:///{database_path}")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)
    reporter = WorkerHeartbeatReporter(
        session_factory,
        "worker-reporter",
        lambda: None,
        interval_seconds=0.01,
    )

    try:
        reporter.start()
        sleep(0.03)
    finally:
        reporter.stop()

    with session_factory() as session:
        heartbeat = session.get(WorkerHeartbeat, "worker-reporter")
        assert heartbeat is not None
        assert heartbeat.status == "stopped"
        assert heartbeat.stopped_at is not None

    Base.metadata.drop_all(engine)
    engine.dispose()
