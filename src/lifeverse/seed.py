from sqlalchemy import select

from .db import SessionLocal
from .models import City, Country, Currency

COUNTRIES = []  # populated by the existing verified seed dataset
