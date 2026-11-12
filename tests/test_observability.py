from concurrent.futures import ThreadPoolExecutor

import pytest

from lifeverse.observability import Metrics


def test_request_metrics_track_status_and_duration():
    metrics = Metrics()
    metrics.record_request(200, 0.01)
    metrics.record_request(404, 0.02)
    metrics.record_request(503, 0.03)

    snapshot = metrics.snapshot()
    assert snapshot["requests"] == 3
    assert snapshot["requests_4xx"] == 1
    assert snapshot["requests_5xx"] == 1
    assert snapshot["request_duration_ms_total"] == pytest.approx(60)
    assert snapshot["request_duration_ms_max"] == pytest.approx(30)


def test_metric_counters_are_thread_safe():
    metrics = Metrics()
    increments = 8_000

    with ThreadPoolExecutor(max_workers=8) as executor:
        list(executor.map(lambda _: metrics.inc("jobs_completed"), range(increments)))

    assert metrics.snapshot()["jobs_completed"] == increments


@pytest.mark.parametrize(
    ("status_code", "duration"),
    [
        (99, 0),
        (600, 0),
        (True, 0),
        (200, -0.1),
        (200, float("nan")),
        (200, float("inf")),
        (200, True),
    ],
)
def test_request_metrics_reject_invalid_values(status_code, duration):
    with pytest.raises(ValueError):
        Metrics().record_request(status_code, duration)


@pytest.mark.parametrize("amount", [-1, 1.5, True])
def test_counter_rejects_invalid_increments(amount):
    with pytest.raises(ValueError):
        Metrics().inc("jobs_completed", amount)


def test_counter_requires_metric_name():
    with pytest.raises(ValueError):
        Metrics().inc("")
