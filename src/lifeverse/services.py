from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from .domain import level_for_xp, validate_character_name, validate_location
from .models import (
    Account, AccountIdentity, Character, CharacterMission, CharacterSkill, CharacterVehicle,
    City, Country, Currency, Employment, GameEvent, Inventory, Item, Job, LedgerAccount,
    LedgerEntry, LedgerTransaction, MarketListing, Mission, NPC, Property, PropertyOwnership,
    Skill, SocialRelation, Travel, Vehicle, Wallet, WorldClock, WorldState,
)

class PlayerService:
    def register(self, session, username, provider=None, external_id=None):
        username=username.strip()
        if not username or len(username)>64: raise ValueError("username must contain 1-64 characters")
        if provider and external_id:
            existing=session.scalar(select(AccountIdentity).where(AccountIdentity.provider==provider,AccountIdentity.external_id==external_id))
            if existing: return existing.account
        account=Account(username=username); session.add(account); session.flush()
        if provider and external_id: session.add(AccountIdentity(account_id=account.id,provider=provider,external_id=external_id))
        session.commit(); session.refresh(account); return account
    def create_character(self,session,account_id,name,country_id=None,city_id=None):
        name=validate_character_name(name); validate_location(country_id,city_id)
        if country_id and not session.get(Country,country_id): raise ValueError("country not found")
        if city_id:
            city=session.get(City,city_id)
            if not city or city.country_id!=country_id: raise ValueError("city does not belong to country")
        if not session.get(Account,account_id): raise ValueError("account not found")
        character=Character(account_id=account_id,name=name,country_id=country_id,city_id=city_id); session.add(character); session.flush()
        if country_id:
            country=session.get(Country,country_id); currency=session.scalar(select(Currency).where(Currency.code==country.currency_code))
            if currency: session.add(Wallet(character_id=character.id,currency_id=currency.id))
        session.commit(); session.refresh(character); return character
    def add_xp(self,session,character_id,amount):
        if amount<=0: raise ValueError("xp amount must be positive")
        c=session.get(Character,character_id)
        if not c: raise ValueError("character not found")
        c.xp+=amount; c.level=level_for_xp(c.xp); session.commit(); session.refresh(c); return c

class WorldService:
    def list_countries(self,s): return list(s.scalars(select(Country).order_by(Country.name)))
    def list_cities(self,s,country_id=None,query=None):
        q=select(City).order_by(City.name)
        if country_id: q=q.where(City.country_id==country_id)
        if query: q=q.where(City.name.ilike(f"%{query.strip()}%"))
        return list(s.scalars(q))
    def initialize(self,s,when=None):
        clock=s.get(WorldClock,1)
        if not clock:
            clock=WorldClock(id=1,world_time=when or datetime.now(timezone.utc),speed=Decimal("1"),paused=False,version=1); s.add(clock); s.commit()
        return clock
    def advance(self,s,seconds):
        if seconds<0: raise ValueError("seconds must be non-negative")
        clock=self.initialize(s)
        if not clock.paused: clock.world_time=clock.world_time+timedelta(seconds=float(Decimal(seconds)*clock.speed))
        clock.version+=1; s.commit(); s.refresh(clock); return clock
    def set_state(self,s,key,value):
        if not key or len(key)>64: raise ValueError("invalid state key")
        row=s.get(WorldState,key) or WorldState(key=key); row.value=value; row.updated_at=datetime.now(timezone.utc); s.add(row); s.commit(); return row

class EconomyService:
    def balance(self,s,character_id):
        w=s.scalar(select(Wallet).where(Wallet.character_id==character_id))
        if not w: raise ValueError("wallet not found")
        return w.balance
    def credit(self,s,character_id,amount,idempotency_key,reference="credit"):
        return self._move(s,character_id,amount,idempotency_key,reference)
    def debit(self,s,character_id,amount,idempotency_key,reference="debit"):
        return self._move(s,character_id,-amount,idempotency_key,reference)
    def _move(self,s,character_id,amount,key,reference):
        amount=Decimal(str(amount))
        if amount==0: raise ValueError("amount must be non-zero")
        existing=s.scalar(select(LedgerTransaction).where(LedgerTransaction.idempotency_key==key))
        if existing: return s.get(Wallet, s.scalar(select(Wallet.character_id).where(Wallet.character_id==character_id)))
        w=s.scalar(select(Wallet).where(Wallet.character_id==character_id))
        if not w: raise ValueError("wallet not found")
        if w.balance+amount<0: raise ValueError("insufficient funds")
        w.balance+=amount
        tx=LedgerTransaction(idempotency_key=key,reference=reference); s.add(tx); s.flush()
        la=s.scalar(select(LedgerAccount).where(LedgerAccount.currency_id==w.currency_id))
        if not la: la=LedgerAccount(code=f"wallet:{w.currency_id}",currency_id=w.currency_id); s.add(la); s.flush()
        s.add(LedgerEntry(transaction_id=tx.id,ledger_account_id=la.id,amount=abs(amount),direction="credit" if amount>0 else "debit"))
        s.commit(); s.refresh(w); return w

class CareerService:
    def hire(self,s,character_id,job_id):
        c=s.get(Character,character_id); j=s.get(Job,job_id)
        if not c or not j: raise ValueError("character or job not found")
        if c.level<j.min_level: raise ValueError("character level is below job requirement")
        if s.scalar(select(Employment).where(Employment.character_id==character_id,Employment.status=="active")): raise ValueError("character already employed")
        e=Employment(character_id=character_id,job_id=job_id,started_at=datetime.now(timezone.utc)); s.add(e); s.commit(); return e
    def fire(self,s,character_id):
        e=s.scalar(select(Employment).where(Employment.character_id==character_id,Employment.status=="active"))
        if not e: raise ValueError("active employment not found")
        e.status="ended"; s.commit(); return e

