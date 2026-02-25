"""api.main - FastAPI 앱 진입점.

uvicorn api.main:app --reload
"""

import logging
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.routers.input import router as input_router
from core.exceptions import (
    ExternalAPIError,
    InvalidInputError,
    PlaceNotFoundError,
    TravelPlannerError,
)
from core.logging_config import setup_logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리."""
    setup_logging()
    logger.info("Application startup")
    yield
    logger.info("Application shutdown")


def create_app() -> FastAPI:
    """FastAPI 앱 팩토리."""
    app = FastAPI(
        title="AI Travel Planner",
        description="AI 기반 여행 일정 최적화 및 POI 추천 API",
        version="0.1.0",
        lifespan=lifespan,
    )

    # 글로벌 예외 핸들러
    @app.exception_handler(InvalidInputError)
    async def invalid_input_handler(request: Request, exc: InvalidInputError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"error": "InvalidInputError", "message": exc.message, "detail": exc.detail},
        )

    @app.exception_handler(PlaceNotFoundError)
    async def place_not_found_handler(request: Request, exc: PlaceNotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "PlaceNotFoundError", "message": exc.message, "detail": exc.detail},
        )

    @app.exception_handler(ExternalAPIError)
    async def external_api_handler(request: Request, exc: ExternalAPIError):
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={"error": "ExternalAPIError", "message": exc.message, "detail": exc.detail},
        )

    @app.exception_handler(TravelPlannerError)
    async def travel_planner_error_handler(request: Request, exc: TravelPlannerError):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": exc.__class__.__name__, "message": exc.message, "detail": exc.detail},
        )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://localhost:8000",
            "http://localhost:8501",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8000",
            "http://127.0.0.1:8501",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # /api/v1 prefix 라우터
    api_v1_router = APIRouter(prefix="/api/v1")
    api_v1_router.include_router(input_router)
    app.include_router(api_v1_router)

    @app.get("/health", status_code=status.HTTP_200_OK)
    def health():
        return {"status": "healthy"}

    return app


app = create_app()
