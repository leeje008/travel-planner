"""api.config - 환경변수 및 설정 관리.

pydantic-settings BaseSettings 기반 설정 클래스입니다.
"""

from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """애플리케이션 설정."""

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/travel_planner"
    REDIS_URL: str = "redis://localhost:6379/0"

    # External APIs
    GOOGLE_MAPS_API_KEY: str = ""
    KAKAO_REST_API_KEY: str = ""

    # LLM
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_TEMPERATURE: float = 0.3

    # App
    APP_ENV: str = "development"
    LOG_LEVEL: str = "DEBUG"

    model_config = {"env_file": ".env", "extra": "ignore"}

    @model_validator(mode="after")
    def normalize_database_url(self) -> "Settings":
        """Railway 등 외부 플랫폼이 제공하는 DB URL을 asyncpg 드라이버 형식으로 변환."""
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://") and "+asyncpg" not in url:
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        self.DATABASE_URL = url
        return self


settings = Settings()
