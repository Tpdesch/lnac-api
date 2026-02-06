import os
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, Optional

app = FastAPI(title="LNAC API", version="0.1.0")

API_KEY = os.getenv("LNAC_API_KEY", "")

def require_key(x_lnac_api_key: Optional[str]):
    if not API_KEY:
        raise HTTPException(status_code=500, detail="LNAC_API_KEY not set on server")
    if x_lnac_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

class InferenceRequest(BaseModel):
    request_id: str
    user: Dict[str, Any]
    context: Dict[str, Any]
    interaction: Dict[str, Any]
    history_summary: Optional[Dict[str, Any]] = None

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/v1/inference")
def inference(req: InferenceRequest, x_lnac_api_key: Optional[str] = Header(default=None)):
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
                "steps": ["Pause 5 seconds", "Ask one clarifying question before deciding"]
            },
            {
                "id": "MA_002",
                "title": "Delegate one decision",
                "steps": ["Pick a decision", "Assign an owner", "Set a 24-hour deadline"]
            }
        ],
        "policy_flags": []
    }
