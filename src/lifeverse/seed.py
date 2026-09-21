from sqlalchemy import select
from .db import SessionLocal
from .models import Country, City, Currency

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
        s.commit()


if __name__ == "__main__":
    seed()
