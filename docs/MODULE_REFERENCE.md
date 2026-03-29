# Backend module reference

One-line map of each Python module to its role (aligned with the current codebase).

| File | Purpose |
|------|---------|
| `backend/main.py` | Creates FastAPI app, wires CORS, mounts `/api` router, exposes `/health`. |
| `backend/api/routes.py` | HTTP endpoints: upload, summary, insights, forecast, charts; delegates to services. |
| `backend/models/schemas.py` | Pydantic models for all JSON bodies and responses. |
| `backend/utils/config.py` | Cached `Settings` (env / `.env`) and `ensure_storage_dir()`. |
| `backend/services/data_service.py` | Persists uploads, loads CSV/Excel into DataFrames, metadata, summary via `describe()`. |
| `backend/services/ml_service.py` | `LinearRegression` forecast using time index or row index; returns `PredictionPoint` list. |
| `backend/services/chart_service.py` | Builds Chart.js-shaped `ChartSpec` from two columns. |
| `backend/services/insight_service.py` | Builds RAG index if needed, aggregates stats + samples + retrieval, calls OpenAI `responses.create`. |
| `backend/rag/rag_engine.py` | Embeds row strings, stores FAISS `IndexFlatL2`, similarity search by question embedding. |

## Dependency direction

```
routes → services / rag
insight_service → data_service, rag_engine, OpenAI
chart_service, ml_service → data_service
rag_engine → OpenAI (embeddings), FAISS
data_service → filesystem, Pandas
```

## External libraries (see `requirements.txt`)

- **FastAPI / Uvicorn:** HTTP server and OpenAPI.
- **Pandas / openpyxl:** Tabular IO (CSV/Excel).
- **scikit-learn:** Regression model.
- **OpenAI SDK:** Embeddings and chat/response API.
- **faiss-cpu:** Vector index and search.
