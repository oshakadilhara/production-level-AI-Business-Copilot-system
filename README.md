# AI Business Copilot (Mini CFO + Data Analyst)

Full-stack AI copilot: upload financial or sales spreadsheets, explore summaries and charts, run baseline forecasts, and ask natural-language questions with **Pandas + FAISS + OpenAI** on the backend and a **React (Vite)** dashboard.

**Step-by-step: how to run locally or with Docker → [docs/RUNNING.md](docs/RUNNING.md)**

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

1. At the **repository root**, create a **`.env`** file (see [Configuration](#configuration)) and set at least `OPENAI_API_KEY`.

2. From the project root:

```powershell
docker compose up --build
```

- **Web UI (nginx + static app):** http://localhost:9080 (override with `WEB_PORT` in `.env`)  
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

Use the same **`.env`** variables as in [Configuration](#configuration). Put `.env` in the **repo root** and copy it to **`backend\.env`**, or only in **`backend\`** if you always start Uvicorn from there (see [docs/RUNNING.md](docs/RUNNING.md)).

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

Create **`.env`** at the **repository root** (gitignored). Docker Compose reads it for the API container and for `WEB_PORT`. For local Uvicorn started inside **`backend/`**, either copy `.env` into `backend/` or rely on shell environment variables.

**Template (all keys the stack uses):**

```env
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
STORAGE_DIR=backend_storage
ENVIRONMENT=development
WEB_PORT=9080
```

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | (empty) | Required for full chat + RAG; insights still return a stats-only message if unset |
| `OPENAI_MODEL` | `gpt-4o-mini` | Chat Completions model |
| `OPENAI_EMBEDDING_MODEL` | `text-embedding-3-small` | Embeddings for FAISS |
| `STORAGE_DIR` | `backend_storage` | Upload directory on disk (`docker-compose` overrides to `/data/storage` in the API container) |
| `ENVIRONMENT` | `development` | Reserved label for future behavior toggles |
| `WEB_PORT` | `9080` | **Docker only:** host port mapped to the nginx UI |

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

- [Documentation index](docs/INDEX.md)  
- **[Run the stack (local + Docker)](docs/RUNNING.md)**  
- [Architecture](docs/ARCHITECTURE.md)  
- [Data flow](docs/DATA_FLOW.md)  
- [API reference](docs/API.md)  
- [Module reference](docs/MODULE_REFERENCE.md)  
- [Scaling](docs/SCALING.md)  

## Publishing to GitHub (public repository)

- **`.gitignore`** excludes **`.env`** (and other `.env.*` variants) so keys are not pushed. The variable list lives in this README and in **`docs/RUNNING.md`**—each developer creates their own local `.env`.
- Before pushing: `git status`, `git diff --cached`, and `git check-ignore -v .env` (should report ignored).
- If `.env` was ever committed, rotate secrets and scrub history (`git filter-repo` / BFG) before the repo stays public.

## Limitations

- **In-memory DataFrames:** `dataset_id` is valid only until the API process restarts (files remain on disk; reload-from-disk is a natural next step).
- **Forecasting:** Simple linear model over time or row index; not a full time-series product.
- **RAG:** First insight build embeds every row—fine for modest files; large tables need batching/queueing (see [docs/SCALING.md](docs/SCALING.md)).

## License

Use and modify per your organization’s policy.
