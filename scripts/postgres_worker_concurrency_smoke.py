"""Verify PostgreSQL row locking and idempotent payroll under concurrency."""

from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import delete, func, select

from lifeverse.db import SessionLocal, engine
from lifeverse.models import (
    Account,
    AuditLog,
    Business,
    BusinessEmployee,
    BusinessPayrollPayment,
    City,
    Country,
    Currency,
    Wallet,
)
from lifeverse.services import EconomyService, PlayerService
from lifeverse.services_16_25 import BusinessService


def main() -> None:
    if engine.dialect.name != "postgresql":
        raise RuntimeError("Payroll concurrency smoke test requires PostgreSQL")

    suffix = uuid4().hex
    owner_username = f"pg-payroll-owner-{suffix}"
    employee_username = f"pg-payroll-employee-{suffix}"
    business_ids = []
    account_usernames = [owner_username, employee_username]
    city_id = None
    country_id = None
    currency_id = None
    created_country = False
    created_currency = False

    try:
        with SessionLocal() as session:
            currency = session.scalar(select(Currency).where(Currency.code == "EUR"))
            if currency is None:
                currency = Currency(code="EUR", name="Euro", symbol="€")
                session.add(currency)
                session.flush()
                created_currency = True
            currency_id = currency.id

            country = session.scalar(select(Country).where(Country.iso2 == "DE"))
            if country is None:
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
                session.add(country)
                session.flush()
                created_country = True
            country_id = country.id

            city = City(
                country_id=country.id,
                name=f"Payroll Concurrency {suffix[:8]}",
                region="CI",
                population=1,
                cost_of_living_index=1,
            )
            session.add(city)
            session.commit()
            city_id = city.id

            player = PlayerService()
            owner_account = player.register(session, owner_username)
            employee_account = player.register(session, employee_username)
            owner = player.create_character(
                session, owner_account.id, "Payroll Owner", country.id, city.id
            )
            employee = player.create_character(
                session, employee_account.id, "Payroll Employee", country.id, city.id
            )

            wallets = list(
                session.scalars(
                    select(Wallet).where(
                        Wallet.character_id.in_([owner.id, employee.id])
                    )
                )
            )
            for wallet in wallets:
                wallet.currency_id = currency.id
            session.commit()

            economy = EconomyService()
            economy.credit(session, owner.id, Decimal("130"), f"pg-payroll-fund-{suffix}")

            limited = BusinessService().create(
                session,
                owner.id,
                city.id,
                f"Limited {suffix[:8]}",
                "retail",
                currency.id,
                Decimal("30"),
                economy,
            )
            repeatable = BusinessService().create(
                session,
                owner.id,
                city.id,
                f"Repeatable {suffix[:8]}",
                "retail",
                currency.id,
                Decimal("100"),
                economy,
            )
            business_ids.extend([limited.id, repeatable.id])
            BusinessService().hire(session, limited.id, employee.id, Decimal("25"))
            BusinessService().hire(session, repeatable.id, employee.id, Decimal("25"))

        def run_payroll(business_id, idempotency_key):
            with SessionLocal() as session:
                try:
                    return BusinessService().payroll(
                        session, business_id, idempotency_key
                    )
                except ValueError as exc:
                    session.rollback()
                    return ("error", str(exc))

        with ThreadPoolExecutor(max_workers=2) as pool:
            limited_results = list(
                pool.map(
                    lambda key: run_payroll(business_ids[0], key),
                    ["distinct-payroll-a", "distinct-payroll-b"],
                )
            )
        limited_paid = [value for value in limited_results if isinstance(value, Decimal)]
        limited_errors = [value for value in limited_results if isinstance(value, tuple)]
        if limited_paid != [Decimal("25.00")] or len(limited_errors) != 1:
            raise RuntimeError(
                f"Distinct payroll concurrency was not serialized safely: {limited_results}"
            )
        if "insufficient business funds" not in limited_errors[0][1]:
            raise RuntimeError(f"Unexpected payroll concurrency failure: {limited_errors[0]}")

        with ThreadPoolExecutor(max_workers=2) as pool:
            duplicate_results = list(
                pool.map(
                    lambda _: run_payroll(business_ids[1], "same-idempotency-key"),
                    range(2),
                )
            )
        if sorted(duplicate_results) != [Decimal("0"), Decimal("25.00")]:
            raise RuntimeError(
                f"Duplicate payroll concurrency was not idempotent: {duplicate_results}"
            )

        with SessionLocal() as session:
            limited_business = session.get(Business, business_ids[0])
            repeatable_business = session.get(Business, business_ids[1])
            employee_wallet = session.scalar(
                select(Wallet).where(Wallet.character_id == employee.id)
            )
            payment_count = session.scalar(
                select(func.count())
                .select_from(BusinessPayrollPayment)
                .where(BusinessPayrollPayment.business_id.in_(business_ids))
            )
            if limited_business.balance != Decimal("5.00"):
                raise RuntimeError("Concurrent distinct payrolls corrupted business balance")
            if repeatable_business.balance != Decimal("75.00"):
                raise RuntimeError("Duplicate payroll was charged more than once")
            if employee_wallet.balance != Decimal("50.00"):
                raise RuntimeError("Concurrent payroll credited an incorrect wallet balance")
            if payment_count != 2:
                raise RuntimeError(f"Expected two unique payroll ledger rows, got {payment_count}")

        print("PostgreSQL payroll concurrency smoke test passed")
    finally:
        with SessionLocal() as session:
            if business_ids:
                session.execute(
                    delete(BusinessPayrollPayment).where(
                        BusinessPayrollPayment.business_id.in_(business_ids)
                    )
                )
                session.execute(
                    delete(AuditLog).where(
                        AuditLog.actor_id.in_([str(value) for value in business_ids])
                    )
                )
                session.execute(
                    delete(BusinessEmployee).where(
                        BusinessEmployee.business_id.in_(business_ids)
                    )
                )
                session.execute(delete(Business).where(Business.id.in_(business_ids)))
            session.execute(
                delete(Account).where(Account.username.in_(account_usernames))
            )
            if city_id is not None:
                session.execute(delete(City).where(City.id == city_id))
            if created_country and country_id is not None:
                session.execute(delete(Country).where(Country.id == country_id))
            if created_currency and currency_id is not None:
                session.execute(delete(Currency).where(Currency.id == currency_id))
            session.commit()
        engine.dispose()


if __name__ == "__main__":
    main()
