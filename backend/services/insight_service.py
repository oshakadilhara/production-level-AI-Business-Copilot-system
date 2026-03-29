from __future__ import annotations

import logging
from typing import Any, Dict

from openai import OpenAI

from application.insight_prompts import insight_chat_messages
from core.constants import (
    INSIGHT_CHAT_TEMPERATURE,
    INSIGHT_PREVIEW_ROW_COUNT,
    RAG_TOP_K,
)
from models.schemas import InsightRequest, InsightResponse
from rag.rag_engine import rag_engine
from services.data_service import data_service
from utils.config import get_settings

logger = logging.getLogger(__name__)

_MISSING_KEY_MESSAGE = (
    "Set **OPENAI_API_KEY** on the server to enable AI-generated "
    "explanations and semantic retrieval. Summary statistics are still "
    "available below and on the Dashboard."
)


class InsightService:
    def __init__(self) -> None:
        settings = get_settings()
        self._client = (
            OpenAI(api_key=settings.openai_api_key)
            if settings.openai_api_key.strip()
            else None
        )
        self._model = settings.openai_model

    async def generate_insight(self, request: InsightRequest) -> InsightResponse:
        df = data_service.get_dataframe(request.dataset_id)
        basic_stats: Dict[str, Any] = df.describe(include="all").to_dict()
        top_rows = df.head(INSIGHT_PREVIEW_ROW_COUNT).to_dict(orient="records")

        if not self._client:
            return InsightResponse(
                answer=_MISSING_KEY_MESSAGE,
                supporting_facts={
                    "summary_statistics": basic_stats,
                    "sample_records": top_rows,
                },
            )

        rag_engine.ensure_index(request.dataset_id, df)
        rag_context = rag_engine.query(
            request.dataset_id, request.question, k=RAG_TOP_K
        )

        messages = insight_chat_messages(
            question=request.question,
            business_context=request.business_context,
            summary_statistics=basic_stats,
            sample_records=top_rows,
            rag_row_texts=rag_context,
        )

        chat = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=INSIGHT_CHAT_TEMPERATURE,
        )
        answer = (chat.choices[0].message.content or "").strip()
        logger.info(
            "Insight completed dataset_id=%s question_len=%s",
            request.dataset_id,
            len(request.question),
        )

        return InsightResponse(
            answer=answer,
            supporting_facts={
                "summary_statistics": basic_stats,
                "sample_records": top_rows,
            },
        )


insight_service = InsightService()
