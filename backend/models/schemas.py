from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class DatasetMetadata(BaseModel):
    filename: str
    columns: List[str]
    row_count: int


class DatasetUploadResponse(BaseModel):
    dataset_id: str
    metadata: DatasetMetadata


class DatasetSummaryResponse(BaseModel):
    dataset_id: str
    metadata: DatasetMetadata
    summary_statistics: Dict[str, Any]
    time_grain: Optional[str] = None


class InsightRequest(BaseModel):
    dataset_id: str
    question: str
    business_context: Optional[str] = None


class InsightResponse(BaseModel):
    answer: str
    supporting_facts: Dict[str, Any] = Field(default_factory=dict)


class PredictionRequest(BaseModel):
    dataset_id: str
    target_column: str
    date_column: Optional[str] = None
    horizon: int = 4


class PredictionPoint(BaseModel):
    timestamp: Any
    predicted_value: float


class PredictionResponse(BaseModel):
    dataset_id: str
    target_column: str
    predictions: List[PredictionPoint]


class ChartRequest(BaseModel):
    dataset_id: str
    x_column: str
    y_column: str
    chart_type: str = "line"  # line or bar


class ChartSpec(BaseModel):
    type: str
    data: Dict[str, Any]
    options: Dict[str, Any] = Field(default_factory=dict)


class ChartResponse(BaseModel):
    dataset_id: str
    spec: ChartSpec

