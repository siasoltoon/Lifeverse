from pathlib import Path

from lifeverse.production import PROFILES


def test_supported_deployment_profiles_are_explicit():
    assert {"local", "vps", "railway", "ci"} <= set(PROFILES)


def test_required_engineering_memory_exists():
    root = Path(__file__).parents[1]
    required = {
        "PROJECT_STATE.md",
        "ARCHITECTURE_MAP.md",
        "PHASE_STATE.md",
        "TASK_STATE.md",
        "TEST_STATE.md",
        "DECISIONS.md",
        "CHANGELOG_ENGINEERING.md",
    }
    found = {p.name for p in (root / "docs" / "engineering").glob("*.md")}
    assert required <= found
