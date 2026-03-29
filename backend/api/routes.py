from fastapi import APIRouter, File, HTTPException, UploadFile

from api.upload_policy import UPLOAD_REJECT_DETAIL, is_allowed_tabular_upload
from infrastructure.bootstrap import copilot_app
from models.schemas import (
    ChartRequest,
    ChartResponse,
    DatasetSummaryResponse,
    DatasetUploadResponse,
    InsightRequest,
    InsightResponse,
    PredictionRequest,
    PredictionResponse,
)

router = APIRouter()


@router.post("/files/upload", response_model=DatasetUploadResponse)
async def upload_file(file: UploadFile = File(...)) -> DatasetUploadResponse:
    if not is_allowed_tabular_upload(file):
        raise HTTPException(status_code=400, detail=UPLOAD_REJECT_DETAIL)
    dataset_id, metadata = await copilot_app.ingest_dataset(file)
    return DatasetUploadResponse(dataset_id=dataset_id, metadata=metadata)


@router.get("/datasets/{dataset_id}/summary", response_model=DatasetSummaryResponse)
async def get_dataset_summary(dataset_id: str) -> DatasetSummaryResponse:
    return copilot_app.summarize_dataset(dataset_id)


@router.post("/insights/query", response_model=InsightResponse)
async def query_insights(request: InsightRequest) -> InsightResponse:
    return await copilot_app.answer_business_question(request)


@router.post("/predictions/forecast", response_model=PredictionResponse)
async def forecast(request: PredictionRequest) -> PredictionResponse:
    return copilot_app.predict_sales(request)


@router.post("/charts/generate", response_model=ChartResponse)
async def generate_chart(request: ChartRequest) -> ChartResponse:
    return copilot_app.build_chart(request)
