from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import time
import logging
import json
import os

from app.rag import RAGPipeline
from app.logger import log_request, log_response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="LLMOps RAG Chatbot API",
    description="Production-ready RAG chatbot with full DevOps pipeline",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag = RAGPipeline()

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"
    prompt_version: Optional[str] = "v1"

class IngestRequest(BaseModel):
    text: str
    source: str

@app.on_event("startup")
async def startup():
    logger.info("LLMOps RAG API started")
    rag.initialize()

@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0", "timestamp": time.time()}

@app.get("/metrics/summary")
def metrics_summary():
    return rag.get_metrics()

@app.post("/ingest")
def ingest_document(req: IngestRequest):
    try:
        doc_id = rag.ingest(req.text, req.source)
        return {"doc_id": doc_id, "status": "ingested"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
def chat(req: ChatRequest, request: Request):
    start = time.time()
    try:
        log_request(req.session_id, req.message, req.prompt_version)
        response, context_docs = rag.query(req.message, prompt_version=req.prompt_version)
        latency = round(time.time() - start, 3)
        log_response(req.session_id, response, latency, len(context_docs))
        return {
            "response": response,
            "latency_s": latency,
            "prompt_version": req.prompt_version,
            "context_docs_used": len(context_docs),
            "session_id": req.session_id
        }
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/prompts")
def list_prompts():
    return rag.list_prompt_versions()

@app.post("/prompts/{version}/activate")
def activate_prompt(version: str):
    success = rag.activate_prompt(version)
    if not success:
        raise HTTPException(status_code=404, detail="Prompt version not found")
    return {"activated": version}
