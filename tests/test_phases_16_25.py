from datetime import UTC, datetime, timedelta
from decimal import Decimal

from lifeverse.models import (
    Business,
    Character,
    EventDefinition,
    GameEvent,
    Item,
    MarketListing,
    Translation,
)
from lifeverse.services import EconomyService, InventoryService, PlayerService
from lifeverse.services_16_25 import (
    AIIntentService,
    AntiExploitService,
    BusinessService,
    CombatService,
    EventService,
    LawService,
    LocalizationService,
    MarketService,
    SecurityService,
)


def setup_two_characters(session):
    from lifeverse.models import City, Country, Currency

    currency = Currency(code="EUR", name="Euro", symbol="€")
    country = Country(
        iso2="DE",
        iso3="DEU",
        name="Germany",
        capital="Berlin",
        region="Europe",
        currency_code="EUR",
        languages="de",
        population=1,
        cost_of_living_index=1,
    )
    session.add_all([currency, country])
    session.flush()
    city = City(
        country_id=country.id,
        name="Berlin",
        region="Berlin",
        population=1,
        cost_of_living_index=1,
    )
    session.add(city)
    session.commit()
    player = PlayerService()
    a = player.register(session, "phase16a")
    b = player.register(session, "phase16b")
    c1 = player.create_character(session, a.id, "Alpha", country.id, city.id)
    c2 = player.create_character(session, b.id, "Beta", country.id, city.id)
    return c1, c2, city, currency


def test_event_engine_categories_and_idempotent_dispatch(session):
    c1, _, _, _ = setup_two_characters(session)
    service = EventService()
    definition = service.define(session, "city_test", "City Test", "city", repeatable=True)
    assert definition.category == "city"
    row = service.schedule_player(session, c1.id, "milestone", datetime.now(UTC) - timedelta(seconds=1))
    processed = service.dispatch_due(session)
    assert row.id in {x.id for x in processed}
    assert session.get(GameEvent, row.id).state == "processed"


def test_business_payroll_and_market_settlement(session):
    seller, buyer, city, currency = setup_two_characters(session)
    business = BusinessService().create(session, seller.id, city.id, "Shop", "retail", currency.id, Decimal("100"))
    BusinessService().hire(session, business.id, buyer.id, Decimal("25"))
    BusinessService().payroll(session, business.id, "payroll-1")
    assert session.get(Business, business.id).balance == Decimal("75.00")

    item = Item(code="apple", name="Apple", kind="food", weight=Decimal("0.2"), base_price=Decimal("5"))
    session.add(item)
    session.commit()
    InventoryService().add(session, seller.id, item.id, 2)
    EconomyService().credit(session, buyer.id, Decimal("50"), "buyer-funds")
    listing = MarketService().list_item(session, seller.id, item.id, 1, Decimal("10"))
    order = MarketService().buy(
        session, buyer.id, listing.id, 1, "order-12345678", EconomyService(), InventoryService()
    )
    assert order.status == "completed"


def test_law_combat_ai_and_localization_boundaries(session):
    c1, c2, _, _ = setup_two_characters(session)
    case = LawService().report(session, c1.id, "theft", 4, {"source": "test"})
    assert LawService().resolve(session, case.id, "cleared").state == "cleared"
    combat = CombatService().start(session, c1.id, c2.id, seed=42)
    result = CombatService().resolve_turn(session, combat.id, 5, 4)
    assert result["result"] in {"attacker", "defender", "draw"}
    intent = AIIntentService().propose(session, c1.id, "travel", {"to_city_id": str(c2.city_id)})
    assert AIIntentService().validate(session, intent.id).state == "validated"
    loc = LocalizationService().set(session, "fa", "test.hello", "سلام")
    assert loc.value == "سلام"
    assert LocalizationService().translate(session, "fa", "test.hello") == "سلام"


def test_security_and_antiexploit_controls(session):
    c1, _, _, _ = setup_two_characters(session)
    security = SecurityService()
    assert security.allow(session, "ip:test", 2)
    assert security.allow(session, "ip:test", 2)
    assert not security.allow(session, "ip:test", 2)
    signal = AntiExploitService().signal(session, c1.id, "manual_test", 5, {"n": 3})
    assert signal.state == "open"