class SkillService:
    def add_xp(self,s,character_id,skill_id,amount):
        if amount<=0: raise ValueError("skill xp must be positive")
        skill=s.get(Skill,skill_id); c=s.get(Character,character_id)
        if not skill or not c: raise ValueError("character or skill not found")
        row=s.scalar(select(CharacterSkill).where(CharacterSkill.character_id==character_id,CharacterSkill.skill_id==skill_id))
        if not row: row=CharacterSkill(character_id=character_id,skill_id=skill_id); s.add(row)
        row.xp+=amount; row.level=min(skill.max_level,row.xp//100); s.commit(); return row

class InventoryService:
    def add(self,s,character_id,item_id,quantity):
        if quantity<=0: raise ValueError("quantity must be positive")
        if not s.get(Character,character_id) or not s.get(Item,item_id): raise ValueError("character or item not found")
        row=s.scalar(select(Inventory).where(Inventory.character_id==character_id,Inventory.item_id==item_id))
        if not row: row=Inventory(character_id=character_id,item_id=item_id,quantity=0); s.add(row)
        row.quantity+=quantity; s.commit(); return row
    def remove(self,s,character_id,item_id,quantity):
        if quantity<=0: raise ValueError("quantity must be positive")
        row=s.scalar(select(Inventory).where(Inventory.character_id==character_id,Inventory.item_id==item_id))
        if not row or row.quantity<quantity: raise ValueError("insufficient inventory")
        row.quantity-=quantity; s.commit(); return row

class PropertyService:
    def buy(self,s,character_id,property_id,economy):
        p=s.get(Property,property_id)
        if not p or not s.get(Character,character_id): raise ValueError("property or character not found")
        if s.scalar(select(PropertyOwnership).where(PropertyOwnership.property_id==property_id)): raise ValueError("property already owned")
        economy.debit(s,character_id,p.price,f"property:{property_id}","property purchase")
        o=PropertyOwnership(property_id=property_id,character_id=character_id,acquired_at=datetime.now(timezone.utc)); s.add(o); s.commit(); return o

class TravelService:
    def schedule(self,s,character_id,to_city_id,departure_at,minutes=60):
        c=s.get(Character,character_id); dest=s.get(City,to_city_id)
        if not c or not c.city_id or not dest: raise ValueError("travel requires current and destination city")
        if c.city_id==to_city_id: raise ValueError("destination must differ")
        if minutes<=0: raise ValueError("travel duration must be positive")
        t=Travel(character_id=character_id,from_city_id=c.city_id,to_city_id=to_city_id,status="scheduled",departure_at=departure_at,arrival_at=departure_at+timedelta(minutes=minutes))
        s.add(t); s.commit(); return t
    def complete(self,s,travel_id):
        t=s.get(Travel,travel_id)
        if not t: raise ValueError("travel not found")
        c=s.get(Character,t.character_id); c.city_id=t.to_city_id; t.status="completed"; s.commit(); return t

class SocialService:
    def relate(self,s,source,target,kind,delta):
        if source==target: raise ValueError("self relation is invalid")
        if not s.get(Character,source) or not s.get(Character,target): raise ValueError("character not found")
        r=s.scalar(select(SocialRelation).where(SocialRelation.source_character_id==source,SocialRelation.target_character_id==target,SocialRelation.kind==kind))
        if not r: r=SocialRelation(source_character_id=source,target_character_id=target,kind=kind,score=0); s.add(r)
        r.score=max(-100,min(100,r.score+delta)); s.commit(); return r

class NPCService:
    def create(self,s,name,city_id,role="citizen",disposition=0):
        if city_id and not s.get(City,city_id): raise ValueError("city not found")
        n=NPC(name=name.strip(),city_id=city_id,role=role,disposition=max(-100,min(100,disposition))); s.add(n); s.commit(); return n
    def move(self,s,npc_id,city_id):
        n=s.get(NPC,npc_id)
        if not n or not s.get(City,city_id): raise ValueError("npc or city not found")
        n.city_id=city_id; s.commit(); return n

class MissionService:
    def start(self,s,character_id,mission_id):
        c=s.get(Character,character_id); m=s.get(Mission,mission_id)
        if not c or not m: raise ValueError("character or mission not found")
        if c.level<m.required_level: raise ValueError("level requirement not met")
        row=s.scalar(select(CharacterMission).where(CharacterMission.character_id==character_id,CharacterMission.mission_id==mission_id))
        if row and row.state!="completed": raise ValueError("mission already active")
        if row: row.state="active"; row.progress=0; row.completed_at=None
        else: row=CharacterMission(character_id=character_id,mission_id=mission_id); s.add(row)
        s.commit(); return row
    def progress(self,s,character_id,mission_id,amount,economy):
        if amount<=0: raise ValueError("progress must be positive")
        row=s.scalar(select(CharacterMission).where(CharacterMission.character_id==character_id,CharacterMission.mission_id==mission_id))
        m=s.get(Mission,mission_id); c=s.get(Character,character_id)
        if not row or not m or not c: raise ValueError("mission state not found")
        if row.state=="completed": return row
        row.progress+=amount
        if row.progress>=100:
            row.progress=100; row.state="completed"; row.completed_at=datetime.now(timezone.utc); c.xp+=m.xp_reward; c.level=level_for_xp(c.xp)
            if m.currency_reward: economy.credit(s,character_id,m.currency_reward,f"mission:{mission_id}:{character_id}","mission reward")
        s.commit(); return row
