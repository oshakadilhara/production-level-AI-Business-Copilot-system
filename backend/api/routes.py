from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List, Optional

from models.schemas import (
    DatasetUploadResponse,
    InsightRequest,
    InsightResponse,
    PredictionRequest,
    PredictionResponse,
    ChartRequest,
    ChartResponse,
    DatasetSummaryResponse,
)
from services.data_service import data_service
from services.insight_service import insight_service
from services.ml_service import ml_service
from services.chart_service import chart_service


router = APIRouter()


@router.post("/files/upload", response_model=DatasetUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    if file.content_type not in [
        "text/csv",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ]:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    dataset_id, metadata = await data_service.save_and_load(file)
    return DatasetUploadResponse(dataset_id=dataset_id, metadata=metadata)


@router.get("/datasets/{dataset_id}/summary", response_model=DatasetSummaryResponse)
async def get_dataset_summary(dataset_id: str):
    summary = data_service.get_summary(dataset_id)
    return summary


@router.post("/insights/query", response_model=InsightResponse)
async def query_insights(request: InsightRequest):
    response = await insight_service.generate_insight(request)
    return response


@router.post("/predictions/forecast", response_model=PredictionResponse)
async def forecast(request: PredictionRequest):
    response = ml_service.forecast(request)
    return response


@router.post("/charts/generate", response_model=ChartResponse)
async def generate_chart(request: ChartRequest):
    response = chart_service.generate_chart(request)
    return response

