from __future__ import annotations

from typing import Tuple

from fastapi import UploadFile

from core.ports import ChartEngine, DatasetRepository, ForecastEngine, InsightEngine
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


class CopilotApplication:
    """
    Application service: single entry for copilot use cases.
    Implements hexagonal / clean architecture — depends on ports, not concrete adapters.
    """

    def __init__(
        self,
        datasets: DatasetRepository,
        insights: InsightEngine,
        forecaster: ForecastEngine,
        charts: ChartEngine,
    ) -> None:
        self._datasets = datasets
        self._insights = insights
        self._forecaster = forecaster
        self._charts = charts

    async def ingest_dataset(self, file: UploadFile) -> Tuple[str, DatasetMetadata]:
        return await self._datasets.save_and_load(file)

    def summarize_dataset(self, dataset_id: str) -> DatasetSummaryResponse:
        return self._datasets.get_summary(dataset_id)

    async def answer_business_question(self, request: InsightRequest) -> InsightResponse:
        return await self._insights.generate_insight(request)

    def predict_sales(self, request: PredictionRequest) -> PredictionResponse:
        return self._forecaster.forecast(request)

    def build_chart(self, request: ChartRequest) -> ChartResponse:
        return self._charts.generate_chart(request)
