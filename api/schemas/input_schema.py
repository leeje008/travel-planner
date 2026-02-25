"""api.schemas.input_schema - 사용자 입력 Pydantic 스키마.

InputRequest, Preferences, CleanInput, CleanSpot 등.
"""

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class SpotInput(BaseModel):
    """개별 관광지 입력."""

    name: str | None = None
    url: str | None = None
    place_id: str | None = None


class Preferences(BaseModel):
    """사용자 선호."""

    categories: list[str] = Field(default_factory=lambda: ["cafe", "restaurant"])
    companion: Literal["solo", "couple", "family", "friends"] = "solo"
    budget: int | None = None
    vibe: list[str] = Field(default_factory=list)
    meal_preference: str | None = None


class InputRequest(BaseModel):
    """Stage 1 입력 요청."""

    spots: list[SpotInput] = Field(..., min_length=2)
    departure: str
    arrival: str | None = None
    dates: list[str] = Field(..., min_length=1)
    transport: Literal["walk", "transit", "drive"] = "transit"
    preferences: Preferences | None = None


class Coordinate(BaseModel):
    """위경도 좌표."""

    latitude: float
    longitude: float


class CleanSpot(BaseModel):
    """Stage 2 정규화된 관광지 정보."""

    place_id: str
    name: str
    latitude: float
    longitude: float
    opening_hours: dict | None = None
    confidence: float = Field(ge=0.0, le=1.0)


class CleanInput(BaseModel):
    """Stage 2 정규화 결과."""

    spots: list[CleanSpot]
    departure: Coordinate
    arrival: Coordinate
    dates: list[date]
    transport: str
    preferences: Preferences
    warnings: list[str] = Field(default_factory=list)
