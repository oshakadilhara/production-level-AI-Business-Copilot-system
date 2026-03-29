"""Map domain errors to HTTP responses — one place, consistent JSON shape."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from core.exceptions import CopilotValidationError, DatasetNotFound


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DatasetNotFound)
    async def _dataset_not_found(_: Request, __: DatasetNotFound) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={"detail": "Dataset not found"},
        )

    @app.exception_handler(CopilotValidationError)
    async def _validation(_: Request, exc: CopilotValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={"detail": exc.message},
        )
