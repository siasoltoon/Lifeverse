# Observability and Health Checks

## Health endpoints

- `GET /health/live` is a process liveness probe. It does not access the database.
- `GET /health/ready` checks database connectivity with a lightweight `SELECT 1`.
- `GET /health` remains a compatibility alias for database readiness.

A successful liveness response does not imply that the application can serve database-backed requests. Deployments should use readiness for traffic admission and liveness for process supervision.

## Request and worker telemetry

The application records these in-process metrics:

- `requests`: total HTTP requests.
- `requests_4xx` and `requests_5xx`: client and server error responses.
- `request_duration_ms_total` and `request_duration_ms_max`: aggregate and maximum request duration.
- `jobs_completed`, `jobs_failed`, and `jobs_dead`: worker outcomes.
- `worker_heartbeats`: durable per-worker status, last-seen time, and optional current job. Each worker writes an initial heartbeat, refreshes it periodically using an independent database session, and marks a clean shutdown as stopped.

Metric updates are thread-safe. Request logs include method, status code, and duration. They intentionally omit URL paths, query strings, request bodies, and client addresses to avoid high-cardinality labels and unnecessary personal-data collection.

## Important deployment limitation

These metrics are process-local and reset when a process restarts. They are not shared between multiple API/worker processes, are not persisted in PostgreSQL, and are not currently exported to Prometheus or another collector. Therefore they are useful for in-process diagnostics and tests, but must not be treated as a complete production monitoring or alerting system.

Do not expose a metrics endpoint publicly until an authenticated exporter/collector design is implemented. A future exporter must account for separate API and worker processes and multiple replicas rather than presenting one process's counters as global totals.

## Alerting status

Worker heartbeats are durable and can be queried for stale running workers. A stale heartbeat is evidence that a worker has stopped reporting; it is not by itself proof that a particular job failed. The heartbeat reporter uses its own database session so long-running handlers do not block liveness updates.

No external alert delivery is configured by this change. Candidate alert conditions for a future centralized monitoring integration:

- Readiness probe continuously failing.
- Sustained HTTP 5xx ratio above the service's agreed error budget.
- Sustained request latency above the service's agreed SLO.
- Any job entering the dead-letter state.
- Worker heartbeat becoming stale (a durable worker heartbeat is not yet implemented).

Thresholds and notification destinations must be selected with the deployment owner and validated end-to-end before alerts are described as active.
