"""core.exceptions - 프로젝트 커스텀 예외 계층.

모든 예외는 TravelPlannerError를 상속하므로
FastAPI exception handler에서 단일 catch-all 처리가 가능합니다.
"""


class TravelPlannerError(Exception):
    """프로젝트 최상위 예외."""

    def __init__(self, message: str = "", *, detail: str | None = None) -> None:
        self.message = message
        self.detail = detail
        super().__init__(message)


# ---------------------------------------------------------------------------
# 입력 관련
# ---------------------------------------------------------------------------

class InvalidInputError(TravelPlannerError):
    """사용자 입력이 유효하지 않을 때 발생."""


# ---------------------------------------------------------------------------
# 장소 / POI 관련
# ---------------------------------------------------------------------------

class PlaceNotFoundError(TravelPlannerError):
    """장소를 찾을 수 없을 때 발생."""


# ---------------------------------------------------------------------------
# 경로 최적화 관련
# ---------------------------------------------------------------------------

class RouteOptimizationError(TravelPlannerError):
    """경로 최적화에 실패했을 때 발생."""


# ---------------------------------------------------------------------------
# 외부 API 관련
# ---------------------------------------------------------------------------

class ExternalAPIError(TravelPlannerError):
    """외부 API 호출 실패 시 발생."""

    def __init__(
        self,
        message: str = "",
        *,
        service: str | None = None,
        status_code: int | None = None,
        detail: str | None = None,
    ) -> None:
        self.service = service
        self.status_code = status_code
        super().__init__(message, detail=detail)


# ---------------------------------------------------------------------------
# LLM 관련
# ---------------------------------------------------------------------------

class LLMResponseError(TravelPlannerError):
    """LLM 응답 파싱/검증 실패 시 발생."""


# ---------------------------------------------------------------------------
# 패키지 관련
# ---------------------------------------------------------------------------

class PackageValidationError(TravelPlannerError):
    """패키지 검증 실패 시 발생."""

    def __init__(
        self,
        message: str = "",
        *,
        issues: list[str] | None = None,
        detail: str | None = None,
    ) -> None:
        self.issues = issues or []
        super().__init__(message, detail=detail)


# ---------------------------------------------------------------------------
# 캐시 관련
# ---------------------------------------------------------------------------

class CacheError(TravelPlannerError):
    """캐시 연산 실패 시 발생."""


# ---------------------------------------------------------------------------
# 데이터베이스 관련
# ---------------------------------------------------------------------------

class DatabaseError(TravelPlannerError):
    """데이터베이스 연산 실패 시 발생."""
