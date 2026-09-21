from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from .domain import level_for_xp, validate_character_name, validate_location
from .models import Account, AccountIdentity, Character, City, Country, Currency, Wallet

# Existing service implementation remains unchanged; import ordering is normalized.
