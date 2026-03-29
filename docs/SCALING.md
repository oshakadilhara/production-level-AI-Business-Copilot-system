# Scaling strategy

The current implementation is a **single-process** FastAPI app with **in-memory** DataFrames and FAISS indexes. That is appropriate for a single-node POC or internal tool. Below is how you evolve it toward a **multi-tenant SaaS** without rewriting the product idea.

## 1. Stateless API tier

**Today:** Upload saves to local disk, but analytical state (`_dataframes`, `_indexes`) lives in RAM on one worker.

**Scale out:**

- Move file blobs to **object storage** (S3, GCS, Azure Blob) with a `dataset_id` prefix.
- Store **metadata** in PostgreSQL: `tenant_id`, `filename`, `storage_uri`, `row_count`, `schema_json`, `created_at`.
- On demand (or via a queue), **hydrate** a DataFrame from object storage into a **short-lived** cache (Redis, or worker memory with TTL).

This lets you run **multiple Uvicorn/Gunicorn workers** or Kubernetes replicas; each request either pulls from shared cache or reconstructs the DataFrame.

## 2. Heavy work off the request path

**Today:** RAG index build embeds **every row** synchronously on first insight request — acceptable for small files, risky for large tables.

**Scale:**

- **Enqueue** jobs (`Celery`, `RQ`, Cloud Tasks, SQS) after upload:
  - Profile schema, compute summaries, chunk rows, build embeddings, write vectors to a **vector database** (Pinecone, pgvector, OpenSearch k-NN).
- Expose **job status** via `GET /api/datasets/{id}/status` so the UI polls instead of blocking.

## 3. Vector search at scale

**Today:** FAISS `IndexFlatL2` in memory — simple and fast for modest row counts.

**Scale:**

- For **very large** tables, avoid one embedding per raw row; instead embed **aggregates** (e.g., monthly revenue rollups) plus a **sample** of detail rows.
- Use **sharded** indexes or a managed vector DB with **filters** (`tenant_id`, `dataset_id`).
- Refresh strategy: on re-upload, version the dataset (`dataset_version`) and query only the active version.

## 4. LLM cost and latency

- **Cache** insight answers keyed by `(dataset_id, question_normalized, stats_hash)` with TTL.
- **Truncate** prompts: send top correlations / top segments rather than full `describe()` for wide tables.
- Use **streaming** responses to the UI for perceived performance.
- Apply **rate limits** per tenant at the API gateway.

## 5. Multi-tenancy and security

- Namespace every resource with **`tenant_id`** (and enforce in middleware).
- Encrypt blobs at rest; use **pre-signed URLs** for uploads from the browser.
- Add **RBAC** (admin, analyst, viewer) at the route and row level if you join to customer identity stores.

## 6. Observability

- Structured logging with `request_id`, `dataset_id`, `tenant_id` (never log secrets or full PII tables).
- Metrics: upload latency, rows/sec ingested, embedding tokens, LLM latency, FAISS/query errors.
- Traces (OpenTelemetry) from API → worker → vector DB → OpenAI.

## 7. Frontend delivery

- Serve the React app from a CDN or static bucket; talk to API on a dedicated subdomain (`api.example.com`).
- Use **environment-specific** CORS and connect **WebSockets** later for streaming chat if needed.

---

**Summary:** Keep FastAPI as the orchestration layer; move storage and vector state to shared services; offload ingestion and index builds to workers; cache LLM outputs. That preserves the same conceptual architecture while supporting many concurrent tenants and larger datasets.
