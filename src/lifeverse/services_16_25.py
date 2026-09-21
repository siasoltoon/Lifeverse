from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from random import Random

from sqlalchemy import select, update

from .models import (
    AIIntent,
    Account,
    AuthSession,
    AuditLog,
    Business,
    BusinessEmployee,
    Character,
    CombatSession,
    EventDefinition,
    ExploitSignal,
    GameEvent,
    Item,
    LawCase,
    MarketListing,
    MarketOrder,
    RateLimitBucket,
    Translation,
    Wallet,
)


class EventService:
    CATEGORIES = {"world", "city", "economic", "social", "random", "scheduled", "seasonal", "player"}

    def define(self, s, code, name, category, repeatable=False, cooldown_seconds=0):
        if category not in self.CATEGORIES:
            raise ValueError("unsupported event category")
        if cooldown_seconds < 0:
            raise ValueError("cooldown must be non-negative")
        row = EventDefinition(
            code=code.strip(),
            name=name.strip(),
            category=category,
            repeatable=repeatable,
            cooldown_seconds=cooldown_seconds,
            enabled=True,
        )
        s.add(row)
        s.commit()
        return row

    def schedule(self, s, event_type, when, payload=None, state="scheduled"):
        if not event_type.strip():
            raise ValueError("event type is required")
        if state not in {"scheduled", "pending"}:
            raise ValueError("invalid event state")
        row = GameEvent(
            event_type=event_type,
            state=state,
            scheduled_at=when,
            payload=json.dumps(payload or {}, sort_keys=True),
            version=1,
        )
        s.add(row)
        s.commit()
        return row

    def schedule_player(self, s, character_id, event_type, when, payload=None):
        if not s.get(Character, character_id):
            raise ValueError("character not found")
        data = dict(payload or {})
        data["character_id"] = str(character_id)
        return self.schedule(s, f"player:{event_type}", when, data)

    def dispatch_due(self, s, now=None, limit=100):
        now = now or datetime.now(UTC)
        if limit < 1 or limit > 1000:
            raise ValueError("limit must be 1-1000")
        rows = list(
            s.scalars(
                select(GameEvent)
                .where(GameEvent.state.in_({"scheduled", "pending"}), GameEvent.scheduled_at <= now)
                .order_by(GameEvent.scheduled_at, GameEvent.id)
                .limit(limit)
            )
        )
        for row in rows:
            row.state = "processed"
            row.version += 1
            s.add(AuditLog(
                actor_type="system",
                actor_id=None,
                action="event.dispatch",
                entity_type="game_event",
                entity_id=str(row.id),
                details=row.payload,
            ))
        s.commit()
        return rows

    def random_event(self, s, seed, when, scope="world"):
        if seed < 0:
            raise ValueError("seed must be non-negative")
        rng = Random(seed)
        choices = ["market_shift", "city_festival", "social_wave", "weather_random", "world_news"]
        event_type = rng.choice(choices)
        return self.schedule(s, f"{scope}:{event_type}", when, {"seed": seed, "scope": scope})


    def seasonal(self, s, year, season, payload=None):
        if season not in {"spring", "summer", "autumn", "winter"}:
            raise ValueError("invalid season")
        when = datetime(year, {"spring": 3, "summer": 6, "autumn": 9, "winter": 12}[season], 1, tzinfo=UTC)
        return self.schedule(s, f"seasonal:{season}", when, payload)


