# 🚀 LLMOps RAG Chatbot Pipeline

| Stack: Ollama · Qdrant · FastAPI · Docker · GitHub Actions · Grafana

---

## 📐 Architecture

```
User Browser (Frontend)
        │
        ▼
  FastAPI Backend  ──►  Qdrant (Vector DB)
        │
        ▼
   Ollama (Local LLM: llama3.2)
        │
  Prometheus ──► Grafana (Monitoring Dashboard)
        │
  GitHub Actions (CI/CD Pipeline)
```

**What this project demonstrates:**
- ✅ **RAG pipeline** — semantic document retrieval + LLM generation
- ✅ **Prompt versioning** — switch between prompt strategies via API
- ✅ **Containerized deployment** — Docker Compose for all services
- ✅ **CI/CD** — GitHub Actions: lint → test → build → push → deploy
- ✅ **Monitoring** — Prometheus metrics + Grafana dashboards
- ✅ **Logging** — structured JSONL request/response logs

---

## 📁 Project Structure

```
llm-devops-pipeline/
├── app/
│   ├── main.py          # FastAPI app & routes
│   ├── rag.py           # RAG pipeline (embed → retrieve → generate)
│   └── logger.py        # Structured request/response logging
├── pipeline/
│   └── validate_prompts.py   # CI prompt validation script
├── tests/
│   └── test_api.py      # Pytest unit tests
├── monitoring/
│   ├── prometheus.yml   # Prometheus scrape config
│   └── grafana/         # Grafana datasources & dashboards
├── frontend/
│   └── index.html       # Chat UI (served by Nginx)
├── docker/
│   └── Dockerfile       # API container
├── .github/
│   └── workflows/
│       └── ci-cd.yml    # Full CI/CD pipeline
├── docker-compose.yml   # All services
├── requirements.txt
└── README.md
```

---

## 🖥️ How to Run on Your Computer

### Prerequisites — Install These First

| Tool | Download Link | Check if installed |
|------|--------------|-------------------|
| **Docker Desktop** | https://www.docker.com/products/docker-desktop | `docker --version` |
| **Git** | https://git-scm.com | `git --version` |
| Python 3.11+ (optional, for local dev) | https://python.org | `python --version` |

> ⚠️ **RAM requirement**: Ollama with llama3.2 needs ~4 GB RAM. 8 GB recommended.

---

### Step 1 — Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/llm-devops-pipeline.git
cd llm-devops-pipeline
```

---

### Step 2 — Start All Services

```bash
docker compose up --build
```

This will automatically:
1. Pull and start **Qdrant** (vector database) on port 6333
2. Pull **Ollama** and download the **llama3.2** model (~2 GB, first time only)
3. Build and start the **FastAPI backend** on port 8000
4. Start **Prometheus** on port 9090
5. Start **Grafana** on port 3001
6. Serve the **frontend** on port 3000

> ⏳ First startup takes 5–10 minutes (model download). Subsequent starts are fast.

---

### Step 3 — Open the Apps

| Service | URL | Credentials |
|---------|-----|-------------|
| 💬 **Chat UI** | http://localhost:3000 | — |
| 📡 **API Docs** | http://localhost:8000/docs | — |
| 📊 **Grafana** | http://localhost:3001 | admin / admin |
| 🔍 **Prometheus** | http://localhost:9090 | — |

---

### Step 4 — Try the Chatbot

Open http://localhost:3000 and ask:
- "What is RAG?"
- "Explain MLOps pipelines"
- "How does Kubernetes work?"
- "What is model drift?"

You can also:
- **Switch prompt versions** (v1 Standard / v2 Concise) in the header
- **Ingest new documents** using the sidebar
- **Monitor metrics** live in the sidebar

---

### Step 5 — Run Tests Locally

```bash
# Install test dependencies
pip install -r requirements.txt pytest

# Run unit tests
pytest tests/ -v
```

---

### Step 6 — Test the API Directly

```bash
# Health check
curl http://localhost:8000/health

# Chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is MLOps?", "prompt_version": "v1"}'

# Ingest a document
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"text": "Your custom knowledge here.", "source": "my_doc"}'

# Switch prompt version
curl -X POST http://localhost:8000/prompts/v2/activate
```

---

### Stopping the Project

```bash
docker compose down          # Stop services (keeps data)
docker compose down -v       # Stop + delete all data volumes
```

---

## 🔄 CI/CD Pipeline (GitHub Actions)

Every `git push` to `main` triggers:

```
Push to main
    │
    ▼
[1] Lint (Ruff)  ──────► fail → stop
    │
    ▼
[2] Unit Tests   ──────► fail → stop
    │
    ▼
[3] Prompt Validation ─► fail → stop
    │
    ▼
[4] Docker Build & Push to GHCR
    │
    ▼
[5] Deploy to Staging
```

To enable: push this repo to GitHub. Actions run automatically.

---

## 💡 Project Extension Ideas

- Add **A/B testing** — route 50% of traffic to each prompt version
- Add **LangChain** for more complex chains
- Deploy to **cloud** (AWS EC2 / GCP Cloud Run / Railway)
- Add **authentication** (JWT tokens)
- Build a **retraining trigger** when latency exceeds threshold

---

## 👥 Team Role Suggestions

| Role | Responsibilities |
|------|-----------------|
| **Member 1** | FastAPI backend, RAG pipeline, API routes |
| **Member 2** | Docker, CI/CD (GitHub Actions), monitoring |
| **Member 3** | Frontend UI, documentation, testing |
