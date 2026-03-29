"""Centralized tunables. Prefer env for deployment-specific values; see `utils.config`."""

# Insights + RAG
RAG_TOP_K: int = 8
INSIGHT_PREVIEW_ROW_COUNT: int = 5
INSIGHT_CHAT_TEMPERATURE: float = 0.35

# Charts (Chart.js palette — single source for UI consistency)
CHART_LINE_BORDER = "rgba(75, 192, 192, 1)"
CHART_LINE_FILL = "rgba(75, 192, 192, 0.2)"

# ML
ML_TRAIN_TEST_SPLIT: float = 0.1
FEATURE_COLUMN_NAME: str = "_feature"
