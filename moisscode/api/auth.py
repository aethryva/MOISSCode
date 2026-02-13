"""
MOISSCode API - API key authentication and rate limiting.

Keys are stored in a local JSON file for development.
Production deployments should replace this with a database backend.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass, field, asdict
from typing import Dict, Optional

from .config import TIERS, DEFAULT_TIER


# ── Key storage path ──────────────────────────────────────

_KEYS_FILE = os.environ.get(
    "MOISSCODE_API_KEYS_FILE",
    os.path.join(os.path.dirname(__file__), ".api_keys.json"),
)


# ── Data structures ───────────────────────────────────────

@dataclass
class APIKeyRecord:
    key_hash: str
    tier: str
    owner: str
    created_at: float
    requests_this_month: int = 0
    month_reset: str = ""  # YYYY-MM format
    active: bool = True


# ── In-memory store with JSON persistence ─────────────────

class KeyStore:
    """Simple file-backed API key store."""

    def __init__(self, path: str = _KEYS_FILE):
        self._path = path
        self._keys: Dict[str, APIKeyRecord] = {}
        self._load()

    # ── persistence ────────────────────────────────────

    def _load(self) -> None:
        if os.path.exists(self._path):
            try:
                with open(self._path, "r") as f:
                    data = json.load(f)
                for h, rec in data.items():
                    self._keys[h] = APIKeyRecord(**rec)
            except (json.JSONDecodeError, TypeError):
                self._keys = {}

    def _save(self) -> None:
        data = {h: asdict(rec) for h, rec in self._keys.items()}
        os.makedirs(os.path.dirname(self._path) or ".", exist_ok=True)
        with open(self._path, "w") as f:
            json.dump(data, f, indent=2)

    # ── key management ─────────────────────────────────

    @staticmethod
    def hash_key(raw_key: str) -> str:
        return hashlib.sha256(raw_key.encode()).hexdigest()

    def register(self, raw_key: str, owner: str, tier: str = DEFAULT_TIER) -> APIKeyRecord:
        """Register a new API key."""
        h = self.hash_key(raw_key)
        now = time.time()
        month = time.strftime("%Y-%m", time.gmtime(now))
        record = APIKeyRecord(
            key_hash=h,
            tier=tier,
            owner=owner,
            created_at=now,
            requests_this_month=0,
            month_reset=month,
            active=True,
        )
        self._keys[h] = record
        self._save()
        return record

    def lookup(self, raw_key: str) -> Optional[APIKeyRecord]:
        """Look up a key. Returns None if not found or inactive."""
        h = self.hash_key(raw_key)
        rec = self._keys.get(h)
        if rec and not rec.active:
            return None
        return rec

    def revoke(self, raw_key: str) -> bool:
        """Revoke a key."""
        h = self.hash_key(raw_key)
        rec = self._keys.get(h)
        if rec:
            rec.active = False
            self._save()
            return True
        return False

    # ── rate limiting ──────────────────────────────────

    def check_and_increment(self, raw_key: str) -> tuple[bool, str]:
        """
        Check if a request is allowed under the key's tier limits.
        Returns (allowed, reason).
        """
        rec = self.lookup(raw_key)
        if rec is None:
            return False, "Invalid or revoked API key"

        tier = TIERS.get(rec.tier)
        if tier is None:
            return False, f"Unknown tier: {rec.tier}"

        # Reset counter if month changed
        current_month = time.strftime("%Y-%m", time.gmtime())
        if rec.month_reset != current_month:
            rec.requests_this_month = 0
            rec.month_reset = current_month

        # Check monthly limit (-1 = unlimited)
        if tier.requests_per_month > 0 and rec.requests_this_month >= tier.requests_per_month:
            return False, (
                f"Monthly request limit reached ({tier.requests_per_month} requests). "
                f"Upgrade your plan at https://moisscode.com/pricing"
            )

        rec.requests_this_month += 1
        self._save()
        return True, "OK"

    def get_usage(self, raw_key: str) -> Optional[dict]:
        """Return usage stats for a key."""
        rec = self.lookup(raw_key)
        if rec is None:
            return None
        tier = TIERS.get(rec.tier)
        current_month = time.strftime("%Y-%m", time.gmtime())
        if rec.month_reset != current_month:
            used = 0
        else:
            used = rec.requests_this_month
        return {
            "tier": rec.tier,
            "owner": rec.owner,
            "requests_used": used,
            "requests_limit": tier.requests_per_month if tier else 0,
            "period": current_month,
        }


# ── Module-level singleton ────────────────────────────────

_store: Optional[KeyStore] = None


def get_store() -> KeyStore:
    global _store
    if _store is None:
        _store = KeyStore()
    return _store
