import os
import json
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

# -------------------------------------------------
# App setup
# -------------------------------------------------

app = FastAPI(title="LNAC API", version="0.1.0")

@app.get("/debug/ping")
def debug_ping():
    return {"ok": True, "code": "candidate-derailer-live"}

API_KEY = os.getenv("LNAC_API_KEY", "")

def require_key(x_lnac_api_key: Optional[str]):
    if not API_KEY:
        raise HTTPException(status_code=500, detail="LNAC_API_KEY not set on server")
    if x_lnac_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

# -------------------------------------------------
# Models
# -------------------------------------------------

class InferenceRequest(BaseModel):
    request_id: str
    user: Dict[str, Any]
    context: Dict[str, Any]
    interaction: Dict[str, Any]
    history_summary: Optional[Dict[str, Any]] = None

# -------------------------------------------------
# Inference endpoint (stub for now)
# -------------------------------------------------

@app.post("/v1/inference")
def inference(
    req: InferenceRequest,
    x_lnac_api_key: Optional[str] = Header(default=None)
):
    require_key(x_lnac_api_key)

    try:
        assessed_level = int(req.user.get("assessed_level", 3))
    except Exception:
        assessed_level = 3

    if assessed_level < 1 or assessed_level > 5:
        assessed_level = 3

    index = _load_json("library-index.json")
    candidates = (index.get("levels") or {}).get(str(assessed_level), [])

    return {
        "debug_code_version": "2026-02-12a",
        "library_version": index.get("version"),
        "primary_classification": {
            "level": assessed_level,
            "derailer_id": candidates[0] if candidates else "NO_DERAILER_FOUND",
            "confidence_bucket": "medium"
        },
        "rationale_bullets": [
            "Stubbed response: LNAC API is reachable and authenticated.",
            "Swap this stub with the real LNAC engine when ready."
        ],
        "clarifying_questions": [
            "What was the trigger in the situation?",
            "What outcome were you trying to protect?"
        ],
        "next_step": {
            "type": "micro_action",
            "message": "Pick one micro-action and run it once this week."
        },
        "micro_actions": [
            {
                "id": "MA_001",
                "title": "Pause before acting",
                "steps": [
                    "Pause 5 seconds",
                    "Ask one clarifying question before responding"
                ]
            },
            {
                "id": "MA_002",
                "title": "Delegate one decision",
                "steps": [
                    "Pick a decision",
                    "Assign an owner",
                    "Set a 24-hour deadline"
                ]
            }
        ],
        "policy_flags": []
    }

# -------------------------------------------------
# Debug: library load sanity check (pilot only)
# -------------------------------------------------

DATA_DIR = Path(__file__).parent / "data"

def _load_json(name: str):
    p = DATA_DIR / name
    return json.loads(p.read_text(encoding="utf-8"))


@app.get("/debug/library")
def debug_library():
    index = _load_json("library-index.json")
    derailers = _load_json("derailer-library.json")
    micro = _load_json("micro-actions.json")

    def count_level_items(obj):
        levels = obj.get("levels", {}) if isinstance(obj, dict) else {}
        total = 0
        for _, items in levels.items():
            if isinstance(items, list):
                total += len(items)
            elif isinstance(items, dict):
                total += len(items)
        return total, sorted(levels.keys())

    derailer_total, derailer_levels = count_level_items(derailers)
    micro_total, micro_levels = count_level_items(micro)

    return {
        "library_index_version": index.get("version"),
        "levels_present": sorted((index.get("levels") or {}).keys()),
        "derailer_count": derailer_total,
        "derailer_levels_present": derailer_levels,
        "micro_action_count": micro_total,
        "micro_levels_present": micro_levels,
        "data_dir_exists": DATA_DIR.exists(),
        "data_files": sorted(p.name for p in DATA_DIR.glob("*.json")),
    }



