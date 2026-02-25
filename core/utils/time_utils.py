"""core.utils.time_utils - 시간 파싱/변환 유틸리티.

minutes-from-midnight 방식으로 시간 연산을 정수 산술로 단순화합니다.
"""

from datetime import date, timedelta


def parse_time_str(time_str: str) -> int:
    """'HH:MM' 문자열을 minutes-from-midnight 정수로 변환합니다.

    Args:
        time_str: "09:30" 형식의 시간 문자열.

    Returns:
        자정부터의 분 수 (예: "09:30" → 570).

    Raises:
        ValueError: 잘못된 형식일 때.
    """
    parts = time_str.strip().split(":")
    if len(parts) != 2:
        raise ValueError(f"잘못된 시간 형식: '{time_str}' (HH:MM 필요)")

    try:
        hours, minutes = int(parts[0]), int(parts[1])
    except ValueError:
        raise ValueError(f"잘못된 시간 형식: '{time_str}' (숫자가 아님)")

    if not (0 <= hours <= 23 and 0 <= minutes <= 59):
        raise ValueError(f"시간 범위 초과: '{time_str}'")

    return hours * 60 + minutes


def minutes_to_time_str(minutes: int) -> str:
    """minutes-from-midnight 정수를 'HH:MM' 문자열로 변환합니다.

    Args:
        minutes: 자정부터의 분 수.

    Returns:
        "09:30" 형식의 시간 문자열.
    """
    if minutes < 0:
        minutes = 0
    h = (minutes // 60) % 24
    m = minutes % 60
    return f"{h:02d}:{m:02d}"


def time_windows_overlap(
    start1: int, end1: int, start2: int, end2: int
) -> bool:
    """두 시간 윈도우가 겹치는지 확인합니다.

    Args:
        start1: 윈도우1 시작 (minutes-from-midnight).
        end1: 윈도우1 종료.
        start2: 윈도우2 시작.
        end2: 윈도우2 종료.

    Returns:
        겹치면 True.
    """
    return start1 < end2 and start2 < end1


def format_duration(minutes: int) -> str:
    """분 단위 시간을 사람이 읽기 쉬운 문자열로 변환합니다.

    Args:
        minutes: 시간(분).

    Returns:
        "1시간 30분", "45분" 등의 문자열.
    """
    if minutes <= 0:
        return "0분"

    h = minutes // 60
    m = minutes % 60

    if h > 0 and m > 0:
        return f"{h}시간 {m}분"
    if h > 0:
        return f"{h}시간"
    return f"{m}분"


def generate_date_range(start_date: date, end_date: date) -> list[date]:
    """시작일부터 종료일까지의 날짜 리스트를 반환합니다.

    Args:
        start_date: 시작 날짜 (포함).
        end_date: 종료 날짜 (포함).

    Returns:
        날짜 리스트.

    Raises:
        ValueError: end_date가 start_date보다 이전일 때.
    """
    if end_date < start_date:
        raise ValueError(
            f"종료일({end_date})이 시작일({start_date})보다 이전입니다."
        )

    days = (end_date - start_date).days + 1
    return [start_date + timedelta(days=i) for i in range(days)]
