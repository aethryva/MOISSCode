"""
MOISSCode API - Configuration and tier definitions.
"""

from dataclasses import dataclass
from typing import Dict

# ── Tier definitions ──────────────────────────────────────

@dataclass
class Tier:
    name: str
    requests_per_month: int
    price_usd: int
    rate_limit_per_minute: int
    description: str


TIERS: Dict[str, Tier] = {
    "sandbox": Tier(
        name="Sandbox",
        requests_per_month=50,
        price_usd=0,
        rate_limit_per_minute=5,
        description="Free evaluation tier for testing and prototyping",
    ),
    "starter": Tier(
        name="Starter",
        requests_per_month=5_000,
        price_usd=99,
        rate_limit_per_minute=30,
        description="For small teams and pilot projects",
    ),
    "professional": Tier(
        name="Professional",
        requests_per_month=50_000,
        price_usd=299,
        rate_limit_per_minute=120,
        description="For production clinical decision support workloads",
    ),
    "enterprise": Tier(
        name="Enterprise",
        requests_per_month=-1,  # unlimited
        price_usd=-1,           # custom
        rate_limit_per_minute=600,
        description="Custom pricing for high-volume and on-premise deployments",
    ),
}


# ── Server settings ───────────────────────────────────────

API_VERSION = "1.0.0"
API_TITLE = "MOISSCode API"
API_DESCRIPTION = (
    "REST API for MOISSCode clinical decision support engine. "
    "Execute protocols, query module functions, and integrate "
    "MOISSCode into clinical workflows."
)

# Default to sandbox if no tier configured
DEFAULT_TIER = "sandbox"
