"""core.utils.geo - 좌표 계산 유틸리티.

Haversine 공식 기반 거리 계산, 좌표 유효성 검증, Bounding Box 등을 제공합니다.
"""

import math

# 지구 반지름 (km)
EARTH_RADIUS_KM = 6371.0


def haversine_distance(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    """두 좌표 사이의 대원 거리를 km 단위로 반환합니다.

    Args:
        lat1: 지점1 위도 (도).
        lon1: 지점1 경도 (도).
        lat2: 지점2 위도 (도).
        lon2: 지점2 경도 (도).

    Returns:
        두 지점 사이 거리 (km).
    """
    lat1_r, lat2_r = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return EARTH_RADIUS_KM * c


def haversine_distance_m(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    """두 좌표 사이의 대원 거리를 미터 단위로 반환합니다."""
    return haversine_distance(lat1, lon1, lat2, lon2) * 1000.0


def validate_coordinates(lat: float, lon: float) -> bool:
    """좌표가 유효한 범위인지 확인합니다.

    Args:
        lat: 위도 (-90 ~ 90).
        lon: 경도 (-180 ~ 180).

    Returns:
        유효하면 True.
    """
    return -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0


def bounding_box(
    lat: float, lon: float, radius_km: float
) -> tuple[float, float, float, float]:
    """중심 좌표와 반경으로 Bounding Box를 계산합니다.

    Args:
        lat: 중심 위도 (도).
        lon: 중심 경도 (도).
        radius_km: 반경 (km).

    Returns:
        (min_lat, min_lon, max_lat, max_lon) 튜플.
    """
    lat_r = math.radians(lat)

    # 위도 1도 ≈ 111km
    dlat = radius_km / 111.0
    # 경도 1도 ≈ 111km * cos(lat)
    dlon = radius_km / (111.0 * math.cos(lat_r))

    return (
        lat - dlat,
        lon - dlon,
        lat + dlat,
        lon + dlon,
    )


def is_within_radius(
    lat1: float, lon1: float, lat2: float, lon2: float, radius_km: float
) -> bool:
    """두 좌표 사이 거리가 지정 반경 이내인지 확인합니다.

    Args:
        lat1: 지점1 위도.
        lon1: 지점1 경도.
        lat2: 지점2 위도.
        lon2: 지점2 경도.
        radius_km: 허용 반경 (km).

    Returns:
        반경 이내이면 True.
    """
    return haversine_distance(lat1, lon1, lat2, lon2) <= radius_km
