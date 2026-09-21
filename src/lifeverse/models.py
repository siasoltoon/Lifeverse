from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base

class Account(Base):
    __tablename__ = "accounts"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    identities: Mapped[list["AccountIdentity"]] = relationship(
        back_populates="account", cascade="all, delete-orphan"
    )
    characters: Mapped[list["Character"]] = relationship(
        back_populates="account", cascade="all, delete-orphan"
    )


class AccountIdentity(Base):
    __tablename__ = "account_identities"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    account_id: Mapped[UUID] = mapped_column(
        ForeignKey("accounts.id", ondelete="CASCADE"), index=True
    )
    provider: Mapped[str] = mapped_column(String(32))
    external_id: Mapped[str] = mapped_column(String(128))
    account: Mapped[Account] = relationship(back_populates="identities")
    __table_args__ = (
        UniqueConstraint("provider", "external_id", name="uq_identity_provider_external"),
    )


class Currency(Base):
    __tablename__ = "currencies"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    code: Mapped[str] = mapped_column(String(3), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(80))
    symbol: Mapped[str] = mapped_column(String(8))


class Country(Base):
    __tablename__ = "countries"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    iso2: Mapped[str] = mapped_column(String(2), unique=True, index=True)
    iso3: Mapped[str] = mapped_column(String(3), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    capital: Mapped[str] = mapped_column(String(120))
    region: Mapped[str] = mapped_column(String(80))
    currency_code: Mapped[str] = mapped_column(String(3))
    languages: Mapped[str] = mapped_column(Text)
    population: Mapped[int] = mapped_column(Integer)
    cost_of_living_index: Mapped[Decimal] = mapped_column(Numeric(8, 2))
    cities: Mapped[list["City"]] = relationship(
        back_populates="country", cascade="all, delete-orphan"
    )


class City(Base):
    __tablename__ = "cities"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    country_id: Mapped[UUID] = mapped_column(
        ForeignKey("countries.id", ondelete="RESTRICT"), index=True
    )
    name: Mapped[str] = mapped_column(String(120))
    region: Mapped[str] = mapped_column(String(120))
    population: Mapped[int] = mapped_column(Integer)
    cost_of_living_index: Mapped[Decimal] = mapped_column(Numeric(8, 2))
    country: Mapped[Country] = relationship(back_populates="cities")
    __table_args__ = (
        UniqueConstraint("country_id", "name", name="uq_city_country_name"),
        Index("ix_city_name", "name"),
    )


class Character(Base):
    __tablename__ = "characters"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    account_id: Mapped[UUID] = mapped_column(
        ForeignKey("accounts.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(80))
    level: Mapped[int] = mapped_column(Integer, default=1)
    xp: Mapped[int] = mapped_column(Integer, default=0)
    reputation: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(32), default="active")
    country_id: Mapped[UUID | None] = mapped_column(ForeignKey("countries.id", ondelete="RESTRICT"))
    city_id: Mapped[UUID | None] = mapped_column(ForeignKey("cities.id", ondelete="RESTRICT"))
    account: Mapped[Account] = relationship(back_populates="characters")


class Wallet(Base):
    __tablename__ = "wallets"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    character_id: Mapped[UUID] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE"), unique=True
    )
    currency_id: Mapped[UUID] = mapped_column(ForeignKey("currencies.id", ondelete="RESTRICT"))
    balance: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0"))


class WorldClock(Base):
    __tablename__ = "world_clock"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    world_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    speed: Mapped[Decimal] = mapped_column(Numeric(8, 2), default=Decimal("1"))
    paused: Mapped[bool] = mapped_column(default=False)
    version: Mapped[int] = mapped_column(Integer, default=1)


class WorldState(Base):
    __tablename__ = "world_state"
    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    value: Mapped[str] = mapped_column(Text, default="")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class Job(Base):
    __tablename__ = "jobs"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    code: Mapped[str] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(String(120))
    min_level: Mapped[int] = mapped_column(Integer, default=1)
    base_salary: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0"))
    work_hours: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("8"))


class Employment(Base):
    __tablename__ = "employments"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    character_id: Mapped[UUID] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE"), unique=True
    )
    job_id: Mapped[UUID] = mapped_column(ForeignKey("jobs.id", ondelete="RESTRICT"))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(32), default="active")


class Skill(Base):
    __tablename__ = "skills"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    code: Mapped[str] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(String(120))
    max_level: Mapped[int] = mapped_column(Integer, default=100)


class CharacterSkill(Base):
    __tablename__ = "character_skills"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    character_id: Mapped[UUID] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE"), index=True
    )
    skill_id: Mapped[UUID] = mapped_column(ForeignKey("skills.id", ondelete="RESTRICT"))
    level: Mapped[int] = mapped_column(Integer, default=0)
    xp: Mapped[int] = mapped_column(Integer, default=0)
    __table_args__ = (UniqueConstraint("character_id", "skill_id", name="uq_character_skill"),)


class Item(Base):
    __tablename__ = "items"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    code: Mapped[str] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(String(120))
    kind: Mapped[str] = mapped_column(String(32), default="generic")
    weight: Mapped[Decimal] = mapped_column(Numeric(8, 3), default=Decimal("0"))
    base_price: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0"))


class Inventory(Base):
    __tablename__ = "inventories"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    character_id: Mapped[UUID] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE"), index=True
    )
    item_id: Mapped[UUID] = mapped_column(ForeignKey("items.id", ondelete="RESTRICT"))
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    __table_args__ = (
        UniqueConstraint("character_id", "item_id", name="uq_inventory_character_item"),
    )


