from fastapi import FastAPI, HTTPException, Security, Request
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client
import os
import hashlib
import traceback
import re
from datetime import datetime, timezone
from dotenv import load_dotenv

# Import MOISSCode internals
from moisscode.lexer import MOISSCodeLexer
from moisscode.parser import MOISSCodeParser
from moisscode.interpreter import MOISSCodeInterpreter
from moisscode.modules.med_io import MedIO
from moisscode.stdlib import StandardLibrary

# Load environment variables
load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
AI_FEATURES_ENABLED = os.environ.get("AI_FEATURES_ENABLED", "true").lower() == "true"
AI_ALERT_THRESHOLD = float(os.environ.get("AI_ALERT_THRESHOLD", "10.0"))
AI_STOP_THRESHOLD = float(os.environ.get("AI_STOP_THRESHOLD", "20.0"))

# Tier-based daily code generation limits
TIER_GEN_LIMITS = {
    "sandbox": 10,
    "starter": 100,
    "professional": 500,
    "enterprise": 1000,
}

if not SUPABASE_URL or not SUPABASE_KEY:
    print("WARNING: Supabase credentials missing. API will fail to authenticate.")

# Initialize Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

# Load system prompt for AI code generation
SYSTEM_PROMPT = ""
try:
    with open(os.path.join(os.path.dirname(__file__), "for-ai-system.md"), "r", encoding="utf-8") as f:
        SYSTEM_PROMPT = f.read()
except FileNotFoundError:
    SYSTEM_PROMPT = "You are MOISSCode Assistant. Generate only valid MOISSCode (.moiss) protocols."
    print("WARNING: for-ai-system.md not found, using minimal system prompt.")

app = FastAPI(title="MOISSCode API", version="2.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security Scheme
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

class CodeRequest(BaseModel):
    code: str

class GenerateRequest(BaseModel):
    prompt: str

# ═══════════════════════════════════════════════════════════════
# Cost Tracking + Circuit Breakers
# ═══════════════════════════════════════════════════════════════

# Model cost rates per million tokens
MODEL_COSTS = {
    "deepseek-chat": {"input": 0.28, "output": 0.42},
    "claude-sonnet-4-5-20241022": {"input": 3.0, "output": 15.0},
    "claude-opus-4-5-20250514": {"input": 5.0, "output": 25.0},
}

def estimate_cost(model: str, tokens_in: int, tokens_out: int) -> float:
    rates = MODEL_COSTS.get(model, {"input": 1.0, "output": 5.0})
    return (tokens_in * rates["input"] / 1_000_000) + (tokens_out * rates["output"] / 1_000_000)

def get_daily_spend() -> float:
    if not supabase:
        return 0.0
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    try:
        result = supabase.table("ai_spend_log") \
            .select("estimated_cost_usd") \
            .gte("created_at", f"{today}T00:00:00Z") \
            .execute()
        return sum(r["estimated_cost_usd"] for r in (result.data or []))
    except Exception:
        return 0.0

def log_spend(feature: str, model: str, tokens_in: int, tokens_out: int, cost: float, user_id=None):
    if not supabase:
        return
    try:
        supabase.table("ai_spend_log").insert({
            "feature": feature,
            "model": model,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "estimated_cost_usd": cost,
            "user_id": user_id,
        }).execute()
    except Exception as e:
        print(f"Spend log error: {e}")

def check_ai_budget():
    """Check if AI features are within budget. Raises HTTPException if not."""
    if not AI_FEATURES_ENABLED:
        raise HTTPException(status_code=503, detail="AI features are currently paused by admin")
    
    daily_spend = get_daily_spend()
    
    if daily_spend >= AI_STOP_THRESHOLD:
        raise HTTPException(
            status_code=503,
            detail=f"AI features paused: daily spend ${daily_spend:.2f} exceeds ${AI_STOP_THRESHOLD:.2f} limit"
        )
    
    return daily_spend

# ═══════════════════════════════════════════════════════════════
# LLM Calls (DeepSeek + Anthropic)
# ═══════════════════════════════════════════════════════════════

def call_deepseek(prompt: str, system: str) -> dict:
    """Call DeepSeek V3.2 via OpenAI-compatible API."""
    import openai
    client = openai.OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com/v1"
    )
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        max_tokens=2000,
        temperature=0.2,
    )
    text = response.choices[0].message.content or ""
    tokens_in = response.usage.prompt_tokens if response.usage else 0
    tokens_out = response.usage.completion_tokens if response.usage else 0
    return {"text": text, "tokens_in": tokens_in, "tokens_out": tokens_out, "model": "deepseek-chat"}

