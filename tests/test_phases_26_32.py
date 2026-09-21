from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from lifeverse.api import app
from lifeverse.jobs import JobRecord, JobService, Worker
from lifeverse.observability import metrics, readiness
from lifeverse.production import profile


def test_job_idempotency_claim_retry_and_completion(session):
    service = JobService()
    first = service.enqueue(
        session,
        "test.echo",
        {"value": 7},
        idempotency_key="test-job-unique",
        max_attempts=2,
    )
    same = service.enqueue(
        session,
        "test.echo",
        {"value": 9},
        idempotency_key="test-job-unique",
        max_attempts=2,
    )
    assert same.id == first.id
    worker = Worker(service=service, worker_id="worker-a")
    result = worker.run_once(session, {"test.echo": lambda s, p: p["value"]})
    assert result == 7
    assert session.get(JobRecord, first.id).status == "completed"


def test_job_recovery_and_dead_letter(session):
    service = JobService()
    row = service.enqueue(
        session, "test.fail", run_at=datetime.now(UTC), idempotency_key="dead-letter", max_attempts=1
    )
    claimed = service.claim(session, "worker-a")
    assert claimed.id == row.id
    failed = service.fail(session, row.id, "worker-a", "boom")
    assert failed.status == "dead"

    stale = service.enqueue(
        session, "test.stale", run_at=datetime.now(UTC), idempotency_key="stale-job"
    )
    claimed = service.claim(session, "worker-a")
    claimed.locked_at = datetime.now(UTC) - timedelta(minutes=10)
    session.commit()
    recovered = service.recover_expired(session, lease_seconds=60)
    assert stale.id in {x.id for x in recovered}
    assert session.get(JobRecord, stale.id).status == "queued"


def test_readiness_metrics_and_deployment_profiles(session):
    assert readiness(session)["status"] == "ready"
    metrics.inc("requests")
    assert metrics.snapshot()["requests"] >= 1
    assert profile("local").scheduler == "worker loop"
    assert profile("railway").process_model == "api+worker"


def test_health_endpoint_is_database_backed():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["database"] == "ok"


def test_job_failure_retries_until_dead(session):
    service = JobService()
    row = service.enqueue(
        session,
        "test.retry",
        run_at=datetime.now(UTC),
        idempotency_key="retry-job",
        max_attempts=2,
    )
    claimed = service.claim(session, "worker-a")
    retry = service.fail(session, claimed.id, "worker-a", "temporary", retry_delay_seconds=0)
    assert retry.status == "queued"
    claimed = service.claim(session, "worker-a")
    dead = service.fail(session, claimed.id, "worker-a", "permanent", retry_delay_seconds=0)
    assert dead.status == "dead"
    assert dead.attempts == 2
