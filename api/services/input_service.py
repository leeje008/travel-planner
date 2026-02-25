"""api.services.input_service - Stage 1-2: 입력 파싱 + 정규화.

사용자 입력을 파싱하고 Place ID 매핑, 좌표 검증, 중복 제거를 수행합니다.
"""

import hashlib
import logging
from datetime import date, datetime

from api.schemas.input_schema import (
    CleanInput,
    CleanSpot,
    Coordinate,
    InputRequest,
    Preferences,
)

logger = logging.getLogger(__name__)


def _generate_temp_place_id(name: str) -> str:
    """이름 기반 임시 Place ID를 생성합니다."""
    hash_val = hashlib.md5(name.encode()).hexdigest()[:12]  # noqa: S324
    return f"temp_{hash_val}"


def _parse_dates(date_strings: list[str]) -> tuple[list[date], list[str]]:
    """날짜 문자열을 파싱합니다. 잘못된 형식은 warnings에 추가."""
    parsed: list[date] = []
    warnings: list[str] = []
    for ds in date_strings:
        try:
            parsed.append(datetime.strptime(ds, "%Y-%m-%d").date())
        except ValueError:
            warnings.append(f"날짜 형식 오류: '{ds}' (YYYY-MM-DD 형식이어야 합니다)")
    return parsed, warnings


async def parse_and_normalize(request: InputRequest) -> CleanInput:
    """사용자 입력을 정규화합니다.

    MVP 버전: 외부 API 없이 동작합니다.
    - place_id가 있으면 그대로 사용 (confidence=1.0)
    - 없으면 name 기반 임시 ID 생성 (confidence=0.0)
    - 좌표 없으면 warnings에 추가
    """
    warnings: list[str] = []

    # 날짜 파싱
    parsed_dates, date_warnings = _parse_dates(request.dates)
    warnings.extend(date_warnings)

    if not parsed_dates:
        parsed_dates = [date.today()]
        warnings.append("유효한 날짜가 없어 오늘 날짜로 설정했습니다")

    # 관광지 정규화
    clean_spots: list[CleanSpot] = []
    seen_ids: set[str] = set()

    for spot in request.spots:
        name = spot.name or "알 수 없는 장소"

        if spot.place_id:
            place_id = spot.place_id
            confidence = 1.0
        else:
            place_id = _generate_temp_place_id(name)
            confidence = 0.0
            warnings.append(f"'{name}': place_id 없음 — 임시 ID 발급, 좌표 미확인")

        if place_id in seen_ids:
            warnings.append(f"'{name}': 중복 제거됨")
            continue
        seen_ids.add(place_id)

        clean_spots.append(
            CleanSpot(
                place_id=place_id,
                name=name,
                latitude=0.0,
                longitude=0.0,
                opening_hours=None,
                confidence=confidence,
            )
        )

    # 출발지/도착지 좌표 (MVP: 임시 좌표, 실제로는 Geocoding API 필요)
    departure_coord = Coordinate(latitude=0.0, longitude=0.0)
    arrival_coord = Coordinate(latitude=0.0, longitude=0.0)
    warnings.append(f"출발지 '{request.departure}': 좌표 미확인 (Geocoding API 연동 필요)")

    if request.arrival:
        warnings.append(f"도착지 '{request.arrival}': 좌표 미확인 (Geocoding API 연동 필요)")

    # 선호 설정
    preferences = request.preferences or Preferences()

    logger.info(
        "입력 정규화 완료: spots=%d, dates=%d, warnings=%d",
        len(clean_spots),
        len(parsed_dates),
        len(warnings),
    )

    return CleanInput(
        spots=clean_spots,
        departure=departure_coord,
        arrival=arrival_coord,
        dates=parsed_dates,
        transport=request.transport,
        preferences=preferences,
        warnings=warnings,
    )
