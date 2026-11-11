from fastapi.testclient import TestClient

from lifeverse.api import app
from lifeverse.observability import metrics


def test_health_and_request_metrics():
    client = TestClient(app)
    before = metrics.snapshot()

    response = client.get("/health")
    not_found = client.get("/route-that-does-not-exist")

    after = metrics.snapshot()
    assert response.json() == {"status": "ready", "database": "ok"}
    assert not_found.status_code == 404
    assert after["requests"] == before["requests"] + 2
    assert after["requests_4xx"] == before["requests_4xx"] + 1
    assert after["requests_5xx"] == before["requests_5xx"]
    assert after["request_duration_ms_total"] >= before["request_duration_ms_total"]


def test_liveness_probe_does_not_require_database():
    response = TestClient(app).get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}
