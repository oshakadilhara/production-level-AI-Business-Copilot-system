from __future__ import annotations

import logging
from typing import List

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

from core.constants import FEATURE_COLUMN_NAME, ML_TRAIN_TEST_SPLIT
from core.exceptions import CopilotValidationError
from models.schemas import PredictionPoint, PredictionRequest, PredictionResponse
from services.data_service import data_service

logger = logging.getLogger(__name__)


class MLService:
    def forecast(self, request: PredictionRequest) -> PredictionResponse:
        df = data_service.get_dataframe(request.dataset_id)
        if request.target_column not in df.columns:
            raise CopilotValidationError("Target column not found in dataset")

        work_df = df.copy()
        date_col = request.date_column
        use_dates = bool(date_col and date_col in work_df.columns)

        if use_dates:
            work_df[date_col] = pd.to_datetime(work_df[date_col], errors="coerce")
            work_df = work_df.dropna(subset=[date_col]).sort_values(date_col)
            work_df[FEATURE_COLUMN_NAME] = range(len(work_df))
            X = work_df[[FEATURE_COLUMN_NAME]]
        else:
            work_df[FEATURE_COLUMN_NAME] = range(len(work_df))
            X = work_df[[FEATURE_COLUMN_NAME]]

        y = pd.to_numeric(work_df[request.target_column], errors="coerce")
        mask = y.notna()
        work_df = work_df.loc[mask].reset_index(drop=True)
        X = work_df[[FEATURE_COLUMN_NAME]]
        y = y.loc[mask].astype(float)

        if len(work_df) < 2:
            raise CopilotValidationError(
                "Not enough valid rows to train a forecast model"
            )

        X_train, _, y_train, _ = train_test_split(
            X, y, test_size=ML_TRAIN_TEST_SPLIT, shuffle=False
        )

        model = LinearRegression()
        model.fit(X_train, y_train)

        last_index = int(X.iloc[-1, 0])
        future_indices = list(
            range(last_index + 1, last_index + 1 + request.horizon)
        )
        future_X = pd.DataFrame({FEATURE_COLUMN_NAME: future_indices})
        y_pred = model.predict(future_X)

        predictions: List[PredictionPoint] = []
        for i, value in enumerate(y_pred):
            if use_dates:
                last_ts = work_df[date_col].iloc[-1]
                ts = last_ts + pd.offsets.MonthEnd(i + 1)
                timestamp = str(ts)
            else:
                timestamp = str(len(work_df) + i)
            predictions.append(
                PredictionPoint(timestamp=timestamp, predicted_value=float(value))
            )

        logger.info(
            "Forecast dataset_id=%s target=%s horizon=%s",
            request.dataset_id,
            request.target_column,
            request.horizon,
        )
        return PredictionResponse(
            dataset_id=request.dataset_id,
            target_column=request.target_column,
            predictions=predictions,
        )


ml_service = MLService()
