import logging

import pandas as pd

from core.constants import CHART_LINE_BORDER, CHART_LINE_FILL
from core.exceptions import CopilotValidationError
from models.schemas import ChartRequest, ChartResponse, ChartSpec
from services.data_service import data_service

logger = logging.getLogger(__name__)


class ChartService:
    def generate_chart(self, request: ChartRequest) -> ChartResponse:
        df = data_service.get_dataframe(request.dataset_id)
        if request.x_column not in df.columns or request.y_column not in df.columns:
            raise CopilotValidationError("Requested columns not in dataset")

        x = df[request.x_column].astype(str).tolist()
        y = pd.to_numeric(df[request.y_column], errors="coerce").fillna(0.0)
        y_list = y.astype(float).tolist()

        spec = ChartSpec(
            type=request.chart_type,
            data={
                "labels": x,
                "datasets": [
                    {
                        "label": request.y_column,
                        "data": y_list,
                        "borderColor": CHART_LINE_BORDER,
                        "backgroundColor": CHART_LINE_FILL,
                    }
                ],
            },
            options={
                "responsive": True,
                "maintainAspectRatio": False,
                "plugins": {
                    "legend": {"position": "top"},
                    "title": {
                        "display": True,
                        "text": (
                            f"{request.chart_type.title()} chart of "
                            f"{request.y_column} by {request.x_column}"
                        ),
                    },
                },
            },
        )

        logger.debug(
            "Chart built chart_type=%s dataset_id=%s",
            request.chart_type,
            request.dataset_id,
        )
        return ChartResponse(dataset_id=request.dataset_id, spec=spec)


chart_service = ChartService()
