from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from uuid import UUID
from .config import get_settings
from .db import get_session
from .logging import configure_logging
from .services import PlayerService, WorldService

s = get_settings()
configure_logging(s.log_level)
app = FastAPI(title=s.app_name, version="0.1.0")
players = PlayerService()
world = WorldService()


class RegisterRequest(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    provider: str | None = Field(default=None, max_length=32)
    external_id: str | None = Field(default=None, max_length=128)


class CharacterRequest(BaseModel):
    account_id: UUID
    name: str = Field(min_length=2, max_length=80)
    country_id: UUID | None = None
    city_id: UUID | None = None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/accounts", status_code=201)
def register(payload: RegisterRequest, session: Session = Depends(get_session)):
    try:
        a = players.register(session, payload.username, payload.provider, payload.external_id)
        return {"id": str(a.id), "username": a.username}
    except ValueError as e:
        raise HTTPException(400, str(e)) from e


@app.post("/characters", status_code=201)
def character(payload: CharacterRequest, session: Session = Depends(get_session)):
    try:
        c = players.create_character(
            session, payload.account_id, payload.name, payload.country_id, payload.city_id
        )
        return {"id": str(c.id), "name": c.name, "level": c.level, "xp": c.xp}
    except ValueError as e:
        raise HTTPException(400, str(e)) from e


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
