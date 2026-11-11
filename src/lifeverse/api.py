import hmac
import json
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from time import perf_counter
from uuid import UUID, uuid4

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request, Response
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .config import get_settings
from .db import SessionLocal, get_session
from .jobs import JobRecord, WorkerHeartbeatService
from .logging import configure_logging
from .observability import MetricsSnapshotReporter, MetricsSnapshotService, metrics, readiness
from .api_16_25 import router as simulation_router
from .services import (
    PlayerService,
    WorldService,
    EconomyService,
    CareerService,
    SkillService,
    InventoryService,
    PropertyService,
    TravelService,
    SocialService,
    NPCService,
    MissionService,
)

s = get_settings()
configure_logging(s.log_level)
logger = logging.getLogger("lifeverse.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    reporter = None
    try:
        if s.metrics_export_enabled:
            reporter = MetricsSnapshotReporter(
                SessionLocal,
                f"api-{uuid4().hex}",
                "api",
                metrics.snapshot,
                interval_seconds=s.metrics_publish_interval_seconds,
            )
            reporter.start()
        yield
    finally:
        if reporter:
            reporter.stop()


app = FastAPI(title=s.app_name, version="0.4.0", lifespan=lifespan)


@app.middleware("http")
async def collect_request_metrics(request: Request, call_next):
    started = perf_counter()
    status_code = 500
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    finally:
        duration_seconds = perf_counter() - started
        metrics.record_request(status_code, duration_seconds)
        logger.info(
            "http_request_completed method=%s status_code=%s duration_ms=%.2f",
            request.method,
            status_code,
            duration_seconds * 1000,
        )


app.include_router(simulation_router)
players = PlayerService()
world = WorldService()
economy = EconomyService()
careers = CareerService()
skills = SkillService()
inventory = InventoryService()
properties = PropertyService()
travel = TravelService()
social = SocialService()
npcs = NPCService()
missions = MissionService()


class RegisterRequest(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    provider: str | None = Field(default=None, max_length=32)
    external_id: str | None = Field(default=None, max_length=128)


class CharacterRequest(BaseModel):
    account_id: UUID
    name: str = Field(min_length=2, max_length=80)
    country_id: UUID | None = None
    city_id: UUID | None = None


class XPRequest(BaseModel):
    amount: int = Field(gt=0)


class ClockRequest(BaseModel):
    seconds: int = Field(ge=0)


class MoneyRequest(BaseModel):
    character_id: UUID
    amount: float = Field(gt=0)
    idempotency_key: str = Field(min_length=8, max_length=128)


class HireRequest(BaseModel):
    character_id: UUID
    job_id: UUID


class SkillXPRequest(BaseModel):
    character_id: UUID
    skill_id: UUID
    amount: int = Field(gt=0)


class ItemRequest(BaseModel):
    character_id: UUID
    item_id: UUID
    quantity: int = Field(gt=0)


class TravelRequest(BaseModel):
    character_id: UUID
    to_city_id: UUID
    departure_at: datetime
    minutes: int = Field(gt=0)


class RelationRequest(BaseModel):
    source: UUID
    target: UUID
    kind: str = Field(min_length=1, max_length=32)
    delta: int = Field(ge=-100, le=100)


class MissionStart(BaseModel):
    character_id: UUID
    mission_id: UUID


class MissionProgress(BaseModel):
    character_id: UUID
    mission_id: UUID
    amount: int = Field(gt=0)


def bad(fn):
    try:
        return fn()
    except ValueError as e:
        raise HTTPException(400, str(e)) from e


@app.get("/health/live")
def liveness():
    return {"status": "alive"}


@app.get("/health/ready")
def readiness_check(session: Session = Depends(get_session)):
    return readiness(session)


@app.get("/health")
def health(session: Session = Depends(get_session)):
    return readiness(session)


@app.get("/internal/metrics", include_in_schema=False)
def internal_metrics(
    authorization: str | None = Header(default=None),
    session: Session = Depends(get_session),
):
    if not s.metrics_export_enabled or not s.metrics_token:
        raise HTTPException(status_code=404, detail="not found")

    supplied_token = (
        authorization[7:]
        if authorization and authorization.startswith("Bearer ")
        else ""
    )
    if not hmac.compare_digest(supplied_token, s.metrics_token):
        raise HTTPException(
            status_code=401,
            detail="invalid metrics credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    snapshots = MetricsSnapshotService().list_active(
        session, stale_after_seconds=s.metrics_snapshot_ttl_seconds
    )
    headers = [
        ("lifeverse_http_requests_total", "Total HTTP requests", "counter"),
        ("lifeverse_http_requests_4xx_total", "HTTP 4xx responses", "counter"),
        ("lifeverse_http_requests_5xx_total", "HTTP 5xx responses", "counter"),
        (
            "lifeverse_http_request_duration_ms_total",
            "Cumulative HTTP request duration in milliseconds",
            "counter",
        ),
        (
            "lifeverse_http_request_duration_ms_max",
            "Maximum HTTP request duration in milliseconds since process start",
            "gauge",
        ),
        ("lifeverse_worker_jobs_completed_total", "Completed background jobs", "counter"),
        ("lifeverse_worker_jobs_failed_total", "Failed background job attempts", "counter"),
        ("lifeverse_worker_jobs_dead_total", "Jobs moved to dead-letter state", "counter"),
        ("lifeverse_worker_heartbeats_stale", "Workers with stale heartbeats", "gauge"),
        ("lifeverse_background_jobs_dead", "Current dead-letter job count", "gauge"),
        ("lifeverse_metrics_active_instances", "Processes with fresh metric snapshots", "gauge"),
    ]
    lines = []
    for name, help_text, metric_type in headers:
        lines.extend([f"# HELP {name} {help_text}", f"# TYPE {name} {metric_type}"])

    for record in snapshots:
        values = json.loads(record.metrics_json)
        labels = f'{{service="{record.service_name}",instance="{record.instance_id}"}}'
        if record.service_name == "api":
            lines.extend(
                [
                    f"lifeverse_http_requests_total{labels} {values.get('requests', 0)}",
                    f"lifeverse_http_requests_4xx_total{labels} {values.get('requests_4xx', 0)}",
                    f"lifeverse_http_requests_5xx_total{labels} {values.get('requests_5xx', 0)}",
                    f"lifeverse_http_request_duration_ms_total{labels} "
                    f"{values.get('request_duration_ms_total', 0)}",
                    f"lifeverse_http_request_duration_ms_max{labels} "
                    f"{values.get('request_duration_ms_max', 0)}",
                ]
            )
        else:
            lines.extend(
                [
                    f"lifeverse_worker_jobs_completed_total{labels} "
                    f"{values.get('jobs_completed', 0)}",
                    f"lifeverse_worker_jobs_failed_total{labels} "
                    f"{values.get('jobs_failed', 0)}",
                    f"lifeverse_worker_jobs_dead_total{labels} {values.get('jobs_dead', 0)}",
                ]
            )

    stale_workers = WorkerHeartbeatService().list_stale(
        session, stale_after_seconds=s.worker_heartbeat_stale_after_seconds
    )
    dead_jobs = session.scalar(
        select(func.count()).select_from(JobRecord).where(JobRecord.status == "dead")
    ) or 0
    lines.extend(
        [
            f"lifeverse_worker_heartbeats_stale {len(stale_workers)}",
            f"lifeverse_background_jobs_dead {dead_jobs}",
            f"lifeverse_metrics_active_instances {len(snapshots)}",
        ]
    )
    return Response(
        content="\n".join(lines) + "\n",
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )


@app.post("/accounts", status_code=201)
def register(payload: RegisterRequest, session: Session = Depends(get_session)):
    return bad(
        lambda: {
            "id": str(
                (
                    a := players.register(
                        session, payload.username, payload.provider, payload.external_id
                    )
                ).id
            ),
            "username": a.username,
        }
    )


@app.post("/characters", status_code=201)
def character(payload: CharacterRequest, session: Session = Depends(get_session)):
    return bad(
        lambda: (lambda c: {"id": str(c.id), "name": c.name, "level": c.level, "xp": c.xp})(
            players.create_character(
                session, payload.account_id, payload.name, payload.country_id, payload.city_id
            )
        )
    )


@app.post("/characters/{character_id}/xp")
def add_xp(character_id: UUID, payload: XPRequest, session: Session = Depends(get_session)):
    return bad(
        lambda: (lambda c: {"id": str(c.id), "level": c.level, "xp": c.xp})(
            players.add_xp(session, character_id, payload.amount)
        )
    )


@app.get("/countries")
def countries(session: Session = Depends(get_session)):
    return [
        {
            "id": str(x.id),
            "iso2": x.iso2,
            "iso3": x.iso3,
            "name": x.name,
            "currency": x.currency_code,
        }
        for x in world.list_countries(session)
    ]


@app.get("/cities")
def cities(
    country_id: UUID | None = None,
    q: str | None = Query(default=None, max_length=120),
    session: Session = Depends(get_session),
):
    return [
        {"id": str(x.id), "country_id": str(x.country_id), "name": x.name, "region": x.region}
        for x in world.list_cities(session, country_id, q)
    ]


@app.post("/world/advance")
def advance(payload: ClockRequest, session: Session = Depends(get_session)):
    return bad(
        lambda: (lambda c: {"world_time": c.world_time.isoformat(), "version": c.version})(
            world.advance(session, payload.seconds)
        )
    )


@app.get("/world/clock")
def clock(session: Session = Depends(get_session)):
    c = world.initialize(session)
    return {
        "world_time": c.world_time.isoformat(),
        "speed": str(c.speed),
        "paused": c.paused,
        "version": c.version,
    }


@app.get("/wallets/{character_id}")
def wallet(character_id: UUID, session: Session = Depends(get_session)):
    return bad(lambda: {"balance": str(economy.balance(session, character_id))})


@app.post("/wallets/credit")
def credit(payload: MoneyRequest, session: Session = Depends(get_session)):
    return bad(
        lambda: {
            "balance": str(
                economy.credit(
                    session, payload.character_id, payload.amount, payload.idempotency_key
                )
            )
        }
    )


@app.post("/wallets/debit")
def debit(payload: MoneyRequest, session: Session = Depends(get_session)):
    return bad(
        lambda: {
            "balance": str(
                economy.debit(
                    session, payload.character_id, payload.amount, payload.idempotency_key
                )
            )
        }
    )


@app.post("/employment")
def hire(payload: HireRequest, session: Session = Depends(get_session)):
    return bad(lambda: {"id": str(careers.hire(session, payload.character_id, payload.job_id).id)})


@app.delete("/employment/{character_id}")
def fire(character_id: UUID, session: Session = Depends(get_session)):
    return bad(lambda: {"status": careers.fire(session, character_id).status})


@app.post("/skills/xp")
def skill_xp(payload: SkillXPRequest, session: Session = Depends(get_session)):
    return bad(
        lambda: {
            "level": skills.add_xp(
                session, payload.character_id, payload.skill_id, payload.amount
            ).level
        }
    )


@app.post("/inventory/add")
def inventory_add(payload: ItemRequest, session: Session = Depends(get_session)):
    return bad(
        lambda: {
            "quantity": inventory.add(
                session, payload.character_id, payload.item_id, payload.quantity
            ).quantity
        }
    )


@app.post("/inventory/remove")
def inventory_remove(payload: ItemRequest, session: Session = Depends(get_session)):
    return bad(
        lambda: {
            "quantity": inventory.remove(
                session, payload.character_id, payload.item_id, payload.quantity
            ).quantity
        }
    )


@app.post("/travel")
def schedule_travel(payload: TravelRequest, session: Session = Depends(get_session)):
    return bad(
        lambda: {
            "id": str(
                travel.schedule(
                    session,
                    payload.character_id,
                    payload.to_city_id,
                    payload.departure_at,
                    payload.minutes,
                ).id
            )
        }
    )


@app.post("/social/relations")
def relation(payload: RelationRequest, session: Session = Depends(get_session)):
    return bad(
        lambda: {
            "score": social.relate(
                session, payload.source, payload.target, payload.kind, payload.delta
            ).score
        }
    )


@app.post("/missions/start")
def mission_start(payload: MissionStart, session: Session = Depends(get_session)):
    return bad(
        lambda: {"id": str(missions.start(session, payload.character_id, payload.mission_id).id)}
    )


@app.post("/missions/progress")
def mission_progress(payload: MissionProgress, session: Session = Depends(get_session)):
    return bad(
        lambda: {
            "state": missions.progress(
                session, payload.character_id, payload.mission_id, payload.amount, economy
            ).state
        }
    )
