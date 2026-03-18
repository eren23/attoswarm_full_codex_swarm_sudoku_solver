"""FastAPI application bootstrap for local runs and tests."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import AsyncIterator

from fastapi import APIRouter, FastAPI
from fastapi.staticfiles import StaticFiles

from src.api.routes.solve import router as solve_router


APP_TITLE = "Sudoku Solver API"
APP_VERSION = "0.1.0"
FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"


@dataclass(frozen=True)
class AppSettings:
    """Runtime settings exposed on application state."""

    environment: str
    testing: bool


def build_settings(*, testing: bool | None = None) -> AppSettings:
    """Build runtime settings for local development and test runs."""

    environment = os.getenv("APP_ENV", "local")
    if testing is None:
        testing = environment == "test" or os.getenv("PYTEST_CURRENT_TEST") is not None
    return AppSettings(environment=environment, testing=testing)


api_router = APIRouter()
api_router.include_router(solve_router)


@api_router.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    """Simple health check used by tests and local monitoring."""

    return {"status": "ok"}


def create_app(*, testing: bool | None = None) -> FastAPI:
    """Create and configure the FastAPI application."""

    settings = build_settings(testing=testing)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.started = True
        yield
        app.state.started = False

    app = FastAPI(
        title=APP_TITLE,
        version=APP_VERSION,
        lifespan=lifespan,
    )
    app.state.settings = settings
    app.include_router(api_router)
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
    return app


app = create_app()
