import pandas as pd

from models.schemas import ChartRequest, ChartResponse, ChartSpec
from services.data_service import data_service


class ChartService:
    def generate_chart(self, request: ChartRequest) -> ChartResponse:
        df = data_service.get_dataframe(request.dataset_id)
        if request.x_column not in df.columns or request.y_column not in df.columns:
            raise ValueError("Requested columns not in dataset")

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
                        "borderColor": "rgba(75, 192, 192, 1)",
                        "backgroundColor": "rgba(75, 192, 192, 0.2)",
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
                        "text": f"{request.chart_type.title()} chart of {request.y_column} by {request.x_column}",
                    },
                },
            },
        )

        return ChartResponse(dataset_id=request.dataset_id, spec=spec)


chart_service = ChartService()
