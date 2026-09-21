from __future__ import annotations

import logging
import time
from contextlib import contextmanager

from sqlalchemy import text

logger = logging.getLogger("lifeverse.observability")


class Metrics:
    def __init__(self):
        self._values = {"jobs_completed": 0, "jobs_failed": 0, "jobs_dead": 0, "requests": 0}

    def inc(self, name, amount=1):
        if name not in self._values:
            self._values[name] = 0
        self._values[name] += amount

    def snapshot(self):
        return dict(self._values)


metrics = Metrics()


@contextmanager
def timed(operation):
    started = time.perf_counter()
    try:
        yield
    finally:
        logger.info("operation=%s duration_ms=%.2f", operation, (time.perf_counter() - started) * 1000)


def readiness(session):
    session.execute(text("SELECT 1"))
    return {"status": "ready", "database": "ok"}
