from __future__ import annotations

import argparse
import time

from .db import SessionLocal
from .jobs import Worker


def main():
    parser = argparse.ArgumentParser(description="LifeVerse persistent background worker")
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--interval", type=float, default=1.0)
    args = parser.parse_args()
    worker = Worker()
    handlers = {}
    while True:
        with SessionLocal() as session:
            worker.run_once(session, handlers)
        if args.once:
            return
        time.sleep(max(0.1, args.interval))


if __name__ == "__main__":
    main()
