"""core.constants - 프로젝트 전역 상수 정의.

StrEnum 기반 열거형과 비즈니스 로직 상수를 포함합니다.
"""

from enum import StrEnum

# ---------------------------------------------------------------------------
# Enum 정의
# ---------------------------------------------------------------------------

class POICategory(StrEnum):
    """POI 카테고리."""

    ATTRACTION = "attraction"
    CAFE = "cafe"
    RESTAURANT = "restaurant"
    ACCOMMODATION = "accommodation"
    SHOPPING = "shopping"
    CULTURE = "culture"
    NATURE = "nature"
    OTHER = "other"


class TransportMode(StrEnum):
    """이동수단."""

    WALK = "walk"
    TRANSIT = "transit"
    DRIVE = "drive"


class CompanionType(StrEnum):
    """동행 유형."""

    SOLO = "solo"
    COUPLE = "couple"
    FAMILY = "family"
    FRIENDS = "friends"


class PipelineStage(StrEnum):
    """API 파이프라인 단계."""

    INPUT = "input"
    NORMALIZE = "normalize"
    ROUTE = "route"
    POI_SEARCH = "poi_search"
    PACKAGE = "package"
    OUTPUT = "output"
    FEEDBACK = "feedback"


class PlanStatus(StrEnum):
    """여행 플랜 상태."""

    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# ---------------------------------------------------------------------------
# 검색 반경 (미터)
# ---------------------------------------------------------------------------

SEARCH_RADIUS_WALK = 500
SEARCH_RADIUS_TRANSIT = 800
SEARCH_RADIUS_DRIVE = 1500

SEARCH_RADIUS_BY_TRANSPORT: dict[TransportMode, int] = {
    TransportMode.WALK: SEARCH_RADIUS_WALK,
    TransportMode.TRANSIT: SEARCH_RADIUS_TRANSIT,
    TransportMode.DRIVE: SEARCH_RADIUS_DRIVE,
}

# ---------------------------------------------------------------------------
# 체류 시간 (분) — 카테고리별 기본값
# ---------------------------------------------------------------------------

DEFAULT_DWELL_MINUTES: dict[POICategory, int] = {
    POICategory.ATTRACTION: 90,
    POICategory.CAFE: 40,
    POICategory.RESTAURANT: 60,
    POICategory.ACCOMMODATION: 0,
    POICategory.SHOPPING: 45,
    POICategory.CULTURE: 60,
    POICategory.NATURE: 60,
    POICategory.OTHER: 30,
}

# ---------------------------------------------------------------------------
# 식사 시간대 (minutes-from-midnight)
# ---------------------------------------------------------------------------

LUNCH_START = 11 * 60 + 30   # 11:30 → 690
LUNCH_END = 13 * 60 + 30     # 13:30 → 810
DINNER_START = 17 * 60 + 30  # 17:30 → 1050
DINNER_END = 19 * 60 + 30    # 19:30 → 1170

CAFE_PREFERRED_START = 14 * 60  # 14:00 → 840
CAFE_PREFERRED_END = 16 * 60    # 16:00 → 960

# ---------------------------------------------------------------------------
# 일정 시간 제약 (minutes-from-midnight)
# ---------------------------------------------------------------------------

DAY_START = 9 * 60   # 09:00 → 540
DAY_END = 21 * 60    # 21:00 → 1260

# ---------------------------------------------------------------------------
# 캐시 TTL (초)
# ---------------------------------------------------------------------------

CACHE_TTL_POI_SEARCH = 3600       # 1시간
CACHE_TTL_DIRECTIONS = 3600       # 1시간
CACHE_TTL_PLACE_DETAILS = 86400   # 24시간
CACHE_TTL_GEOCODING = 604800      # 7일

# ---------------------------------------------------------------------------
# POI 랭킹 가중치
# ---------------------------------------------------------------------------

RANKING_WEIGHT_RATING = 0.3
RANKING_WEIGHT_REVIEWS = 0.2
RANKING_WEIGHT_DISTANCE = 0.3
RANKING_WEIGHT_CATEGORY = 0.2

# ---------------------------------------------------------------------------
# LLM Agent 설정
# ---------------------------------------------------------------------------

MAX_AGENT_RETRIES = 2
MAX_CANDIDATE_POIS = 20
MAX_DETOUR_METERS = 500
