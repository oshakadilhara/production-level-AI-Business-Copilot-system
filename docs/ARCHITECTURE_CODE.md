# Backend architecture (code layers)

The FastAPI app follows a **pragmatic hexagonal / clean architecture**: dependencies point **inward**, and cross-cutting **ports** isolate the application from frameworks and vendors.

## Layers (inside `backend/`)

| Layer | Package / location | Responsibility |
|--------|--------------------|----------------|
| **Presentation** | `api/` | Routers, upload policy, **central exception handlers** (`register_exception_handlers`). No business rules. |
| **Application** | `application/` | Use cases (`CopilotApplication`) and **pure prompt builders** (`insight_prompts.py`). No FastAPI / vendor SDKs. |
| **Domain / contracts** | `core/` | **Ports** (`Protocol`s), **exceptions**, **constants** (tunables). No I/O. |
| **Infrastructure** | `infrastructure/`, `services/`, `rag/`, `utils/` | Concrete adapters: Pandas files, FAISS, OpenAI, sklearn, settings. |
| **DTOs** | `models/schemas.py` | Pydantic API contracts (shared across layers). |

## Dependency rule

```
api  →  application  →  core
         ↑
infrastructure (services, rag, utils) implements core.ports
infrastructure.bootstrap wires concrete instances into CopilotApplication
```

- **`application`** must not import `fastapi`, `openai`, `faiss`, or `pandas` directly—only through port types implemented elsewhere.
- **`api`** should call **`CopilotApplication`** (via `infrastructure.bootstrap.copilot_app`), not individual services, so HTTP stays thin.

## Composition root

`infrastructure/bootstrap.py` is the **composition root**: the only place that constructs `CopilotApplication` with production adapters.

- **Tests:** build `CopilotApplication` with fakes or in-memory repositories that implement the same ports.
- **Future (e.g. S3):** replace `data_service` with `S3DatasetRepository` without changing routes or use cases.

## Exceptions → HTTP

Registered once in `main.create_app()` via `api/exception_handlers.py`:

| Exception | HTTP |
|-----------|------|
| `core.exceptions.DatasetNotFound` | 404 `{ "detail": "Dataset not found" }` |
| `core.exceptions.CopilotValidationError` | 400 `{ "detail": "<message>" }` |

Routers stay free of `try/except` for these paths.

## File map (architecture-related)

| Path | Role |
|------|------|
| `core/ports.py` | `DatasetRepository`, `InsightEngine`, `ForecastEngine`, `ChartEngine` protocols |
| `core/exceptions.py` | `DatasetNotFound`, `CopilotValidationError` |
| `core/constants.py` | Shared numeric/string tunables (RAG k, chart colors, ML split, feature column name) |
| `application/copilot_application.py` | `ingest_dataset`, `summarize_dataset`, `answer_business_question`, `predict_sales`, `build_chart` |
| `application/insight_prompts.py` | Pure functions → LLM message list |
| `infrastructure/bootstrap.py` | `create_copilot_app()`, default `copilot_app` singleton |
| `api/routes.py` | Thin handlers → `copilot_app` |
| `api/upload_policy.py` | Tabular upload MIME/extension rules |
| `api/exception_handlers.py` | `register_exception_handlers(app)` |
| `main.py` | Logging bootstrap + app factory |

See also [ARCHITECTURE.md](ARCHITECTURE.md) for system context and [MODULE_REFERENCE.md](MODULE_REFERENCE.md) for all modules.
