from typing import Dict, Any

import pandas as pd
from openai import OpenAI

from models.schemas import InsightRequest, InsightResponse
from services.data_service import data_service
from rag.rag_engine import rag_engine
from utils.config import get_settings


class InsightService:
    def __init__(self) -> None:
        settings = get_settings()
        self._client = OpenAI(api_key=settings.openai_api_key)
        self._model = settings.openai_model

    async def generate_insight(self, request: InsightRequest) -> InsightResponse:
        df = data_service.get_dataframe(request.dataset_id)
        if request.dataset_id not in rag_engine._indexes:
            rag_engine.build_index(request.dataset_id, df)

        basic_stats: Dict[str, Any] = df.describe(include="all").to_dict()
        top_rows = df.head(5).to_dict(orient="records")
        rag_context = rag_engine.query(request.dataset_id, request.question, k=8)

        system_prompt = (
            "You are a senior financial analyst and virtual CFO. "
            "Given tabular business data, you perform precise numeric analysis "
            "using the provided statistics and context, then answer in clear business language."
        )
        user_prompt = (
            f"Business question: {request.question}\n\n"
            f"Optional business context: {request.business_context or 'N/A'}\n\n"
            f"Summary statistics (per column): {basic_stats}\n\n"
            f"Sample records: {top_rows}\n\n"
            f"Relevant rows (RAG context): {rag_context}\n\n"
            "1) Explain any notable trends, anomalies, and revenue or sales drivers.\n"
            "2) If the question is about drops/spikes, hypothesize plausible reasons grounded in the data.\n"
            "3) Suggest 2-3 concrete business actions.\n"
            "Keep the answer under 6 paragraphs."
        )

        completion = self._client.responses.create(
            model=self._model,
            reasoning={"effort": "medium"},
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        answer = completion.output_text

        return InsightResponse(
            answer=answer,
            supporting_facts={
                "summary_statistics": basic_stats,
                "sample_records": top_rows,
            },
        )


insight_service = InsightService()

