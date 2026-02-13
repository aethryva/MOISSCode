"""
MOISSCode API - Request and response models.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


# ── Request models ────────────────────────────────────────

@dataclass
class RunRequest:
    """Execute a MOISSCode protocol."""
    code: str
    verbose: bool = False
    patient: Optional[Dict[str, Any]] = None


@dataclass
class ModuleCallRequest:
    """Call a single module function directly."""
    module: str       # e.g. "scores"
    function: str     # e.g. "qsofa"
    args: List[Any] = field(default_factory=list)
    kwargs: Dict[str, Any] = field(default_factory=dict)


# ── Response models ───────────────────────────────────────

@dataclass
class RunResponse:
    success: bool
    events: List[Dict[str, Any]]
    alerts: List[Dict[str, str]]
    stats: Dict[str, Any]
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ModuleCallResponse:
    success: bool
    result: Any
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class HealthResponse:
    status: str
    version: str
    engine_version: str
    modules: int

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class TierInfoResponse:
    tiers: List[Dict[str, Any]]

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class UsageResponse:
    api_key: str
    tier: str
    requests_used: int
    requests_limit: int
    period: str

    def to_dict(self) -> dict:
        return asdict(self)