class Property(Base):
    __tablename__ = "properties"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    city_id: Mapped[UUID] = mapped_column(ForeignKey("cities.id", ondelete="RESTRICT"), index=True)
    kind: Mapped[str] = mapped_column(String(32))
    name: Mapped[str] = mapped_column(String(120))
    capacity: Mapped[int] = mapped_column(Integer, default=1)
    price: Mapped[Decimal] = mapped_column(Numeric(18, 2))


class PropertyOwnership(Base):
    __tablename__ = "property_ownerships"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    property_id: Mapped[UUID] = mapped_column(
        ForeignKey("properties.id", ondelete="CASCADE"), unique=True
    )
    character_id: Mapped[UUID] = mapped_column(ForeignKey("characters.id", ondelete="CASCADE"))
    acquired_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Vehicle(Base):
    __tablename__ = "vehicles"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    code: Mapped[str] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(String(120))
    kind: Mapped[str] = mapped_column(String(32))
    capacity: Mapped[int] = mapped_column(Integer, default=1)
    travel_speed: Mapped[Decimal] = mapped_column(Numeric(8, 2), default=Decimal("1"))


class CharacterVehicle(Base):
    __tablename__ = "character_vehicles"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    character_id: Mapped[UUID] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE"), index=True
    )
    vehicle_id: Mapped[UUID] = mapped_column(ForeignKey("vehicles.id", ondelete="RESTRICT"))
    acquired_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Travel(Base):
    __tablename__ = "travels"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    character_id: Mapped[UUID] = mapped_column(ForeignKey("characters.id", ondelete="CASCADE"))
    from_city_id: Mapped[UUID] = mapped_column(ForeignKey("cities.id", ondelete="RESTRICT"))
    to_city_id: Mapped[UUID] = mapped_column(ForeignKey("cities.id", ondelete="RESTRICT"))
    status: Mapped[str] = mapped_column(String(32), default="scheduled")
    departure_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    arrival_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class SocialRelation(Base):
    __tablename__ = "social_relations"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    source_character_id: Mapped[UUID] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE")
    )
    target_character_id: Mapped[UUID] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE")
    )
    kind: Mapped[str] = mapped_column(String(32))
    score: Mapped[int] = mapped_column(Integer, default=0)
    __table_args__ = (
        UniqueConstraint(
            "source_character_id", "target_character_id", "kind", name="uq_social_relation"
        ),
    )


class NPC(Base):
    __tablename__ = "npcs"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(120))
    city_id: Mapped[UUID | None] = mapped_column(ForeignKey("cities.id", ondelete="RESTRICT"))
    role: Mapped[str] = mapped_column(String(64), default="citizen")
    disposition: Mapped[int] = mapped_column(Integer, default=0)


class Mission(Base):
    __tablename__ = "missions"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    code: Mapped[str] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text, default="")
    xp_reward: Mapped[int] = mapped_column(Integer, default=0)
    currency_reward: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0"))
    required_level: Mapped[int] = mapped_column(Integer, default=1)


class CharacterMission(Base):
    __tablename__ = "character_missions"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    character_id: Mapped[UUID] = mapped_column(ForeignKey("characters.id", ondelete="CASCADE"))
    mission_id: Mapped[UUID] = mapped_column(ForeignKey("missions.id", ondelete="RESTRICT"))
    state: Mapped[str] = mapped_column(String(32), default="active")
    progress: Mapped[int] = mapped_column(Integer, default=0)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    __table_args__ = (UniqueConstraint("character_id", "mission_id", name="uq_character_mission"),)


class LedgerAccount(Base):
    __tablename__ = "ledger_accounts"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    code: Mapped[str] = mapped_column(String(64), unique=True)
    currency_id: Mapped[UUID] = mapped_column(ForeignKey("currencies.id", ondelete="RESTRICT"))


class LedgerTransaction(Base):
    __tablename__ = "ledger_transactions"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    idempotency_key: Mapped[str] = mapped_column(String(128), unique=True)
    reference: Mapped[str] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class LedgerEntry(Base):
    __tablename__ = "ledger_entries"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    transaction_id: Mapped[UUID] = mapped_column(
        ForeignKey("ledger_transactions.id", ondelete="CASCADE"), index=True
    )
    ledger_account_id: Mapped[UUID] = mapped_column(
        ForeignKey("ledger_accounts.id", ondelete="RESTRICT")
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    direction: Mapped[str] = mapped_column(String(8))
    __table_args__ = (Index("ix_ledger_entries_tx_account", "transaction_id", "ledger_account_id"),)


class MarketListing(Base):
    __tablename__ = "market_listings"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    seller_character_id: Mapped[UUID] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE")
    )
    item_id: Mapped[UUID] = mapped_column(ForeignKey("items.id", ondelete="RESTRICT"))
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    status: Mapped[str] = mapped_column(String(32), default="open")


class Business(Base):
    __tablename__ = "businesses"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    owner_character_id: Mapped[UUID] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE")
    )
    city_id: Mapped[UUID] = mapped_column(ForeignKey("cities.id", ondelete="RESTRICT"))
    name: Mapped[str] = mapped_column(String(120))
    kind: Mapped[str] = mapped_column(String(64))
    balance: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0"))


class GameEvent(Base):
    __tablename__ = "game_events"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    event_type: Mapped[str] = mapped_column(String(64))
    state: Mapped[str] = mapped_column(String(32), default="scheduled")
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    payload: Mapped[str] = mapped_column(Text, default="{}")
    version: Mapped[int] = mapped_column(Integer, default=1)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    actor_type: Mapped[str] = mapped_column(String(32))
    actor_id: Mapped[str | None] = mapped_column(String(128))
    action: Mapped[str] = mapped_column(String(128))
    entity_type: Mapped[str] = mapped_column(String(64))
    entity_id: Mapped[str] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    details: Mapped[str] = mapped_column(Text, default="{}")