class BusinessService:
    def create(self, s, owner_character_id, city_id, name, kind, currency_id, capital=Decimal("0"), economy=None):
        if not s.get(Character, owner_character_id):
            raise ValueError("owner not found")
        if capital > 0:
            if economy is None:
                raise ValueError("economy service is required for funded businesses")
            wallet = s.scalar(select(Wallet).where(Wallet.character_id == owner_character_id))
            if not wallet or wallet.currency_id != currency_id:
                raise ValueError("owner wallet currency mismatch")
            economy._apply_move(s, owner_character_id, -Decimal(str(capital)), f"business-capital:{owner_character_id}:{name}", "business capital")
        row = Business(
            owner_character_id=owner_character_id,
            city_id=city_id,
            name=name.strip(),
            kind=kind.strip(),
            balance=Decimal(str(capital)),
            currency_id=currency_id,
        )
        if row.balance < 0:
            raise ValueError("capital cannot be negative")
        s.add(row)
        s.commit()
        return row

    def hire(self, s, business_id, character_id, wage):
        business = s.get(Business, business_id)
        if not business or not s.get(Character, character_id):
            raise ValueError("business or character not found")
        wage = Decimal(str(wage))
        if wage < 0:
            raise ValueError("wage cannot be negative")
        row = BusinessEmployee(business_id=business_id, character_id=character_id, wage=wage)
        s.add(row)
        s.commit()
        return row

    def payroll(self, s, business_id, idempotency_prefix):
        business = s.get(Business, business_id)
        if not business:
            raise ValueError("business not found")
        employees = list(s.scalars(select(BusinessEmployee).where(
            BusinessEmployee.business_id == business_id, BusinessEmployee.status == "active"
        )))
        total = sum((e.wage for e in employees), Decimal("0"))
        if business.balance < total:
            raise ValueError("insufficient business funds")
        business.balance -= total
        for employee in employees:
            wallet = s.scalar(select(Wallet).where(Wallet.character_id == employee.character_id))
            if not wallet or wallet.currency_id != business.currency_id:
                raise ValueError("employee wallet currency mismatch")
            wallet.balance += employee.wage
            key = f"{idempotency_prefix}:{employee.id}"
            if s.scalar(select(AuditLog).where(AuditLog.action == "business.payroll", AuditLog.details.like(f'%{key}%'))):
                continue
            s.add(AuditLog(
                actor_type="business",
                actor_id=str(business.id),
                action="business.payroll",
                entity_type="character",
                entity_id=str(employee.character_id),
                details=json.dumps({"amount": str(employee.wage), "idempotency_key": key}),
            ))
        s.commit()
        return total


class MarketService:
    def list_item(self, s, seller_character_id, item_id, quantity, unit_price):
        if not s.get(Character, seller_character_id) or not s.get(Item, item_id):
            raise ValueError("seller or item not found")
        if quantity <= 0 or Decimal(str(unit_price)) <= 0:
            raise ValueError("quantity and price must be positive")
        row = MarketListing(
            seller_character_id=seller_character_id,
            item_id=item_id,
            quantity=quantity,
            unit_price=Decimal(str(unit_price)),
            status="open",
        )
        s.add(row)
        s.commit()
        return row

    def buy(self, s, buyer_character_id, listing_id, quantity, idempotency_key, economy, inventory):
        existing = s.scalar(select(MarketOrder).where(MarketOrder.idempotency_key == idempotency_key))
        if existing:
            return existing
        listing = s.get(MarketListing, listing_id)
        if not listing or listing.status != "open":
            raise ValueError("listing unavailable")
        if listing.seller_character_id == buyer_character_id:
            raise ValueError("seller cannot buy own listing")
        if quantity <= 0 or quantity > listing.quantity:
            raise ValueError("invalid quantity")
        total = listing.unit_price * quantity
        economy._apply_move(s, buyer_character_id, -total, idempotency_key, "market purchase")
        economy._apply_move(s, listing.seller_character_id, total, f"{idempotency_key}:seller", "market sale")
        inventory.add_in_session(s, buyer_character_id, listing.item_id, quantity)
        listing.quantity -= quantity
        if listing.quantity == 0:
            listing.status = "closed"
        order = MarketOrder(
            listing_id=listing.id,
            buyer_character_id=buyer_character_id,
            quantity=quantity,
            total_price=total,
            idempotency_key=idempotency_key,
        )
        s.add(order)
        s.commit()
        return order


