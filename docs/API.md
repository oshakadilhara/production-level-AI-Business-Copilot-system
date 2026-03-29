# API reference

Base URL (local): `http://localhost:8000`  
All business routes are under **`/api`**. OpenAPI JSON: `/openapi.json`.

## Authentication

No auth is implemented in the current codebase. For production, add API keys, OAuth2, or mutual TLS at the gateway or FastAPI dependency layer.

## Error shape

JSON errors follow FastAPI conventions:

- **404:** `{ "detail": "Dataset not found" }` — unknown `dataset_id` (in-memory session).
- **400:** `{ "detail": "<message>" }` — validation / business rule (`CopilotValidationError`), e.g. missing column, insufficient rows for forecast.

---

## `GET /health`

**Response:** `{ "status": "ok" }`

---

## `POST /api/files/upload`

Upload a CSV or Excel file.

**Content-Type:** `multipart/form-data`  
**Field:** `file` (binary)

**Accepted uploads:** CSV or Excel. The API allows common browser `Content-Type` values (`text/csv`, Excel MIME types, `application/octet-stream`, `text/plain`) **or** a filename ending in `.csv`, `.xlsx`, or `.xls`.

**Response:** `DatasetUploadResponse`

```json
{
  "dataset_id": "uuid",
  "metadata": {
    "filename": "sales.csv",
    "columns": ["date", "revenue", "product"],
    "row_count": 1200
  }
}
```

**Errors:** `400` if MIME type is not in the allowed list.

---

## `GET /api/datasets/{dataset_id}/summary`

Returns Pandas `describe(include="all")` as JSON-friendly dict plus metadata.

**Response:** `DatasetSummaryResponse`

```json
{
  "dataset_id": "uuid",
  "metadata": { "filename": "...", "columns": [], "row_count": 0 },
  "summary_statistics": { },
  "time_grain": null
}
```

`time_grain` is `"auto"` if the DataFrame has at least one `datetime64[ns]` column; otherwise `null`.

**Errors:** Propagates as `500` if `dataset_id` is unknown (`KeyError` from `DataService`).

---

## `POST /api/insights/query`

Natural-language business question over a loaded dataset.

**Request body:** `InsightRequest`

```json
{
  "dataset_id": "uuid",
  "question": "Why did revenue drop last month?",
  "business_context": "B2B SaaS, fiscal month end"
}
```

**Response:** `InsightResponse`

```json
{
  "answer": "… narrative …",
  "supporting_facts": {
    "summary_statistics": { },
    "sample_records": [ ]
  }
}
```

**Behavior:**

- Builds or reuses a **FAISS** index per `dataset_id` (OpenAI embeddings).
- Sends **summary statistics**, sample rows, and top retrieved rows to the LLM.

**Requirements:** Valid `OPENAI_API_KEY`. Failures without it follow the OpenAI client exception behavior (may surface as 500 unless wrapped).

---

## `POST /api/predictions/forecast`

Baseline linear regression forecast.

**Request body:** `PredictionRequest`

```json
{
  "dataset_id": "uuid",
  "target_column": "revenue",
  "date_column": "month",
  "horizon": 4
}
```

- `date_column`: optional; if present and valid, rows are sorted by this column after `pd.to_datetime`.
- `horizon`: number of future steps (default `4`).

**Response:** `PredictionResponse`

```json
{
  "dataset_id": "uuid",
  "target_column": "revenue",
  "predictions": [
    { "timestamp": "2025-05-01 00:00:00", "predicted_value": 12345.67 }
  ]
}
```

**Errors:** `ValueError` from service if `target_column` is missing (may surface as 500 unless error handlers map it).

---

## `POST /api/charts/generate`

Returns a Chart.js-oriented spec for line or bar charts.

**Request body:** `ChartRequest`

```json
{
  "dataset_id": "uuid",
  "x_column": "month",
  "y_column": "revenue",
  "chart_type": "line"
}
```

**Response:** `ChartResponse`

```json
{
  "dataset_id": "uuid",
  "spec": {
    "type": "line",
    "data": {
      "labels": ["2024-01", "2024-02"],
      "datasets": [
        {
          "label": "revenue",
          "data": [100.0, 120.0],
          "borderColor": "rgba(75, 192, 192, 1)",
          "backgroundColor": "rgba(75, 192, 192, 0.2)"
        }
      ]
    },
    "options": { }
  }
}
```

**Errors:** `ValueError` if columns are not in the dataset.

---

## Type definitions (Pydantic)

Defined in `backend/models/schemas.py`:

- `DatasetMetadata`, `DatasetUploadResponse`, `DatasetSummaryResponse`
- `InsightRequest`, `InsightResponse`
- `PredictionRequest`, `PredictionPoint`, `PredictionResponse`
- `ChartRequest`, `ChartSpec`, `ChartResponse`
