# Backend module reference

## Architecture layers

| Path | Purpose |
|------|---------|
| `backend/core/ports.py` | Protocols: `DatasetRepository`, `InsightEngine`, `ForecastEngine`, `ChartEngine` |
| `backend/core/exceptions.py` | `DatasetNotFound` (404), `CopilotValidationError` (400) |
| `backend/application/copilot_application.py` | Use cases: ingest, summarize, Q&A, forecast, chart |
| `backend/infrastructure/bootstrap.py` | Composition root: wires services into `copilot_app` |
| `backend/api/routes.py` | HTTP layer; delegates to `copilot_app` |
| `backend/api/upload_policy.py` | Allowed CSV/Excel MIME types and extensions |
| `backend/api/exception_handlers.py` | Registers global handlers for `DatasetNotFound`, `CopilotValidationError` |
| `backend/main.py` | Logging, `create_app()`, CORS, routers, health |
| `backend/core/constants.py` | RAG k, insight preview rows, chart palette, ML split |
| `backend/application/insight_prompts.py` | Pure LLM prompt construction for insights |

## Adapters & shared modules

| File | Purpose |
|------|---------|
| `backend/models/schemas.py` | Pydantic request/response models |
| `backend/utils/config.py` | Cached `Settings` (env / `.env`) and `ensure_storage_dir()` |
| `backend/services/data_service.py` | Persist uploads, load CSV/Excel, metadata, `describe()` summary |
| `backend/services/ml_service.py` | `LinearRegression` forecast (time or row index) |
| `backend/services/chart_service.py` | Chart.js-shaped `ChartSpec` from two columns |
| `backend/services/insight_service.py` | Stats + FAISS retrieval + OpenAI `chat.completions` |
| `backend/rag/rag_engine.py` | Row embeddings, FAISS `IndexFlatL2`, similarity search |

## Dependency direction (target)

```
api → application → core (ports)
services / rag → core, models, utils
infrastructure.bootstrap → application + services
```

## External libraries (`requirements.txt`)

- **FastAPI / Uvicorn** — HTTP and OpenAPI  
- **Pandas / openpyxl** — Tabular I/O  
- **scikit-learn** — Regression  
- **OpenAI SDK** — Embeddings and chat  
- **faiss-cpu** — Vector index  

See **[ARCHITECTURE_CODE.md](ARCHITECTURE_CODE.md)** for the full layering contract.
