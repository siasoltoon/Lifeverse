from uuid import UUID


def level_for_xp(xp: int) -> int:
    if xp < 0:
        raise ValueError("xp must be non-negative")
    return 1 + xp // 100


def validate_character_name(name: str) -> str:
    value = name.strip()
    if not 2 <= len(value) <= 80:
        raise ValueError("character name must contain 2-80 characters")
    return value


def validate_location(country_id: UUID | None, city_id: UUID | None) -> None:
    if city_id is not None and country_id is None:
        raise ValueError("city requires a country")
