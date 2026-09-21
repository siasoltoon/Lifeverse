# Operations Runbook

## Health

GET /health performs a real database connectivity check. status=ready and database=ok are required before serving traffic.

## Background jobs

Jobs are persisted in background_jobs. A worker claims one due job with a lease. Successful work becomes completed; retryable failures return to queued; exhausted failures become dead.

Useful operational fields are job_type, status, attempts, locked_by, locked_at, last_error and updated_at.

## Incident recovery

1. Check API health.
2. Check database connectivity and migration version.
3. Inspect background_jobs for running rows with stale locked_at.
4. Restart or replace the worker if necessary; stale leases are recoverable.
5. Inspect dead jobs and their errors before replaying.
6. Replay only with a deliberate idempotency key and validated payload.

## Security

Authentication sessions are revocable, rate limiting is persistent, and authoritative mutations remain in services. Client adapters must not mutate authoritative state.

## Verification

Before release run the complete test suite and alembic upgrade head. Production readiness requires the final audit and E2E gates to pass.
