import os
from uuid import UUID

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from lifeverse.db import Base

os.environ["LIFEVERSE_DATABASE_URL"] = "sqlite://"

@pytest.fixture()
def session():
    e = create_engine("sqlite://", connect_args={"check_same_thread": False})
    Base.metadata.create_all(e)
    S = sessionmaker(bind=e)
    with S() as s:
        yield s
    Base.metadata.drop_all(e)
    e.dispose()
