from decimal import Decimal
from sqlalchemy import select
from .db import SessionLocal
from .models import Country, City, Currency, Job, Skill, Item, Vehicle, Mission

COUNTRIES = [
    {
        "iso2": "IR",
        "iso3": "IRN",
        "name": "Iran",
        "capital": "Tehran",
        "region": "Middle East",
        "currency_code": "IRR",
        "languages": "fa",
        "population": 88550570,
        "cost_of_living_index": 23.2,
        "cities": [
            ("Tehran", "Tehran Province", 9046800, 31.5),
            ("Rasht", "Gilan Province", 679995, 24.1),
            ("Ramsar", "Mazandaran Province", 35000, 22.4),
        ],
    },
    {
        "iso2": "TR",
        "iso3": "TUR",
        "name": "Türkiye",
        "capital": "Ankara",
        "region": "Western Asia",
        "currency_code": "TRY",
        "languages": "tr",
        "population": 85326000,
        "cost_of_living_index": 39.2,
        "cities": [
            ("Istanbul", "Istanbul Province", 15840900, 50.1),
            ("Ankara", "Ankara Province", 5747325, 42.0),
        ],
    },
    {
        "iso2": "AZ",
        "iso3": "AZE",
        "name": "Azerbaijan",
        "capital": "Baku",
        "region": "Caucasus",
        "currency_code": "AZN",
        "languages": "az",
        "population": 10318000,
        "cost_of_living_index": 31.4,
        "cities": [("Baku", "Absheron", 2303100, 38.7)],
    },
]
CURRENCIES = [
    ("IRR", "Iranian rial", "﷼"),
    ("TRY", "Turkish lira", "₺"),
    ("AZN", "Azerbaijani manat", "₼"),
]


def seed():
    with SessionLocal() as s:
        for code, name, symbol in CURRENCIES:
            if not s.scalar(select(Currency).where(Currency.code == code)):
                s.add(Currency(code=code, name=name, symbol=symbol))
        s.flush()
        for row in COUNTRIES:
            cities = row["cities"]
            data = {k: v for k, v in row.items() if k != "cities"}
            country = s.scalar(select(Country).where(Country.iso2 == data["iso2"]))
            if not country:
                country = Country(**data)
                s.add(country)
                s.flush()
                for name, region, pop, col in cities:
                    s.add(
                        City(
                            country_id=country.id,
                            name=name,
                            region=region,
                            population=pop,
                            cost_of_living_index=col,
                        )
                    )
        jobs = [
            ("software_developer", "Software Developer", 1, Decimal("2500"), 8),
            ("retail_clerk", "Retail Clerk", 1, Decimal("900"), 8),
            ("teacher", "Teacher", 2, Decimal("1600"), 6),
        ]
        for code, name, min_level, salary, hours in jobs:
            if not s.scalar(select(Job).where(Job.code == code)):
                s.add(
                    Job(
                        code=code,
                        name=name,
                        min_level=min_level,
                        base_salary=salary,
                        work_hours=hours,
                    )
                )
        skills = [
            ("programming", "Programming"),
            ("communication", "Communication"),
            ("fitness", "Fitness"),
        ]
        for code, name in skills:
            if not s.scalar(select(Skill).where(Skill.code == code)):
                s.add(Skill(code=code, name=name, max_level=100))
        items = [
            ("basic_phone", "Basic Phone", "device", 0.18, 120),
            ("laptop", "Laptop", "device", 1.8, 900),
            ("bread", "Bread", "food", 0.5, 2),
        ]
        for code, name, kind, weight, price in items:
            if not s.scalar(select(Item).where(Item.code == code)):
                s.add(Item(code=code, name=name, kind=kind, weight=weight, base_price=price))
        vehicles = [
            ("bicycle", "Bicycle", "bike", 1, 12),
            ("compact_car", "Compact Car", "car", 4, 60),
        ]
        for code, name, kind, capacity, speed in vehicles:
            if not s.scalar(select(Vehicle).where(Vehicle.code == code)):
                s.add(
                    Vehicle(code=code, name=name, kind=kind, capacity=capacity, travel_speed=speed)
                )
        missions = [
            ("first_day", "First Day", "Complete your first meaningful activity.", 100, 50, 1),
            ("learn_skill", "Learn a Skill", "Reach your first skill level.", 150, 100, 1),
        ]
        for code, name, description, xp, reward, level in missions:
            if not s.scalar(select(Mission).where(Mission.code == code)):
                s.add(
                    Mission(
                        code=code,
                        name=name,
                        description=description,
                        xp_reward=xp,
                        currency_reward=reward,
                        required_level=level,
                    )
                )
        seed_phase_16_25(s)
        s.commit()


if __name__ == "__main__":
    seed()


def seed_phase_16_25(session):
    from .models import EventDefinition, Translation

    events = [
        ("market_shift", "Market Shift", "economic"),
        ("city_festival", "City Festival", "city"),
        ("social_wave", "Social Wave", "social"),
        ("weather_random", "Weather Event", "random"),
        ("season_change", "Season Change", "seasonal"),
        ("world_news", "World News", "world"),
        ("player_milestone", "Player Milestone", "player"),
    ]
    for code, name, category in events:
        if not session.scalar(select(EventDefinition).where(EventDefinition.code == code)):
            session.add(EventDefinition(code=code, name=name, category=category, repeatable=True))
    translations = {
        ("en", "common.ok"): "OK",
        ("en", "event.dispatched"): "Event dispatched",
        ("fa", "common.ok"): "تأیید",
        ("fa", "event.dispatched"): "رویداد اجرا شد",
    }
    for (locale, key), value in translations.items():
        row = session.scalar(
            select(Translation).where(Translation.locale == locale, Translation.key == key)
        )
        if not row:
            session.add(Translation(locale=locale, key=key, value=value))
    session.commit()
