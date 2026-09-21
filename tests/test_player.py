from lifeverse.models import Country, Currency
from lifeverse.services import PlayerService


def test_identity_idempotency(session):
    s = PlayerService()
    a = s.register(session, "player", "telegram", "123")
    b = s.register(session, "other", "telegram", "123")
    assert a.id == b.id


def test_character_and_progression(session):
    s = PlayerService()
    session.add_all(
        [
            Currency(code="IRR", name="Iranian rial", symbol="﷼"),
            Country(
                iso2="IR",
                iso3="IRN",
                name="Iran",
                capital="Tehran",
                region="Middle East",
                currency_code="IRR",
                languages="fa",
                population=1,
                cost_of_living_index=1,
            ),
        ]
    )
    session.commit()
    c = s.register(session, "player")
    country = session.query(Country).first()
    ch = s.create_character(session, c.id, "Ali", country.id)
    session.expire_all()
    loaded = s.add_xp(session, ch.id, 100)
    assert loaded.level == 2 and loaded.xp == 100
