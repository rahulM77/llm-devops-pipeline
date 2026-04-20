import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


@pytest.fixture
def client():
    with patch("app.rag.RAGPipeline.initialize"), \
         patch("app.rag.RAGPipeline.query", return_value=("Test answer", ["doc1", "doc2"])), \
         patch("app.rag.RAGPipeline.ingest", return_value="mock-id"), \
         patch("app.rag.RAGPipeline.get_metrics", return_value={"total_queries": 5, "average_latency_s": 0.5}):
        from app.main import app
        yield TestClient(app)


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_chat_returns_response(client):
    resp = client.post("/chat", json={"message": "What is RAG?", "session_id": "test-1"})
    assert resp.status_code == 200
    data = resp.json()
    assert "response" in data
    assert "latency_s" in data
    assert "prompt_version" in data


def test_chat_empty_message(client):
    resp = client.post("/chat", json={"message": ""})
    assert resp.status_code in [200, 422]


def test_ingest(client):
    resp = client.post("/ingest", json={"text": "Test document content.", "source": "test"})
    assert resp.status_code == 200
    assert "doc_id" in resp.json()


def test_metrics_endpoint(client):
    resp = client.get("/metrics/summary")
    assert resp.status_code == 200


def test_list_prompts(client):
    resp = client.get("/prompts")
    assert resp.status_code == 200
    assert "versions" in resp.json()
