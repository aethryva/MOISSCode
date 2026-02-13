"""
MOISSCode API Server

A FastAPI service that wraps the MOISSCode engine for remote
protocol execution and module function calls.

Usage:
    pip install -e ".[api]"
    uvicorn moisscode.api.server:app --reload

Environment variables:
    MOISSCODE_API_KEYS_FILE   Path to JSON key store (default: .api_keys.json)
    MOISSCODE_API_DEV_MODE    Set to "1" to enable dev mode (no auth required)
"""

from __future__ import annotations

import json
import logging
import os
import threading
import time
import traceback
from collections import defaultdict
from typing import Any, Dict, List, Optional

try:
    from fastapi import FastAPI, Header, HTTPException, Request
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
except ImportError:
    raise ImportError(
        "FastAPI is required for the API server. "
        "Install with: pip install -e '.[api]'"
    )

from ..version import __version__
from ..lexer import MOISSCodeLexer
from ..parser import MOISSCodeParser
from ..interpreter import MOISSCodeInterpreter
from ..typesystem import Patient

from .config import API_VERSION, API_TITLE, API_DESCRIPTION, TIERS
from .auth import get_store


# ── Constants ─────────────────────────────────────────────

MAX_CODE_LENGTH = 10_000       # 10,000 characters
MAX_BODY_BYTES = 65_536        # 64 KB
EXECUTION_TIMEOUT_SEC = 10     # 10 seconds

ALLOWED_ORIGINS = [
    "https://moisscode.com",
    "https://www.moisscode.com",
    "https://api.moisscode.com",
]

# ── App setup ─────────────────────────────────────────────

DEV_MODE = os.environ.get("MOISSCODE_API_DEV_MODE", "0") == "1"

logger = logging.getLogger("moisscode.api")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if not DEV_MODE else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["X-API-Key", "Content-Type"],
)


# ── Burst rate limiter ────────────────────────────────────

class BurstLimiter:
    """Per-minute sliding window rate limiter."""

    def __init__(self):
        self._windows: Dict[str, List[float]] = defaultdict(list)

    def check(self, key_hash: str, limit: int) -> tuple[bool, int]:
        """Check if request is within per-minute limit.
        Returns (allowed, remaining)."""
        now = time.time()
        window = self._windows[key_hash]
        # Remove entries older than 60 seconds
        window[:] = [t for t in window if now - t < 60]
        if len(window) >= limit:
            return False, 0
        window.append(now)
        return True, limit - len(window)


_burst_limiter = BurstLimiter()


# ── Auth dependency ───────────────────────────────────────

def require_auth(x_api_key: Optional[str] = Header(None), endpoint: str = "") -> str:
    """Validate API key, enforce rate limits, log the request."""
    if DEV_MODE:
        return "dev"
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="Missing X-API-Key header",
        )
    store = get_store()
    rec = store.lookup(x_api_key)
    if rec is None:
        logger.warning("AUTH_FAIL key=%s... endpoint=%s", x_api_key[:8], endpoint)
        raise HTTPException(
            status_code=401,
            detail="Invalid or revoked API key",
        )

    # Monthly limit
    allowed, reason = store.check_and_increment(x_api_key)
    if not allowed:
        logger.warning("RATE_MONTHLY key=%s... endpoint=%s", x_api_key[:8], endpoint)
        raise HTTPException(status_code=429, detail=reason)

    # Per-minute burst limit
    tier = TIERS.get(rec.tier)
    if tier:
        burst_ok, remaining = _burst_limiter.check(
            rec.key_hash, tier.rate_limit_per_minute
        )
        if not burst_ok:
            logger.warning("RATE_BURST key=%s... endpoint=%s limit=%d/min",
                           x_api_key[:8], endpoint, tier.rate_limit_per_minute)
            raise HTTPException(
                status_code=429,
                detail=f"Per-minute rate limit exceeded ({tier.rate_limit_per_minute}/min). "
                       f"Try again in a few seconds.",
            )

    # Audit log
    logger.info("API_CALL key=%s... tier=%s endpoint=%s",
                x_api_key[:8], rec.tier, endpoint)
    return x_api_key


# ── Engine helpers ────────────────────────────────────────

def _make_patient(data: Optional[Dict[str, Any]] = None) -> Patient:
    """Build a Patient from request data, or use defaults."""
    defaults = dict(
        bp=90, hr=110, rr=22, temp=38.3, spo2=94,
        weight=70, age=55, gcs=15, lactate=2.0, sex="M",
    )
    if data:
        defaults.update(data)
    return Patient(**defaults)


