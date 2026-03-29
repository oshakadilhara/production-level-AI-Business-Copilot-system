# How to run the AI Business Copilot

This guide covers **local development** (backend + frontend in two terminals), **Docker**, and quick checks. Use the path where you cloned the project (below, `PROJECT_ROOT`).

---

## Prerequisites

| Tool | Purpose | Notes |
|------|---------|--------|
| **Python 3.11 or 3.12** | Backend | Avoid 3.14+ on Windows if `pip install pandas` fails (no wheels). |
| **Node.js 20 LTS** | Frontend | For `npm install` / `npm run dev`. |
| **OpenAI API key** | AI insights + RAG | Optional for upload/summary/charts/forecast; required for full chat. |

---

## 1. One-time setup

### 1.1 Environment file

From **`PROJECT_ROOT`**, create a file named **`.env`** (it is gitignored). Use the same keys as in the repo **README → Configuration**, for example:

```env
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
STORAGE_DIR=backend_storage
ENVIRONMENT=development
WEB_PORT=9080
```

`WEB_PORT` is only used by **Docker Compose** for the nginx UI port mapping.

The backend loads `.env` from the **current working directory** when you start Uvicorn. Easiest: keep a copy at the repo root **and** copy `.env` into **`backend\`** if you always run `uvicorn` from `backend\`, or set variables in your shell instead.

### 1.2 Backend virtual environment

```powershell
cd PROJECT_ROOT\backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

If `py -3.12` is not installed, install Python 3.12 from [python.org](https://www.python.org/downloads/) and rerun.

### 1.3 Frontend dependencies

```powershell
cd PROJECT_ROOT\frontend
npm install
```

---

## 2. Run locally (two terminals)

Start the **API first**, then the **UI**.

### Terminal A — Backend (FastAPI)

```powershell
cd PROJECT_ROOT\backend
.\.venv\Scripts\Activate.ps1
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

If `.env` is only at repo root, either:

- Copy `.env` into `backend\`, **or**
- Run from root and set `PYTHONPATH`:

```powershell
cd PROJECT_ROOT
$env:PYTHONPATH = "backend"
cd backend
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

(Alternatively, define `OPENAI_API_KEY` in the shell: `$env:OPENAI_API_KEY = "sk-..."`.)

**Verify:**

- Open http://127.0.0.1:8000/health — expect `{"status":"ok"}`
- Open http://127.0.0.1:8000/docs — Swagger UI

### Terminal B — Frontend (Vite)

```powershell
cd PROJECT_ROOT\frontend
npm run dev
```

**Verify:**

- Open http://localhost:5173 (Vite prints the exact URL)
- Upload a CSV/XLSX on the **Upload** page; **Dashboard** and **Chat** need that dataset in the same browser session.

**How traffic flows in dev:**

- The browser calls `http://localhost:5173/api/...`
- Vite **proxies** `/api` to `http://127.0.0.1:8000` (see `frontend/vite.config.ts`)
- No need to set `VITE_API_URL` for local dev unless you change ports

---

## 3. Run with Docker

From `PROJECT_ROOT`, ensure **`.env`** exists (see §1.1), then:

```powershell
docker compose up --build
```

| URL | What |
|-----|------|
| http://localhost:9080 | Web UI (nginx serves the SPA and proxies `/api` to the API container). Set `WEB_PORT` in `.env` if 9080 is taken. |
| http://localhost:8000/docs | API Swagger (direct to API port) |

Uploads in Docker use the volume mapped for `STORAGE_DIR` (see `docker-compose.yml`).

---

## 4. Production build (frontend only)

```powershell
cd PROJECT_ROOT\frontend
npm run build
```

Output: `frontend/dist`. Serve with nginx or any static host. If the API is on another origin, build with:

```powershell
$env:VITE_API_URL = "https://api.yourcompany.com"
npm run build
```

If the UI and API share the same host and path prefix (e.g. nginx `/api` → backend), leave `VITE_API_URL` empty and use relative `/api` URLs.

---

## 5. Troubleshooting

| Problem | What to try |
|--------|-------------|
| `ModuleNotFoundError: fastapi` | Activate `backend\.venv`; run `pip install -r requirements.txt` from `backend`. |
| `pip install pandas` fails on Windows | Use Python **3.12** (64-bit), or use **Docker** for the API. |
| Frontend shows network errors on upload | Ensure backend is running on port **8000**; check Terminal A for tracebacks. |
| Chat returns “Set OPENAI_API_KEY…” | Set the key in `.env` in the folder from which you start Uvicorn, or export it in the shell. |
| CORS errors when not using Vite | Dev uses proxy; for custom setups, enable CORS on FastAPI or serve UI through the same origin. |
| Port 8000 or 5173 in use | Change port: `uvicorn main:app --port 8001` and update `frontend/vite.config.ts` `proxy.target` to match. |

---

## 6. Documentation index

| Doc | Topic |
|-----|--------|
| [README.md](../README.md) | Overview, layout, quick pointers |
| **RUNNING.md** (this file) | Step-by-step run instructions |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design |
| [DATA_FLOW.md](DATA_FLOW.md) | Request flows |
| [API.md](API.md) | REST reference |
| [MODULE_REFERENCE.md](MODULE_REFERENCE.md) | Backend file map |
| [SCALING.md](SCALING.md) | Growth / production |
