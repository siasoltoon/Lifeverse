from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session
from .domain import level_for_xp, validate_character_name, validate_location
from .models import Account, AccountIdentity, Character, Country, City, Currency, Wallet


class PlayerService:
    def register(
        self,
        session: Session,
        username: str,
        provider: str | None = None,
        external_id: str | None = None,
    ) -> Account:
        username = username.strip()
        if not username or len(username) > 64:
            raise ValueError("username must contain 1-64 characters")
        if provider and external_id:
            existing = session.scalar(
                select(AccountIdentity).where(
                    AccountIdentity.provider == provider, AccountIdentity.external_id == external_id
                )
            )
            if existing:
                return existing.account
        account = Account(username=username)
        session.add(account)
        session.flush()
        if provider and external_id:
            session.add(
                AccountIdentity(account_id=account.id, provider=provider, external_id=external_id)
            )
        session.commit()
        session.refresh(account)
        return account

    def create_character(
        self,
        session: Session,
        account_id: UUID,
        name: str,
        country_id: UUID | None = None,
        city_id: UUID | None = None,
    ) -> Character:
        name = validate_character_name(name)
        validate_location(country_id, city_id)
        if country_id and not session.get(Country, country_id):
            raise ValueError("country not found")
        if city_id:
            city = session.get(City, city_id)
            if not city or city.country_id != country_id:
                raise ValueError("city does not belong to country")
        if not session.get(Account, account_id):
            raise ValueError("account not found")
        character = Character(
            account_id=account_id, name=name, country_id=country_id, city_id=city_id
        )
        session.add(character)
        session.flush()
        if country_id:
            country = session.get(Country, country_id)
            currency = session.scalar(
                select(Currency).where(Currency.code == country.currency_code)
            )
            if currency:
                session.add(Wallet(character_id=character.id, currency_id=currency.id))
        session.commit()
        session.refresh(character)
        return character

    def add_xp(self, session: Session, character_id: UUID, amount: int) -> Character:
        if amount <= 0:
            raise ValueError("xp amount must be positive")
        character = session.get(Character, character_id)
        if not character:
            raise ValueError("character not found")
        character.xp += amount
        character.level = level_for_xp(character.xp)
        session.commit()
        session.refresh(character)
        return character


class WorldService:
    def list_countries(self, session: Session):
        return list(session.scalars(select(Country).order_by(Country.name)))

    def list_cities(
        self, session: Session, country_id: UUID | None = None, query: str | None = None
    ):
        stmt = select(City).order_by(City.name)
        if country_id:
            stmt = stmt.where(City.country_id == country_id)
        if query:
            stmt = stmt.where(City.name.ilike(f"%{query.strip()}%"))
        return list(session.scalars(stmt))