def _run_code(code: str, patient_data: Optional[Dict[str, Any]] = None) -> dict:
    """Parse and execute MOISSCode with timeout enforcement."""
    start = time.perf_counter()

    lexer = MOISSCodeLexer()
    tokens = lexer.tokenize(code)
    parser = MOISSCodeParser(tokens)
    program = parser.parse_program()

    interp = MOISSCodeInterpreter()
    patient = _make_patient(patient_data)
    interp.scope["p"] = {"type": "Patient", "value": patient}

    # Execute with timeout
    result_holder: Dict[str, Any] = {}
    error_holder: Dict[str, Any] = {}

    def _execute():
        try:
            result_holder["events"] = interp.execute(program)
        except Exception as exc:
            error_holder["error"] = exc

    thread = threading.Thread(target=_execute, daemon=True)
    thread.start()
    thread.join(timeout=EXECUTION_TIMEOUT_SEC)

    if thread.is_alive():
        # Thread is still running - execution timed out
        logger.warning("TIMEOUT code_length=%d", len(code))
        return {
            "success": False,
            "events": [],
            "alerts": [],
            "stats": {"execution_time_ms": EXECUTION_TIMEOUT_SEC * 1000},
            "error": f"Execution timed out ({EXECUTION_TIMEOUT_SEC}s limit). "
                     f"Check for infinite loops or reduce protocol complexity.",
        }

    if "error" in error_holder:
        raise error_holder["error"]

    events = result_holder.get("events", [])
    elapsed = time.perf_counter() - start

    # Separate alerts from other events
    alerts = []
    log_events = []
    for e in events:
        e_str = str(e)
        if "ALERT" in e_str or "alert" in e_str:
            alerts.append({"message": e_str})
        else:
            log_events.append({"event": e_str})

    return {
        "success": True,
        "events": log_events,
        "alerts": alerts,
        "stats": {
            "event_count": len(events),
            "execution_time_ms": round(elapsed * 1000, 2),
            "engine_version": __version__,
        },
        "error": None,
    }


def _call_module(module: str, function: str, args: list, kwargs: dict) -> dict:
    """Call a single module function directly."""
    from ..stdlib import StandardLibrary

    stdlib = StandardLibrary()

    # Resolve module
    mod = getattr(stdlib, module, None)
    if mod is None:
        return {
            "success": False,
            "result": None,
            "error": f"Unknown module: med.{module}",
        }

    # Resolve function
    fn = getattr(mod, function, None)
    if fn is None:
        return {
            "success": False,
            "result": None,
            "error": f"Unknown function: med.{module}.{function}",
        }

    # Special handling: if the function expects a Patient, build it
    # from the first arg if it's a dict
    if args and isinstance(args[0], dict) and "bp" in args[0]:
        args[0] = _make_patient(args[0])

    result = fn(*args, **kwargs)
    return {
        "success": True,
        "result": result,
        "error": None,
    }


# ── Routes ────────────────────────────────────────────────

@app.get("/")
async def root():
    """API root - basic info."""
    return {
        "service": API_TITLE,
        "version": API_VERSION,
        "engine_version": __version__,
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": API_VERSION,
        "engine_version": __version__,
        "modules": 19,
    }


@app.get("/tiers")
async def list_tiers():
    """List available pricing tiers."""
    tiers = []
    for key, tier in TIERS.items():
        tiers.append({
            "id": key,
            "name": tier.name,
            "requests_per_month": tier.requests_per_month,
            "price_usd": tier.price_usd,
            "rate_limit_per_minute": tier.rate_limit_per_minute,
            "description": tier.description,
        })
    return {"tiers": tiers}


@app.post("/run")
async def run_protocol(request: Request, x_api_key: Optional[str] = Header(None)):
    """
    Execute a MOISSCode protocol.

    Body:
        code (str): MOISSCode source code
        patient (dict, optional): Patient vital signs override
    """
    api_key = require_auth(x_api_key, endpoint="/run")

    # Input size validation
    body_bytes = await request.body()
    if len(body_bytes) > MAX_BODY_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Request body too large ({len(body_bytes)} bytes, limit {MAX_BODY_BYTES})",
        )

    body = json.loads(body_bytes)
    code = body.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Missing 'code' field")

    if len(code) > MAX_CODE_LENGTH:
        raise HTTPException(
            status_code=413,
            detail=f"Code too long ({len(code)} chars, limit {MAX_CODE_LENGTH})",
        )

    patient_data = body.get("patient")

    try:
        result = _run_code(code, patient_data)
        return JSONResponse(content=result)
    except SyntaxError as e:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "events": [],
                "alerts": [],
                "stats": {},
                "error": f"Syntax error: {e}",
            },
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "events": [],
                "alerts": [],
                "stats": {},
                "error": f"Execution error: {e}",
            },
        )


@app.post("/call")
async def call_module(request: Request, x_api_key: Optional[str] = Header(None)):
    """
    Call a single module function directly.

    Body:
        module (str): Module name (e.g. "scores", "pk")
        function (str): Function name (e.g. "qsofa", "calculate_dose")
        args (list): Positional arguments
        kwargs (dict): Keyword arguments
    """
    api_key = require_auth(x_api_key, endpoint="/call")
    body = await request.json()

    module = body.get("module")
    function = body.get("function")
    if not module or not function:
        raise HTTPException(
            status_code=400,
            detail="Missing 'module' and/or 'function' fields",
        )

    args = body.get("args", [])
    kwargs = body.get("kwargs", {})

    try:
        result = _call_module(module, function, args, kwargs)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "result": None,
                "error": f"Execution error: {e}",
            },
        )