def call_anthropic(prompt: str, system: str, model: str = "claude-sonnet-4-5-20241022") -> dict:
    """Call Anthropic Claude API."""
    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    response = client.messages.create(
        model=model,
        max_tokens=2000,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.content[0].text if response.content else ""
    tokens_in = response.usage.input_tokens
    tokens_out = response.usage.output_tokens
    return {"text": text, "tokens_in": tokens_in, "tokens_out": tokens_out, "model": model}

# ═══════════════════════════════════════════════════════════════
# Code Validation
# ═══════════════════════════════════════════════════════════════

def extract_moiss_code(text: str) -> str:
    """Extract .moiss code from markdown code blocks or raw text."""
    # Try to extract from ```moiss or ``` blocks
    pattern = r'```(?:moiss|moiss\w*)?\s*\n([\s\S]*?)```'
    matches = re.findall(pattern, text)
    if matches:
        return "\n\n".join(matches)
    # If no code blocks, try the whole text (LLM might return raw code)
    if "protocol " in text:
        return text
    return text

def validate_moiss_code(code: str) -> dict:
    """Run code through Lexer + Parser. Returns {valid, error}."""
    try:
        lexer = MOISSCodeLexer()
        tokens = lexer.tokenize(code)
        parser = MOISSCodeParser(tokens)
        parser.parse_program()
        return {"valid": True, "error": None}
    except Exception as e:
        return {"valid": False, "error": str(e)}

# ═══════════════════════════════════════════════════════════════
# Input Validation
# ═══════════════════════════════════════════════════════════════

INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"ignore\s+(all\s+)?above",
    r"you\s+are\s+now",
    r"system\s*prompt",
    r"reveal\s+(your|the)\s+instructions",
    r"pretend\s+you\s+are",
    r"forget\s+(your|all)",
    r"new\s+instructions",
    r"override\s+(your|previous)",
]

def validate_prompt(prompt: str) -> str:
    """Sanitize and validate user prompt. Returns cleaned prompt or raises."""
    if not prompt or not prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    
    if len(prompt) > 2000:
        raise HTTPException(status_code=400, detail="Prompt too long (max 2000 chars)")
    
    # Strip HTML
    cleaned = re.sub(r'<[^>]*>', '', prompt).strip()
    
    # Check injection
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, cleaned, re.IGNORECASE):
            raise HTTPException(status_code=400, detail="Invalid prompt")
    
    return cleaned

# ═══════════════════════════════════════════════════════════════
# Auth
# ═══════════════════════════════════════════════════════════════

async def verify_api_key(api_key: str = Security(api_key_header)):
    """Authenticate and authorize the request based on API Key."""
    if not api_key:
        raise HTTPException(status_code=403, detail="Missing X-API-Key header")
    
    if not supabase:
        raise HTTPException(status_code=500, detail="Server configuration error (Database unavailable)")

    key_hash = hashlib.sha256(api_key.encode()).hexdigest()

    try:
        response = supabase.table("api_keys").select("*").eq("key_hash", key_hash).single().execute()
        if not response.data:
            raise HTTPException(status_code=401, detail="Invalid API Key")
        
        key_record = response.data

        if not key_record.get("is_active"):
            raise HTTPException(status_code=403, detail="API Key is inactive or revoked")

        limit = key_record.get("monthly_limit", 0)
        usage = key_record.get("monthly_requests", 0)
        
        if limit != -1 and usage >= limit:
            raise HTTPException(status_code=429, detail="Monthly rate limit exceeded")

        return key_record

    except HTTPException:
        raise
    except Exception as e:
        print(f"Auth Error: {e}")
        raise HTTPException(status_code=500, detail="Authentication failed")

