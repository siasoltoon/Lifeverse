from __future__ import annotations

import argparse
import logging
import time
from uuid import UUID

from .db import SessionLocal
from .jobs import Worker, WorkerHeartbeatReporter
from .services import TravelService
from .services_16_25 import BusinessService, EventService


def event_dispatch(session, payload):
    return [str(x.id) for x in EventService().dispatch_due(session)]


def business_payroll(session, payload):
    return str(
        BusinessService()
        .payroll(session, UUID(payload["business_id"]), payload["idempotency_key"])
        .id
    )


def travel_complete(session, payload):
    return str(TravelService().complete(session, UUID(payload["travel_id"])).id)


logger = logging.getLogger("lifeverse.worker")


def main():
    parser = argparse.ArgumentParser(description="LifeVerse persistent background worker")
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--interval", type=float, default=1.0)
    parser.add_argument("--heartbeat-interval", type=float, default=15.0)
    args = parser.parse_args()
    if args.interval <= 0:
        parser.error("--interval must be positive")
    if args.heartbeat_interval <= 0:
        parser.error("--heartbeat-interval must be positive")

    worker = Worker()
    handlers = {
        "event.dispatch": event_dispatch,
        "business.payroll": business_payroll,
        "travel.complete": travel_complete,
    }
    reporter = WorkerHeartbeatReporter(
        SessionLocal,
        worker.worker_id,
        lambda: worker.current_job_id,
        interval_seconds=args.heartbeat_interval,
    )
    reporter.start()
    try:
        while True:
            with SessionLocal() as session:
                worker.run_once(session, handlers)
            if args.once:
                return
            time.sleep(args.interval)
    except KeyboardInterrupt:
        logger.info("worker_shutdown_requested worker_id=%s", worker.worker_id)
    finally:
        reporter.stop()


if __name__ == "__main__":
    main()