class LawService:
    def report(self, s, character_id, category, severity, evidence=None):
        if not s.get(Character, character_id):
            raise ValueError("character not found")
        if severity < 1 or severity > 10:
            raise ValueError("severity must be 1-10")
        row = LawCase(
            character_id=character_id,
            category=category,
            severity=severity,
            evidence=json.dumps(evidence or {}, sort_keys=True),
        )
        s.add(row)
        s.commit()
        return row

    def resolve(self, s, case_id, outcome):
        row = s.get(LawCase, case_id)
        if not row or row.state != "open":
            raise ValueError("open case not found")
        if outcome not in {"dismissed", "convicted", "cleared"}:
            raise ValueError("invalid outcome")
        row.state = outcome
        s.commit()
        return row


class CombatService:
    def start(self, s, attacker_id, defender_id, seed=None):
        if attacker_id == defender_id:
            raise ValueError("combat requires two characters")
        if not s.get(Character, attacker_id) or not s.get(Character, defender_id):
            raise ValueError("combatant not found")
        row = CombatSession(
            attacker_id=attacker_id,
            defender_id=defender_id,
            seed=seed if seed is not None else secrets.randbelow(2**31),
        )
        s.add(row)
        s.commit()
        return row

    def resolve_turn(self, s, session_id, attacker_power, defender_power):
        row = s.get(CombatSession, session_id)
        if not row or row.state != "active":
            raise ValueError("active combat not found")
        if attacker_power < 0 or defender_power < 0:
            raise ValueError("power cannot be negative")
        rng = Random(row.seed + row.turn)
        attacker_roll = attacker_power + rng.randint(0, 9)
        defender_roll = defender_power + rng.randint(0, 9)
        if attacker_roll > defender_roll:
            result = "attacker"
        elif defender_roll > attacker_roll:
            result = "defender"
        else:
            result = "draw"
        row.turn += 1
        if row.turn > 10:
            row.state = "completed"
        s.commit()
        return {"result": result, "attacker_roll": attacker_roll, "defender_roll": defender_roll, "state": row.state}


class AIIntentService:
    ALLOWED = {"move", "work", "trade", "travel", "social", "rest", "mission"}

    def propose(self, s, actor_id, intent_type, payload):
        if actor_id is not None and not s.get(Character, actor_id):
            raise ValueError("actor not found")
        if intent_type not in self.ALLOWED:
            raise ValueError("unsupported intent")
        row = AIIntent(actor_id=actor_id, intent_type=intent_type, payload=json.dumps(payload, sort_keys=True))
        s.add(row)
        s.commit()
        return row

    def validate(self, s, intent_id):
        row = s.get(AIIntent, intent_id)
        if not row or row.state != "proposed":
            raise ValueError("proposed intent not found")
        try:
            data = json.loads(row.payload)
        except json.JSONDecodeError:
            row.state, row.rejection_reason = "rejected", "invalid payload"
            s.commit()
            return row
        if row.intent_type == "travel" and "to_city_id" not in data:
            row.state, row.rejection_reason = "rejected", "missing destination"
        else:
            row.state = "validated"
        s.commit()
        return row

    def execute(self, s, intent_id, executor):
        row = s.get(AIIntent, intent_id)
        if not row or row.state != "validated":
            raise ValueError("validated intent not found")
        result = executor(row.intent_type, json.loads(row.payload))
        row.state = "executed"
        s.commit()
        return result


class LocalizationService:
    def set(self, s, locale, key, value):
        if locale not in {"fa", "en"}:
            raise ValueError("unsupported locale")
        row = s.scalar(select(Translation).where(Translation.locale == locale, Translation.key == key))
        if not row:
            row = Translation(locale=locale, key=key, value=value)
            s.add(row)
        else:
            row.value = value
        s.commit()
        return row

    def translate(self, s, locale, key, fallback="en"):
        row = s.scalar(select(Translation).where(Translation.locale == locale, Translation.key == key))
        if row:
            return row.value
        row = s.scalar(select(Translation).where(Translation.locale == fallback, Translation.key == key))
        return row.value if row else key


