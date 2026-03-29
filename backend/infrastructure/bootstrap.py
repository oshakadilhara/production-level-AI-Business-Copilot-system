"""
Composition root: wire concrete adapters into the application.

Tests or alternate deployments should call `create_copilot_app(...)` with doubles.
"""

from __future__ import annotations

from typing import Optional

from application.copilot_application import CopilotApplication
from core.ports import ChartEngine, DatasetRepository, ForecastEngine, InsightEngine
from services.chart_service import chart_service
from services.data_service import data_service
from services.insight_service import insight_service
from services.ml_service import ml_service


def create_copilot_app(
    datasets: Optional[DatasetRepository] = None,
    insights: Optional[InsightEngine] = None,
    forecaster: Optional[ForecastEngine] = None,
    charts: Optional[ChartEngine] = None,
) -> CopilotApplication:
    return CopilotApplication(
        datasets=datasets or data_service,
        insights=insights or insight_service,
        forecaster=forecaster or ml_service,
        charts=charts or chart_service,
    )


copilot_app: CopilotApplication = create_copilot_app()
