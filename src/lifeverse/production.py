from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DeploymentProfile:
    name: str
    process_model: str
    database: str
    scheduler: str


PROFILES = {
    "local": DeploymentProfile("local", "api+worker", "configured SQLAlchemy URL", "worker loop"),
    "vps": DeploymentProfile("vps", "api+worker", "configured SQLAlchemy URL", "system service/cron"),
    "railway": DeploymentProfile("railway", "api+worker", "managed database", "separate worker service"),
    "ci": DeploymentProfile("ci", "test process", "ephemeral test database", "test scheduler"),
}


def profile(name):
    try:
        return PROFILES[name]
    except KeyError as exc:
        raise ValueError(f"unsupported deployment profile: {name}") from exc
