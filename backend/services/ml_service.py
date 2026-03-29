from typing import List

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

from models.schemas import PredictionRequest, PredictionResponse, PredictionPoint
from services.data_service import data_service


class MLService:
    def forecast(self, request: PredictionRequest) -> PredictionResponse:
        df = data_service.get_dataframe(request.dataset_id)
        if request.target_column not in df.columns:
            raise ValueError("Target column not found in dataset")

        work_df = df.copy()
        if request.date_column and request.date_column in work_df.columns:
            work_df[request.date_column] = pd.to_datetime(work_df[request.date_column])
            work_df = work_df.sort_values(request.date_column)
            work_df["time_index"] = range(len(work_df))
            X = work_df[["time_index"]]
        else:
            work_df["row_index"] = range(len(work_df))
            X = work_df[["row_index"]]

        y = work_df[request.target_column].astype(float)

        X_train, _, y_train, _ = train_test_split(
            X, y, test_size=0.1, shuffle=False
        )

        model = LinearRegression()
        model.fit(X_train, y_train)

        last_index = X.iloc[-1, 0]
        future_indices = list(range(last_index + 1, last_index + 1 + request.horizon))
        future_X = pd.DataFrame({"time_index": future_indices})
        y_pred = model.predict(future_X)

        predictions: List[PredictionPoint] = []
        for i, value in enumerate(y_pred):
            timestamp = (
                work_df[request.date_column].iloc[-1] + pd.offsets.PeriodIndex(
                    [i + 1], freq="M"
                ).to_timestamp()[0]
                if request.date_column and request.date_column in work_df.columns
                else len(work_df) + i
            )
            predictions.append(
                PredictionPoint(timestamp=str(timestamp), predicted_value=float(value))
            )

        return PredictionResponse(
            dataset_id=request.dataset_id,
            target_column=request.target_column,
            predictions=predictions,
        )


ml_service = MLService()

