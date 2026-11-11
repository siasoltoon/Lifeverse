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
- `worker_heartbeats`: durable per-worker status, last-seen time, and optional current job.

Metric updates are thread-safe. Request logs include method, status code, and duration. They intentionally omit URL paths, query strings, request bodies, and client addresses to avoid high-cardinality labels and unnecessary personal-data collection.

## Centralized metrics export

Metrics remain inexpensive process-local counters during normal request/job execution. When `LIFEVERSE_METRICS_EXPORT_ENABLED=true`, each API and worker process publishes a snapshot every configured interval to `operational_metric_snapshots` using an independent database session. The API exposes fresh per-process snapshots as Prometheus text at `GET /internal/metrics`.

The endpoint is disabled by default and requires an Authorization Bearer token of at least 32 characters. Configure the same `LIFEVERSE_METRICS_TOKEN` in the API and Prometheus secret file. Snapshots older than the configured TTL are excluded; old rows are pruned after seven days. Metrics are labelled only by fixed service name and generated process instance ID; request paths, user IDs, payloads and IP addresses are never labels.

The database is the cross-process snapshot transport, not a historical time-series store. Prometheus retains and queries the scraped series. If the database is unavailable, the exporter returns an error and Prometheus marks the target scrape as failed.

## Prometheus and Alertmanager

An optional Docker Compose monitoring profile is provided:

1. Create `secrets/metrics_token` with the exact same random token configured as `LIFEVERSE_METRICS_TOKEN` in the ignored `.env` file.
2. Set `LIFEVERSE_METRICS_EXPORT_ENABLED=true`.
3. Create `secrets/alert_webhook_url` containing an Alertmanager-compatible webhook receiver URL.
4. Start the stack with `docker compose --profile monitoring up --build -d`.

Prometheus and Alertmanager ports bind to localhost only. The metrics endpoint itself is bearer-token protected. The `secrets/` directory is ignored by Git and must not be committed.

Alert rules cover exporter unavailability, sustained HTTP 5xx ratio, sustained average request latency, stale worker heartbeats and dead-letter jobs. Alertmanager delivers notifications to the configured generic webhook endpoint. The receiver must accept Alertmanager's webhook payload; this is not automatically a Slack/Discord-specific payload adapter.

## Alerting limits

Alert rules and delivery configuration are implemented, but alerts are not considered active until a real receiver URL is configured and a delivery test succeeds. Thresholds are initial operational defaults and must be reviewed against agreed service objectives.

A stale heartbeat is evidence that a worker has stopped reporting; it is not by itself proof that a particular job failed. The heartbeat reporter uses its own database session so long-running handlers do not block liveness updates.

Backup/restore/PITR and CA/hostname certificate validation remain deferred by decision.
