import os
import uuid
import time
import requests
import json
from typing import Tuple, List, Dict
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
COLLECTION = "rag_docs"
EMBED_MODEL = "all-MiniLM-L6-v2"

PROMPT_REGISTRY: Dict[str, str] = {
    "v1": (
        "You are a helpful assistant. Use the following context to answer the question.\n\n"
        "Context:\n{context}\n\n"
        "Question: {question}\n\n"
        "Answer:"
    ),
    "v2": (
        "You are a concise, expert assistant. Answer using ONLY the provided context. "
        "If unsure, say 'I don't have enough information.'\n\n"
        "Context:\n{context}\n\nQuestion: {question}\nConcise Answer:"
    ),
}

ACTIVE_PROMPT = "v1"
METRICS = {"total_queries": 0, "total_latency": 0.0, "errors": 0}


class RAGPipeline:
    def __init__(self):
        self.client = None
        self.embedder = None

    def initialize(self):
        self.client = QdrantClient(url=QDRANT_URL)
        self.embedder = SentenceTransformer(EMBED_MODEL)
        try:
            self.client.get_collection(COLLECTION)
        except Exception:
            self.client.create_collection(
                collection_name=COLLECTION,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )
        self._seed_sample_docs()

    def _seed_sample_docs(self):
        sample_docs = [
            ("DevOps is the combination of development and operations practices to shorten the systems development lifecycle.", "devops_intro"),
            ("CI/CD pipelines automate the building, testing, and deployment of applications.", "cicd"),
            ("Docker containers package applications with all their dependencies for consistent deployment.", "docker"),
            ("Kubernetes orchestrates containerized applications across multiple hosts.", "kubernetes"),
            ("MLOps extends DevOps principles to machine learning workflows including model training and deployment.", "mlops"),
            ("Prompt versioning allows teams to track, compare, and roll back prompt changes in LLM applications.", "llmops"),
            ("RAG (Retrieval Augmented Generation) combines document retrieval with LLM generation for accurate responses.", "rag"),
            ("Qdrant is an open-source vector database used for semantic similarity search.", "qdrant"),
            ("Ollama allows you to run large language models locally on your machine.", "ollama"),
            ("Model drift occurs when a deployed model's performance degrades due to changes in input data distribution.", "drift"),
        ]
        for text, source in sample_docs:
            self.ingest(text, source)

    def ingest(self, text: str, source: str) -> str:
        doc_id = str(uuid.uuid4())
        embedding = self.embedder.encode([text])[0].tolist()
        self.client.upsert(
            collection_name=COLLECTION,
            points=[PointStruct(id=doc_id, vector=embedding, payload={"text": text, "source": source})]
        )
        return doc_id

    def retrieve(self, query: str, top_k: int = 3) -> List[str]:
        embedding = self.embedder.encode([query])[0].tolist()
        results = self.client.search(collection_name=COLLECTION, query_vector=embedding, limit=top_k)
        return [r.payload["text"] for r in results]

    def generate(self, prompt: str) -> str:
        resp = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()["response"].strip()

    def query(self, question: str, prompt_version: str = "v1") -> Tuple[str, List[str]]:
        global METRICS
        version = prompt_version if prompt_version in PROMPT_REGISTRY else ACTIVE_PROMPT
        docs = self.retrieve(question)
        context = "\n".join(f"- {d}" for d in docs)
        prompt = PROMPT_REGISTRY[version].format(context=context, question=question)
        start = time.time()
        try:
            answer = self.generate(prompt)
            METRICS["total_queries"] += 1
            METRICS["total_latency"] += time.time() - start
        except Exception as e:
            METRICS["errors"] += 1
            raise e
        return answer, docs

    def get_metrics(self) -> dict:
        total = METRICS["total_queries"]
        return {
            "total_queries": total,
            "average_latency_s": round(METRICS["total_latency"] / total, 3) if total > 0 else 0,
            "error_count": METRICS["errors"],
            "active_prompt": ACTIVE_PROMPT,
        }

    def list_prompt_versions(self) -> dict:
        return {"versions": list(PROMPT_REGISTRY.keys()), "active": ACTIVE_PROMPT}

    def activate_prompt(self, version: str) -> bool:
        global ACTIVE_PROMPT
        if version in PROMPT_REGISTRY:
            ACTIVE_PROMPT = version
            return True
        return False