# ═══════════════════════════════════════════════════════════════
# Endpoints
# ═══════════════════════════════════════════════════════════════

@app.get("/")
def read_root():
    daily = get_daily_spend()
    return {
        "status": "MOISSCode Engine Online",
        "version": "2.0",
        "ai_enabled": AI_FEATURES_ENABLED,
        "daily_spend": f"${daily:.4f}",
        "alert_at": f"${AI_ALERT_THRESHOLD}",
        "stop_at": f"${AI_STOP_THRESHOLD}",
    }

@app.get("/devices")
def get_devices(key_record: dict = Security(verify_api_key)):
    return MedIO.devices.devices

@app.get("/finance")
def get_finance(key_record: dict = Security(verify_api_key)):
    return {
        "total": StandardLibrary.finance.get_total(),
        "ledger": StandardLibrary.finance.get_ledger()
    }

@app.get("/ai/status")
def ai_status():
    """Public endpoint: check AI feature status and spend."""
    daily = get_daily_spend()
    return {
        "enabled": AI_FEATURES_ENABLED,
        "daily_spend_usd": round(daily, 4),
        "alert_threshold": AI_ALERT_THRESHOLD,
        "stop_threshold": AI_STOP_THRESHOLD,
        "status": "stopped" if daily >= AI_STOP_THRESHOLD else ("alert" if daily >= AI_ALERT_THRESHOLD else "ok"),
    }

@app.post("/run")
def run_code(request: CodeRequest, key_record: dict = Security(verify_api_key)):
    """Execute MOISSCode script."""
    try:
        new_usage = key_record.get("monthly_requests", 0) + 1
        supabase.table("api_keys").update({"monthly_requests": new_usage}).eq("id", key_record["id"]).execute()
    except Exception as e:
        print(f"Usage update failed: {e}")

    print(f"Executing request for user {key_record.get('user_id')} (Usage: {new_usage}/{key_record.get('monthly_limit')})")

    try:
        lexer = MOISSCodeLexer()
        tokens = lexer.tokenize(request.code)
        
        parser = MOISSCodeParser(tokens)
        program = parser.parse_program()
        
        interpreter = MOISSCodeInterpreter()
        events = interpreter.execute(program)
        
        return {
            "status": "success",
            "events": events,
            "usage": {"current": new_usage, "limit": key_record.get("monthly_limit")}
        }
        
    except Exception as e:
        print(f"Execution Error: {e}")
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

