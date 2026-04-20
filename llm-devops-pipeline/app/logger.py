import logging
import json
import os
from datetime import datetime

LOG_FILE = os.getenv("LOG_FILE", "logs/requests.jsonl")
os.makedirs("logs", exist_ok=True)

logger = logging.getLogger("llmops.logger")


def _write(record: dict):
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(record) + "\n")


def log_request(session_id: str, message: str, prompt_version: str):
    record = {
        "type": "request",
        "timestamp": datetime.utcnow().isoformat(),
        "session_id": session_id,
        "message_length": len(message),
        "prompt_version": prompt_version,
    }
    logger.info(f"[REQUEST] session={session_id} version={prompt_version}")
    _write(record)


def log_response(session_id: str, response: str, latency_s: float, docs_used: int):
    record = {
        "type": "response",
        "timestamp": datetime.utcnow().isoformat(),
        "session_id": session_id,
        "response_length": len(response),
        "latency_s": latency_s,
        "docs_used": docs_used,
    }
    logger.info(f"[RESPONSE] session={session_id} latency={latency_s}s docs={docs_used}")
    _write(record)
