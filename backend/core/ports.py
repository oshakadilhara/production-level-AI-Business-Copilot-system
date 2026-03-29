"""
Ports (interfaces). Application depends on these Protocols; infrastructure implements them.

Dependency rule: `application` → `core` only. `services` / `rag` → `core` + `models`.
`api` → `application` + FastAPI types.
"""

from __future__ import annotations

from typing import Protocol, Tuple, runtime_checkable

from fastapi import UploadFile

from models.schemas import (
    ChartRequest,
    ChartResponse,
    DatasetMetadata,
    DatasetSummaryResponse,
    InsightRequest,
    InsightResponse,
    PredictionRequest,
    PredictionResponse,
)


@runtime_checkable
class DatasetRepository(Protocol):
    """Load and summarize uploaded tabular datasets."""

    async def save_and_load(self, file: UploadFile) -> Tuple[str, DatasetMetadata]:
        ...

    def get_summary(self, dataset_id: str) -> DatasetSummaryResponse:
        ...


@runtime_checkable
class InsightEngine(Protocol):
    """Hybrid stats + RAG + LLM narrative."""

    async def generate_insight(self, request: InsightRequest) -> InsightResponse:
        ...


@runtime_checkable
class ForecastEngine(Protocol):
    """Baseline forecasting over a dataset."""

    def forecast(self, request: PredictionRequest) -> PredictionResponse:
        ...


@runtime_checkable
class ChartEngine(Protocol):
    """Chart specification builder for the frontend."""

    def generate_chart(self, request: ChartRequest) -> ChartResponse:
        ...