@app.get("/usage")
async def get_usage(x_api_key: Optional[str] = Header(None)):
    """Get usage statistics for the authenticated API key."""
    if DEV_MODE:
        return {"tier": "dev", "requests_used": 0, "requests_limit": -1, "period": "dev"}

    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing X-API-Key header")

    store = get_store()
    usage = store.get_usage(x_api_key)
    if usage is None:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return usage


@app.get("/modules")
async def list_modules():
    """List all available modules and their functions."""
    modules = {
        "scores": ["qsofa", "sofa", "news2", "meld", "cha2ds2vasc", "heart_score",
                    "framingham", "child_pugh", "curb65", "wells_pe",
                    "glasgow_blatchford", "kdigo_aki"],
        "pk": ["calculate_dose", "check_interactions", "renal_adjust",
               "hepatic_adjust", "therapeutic_range", "trough_estimate"],
        "lab": ["interpret", "gfr", "panel"],
        "micro": ["identify", "susceptibility", "gram_stain_ddx", "empiric_therapy"],
        "genomics": ["drug_gene_check", "dosing_guidance", "interaction_check",
                      "metabolizer_status"],
        "biochem": ["michaelis_menten", "lineweaver_burk", "enzyme_inhibition",
                     "pathway_lookup"],
        "epi": ["disease_params", "r0", "sir_model", "seir_model",
                "herd_immunity", "incidence_rate", "prevalence", "cfr"],
        "nutrition": ["bmi", "harris_benedict", "icu_caloric_target",
                      "maintenance_fluids", "tpn_calculate"],
        "fhir": ["to_patient", "to_bundle", "to_medication_request"],
        "db": ["save_patient", "save_lab", "query_patient", "audit_log"],
        "io": ["connect", "send_command", "bolus", "stop_infusion",
               "read_monitor", "read_all_vitals", "send_ventilator",
               "read_ventilator", "read_waveform", "set_alarm",
               "check_alarms", "disconnect", "status"],
        "finance": ["bill_cpt", "estimate_cost", "summary"],
        "research": ["deidentify", "consent_check", "randomize",
                     "sample_size", "stratify", "data_lake_log"],
        "glucose": ["hba1c_from_glucose", "eag", "time_in_range", "gmi",
                    "glycemic_variability", "insulin_sensitivity_factor",
                    "carb_ratio", "correction_dose", "basal_rate",
                    "sliding_scale", "full_regimen", "dka_check", "hypo_check"],
        "chem": ["molecular_weight", "lipinski_check", "bcs_classify",
                 "admet_screen", "tox_screen", "lookup", "search_by_target",
                 "search_by_class", "list_compounds", "screen_compound"],
        "signal": ["detect_peaks", "heart_rate_from_rr", "hrv_metrics",
                   "classify_rhythm", "spo2_from_pleth", "moving_average_filter",
                   "detect_anomalies", "respiratory_rate", "perfusion_index"],
        "icd": ["lookup", "search", "drg_lookup", "snomed_to_icd",
                "validate_codes", "filter_by_chapter", "related_codes"],
        "kae": ["track (via protocol syntax)"],
        "moiss": ["classify (via protocol syntax)"],
    }
    return {"module_count": 19, "modules": modules}


# ── Admin routes (dev mode only) ──────────────────────────

@app.post("/admin/keys")
async def create_key(request: Request):
    """Create a new API key (dev mode only)."""
    if not DEV_MODE:
        raise HTTPException(status_code=403, detail="Admin routes require dev mode")

    body = await request.json()
    raw_key = body.get("key")
    owner = body.get("owner", "anonymous")
    tier = body.get("tier", "sandbox")

    if not raw_key:
        raise HTTPException(status_code=400, detail="Missing 'key' field")
    if tier not in TIERS:
        raise HTTPException(status_code=400, detail=f"Unknown tier: {tier}")

    store = get_store()
    record = store.register(raw_key, owner, tier)
    return {
        "message": "Key registered",
        "owner": owner,
        "tier": tier,
        "key_hash": record.key_hash[:16] + "...",
    }


@app.delete("/admin/keys")
async def revoke_key(request: Request):
    """Revoke an API key (dev mode only)."""
    if not DEV_MODE:
        raise HTTPException(status_code=403, detail="Admin routes require dev mode")

    body = await request.json()
    raw_key = body.get("key")
    if not raw_key:
        raise HTTPException(status_code=400, detail="Missing 'key' field")

    store = get_store()
    revoked = store.revoke(raw_key)
    if revoked:
        return {"message": "Key revoked"}
    raise HTTPException(status_code=404, detail="Key not found")
