"""
Pure prompt construction for the insight use case — no I/O, no frameworks.

Keeps `InsightService` focused on orchestration and makes prompts testable/versionable.
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, MutableSequence, TypedDict


class ChatMessage(TypedDict):
    role: str
    content: str


def system_prompt_financial_copilot() -> str:
    return (
        "You are a senior financial analyst and virtual CFO. "
        "Given tabular business data, you perform precise numeric analysis "
        "using the provided statistics and context, then answer in clear business language."
    )


def user_prompt_for_insight(
    question: str,
    business_context: str | None,
    summary_statistics: Mapping[str, Any],
    sample_records: List[Mapping[str, Any]],
    rag_row_texts: List[str],
) -> str:
    ctx = business_context or "N/A"
    return (
        f"Business question: {question}\n\n"
        f"Optional business context: {ctx}\n\n"
        f"Summary statistics (per column): {dict(summary_statistics)}\n\n"
        f"Sample records: {sample_records}\n\n"
        f"Relevant rows (RAG context): {rag_row_texts}\n\n"
        "1) Explain any notable trends, anomalies, and revenue or sales drivers.\n"
        "2) If the question is about drops/spikes, hypothesize plausible reasons grounded in the data.\n"
        "3) Suggest 2-3 concrete business actions.\n"
        "Keep the answer under 6 paragraphs."
    )


def insight_chat_messages(
    question: str,
    business_context: str | None,
    summary_statistics: Dict[str, Any],
    sample_records: List[Dict[str, Any]],
    rag_row_texts: List[str],
) -> MutableSequence[ChatMessage]:
    return [
        {"role": "system", "content": system_prompt_financial_copilot()},
        {
            "role": "user",
            "content": user_prompt_for_insight(
                question=question,
                business_context=business_context,
                summary_statistics=summary_statistics,
                sample_records=sample_records,
                rag_row_texts=rag_row_texts,
            ),
        },
    ]
