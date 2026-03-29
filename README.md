# AI Business Copilot (Mini CFO + Data Analyst)

Full-stack AI copilot: upload financial or sales spreadsheets, explore summaries and charts, run baseline forecasts, and ask natural-language questions with **Pandas + FAISS + OpenAI** on the backend and a **React (Vite)** dashboard.

## Repository layout

```
/backend          FastAPI application
  /api            HTTP routes
  /services       Data, ML, charts, insights
  /models         Pydantic schemas
  /rag            Embeddings + FAISS retrieval
  /utils          Settings
/frontend         React + TypeScript SPA (Vite)
/docs             Architecture and API docs
/docker           Dockerfiles + nginx config
docker-compose.yml
```

## Option A: Docker (recommended)

1. Copy environment template and set your key:

```powershell
copy .env.example .env
```

Edit `.env` and set `OPENAI_API_KEY`.

2. From the project root:

```powershell
docker compose up --build
```

- **Web UI (nginx + static app):** http://localhost:8080  
- **API (direct):** http://localhost:8000/docs  

The UI calls `/api/...` on the same origin; nginx proxies those requests to the `api` service.

## Option B: Local development

### Backend

Use **Python 3.12** (or 3.11) for reliable wheels (`pandas`, `faiss-cpu`). Python 3.14 may require building from source.

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create `backend\.env` or root `.env`:

```env
OPENAI_API_KEY=sk-...
STORAGE_DIR=backend_storage
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

Run the API **from the `backend` folder**:

```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- Swagger: http://localhost:8000/docs  

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

- App: http://localhost:5173  
- Vite proxies `/api` → `http://127.0.0.1:8000` (start the backend first).

**Production build (optional):**

```powershell
cd frontend
npm run build
```

Serve `frontend/dist` behind nginx or use Docker.

### Optional: separate API origin

If the UI is not served behind the same host as the API, set at build time:

```powershell
$env:VITE_API_URL = "http://localhost:8000"
npm run build
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | (empty) | Required for full chat + RAG embeddings (insights still return stats-only message if unset) |
| `STORAGE_DIR` / `storage_dir` | `backend_storage` | Uploaded files directory |
| `OPENAI_MODEL` | `gpt-4o-mini` | Chat model for insights |
| `OPENAI_EMBEDDING_MODEL` | `text-embedding-3-small` | Embeddings for FAISS |

Settings load from `.env` via `pydantic-settings` (`backend/utils/config.py`).

## API overview

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/files/upload` | Upload CSV / Excel → `dataset_id` |
| `GET` | `/api/datasets/{id}/summary` | `describe()` summary |
| `POST` | `/api/insights/query` | Stats + optional RAG + LLM |
| `POST` | `/api/predictions/forecast` | Linear regression baseline |
| `POST` | `/api/charts/generate` | Chart.js-style JSON |

Details: [docs/API.md](docs/API.md).

## Documentation

- [Architecture](docs/ARCHITECTURE.md)  
- [Data flow](docs/DATA_FLOW.md)  
- [API reference](docs/API.md)  
- [Module reference](docs/MODULE_REFERENCE.md)  
- [Scaling](docs/SCALING.md)  

## Limitations

- **In-memory DataFrames:** `dataset_id` is valid only until the API process restarts (files remain on disk; reload-from-disk is a natural next step).
- **Forecasting:** Simple linear model over time or row index; not a full time-series product.
- **RAG:** First insight build embeds every row—fine for modest files; large tables need batching/queueing (see [docs/SCALING.md](docs/SCALING.md)).

## License

Use and modify per your organization’s policy.
