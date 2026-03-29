import os
import uuid
from typing import Dict, Any, Tuple

import pandas as pd
from fastapi import UploadFile

from core.exceptions import DatasetNotFound
from models.schemas import DatasetMetadata, DatasetSummaryResponse
from utils.config import ensure_storage_dir


class DataService:
    def __init__(self) -> None:
        self._dataframes: Dict[str, pd.DataFrame] = {}
        self._metadata: Dict[str, DatasetMetadata] = {}

    async def save_and_load(self, file: UploadFile) -> Tuple[str, DatasetMetadata]:
        storage_dir = ensure_storage_dir()
        dataset_id = str(uuid.uuid4())
        file_ext = os.path.splitext(file.filename)[1].lower()
        saved_path = os.path.join(storage_dir, f"{dataset_id}{file_ext}")

        with open(saved_path, "wb") as out_file:
            content = await file.read()
            out_file.write(content)

        if file_ext in [".csv", ".txt"]:
            df = pd.read_csv(saved_path)
        else:
            df = pd.read_excel(saved_path)

        self._dataframes[dataset_id] = df
        metadata = DatasetMetadata(
            filename=file.filename,
            columns=list(df.columns),
            row_count=len(df),
        )
        self._metadata[dataset_id] = metadata
        return dataset_id, metadata

    def get_dataframe(self, dataset_id: str) -> pd.DataFrame:
        if dataset_id not in self._dataframes:
            raise DatasetNotFound(dataset_id)
        return self._dataframes[dataset_id]

    def get_summary(self, dataset_id: str) -> DatasetSummaryResponse:
        df = self.get_dataframe(dataset_id)
        metadata = self._metadata[dataset_id]
        summary_stats: Dict[str, Any] = df.describe(include="all").to_dict()
        # naive heuristic: infer time column
        time_grain = None
        datetime_cols = df.select_dtypes(include=["datetime64[ns]"]).columns
        if len(datetime_cols) > 0:
            time_grain = "auto"
        return DatasetSummaryResponse(
            dataset_id=dataset_id,
            metadata=metadata,
            summary_statistics=summary_stats,
            time_grain=time_grain,
        )


data_service = DataService()