@app.post("/generate")
def generate_code(request: GenerateRequest, key_record: dict = Security(verify_api_key)):
    """
    AI Code Generator: Convert natural language → validated MOISSCode.
    
    Model routing:
    - Sandbox / Starter → DeepSeek V3.2 (cheap) → Claude Sonnet fallback
    - Professional / Enterprise → Claude Sonnet → Claude Opus fallback
    """
    # 1. Check AI budget
    daily_spend = check_ai_budget()
    
    # 2. Validate prompt
    clean_prompt = validate_prompt(request.prompt)
    
    # 3. Check daily generation limit for this user
    user_id = key_record.get("user_id")
    tier = key_record.get("tier", "sandbox").lower()
    daily_limit = TIER_GEN_LIMITS.get(tier, 10)
    
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    try:
        usage_result = supabase.table("ai_usage") \
            .select("code_generations") \
            .eq("user_id", user_id) \
            .eq("date", today) \
            .single() \
            .execute()
        current_gens = usage_result.data.get("code_generations", 0) if usage_result.data else 0
    except Exception:
        current_gens = 0
    
    if current_gens >= daily_limit:
        raise HTTPException(
            status_code=429,
            detail=f"Daily generation limit reached ({daily_limit} for {tier} tier)"
        )
    
    # 4. Determine model chain based on tier
    if tier in ("professional", "enterprise"):
        primary_model = "anthropic"
        primary_name = "claude-sonnet-4-5-20241022"
        fallback_model = "anthropic"
        fallback_name = "claude-opus-4-5-20250514"
    else:
        primary_model = "deepseek"
        primary_name = "deepseek-chat"
        fallback_model = "anthropic"
        fallback_name = "claude-sonnet-4-5-20241022"
    
    # 5. Generation prompt
    gen_prompt = (
        f"Generate a complete MOISSCode protocol for the following request. "
        f"Output ONLY the .moiss code inside a ```moiss code block. "
        f"Do NOT include explanations outside the code block.\n\n"
        f"Request: {clean_prompt}"
    )
    
    # 6. Try primary model
    generated_code = ""
    model_used = primary_name
    total_cost = 0.0
    
    try:
        if primary_model == "deepseek":
            result = call_deepseek(gen_prompt, SYSTEM_PROMPT)
        else:
            result = call_anthropic(gen_prompt, SYSTEM_PROMPT, primary_name)
        
        cost = estimate_cost(result["model"], result["tokens_in"], result["tokens_out"])
        total_cost += cost
        log_spend("code_gen", result["model"], result["tokens_in"], result["tokens_out"], cost, user_id)
        
        generated_code = extract_moiss_code(result["text"])
        model_used = result["model"]
        
    except Exception as e:
        print(f"Primary model error ({primary_name}): {e}")
        # Fall through to fallback
    
    # 7. Validate
    validation = validate_moiss_code(generated_code) if generated_code else {"valid": False, "error": "No code generated"}
    
    # 8. If invalid, retry with error feedback
    if not validation["valid"] and generated_code:
        retry_prompt = (
            f"The MOISSCode you generated has a syntax error:\n"
            f"Error: {validation['error']}\n\n"
            f"Original code:\n```\n{generated_code}\n```\n\n"
            f"Fix the error and output ONLY the corrected .moiss code in a ```moiss code block."
        )
        try:
            if primary_model == "deepseek":
                result = call_deepseek(retry_prompt, SYSTEM_PROMPT)
            else:
                result = call_anthropic(retry_prompt, SYSTEM_PROMPT, primary_name)
            
            cost = estimate_cost(result["model"], result["tokens_in"], result["tokens_out"])
            total_cost += cost
            log_spend("code_gen", result["model"], result["tokens_in"], result["tokens_out"], cost, user_id)
            
            generated_code = extract_moiss_code(result["text"])
            validation = validate_moiss_code(generated_code)
            
        except Exception as e:
            print(f"Retry error ({primary_name}): {e}")
    
    # 9. If still invalid, escalate to fallback model
    if not validation["valid"]:
        try:
            if fallback_model == "anthropic":
                result = call_anthropic(gen_prompt, SYSTEM_PROMPT, fallback_name)
            else:
                result = call_deepseek(gen_prompt, SYSTEM_PROMPT)
            
            cost = estimate_cost(result["model"], result["tokens_in"], result["tokens_out"])
            total_cost += cost
            log_spend("code_gen", result["model"], result["tokens_in"], result["tokens_out"], cost, user_id)
            
            generated_code = extract_moiss_code(result["text"])
            model_used = result["model"]
            validation = validate_moiss_code(generated_code)
            
        except Exception as e:
            print(f"Fallback error ({fallback_name}): {e}")
    
    # 10. Update usage counter
    try:
        supabase.table("ai_usage").upsert({
            "user_id": user_id,
            "date": today,
            "code_generations": current_gens + 1,
        }, on_conflict="user_id,date").execute()
    except Exception as e:
        print(f"Usage update error: {e}")
    
    # 11. Check if alert threshold crossed
    new_daily = daily_spend + total_cost
    spend_status = "ok"
    if new_daily >= AI_STOP_THRESHOLD:
        spend_status = "stopped"
    elif new_daily >= AI_ALERT_THRESHOLD:
        spend_status = "alert"
    
    return {
        "status": "success",
        "code": generated_code,
        "valid": validation["valid"],
        "validation_error": validation["error"],
        "model_used": model_used,
        "cost_usd": round(total_cost, 6),
        "usage": {
            "generations_today": current_gens + 1,
            "daily_limit": daily_limit,
            "tier": tier,
        },
        "spend": {
            "daily_total": round(new_daily, 4),
            "status": spend_status,
        }
    }

if __name__ == "__main__":
    print("Starting Secure MOISSCode API v2.0...")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
