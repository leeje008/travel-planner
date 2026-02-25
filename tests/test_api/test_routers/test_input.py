"""tests.test_api.test_routers.test_input - input 라우터 테스트."""

import pytest


def test_health_check(client):
    """GET /health 정상 응답."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_parse_input_success(client):
    """POST /api/v1/plan/input 정상 요청."""
    payload = {
        "spots": [{"name": "경복궁"}, {"name": "남산타워"}],
        "departure": "서울역",
        "dates": ["2026-03-01", "2026-03-02"],
        "transport": "transit",
    }
    response = client.post("/api/v1/plan/input", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert len(data["spots"]) == 2
    assert data["spots"][0]["name"] == "경복궁"
    assert data["spots"][1]["name"] == "남산타워"
    assert data["transport"] == "transit"
    assert len(data["dates"]) == 2


def test_parse_input_with_place_id(client):
    """place_id가 있으면 confidence=1.0."""
    payload = {
        "spots": [
            {"name": "경복궁", "place_id": "ChIJ1234"},
            {"name": "남산타워"},
        ],
        "departure": "서울역",
        "dates": ["2026-03-01"],
        "transport": "walk",
    }
    response = client.post("/api/v1/plan/input", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["spots"][0]["confidence"] == 1.0
    assert data["spots"][0]["place_id"] == "ChIJ1234"
    assert data["spots"][1]["confidence"] == 0.0


def test_parse_input_too_few_spots(client):
    """관광지 1개만 입력하면 422."""
    payload = {
        "spots": [{"name": "경복궁"}],
        "departure": "서울역",
        "dates": ["2026-03-01"],
        "transport": "transit",
    }
    response = client.post("/api/v1/plan/input", json=payload)
    assert response.status_code == 422


def test_parse_input_no_spots(client):
    """관광지 없으면 422."""
    payload = {
        "spots": [],
        "departure": "서울역",
        "dates": ["2026-03-01"],
        "transport": "transit",
    }
    response = client.post("/api/v1/plan/input", json=payload)
    assert response.status_code == 422


def test_parse_input_duplicate_spots(client):
    """중복 관광지는 제거되고 warnings에 표시."""
    payload = {
        "spots": [
            {"name": "경복궁"},
            {"name": "경복궁"},
            {"name": "남산타워"},
        ],
        "departure": "서울역",
        "dates": ["2026-03-01"],
        "transport": "transit",
    }
    response = client.post("/api/v1/plan/input", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert len(data["spots"]) == 2
    assert any("중복" in w for w in data["warnings"])


def test_parse_input_invalid_date(client):
    """잘못된 날짜 형식은 warnings에 추가."""
    payload = {
        "spots": [{"name": "경복궁"}, {"name": "남산타워"}],
        "departure": "서울역",
        "dates": ["not-a-date"],
        "transport": "transit",
    }
    response = client.post("/api/v1/plan/input", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert any("날짜 형식 오류" in w for w in data["warnings"])


def test_parse_input_with_preferences(client):
    """선호 설정이 포함된 요청."""
    payload = {
        "spots": [{"name": "경복궁"}, {"name": "남산타워"}],
        "departure": "서울역",
        "dates": ["2026-03-01"],
        "transport": "drive",
        "preferences": {
            "categories": ["cafe", "culture"],
            "companion": "couple",
            "budget": 200000,
            "meal_preference": "한식",
        },
    }
    response = client.post("/api/v1/plan/input", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["preferences"]["companion"] == "couple"
    assert data["preferences"]["budget"] == 200000


def test_parse_input_arrival_defaults_to_departure(client):
    """도착지 미지정 시 출발지와 동일."""
    payload = {
        "spots": [{"name": "경복궁"}, {"name": "남산타워"}],
        "departure": "서울역",
        "dates": ["2026-03-01"],
        "transport": "transit",
    }
    response = client.post("/api/v1/plan/input", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["departure"] == data["arrival"]
