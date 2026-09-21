from uuid import uuid4

import pytest

from lifeverse.domain import level_for_xp, validate_character_name, validate_location


def test_level():
    assert level_for_xp(0) == 1 and level_for_xp(99) == 1 and level_for_xp(100) == 2


def test_name():
    assert validate_character_name(" Ali ") == "Ali"
    with pytest.raises(ValueError):
        validate_character_name("x")


def test_location():
    with pytest.raises(ValueError):
        validate_location(None, uuid4())
