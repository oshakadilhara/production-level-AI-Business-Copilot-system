from __future__ import annotations

import logging
from typing import Dict, List

import faiss
import numpy as np
import pandas as pd
from openai import OpenAI

from utils.config import get_settings

logger = logging.getLogger(__name__)


class RAGEngine:
    """
    Tabular RAG: each row is linearized to text, embedded, indexed with FAISS.
    Encapsulation: callers use ensure_index + query only (no raw index access).
    """

    def __init__(self) -> None:
        self._indexes: Dict[str, faiss.IndexFlatL2] = {}
        self._rows_text: Dict[str, List[str]] = {}
        settings = get_settings()
        self._client = (
            OpenAI(api_key=settings.openai_api_key)
            if settings.openai_api_key.strip()
            else None
        )
        self._embed_model = settings.openai_embedding_model

    def _embed(self, texts: List[str]) -> np.ndarray:
        if not self._client:
            raise RuntimeError("OpenAI client not configured for embeddings")
        resp = self._client.embeddings.create(
            model=self._embed_model,
            input=texts,
        )
        vectors = [d.embedding for d in resp.data]
        return np.array(vectors).astype("float32")

    def ensure_index(self, dataset_id: str, df: pd.DataFrame) -> None:
        """Idempotent: builds FAISS index once per dataset when an API key is configured."""
        if not self._client or dataset_id in self._indexes:
            return
        rows_as_text = [
            ", ".join(f"{col}={row[col]}" for col in df.columns)
            for _, row in df.iterrows()
        ]
        if not rows_as_text:
            return
        embeddings = self._embed(rows_as_text)
        dim = embeddings.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(embeddings)
        self._indexes[dataset_id] = index
        self._rows_text[dataset_id] = rows_as_text
        logger.info("RAG index materialized dataset_id=%s rows=%s", dataset_id, len(rows_as_text))

    def query(self, dataset_id: str, query: str, k: int = 10) -> List[str]:
        if not self._client or dataset_id not in self._indexes:
            return []
        q_emb = self._embed([query])
        _, indices = self._indexes[dataset_id].search(q_emb, k)
        rows = self._rows_text[dataset_id]
        return [rows[i] for i in indices[0] if 0 <= i < len(rows)]


rag_engine = RAGEngine()
