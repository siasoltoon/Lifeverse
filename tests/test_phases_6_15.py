from datetime import datetime, timezone
from decimal import Decimal

from lifeverse.models import Character, City, Currency, Item, Job, Mission, Skill, Property
from lifeverse.services import (
    CareerService, EconomyService, InventoryService, MissionService, PlayerService,
    PropertyService, SkillService, SocialService, TravelService, WorldService,
)

def setup_character(session):
    session.add(Currency(code="USD", name="US dollar", symbol="$"))
    session.add_all([
        Job(code="dev",name="Developer",min_level=1,base_salary=Decimal("1000"),work_hours=8),
        Skill(code="code",name="Coding",max_level=10),
        Item(code="book",name="Book",kind="education",weight=1,base_price=10),
        Mission(code="m1",name="Starter",description="x",xp_reward=100,currency_reward=Decimal("5"),required_level=1),
    ])
    from lifeverse.models import Country
    country=Country(iso2="US",iso3="USA",name="United States",capital="Washington",region="Americas",currency_code="USD",languages="en",population=1,cost_of_living_index=1)
    session.add(country); session.flush()
    city=City(country_id=country.id,name="Test City",region="Test",population=1,cost_of_living_index=1); session.add(city); session.commit()
    p=PlayerService(); a=p.register(session,"p"); c=p.create_character(session,a.id,"Hero",country.id,city.id)
    return c,city

def test_world_clock_persists(session):
    c,_=setup_character(session); w=WorldService(); first=w.initialize(session,datetime(2026,1,1,tzinfo=timezone.utc)); w.advance(session,60); session.expire_all()
    second=session.get(type(first),1); assert second.version==2 and second.world_time>first.world_time

def test_economy_idempotency_and_no_negative_balance(session):
    c,_=setup_character(session); e=EconomyService(); e.credit(session,c.id,100,"k-12345678")
    e.debit(session,c.id,30,"k-12345679"); e.debit(session,c.id,30,"k-12345679")
    assert e.balance(session,c.id)==Decimal("70.00")

def test_jobs_skills_inventory_social_and_mission(session):
    c1,city=setup_character(session); p=PlayerService(); a2=p.register(session,"p2"); c2=p.create_character(session,a2.id,"Friend",c1.country_id,city.id)
    career=CareerService(); job=session.query(Job).first(); career.hire(session,c1.id,job.id)
    skill=session.query(Skill).first(); SkillService().add_xp(session,c1.id,skill.id,100)
    item=session.query(Item).first(); InventoryService().add(session,c1.id,item.id,2); InventoryService().remove(session,c1.id,item.id,1)
    SocialService().relate(session,c1.id,c2.id,"friend",20)
    mission=session.query(Mission).first(); MissionService().start(session,c1.id,mission.id); MissionService().progress(session,c1.id,mission.id,100,EconomyService())
    assert session.get(Character,c1.id).level==2

def test_travel_requires_distinct_destination(session):
    c,city=setup_character(session)
    from lifeverse.models import City as C
    other=C(country_id=c.country_id,name="Other",region="Test",population=1,cost_of_living_index=1); session.add(other); session.commit()
    t=TravelService().schedule(session,c.id,other.id,datetime.now(timezone.utc),10)
    TravelService().complete(session,t.id)
    assert session.get(Character,c.id).city_id==other.id
