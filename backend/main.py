from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router as api_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Business Copilot",
        description="Production-style AI mini-CFO and data analyst backend",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix="/api")

    return app


app = create_app()


@app.get("/health")
async def health_check():
    return {"status": "ok"}

