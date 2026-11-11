from __future__ import annotations

import logging
import time
from contextlib import contextmanager
from math import isfinite
from threading import Lock

from sqlalchemy import text

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
