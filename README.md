# AI Business Copilot (Mini CFO + Data Analyst)

Production-oriented backend for an AI-powered business copilot: file upload, tabular analysis, simple forecasting, chart specs for the frontend, and hybrid insights (Pandas statistics + FAISS retrieval + OpenAI).

## Repository layout

```
/backend          FastAPI application
  /api            HTTP routes
  /services       Business logic (data, ML, charts, insights)
  /models         Pydantic request/response schemas
  /rag            FAISS + embeddings retrieval
  /utils          Configuration
/docs             Architecture and API documentation
/frontend         (planned) React dashboard
/docker           (planned) Container definitions
```

## Prerequisites

- Python 3.10+ (tested workflow uses a virtual environment)
- [OpenAI API key](https://platform.openai.com/) for embeddings and chat (`OPENAI_API_KEY`)

## Quick start

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
```

Create a `.env` file in the project root (or `backend/`) if you use file-based config:

```env
OPENAI_API_KEY=sk-...
# Optional overrides
STORAGE_DIR=backend_storage
OPENAI_MODEL=gpt-4.1-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

**Run the API** (from repo root; ensures imports resolve):

```powershell
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Or from repo root with module path (if you configure `PYTHONPATH` to include `backend`):

```powershell
$env:PYTHONPATH = "backend"
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- **Swagger UI:** http://localhost:8000/docs  
- **Health:** http://localhost:8000/health  

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | (empty) | Required for `/api/insights/query` and RAG embeddings |
| `storage_dir` / env | `backend_storage` | Upload directory (see `utils/config.py`: field `storage_dir`) |
| `openai_model` | `gpt-4.1-mini` | Chat model for insights |
| `openai_embedding_model` | `text-embedding-3-small` | Embeddings for FAISS |

> **Note:** Pydantic settings load `.env` from the current working directory when the app starts.

## API overview

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/files/upload` | Upload CSV or Excel; returns `dataset_id` |
| `GET` | `/api/datasets/{dataset_id}/summary` | Summary statistics via Pandas |
| `POST` | `/api/insights/query` | Hybrid insight: stats + RAG + LLM |
| `POST` | `/api/predictions/forecast` | Linear regression forecast |
| `POST` | `/api/charts/generate` | Chart.js–style JSON spec |

Full schemas and examples: [docs/API.md](docs/API.md).

## Documentation index

- [Architecture](docs/ARCHITECTURE.md) — components, diagram, module map  
- [Data flow](docs/DATA_FLOW.md) — upload → analysis → RAG → LLM  
- [API reference](docs/API.md) — endpoints and payloads  
- [Module reference](docs/MODULE_REFERENCE.md) — file-by-file backend map  
- [Scaling](docs/SCALING.md) — horizontal scaling and hardening  

## Limitations (current codebase)

- **In-memory datasets:** After restart, `dataset_id` values are invalid unless you reload from persisted files (future: metadata DB + reload from disk).
- **Forecasting:** Uses a simple time index (or row index) and `LinearRegression`; timestamps for non-date mode are row offsets. See `services/ml_service.py`.
- **CORS:** `allow_origins=["*"]` is suitable for development; tighten for production.

## License

Use and modify per your organization’s policy.
