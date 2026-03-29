class DatasetNotFound(LookupError):
    """Raised when no in-memory dataset exists for the given id."""

    def __init__(self, dataset_id: str) -> None:
        self.dataset_id = dataset_id
        super().__init__(f"Dataset not found: {dataset_id}")


class CopilotValidationError(Exception):
    """
    Predictable client or input error (unknown column, insufficient rows, etc.).
    Maps to HTTP 400 — do not use bare ValueError for these cases.
    """

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)
