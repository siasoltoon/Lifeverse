from __future__ import annotations

import argparse
import time
from uuid import UUID

from .db import SessionLocal
from .jobs import Worker
from .services import TravelService
from .services_16_25 import BusinessService, EventService


def event_dispatch(session, payload):
    return [str(x.id) for x in EventService().dispatch_due(session)]


def business_payroll(session, payload):
    return str(BusinessService().payroll(session, UUID(payload["business_id"]), payload["idempotency_key"]).id)


def travel_complete(session, payload):
    return str(TravelService().complete(session, UUID(payload["travel_id"])).id)


def main():
    parser = argparse.ArgumentParser(description="LifeVerse persistent background worker")
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--interval", type=float, default=1.0)
    args = parser.parse_args()
    worker = Worker()
    handlers = {
        "event.dispatch": event_dispatch,
        "business.payroll": business_payroll,
        "travel.complete": travel_complete,
    }
    while True:
        with SessionLocal() as session:
            worker.run_once(session, handlers)
        if args.once:
            return
        time.sleep(max(0.1, args.interval))


if __name__ == "__main__":
    main()
