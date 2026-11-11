import json
import re
from datetime import UTC, datetime, timedelta
from pathlib import Path
from threading import Event

import pytest
import yaml
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from lifeverse import api
from lifeverse.api import app
from lifeverse.config import Settings
from lifeverse.db import Base, get_session
from lifeverse.observability import (
    MetricsSnapshotRecord,
    MetricsSnapshotReporter,
    MetricsSnapshotService,
)

ROOT = Path(__file__).resolve().parents[1]


def test_metric_snapshots_upsert_per_process_and_filter_stale_rows(session):
    service = MetricsSnapshotService()
    now = datetime(2026, 11, 12, 12, 0, tzinfo=UTC)
    service.publish(session, "api-one", "api", {"requests": 3}, now=now)
    service.publish(
        session, "worker-one", "worker", {"jobs_completed": 4}, now=now + timedelta(seconds=50)
    )
    updated = service.publish(
        session, "api-one", "api", {"requests": 7}, now=now + timedelta(seconds=30)
    )

    assert updated.service_name == "api"
    assert json.loads(updated.metrics_json) == {"requests": 7}
    assert (
        len(service.list_active(session, stale_after_seconds=60, now=now + timedelta(seconds=55)))
        == 2
    )
    assert [
        row.instance_id
        for row in service.list_active(
            session, stale_after_seconds=20, now=now + timedelta(seconds=60)
        )
    ] == ["worker-one"]


@pytest.mark.parametrize(
    ("instance_id", "service_name", "snapshot"),
    [
        ("", "api", {}),
        ("invalid instance", "api", {}),
        ("api-one", "scheduler", {}),
        ("api-one", "api", {"requests": -1}),
        ("api-one", "api", {"requests": float("nan")}),
        ("api-one", "api", {"Bad Name": 1}),
    ],
)
def test_metric_snapshot_rejects_invalid_data(session, instance_id, service_name, snapshot):
    with pytest.raises(ValueError):
        MetricsSnapshotService().publish(session, instance_id, service_name, snapshot)


def test_metrics_snapshot_reporter_publishes_updates_and_stops(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'metrics.db'}")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)
    value = {"requests": 1}
    updated = Event()

    def snapshot_provider():
        if value["requests"] == 2:
            updated.set()
        return value.copy()

    reporter = MetricsSnapshotReporter(
        session_factory,
        "api-reporter",
        "api",
        snapshot_provider,
        interval_seconds=0.01,
    )
    try:
        reporter.start()
        value["requests"] = 2
        assert updated.wait(1)
    finally:
        reporter.stop()

    with session_factory() as session:
        record = session.get(MetricsSnapshotRecord, "api-reporter")
        assert record is not None
        assert json.loads(record.metrics_json) == {"requests": 2}

    Base.metadata.drop_all(engine)
    engine.dispose()


def test_metrics_export_settings_require_secure_configuration():
    defaults = Settings(_env_file=None, _env_prefix="TEST_")
    assert defaults.metrics_export_enabled is False
    assert defaults.metrics_token is None

    with pytest.raises(ValidationError):
        Settings(_env_file=None, _env_prefix="TEST_", metrics_export_enabled=True)
    with pytest.raises(ValidationError):
        Settings(_env_file=None, _env_prefix="TEST_", metrics_token="too-short")
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            _env_prefix="TEST_",
            metrics_publish_interval_seconds=30,
            metrics_snapshot_ttl_seconds=30,
        )


def test_internal_metrics_endpoint_requires_bearer_token_and_exports_snapshots(
    session, monkeypatch
):
    token = "m" * 40
    monkeypatch.setattr(api.s, "metrics_export_enabled", True)
    monkeypatch.setattr(api.s, "metrics_token", token)
    MetricsSnapshotService().publish(
        session,
        "api-test-instance",
        "api",
        {
            "requests": 12,
            "requests_4xx": 2,
            "requests_5xx": 1,
            "request_duration_ms_total": 125.0,
            "request_duration_ms_max": 40.0,
        },
    )

    def override_session():
        yield session

    app.dependency_overrides[get_session] = override_session
    try:
        client = TestClient(app)
        unauthorized = client.get("/internal/metrics")
        response = client.get("/internal/metrics", headers={"Authorization": f"Bearer {token}"})
    finally:
        app.dependency_overrides.pop(get_session, None)

    assert unauthorized.status_code == 401
    assert response.status_code == 200
    assert (
        'lifeverse_http_requests_total{service="api",process_instance="api-test-instance"} 12'
        in response.text
    )
    assert "lifeverse_worker_heartbeats_stale 0" in response.text


def test_prometheus_and_alertmanager_configs_are_valid_yaml_and_wired():
    prometheus = yaml.safe_load((ROOT / "monitoring/prometheus.yml").read_text())
    alert_rules = yaml.safe_load((ROOT / "monitoring/alert_rules.yml").read_text())
    alertmanager = yaml.safe_load((ROOT / "monitoring/alertmanager.yml").read_text())

    scrape = prometheus["scrape_configs"][0]
    assert scrape["metrics_path"] == "/internal/metrics"
    assert scrape["authorization"]["credentials_file"] == "/run/secrets/metrics_token"
    assert prometheus["alerting"]["alertmanagers"][0]["static_configs"][0]["targets"] == [
        "alertmanager:9093"
    ]

    alerts = {rule["alert"] for group in alert_rules["groups"] for rule in group["rules"]}
    assert {
        "LifeVerseMetricsExporterUnavailable",
        "LifeVerseHighHTTP5xxRate",
        "LifeVerseHighAverageRequestLatency",
        "LifeVerseWorkerHeartbeatStale",
        "LifeVerseDeadLetterJobs",
    } <= alerts

    receiver = alertmanager["receivers"][0]["webhook_configs"][0]
    assert receiver["url_file"] == "/run/secrets/alert_webhook_url"
    assert receiver["send_resolved"] is True


def test_compose_monitoring_services_are_opt_in_and_localhost_bound():
    compose = yaml.safe_load((ROOT / "docker-compose.yml").read_text())
    assert compose["services"]["prometheus"]["profiles"] == ["monitoring"]
    assert compose["services"]["alertmanager"]["profiles"] == ["monitoring"]
    assert "127.0.0.1:9090:9090" in compose["services"]["prometheus"]["ports"]
    assert "127.0.0.1:9093:9093" in compose["services"]["alertmanager"]["ports"]



def test_alembic_revision_ids_fit_version_column_limit():
    versions = ROOT / "migrations/versions"
    revision_pattern = re.compile(r"^revision = [\"']([^\"']+)[\"']", re.MULTILINE)
    for migration_path in versions.glob("*.py"):
        match = revision_pattern.search(migration_path.read_text())
        if match:
            assert len(match.group(1)) <= 32, migration_path.name
