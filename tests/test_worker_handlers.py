import json
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import func, select

from lifeverse.jobs import JobRecord, JobService, Worker
from lifeverse.models import (
    AuditLog,
    Business,
    BusinessPayrollPayment,
    Character,
    City,
    Country,
    Currency,
    GameEvent,
    Travel,
    Wallet,
)
from lifeverse.services import EconomyService, PlayerService, TravelService
from lifeverse.services_16_25 import BusinessService, EventService
from lifeverse.worker import business_payroll, event_dispatch, travel_complete


def setup_worker_world(session):
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
    origin = City(
        country_id=country.id,
        name="Berlin",
        region="Berlin",
        population=1,
        cost_of_living_index=1,
    )
    destination = City(
        country_id=country.id,
        name="Hamburg",
        region="Hamburg",
        population=1,
        cost_of_living_index=1,
    )
    session.add_all([origin, destination])
    session.commit()

    player = PlayerService()
    owner_account = player.register(session, "worker-payroll-owner")
    employee_account = player.register(session, "worker-payroll-employee")
    owner = player.create_character(session, owner_account.id, "Owner", country.id, origin.id)
    employee = player.create_character(
        session, employee_account.id, "Employee", country.id, origin.id
    )
    return owner, employee, origin, destination, currency


class FailFirstComplete(JobService):
    def __init__(self):
        super().__init__()
        self.fail_next_complete = True

    def complete(self, session, job_id, worker_id):
        if self.fail_next_complete:
            self.fail_next_complete = False
            raise RuntimeError("simulated failure after handler transaction committed")
        return super().complete(session, job_id, worker_id)


def make_retryable(session, job_id):
    job = session.get(JobRecord, job_id)
    assert job.status == "queued"
    job.run_at = datetime.now(UTC) - timedelta(seconds=1)
    session.commit()


def test_business_payroll_worker_retry_cannot_duplicate_currency(session):
    owner, employee, city, _, currency = setup_worker_world(session)
    economy = EconomyService()
    economy.credit(session, owner.id, Decimal("100"), "worker-owner-capital")
    business = BusinessService().create(
        session,
        owner.id,
        city.id,
        "Worker Shop",
        "retail",
        currency.id,
        Decimal("100"),
        economy,
    )
    BusinessService().hire(session, business.id, employee.id, Decimal("25"))
    job = JobService().enqueue(
        session,
        "business.payroll",
        {"business_id": str(business.id), "idempotency_key": "worker-payroll-key"},
        idempotency_key="worker-payroll-job",
        run_at=datetime.now(UTC),
        max_attempts=3,
    )
    worker = Worker(
        service=FailFirstComplete(),
        worker_id="worker-payroll-integration",
    )

    assert worker.run_once(session, {"business.payroll": business_payroll}) is None
    assert session.get(JobRecord, job.id).status == "queued"
    assert session.get(Business, business.id).balance == Decimal("75.00")
    wallet = session.scalar(select(Wallet).where(Wallet.character_id == employee.id))
    assert wallet.balance == Decimal("25.00")
    assert session.scalar(select(func.count()).select_from(BusinessPayrollPayment)) == 1

    make_retryable(session, job.id)
    result = worker.run_once(session, {"business.payroll": business_payroll})

    assert result == "0"
    assert session.get(JobRecord, job.id).status == "completed"
    assert session.get(Business, business.id).balance == Decimal("75.00")
    assert wallet.balance == Decimal("25.00")
    assert session.scalar(select(func.count()).select_from(BusinessPayrollPayment)) == 1
    assert (
        session.scalar(
            select(func.count()).select_from(AuditLog).where(AuditLog.action == "business.payroll")
        )
        == 1
    )


def test_legacy_payroll_audit_record_is_backfilled_without_repayment(session):
    owner, employee, city, _, currency = setup_worker_world(session)
    economy = EconomyService()
    economy.credit(session, owner.id, Decimal("100"), "legacy-owner-capital")
    business = BusinessService().create(
        session,
        owner.id,
        city.id,
        "Legacy Shop",
        "retail",
        currency.id,
        Decimal("100"),
        economy,
    )
    employee_record = BusinessService().hire(session, business.id, employee.id, Decimal("25"))
    wallet = session.scalar(select(Wallet).where(Wallet.character_id == employee.id))
    business.balance = Decimal("75")
    wallet.balance = Decimal("25")
    legacy_key = f"legacy-payroll:{employee_record.id}"
    session.add(
        AuditLog(
            actor_type="business",
            actor_id=str(business.id),
            action="business.payroll",
            entity_type="character",
            entity_id=str(employee.id),
            details=json.dumps({"amount": "25.00", "idempotency_key": legacy_key}),
        )
    )
    session.commit()

    paid = BusinessService().payroll(session, business.id, "legacy-payroll")

    assert paid == Decimal("0")
    assert session.get(Business, business.id).balance == Decimal("75.00")
    assert wallet.balance == Decimal("25.00")
    payment = session.scalar(select(BusinessPayrollPayment))
    assert payment is not None
    assert payment.amount == Decimal("25.00")


def test_event_dispatch_worker_retry_does_not_duplicate_event_audit(session):
    event = EventService().schedule(
        session,
        "world:worker-test",
        datetime.now(UTC) - timedelta(seconds=1),
        {"source": "worker-integration"},
    )
    job = JobService().enqueue(
        session,
        "event.dispatch",
        {},
        idempotency_key="worker-event-job",
        run_at=datetime.now(UTC),
        max_attempts=3,
    )
    worker = Worker(service=FailFirstComplete(), worker_id="worker-event-integration")

    assert worker.run_once(session, {"event.dispatch": event_dispatch}) is None
    assert session.get(GameEvent, event.id).state == "processed"
    assert (
        session.scalar(
            select(func.count())
            .select_from(AuditLog)
            .where(AuditLog.action == "event.dispatch", AuditLog.entity_id == str(event.id))
        )
        == 1
    )

    make_retryable(session, job.id)
    assert worker.run_once(session, {"event.dispatch": event_dispatch}) == []
    assert session.get(JobRecord, job.id).status == "completed"
    assert (
        session.scalar(
            select(func.count())
            .select_from(AuditLog)
            .where(AuditLog.action == "event.dispatch", AuditLog.entity_id == str(event.id))
        )
        == 1
    )


def test_travel_completion_worker_retry_is_idempotent(session):
    character, _, _, destination, _ = setup_worker_world(session)
    travel = TravelService().schedule(
        session,
        character.id,
        destination.id,
        datetime.now(UTC) - timedelta(minutes=120),
        minutes=60,
    )
    job = JobService().enqueue(
        session,
        "travel.complete",
        {"travel_id": str(travel.id)},
        idempotency_key="worker-travel-job",
        run_at=datetime.now(UTC),
        max_attempts=3,
    )
    worker = Worker(service=FailFirstComplete(), worker_id="worker-travel-integration")

    assert worker.run_once(session, {"travel.complete": travel_complete}) is None
    assert session.get(Travel, travel.id).status == "completed"
    assert session.get(Character, character.id).city_id == destination.id

    make_retryable(session, job.id)
    assert worker.run_once(session, {"travel.complete": travel_complete}) == str(travel.id)
    assert session.get(JobRecord, job.id).status == "completed"
    assert session.get(Character, character.id).city_id == destination.id