class AntiExploitService:
    def signal(self, s, character_id, rule, severity, evidence):
        if severity < 1 or severity > 10:
            raise ValueError("severity must be 1-10")
        row = ExploitSignal(
            character_id=character_id,
            rule=rule,
            severity=severity,
            evidence=json.dumps(evidence, sort_keys=True),
        )
        s.add(row)
        s.commit()
        return row

    def repeated_action(self, s, character_id, action, since, threshold):
        count = len(list(s.scalars(select(AuditLog).where(
            AuditLog.actor_id == str(character_id),
            AuditLog.action == action,
            AuditLog.created_at >= since,
        ))))
        if count >= threshold:
            return self.signal(s, character_id, "repeated_action", min(10, count), {"action": action, "count": count})
        return None


class SecurityService:
    def allow(self, s, key, limit_value, window_seconds=60, now=None):
        if limit_value <= 0 or window_seconds <= 0:
            raise ValueError("invalid rate limit")
        now = now or datetime.now(UTC)
        row = s.get(RateLimitBucket, key)
        if not row or now - row.window_started_at >= timedelta(seconds=window_seconds):
            row = RateLimitBucket(key=key, window_started_at=now, count=0, limit_value=limit_value)
            s.merge(row)
            s.flush()
        if row.count >= limit_value:
            s.commit()
            return False
        row.count += 1
        row.limit_value = limit_value
        s.commit()
        return True


class PerformanceService:
    def paginate(self, s, query, offset=0, limit=50):
        if offset < 0 or limit < 1 or limit > 200:
            raise ValueError("invalid pagination")
        return list(s.scalars(query.offset(offset).limit(limit)))

    def explainable_page(self, s, query, offset=0, limit=50):
        rows = self.paginate(s, query, offset, limit)
        return {"items": rows, "offset": offset, "limit": limit, "count": len(rows)}


class AuthService:
    def set_password(self, s, account_id, password):
        if len(password) < 12 or len(password) > 256:
            raise ValueError("password must contain 12-256 characters")
        account = s.get(Account, account_id)
        if not account:
            raise ValueError("account not found")
        salt = secrets.token_bytes(16)
        digest = hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt,
            n=2**15,
            r=8,
            p=3,
        )
        account.password_hash = "scrypt$32768$8$3$" + base64.urlsafe_b64encode(salt).decode() + "$" + base64.urlsafe_b64encode(digest).decode()
        s.commit()
        return account

    def verify_password(self, account, password):
        if not account.password_hash:
            return False
        try:
            _, n, r, p, salt_text, digest_text = account.password_hash.split("$")
            salt = base64.urlsafe_b64decode(salt_text.encode())
            expected = base64.urlsafe_b64decode(digest_text.encode())
            actual = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=int(n), r=int(r), p=int(p))
            return hmac.compare_digest(actual, expected)
        except (ValueError, TypeError):
            return False

    def login(self, s, username, password, ttl_seconds=3600):
        account = s.scalar(select(Account).where(Account.username == username.strip()))
        if not account or not self.verify_password(account, password):
            raise ValueError("invalid credentials")
        token = secrets.token_urlsafe(48)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        session = AuthSession(
            account_id=account.id,
            token_hash=token_hash,
            expires_at=datetime.now(UTC) + timedelta(seconds=ttl_seconds),
        )
        s.add(session)
        s.commit()
        return token, session

    def authenticate(self, s, token):
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        session = s.scalar(select(AuthSession).where(AuthSession.token_hash == token_hash))
        if not session or session.revoked_at or session.expires_at <= datetime.now(UTC):
            raise ValueError("invalid or expired session")
        return session.account_id

    def revoke(self, s, token):
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        session = s.scalar(select(AuthSession).where(AuthSession.token_hash == token_hash))
        if session:
            session.revoked_at = datetime.now(UTC)
            s.commit()
