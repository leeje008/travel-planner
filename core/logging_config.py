"""core.logging_config - 로깅 설정.

개발 환경(컬러 콘솔)과 프로덕션 환경(JSON) 분기를 지원합니다.

Usage::

    from core.logging_config import setup_logging, get_logger

    setup_logging()  # 앱 시작 시 한 번 호출
    logger = get_logger(__name__)
    logger.info("서버 시작")
"""

import json
import logging
import os
import sys
from datetime import UTC, datetime


class JsonFormatter(logging.Formatter):
    """프로덕션용 JSON 로그 포매터."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info and record.exc_info[1]:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data, ensure_ascii=False)


class ColorFormatter(logging.Formatter):
    """개발용 컬러 콘솔 포매터."""

    COLORS = {
        "DEBUG": "\033[36m",     # cyan
        "INFO": "\033[32m",      # green
        "WARNING": "\033[33m",   # yellow
        "ERROR": "\033[31m",     # red
        "CRITICAL": "\033[35m",  # magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname:<8}{self.RESET}"
        return super().format(record)


def setup_logging(level: str | None = None) -> None:
    """로깅 시스템을 초기화합니다.

    Args:
        level: 로그 레벨. None이면 LOG_LEVEL 환경변수 또는 INFO 사용.
    """
    log_level = (level or os.getenv("LOG_LEVEL", "INFO")).upper()
    app_env = os.getenv("APP_ENV", "development")

    root = logging.getLogger()
    root.setLevel(log_level)

    # 기존 핸들러 제거
    root.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)

    if app_env == "production":
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(
            ColorFormatter(
                fmt="%(asctime)s %(levelname)s [%(name)s] %(message)s",
                datefmt="%H:%M:%S",
            )
        )

    root.addHandler(handler)

    # 서드파티 라이브러리 로그 레벨 조정
    for noisy_logger in ("httpx", "httpcore", "urllib3", "sqlalchemy.engine"):
        logging.getLogger(noisy_logger).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """모듈별 로거를 반환합니다.

    Args:
        name: 보통 ``__name__`` 을 전달합니다.

    Returns:
        설정이 적용된 Logger 인스턴스.
    """
    return logging.getLogger(name)
