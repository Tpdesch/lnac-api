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

    assessed_level = req.user.get("assessed_level", 3)

    return {
        "engine_version": "0.1.0",
        "library_version": req.context.get("library_version", "v0.1.0"),
        "primary_classification": {
            "level": assessed_level,
            "derailer_id": "DUMMY_DERAILER",
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

    if isinstance(derailers, dict) and "derailers" in derailers:
        derailer_items = derailers["derailers"]
    elif isinstance(derailers, dict):
        derailer_items = list(derailers.values())
    elif isinstance(derailers, list):
        derailer_items = derailers
    else:
        derailer_items = []

    if isinstance(micro, dict) and "micro_actions" in micro:
        micro_items = micro["micro_actions"]
    elif isinstance(micro, list):
        micro_items = micro
    else:
        micro_items = []

    return {
        "library_index_version": index.get("version"),
        "levels_present": sorted((index.get("levels") or {}).keys()),
        "derailer_count": len(derailer_items),
        "micro_action_count": len(micro_items),
        "data_dir_exists": DATA_DIR.exists(),
        "data_files": sorted(p.name for p in DATA_DIR.glob("*.json")),
    }

