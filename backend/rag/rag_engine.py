from typing import List, Tuple

import faiss
import numpy as np
import pandas as pd
from openai import OpenAI

from utils.config import get_settings


class RAGEngine:
    def __init__(self) -> None:
        self._indexes = {}
        self._rows_text = {}
        self._client = OpenAI(api_key=get_settings().openai_api_key)
        self._embed_model = get_settings().openai_embedding_model

    def _embed(self, texts: List[str]) -> np.ndarray:
        resp = self._client.embeddings.create(
            model=self._embed_model,
            input=texts,
        )
        vectors = [d.embedding for d in resp.data]
        return np.array(vectors).astype("float32")

    def build_index(self, dataset_id: str, df: pd.DataFrame) -> None:
        rows_as_text = [
            ", ".join(f"{col}={row[col]}" for col in df.columns) for _, row in df.iterrows()
        ]
        if not rows_as_text:
            return
        embeddings = self._embed(rows_as_text)
        dim = embeddings.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(embeddings)
        self._indexes[dataset_id] = index
        self._rows_text[dataset_id] = rows_as_text

    def query(self, dataset_id: str, query: str, k: int = 10) -> List[str]:
        if dataset_id not in self._indexes:
            raise KeyError("No index for dataset")
        q_emb = self._embed([query])
        D, I = self._indexes[dataset_id].search(q_emb, k)
        rows = self._rows_text[dataset_id]
        return [rows[i] for i in I[0] if 0 <= i < len(rows)]


rag_engine = RAGEngine()

