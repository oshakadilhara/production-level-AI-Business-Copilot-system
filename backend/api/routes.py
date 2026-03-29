from typing import Set

from fastapi import APIRouter, UploadFile, File, HTTPException

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

ALLOWED_CONTENT_TYPES: Set[str] = {
    "text/csv",
    "text/plain",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/octet-stream",
}


def _upload_allowed(file: UploadFile) -> bool:
    ct = (file.content_type or "").split(";")[0].strip().lower()
    if ct in ALLOWED_CONTENT_TYPES:
        return True
    name = (file.filename or "").lower()
    return name.endswith((".csv", ".xlsx", ".xls"))


@router.post("/files/upload", response_model=DatasetUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    if not _upload_allowed(file):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Use CSV or Excel (.csv, .xlsx, .xls).",
        )
    dataset_id, metadata = await data_service.save_and_load(file)
    return DatasetUploadResponse(dataset_id=dataset_id, metadata=metadata)


@router.get("/datasets/{dataset_id}/summary", response_model=DatasetSummaryResponse)
async def get_dataset_summary(dataset_id: str):
    try:
        summary = data_service.get_summary(dataset_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return summary


@router.post("/insights/query", response_model=InsightResponse)
async def query_insights(request: InsightRequest):
    try:
        response = await insight_service.generate_insight(request)
    except KeyError:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return response


@router.post("/predictions/forecast", response_model=PredictionResponse)
async def forecast(request: PredictionRequest):
    try:
        response = ml_service.forecast(request)
    except KeyError:
        raise HTTPException(status_code=404, detail="Dataset not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return response


@router.post("/charts/generate", response_model=ChartResponse)
async def generate_chart(request: ChartRequest):
    try:
        response = chart_service.generate_chart(request)
    except KeyError:
        raise HTTPException(status_code=404, detail="Dataset not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return response
