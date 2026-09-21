from datetime import datetime
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .db import get_session
from .services import EconomyService, InventoryService
from .services_16_25 import (
    AIIntentService,
    BusinessService,
    EventService,
    LawService,
    LocalizationService,
    MarketService,
    SecurityService,
    AuthService,
)

security = SecurityService()\n\n\ndef rate_limit(request: Request, session: Session = Depends(get_session)):\n    key = "api:" + (request.client.host if request.client else "unknown")\n    if not security.allow(session, key, 120, 60):\n        raise HTTPException(429, "rate limit exceeded")\n\n\nrouter = APIRouter(prefix="/v1", dependencies=[Depends(rate_limit)])
events = EventService()
businesses = BusinessService()
market = MarketService()
law = LawService()
ai_intents = AIIntentService()
localization = LocalizationService()
economy = EconomyService()
inventory = InventoryService()


def bad(fn):
    try:
        return fn()
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


class EventRequest(BaseModel):
    event_type: str = Field(min_length=1, max_length=64)
    scheduled_at: datetime
    payload: dict = Field(default_factory=dict)


class BusinessRequest(BaseModel):
    owner_character_id: UUID
    city_id: UUID
    name: str = Field(min_length=1, max_length=120)
    kind: str = Field(min_length=1, max_length=64)
    currency_id: UUID\n    capital: Decimal = Field(default=Decimal("0"), ge=0)


class ListingRequest(BaseModel):
    seller_character_id: UUID
    item_id: UUID
    quantity: int = Field(gt=0)
    unit_price: Decimal = Field(gt=0)


class MarketBuyRequest(BaseModel):
    buyer_character_id: UUID
    quantity: int = Field(gt=0)
    idempotency_key: str = Field(min_length=8, max_length=128)


class IntentRequest(BaseModel):
    actor_id: UUID | None = None
    intent_type: str = Field(min_length=1, max_length=64)
    payload: dict = Field(default_factory=dict)


class TranslationRequest(BaseModel):
    locale: str = Field(min_length=2, max_length=8)
    key: str = Field(min_length=1, max_length=128)
    value: str = Field(min_length=1)


@router.post("/events", status_code=201)
def schedule_event(payload: EventRequest, session: Session = Depends(get_session)):
    return bad(lambda: {"id": str(events.schedule(session, payload.event_type, payload.scheduled_at, payload.payload).id)})


@router.post("/events/dispatch")
def dispatch_events(session: Session = Depends(get_session)):
    return bad(lambda: [{"id": str(x.id), "type": x.event_type, "state": x.state} for x in events.dispatch_due(session)])


@router.post("/businesses", status_code=201)
def create_business(payload: BusinessRequest, session: Session = Depends(get_session)):
    return bad(lambda: {"id": str(businesses.create(
        session, payload.owner_character_id, payload.city_id, payload.name, payload.kind, payload.currency_id, payload.capital, economy
    ).id)})


@router.post("/market/listings", status_code=201)
def create_listing(payload: ListingRequest, session: Session = Depends(get_session)):
    return bad(lambda: {"id": str(market.list_item(
        session, payload.seller_character_id, payload.item_id, payload.quantity, payload.unit_price
    ).id)})


@router.post("/market/listings/{listing_id}/buy")
def buy_listing(listing_id: UUID, payload: MarketBuyRequest, session: Session = Depends(get_session)):
    return bad(lambda: {"id": str(market.buy(
        session, payload.buyer_character_id, listing_id, payload.quantity, payload.idempotency_key, economy, inventory
    ).id)})


@router.post("/law/cases", status_code=201)
def create_case(character_id: UUID, category: str, severity: int, session: Session = Depends(get_session)):
    return bad(lambda: {"id": str(law.report(session, character_id, category, severity).id)})


@router.post("/ai/intents", status_code=201)
def propose_intent(payload: IntentRequest, session: Session = Depends(get_session)):
    return bad(lambda: {"id": str(ai_intents.propose(session, payload.actor_id, payload.intent_type, payload.payload).id)})


@router.post("/ai/intents/{intent_id}/validate")
def validate_intent(intent_id: UUID, session: Session = Depends(get_session)):
    return bad(lambda: (lambda row: {"id": str(row.id), "state": row.state})(ai_intents.validate(session, intent_id)))


@router.post("/localization")
def set_translation(payload: TranslationRequest, session: Session = Depends(get_session)):
    return bad(lambda: {"key": localization.set(session, payload.locale, payload.key, payload.value).key})


@router.get("/localization/{locale}/{key}")
def get_translation(locale: str, key: str, session: Session = Depends(get_session)):
    return {"locale": locale, "key": key, "value": localization.translate(session, locale, key)}


@router.get("/ui/config")
def ui_config(locale: str = Query("fa"), session: Session = Depends(get_session)):
    if locale not in {"fa", "en"}:
        raise HTTPException(400, "unsupported locale")
    return {
        "locale": locale,
        "fallback_locale": "en",
        "api_version": "v1",
        "features": {"events": True, "business": True, "market": True, "law": True, "ai_intents": True},
    }


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=12, max_length=256)


class PasswordRequest(BaseModel):
    password: str = Field(min_length=12, max_length=256)


def bearer(authorization: str | None):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "bearer token required")
    return authorization[7:].strip()


@router.post("/auth/login")
def login(payload: LoginRequest, session: Session = Depends(get_session)):
    return bad(lambda: (lambda result: {"access_token": result[0], "expires_at": result[1].expires_at.isoformat()})(
        auth.login(session, payload.username, payload.password)
    ))


@router.post("/auth/password")
def set_password(
    payload: PasswordRequest,
    authorization: str | None = Header(default=None),
    session: Session = Depends(get_session),
):
    token = bearer(authorization)
    return bad(lambda: (lambda account_id: {"account_id": str(auth.set_password(session, account_id, payload.password).id)})(
        auth.authenticate(session, token)
    ))


@router.post("/auth/logout")
def logout(authorization: str | None = Header(default=None), session: Session = Depends(get_session)):
    token = bearer(authorization)
    auth.revoke(session, token)
    return {"status": "revoked"}
