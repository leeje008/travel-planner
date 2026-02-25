"""api.db.models - SQLAlchemy ORM 모델 정의.

POI, POIEmbedding, TravelPlan, Feedback 테이블을 정의합니다.
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.db.database import Base


class POI(Base):
    """관광지/카페/맛집 등 POI 정보."""

    __tablename__ = "poi"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    place_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(50))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    address: Mapped[str] = mapped_column(String(500), default="")
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    review_count: Mapped[int] = mapped_column(Integer, default=0)
    price_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    opening_hours: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    embedding: Mapped["POIEmbedding | None"] = relationship(back_populates="poi")


class POIEmbedding(Base):
    """POI 벡터 임베딩 (PGVector)."""

    __tablename__ = "poi_embedding"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    poi_id: Mapped[int] = mapped_column(Integer, ForeignKey("poi.id"), unique=True)
    content: Mapped[str] = mapped_column(Text)
    # embedding 컬럼은 PGVector 확장 활성화 후 마이그레이션에서 추가
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)

    poi: Mapped["POI"] = relationship(back_populates="embedding")


class TravelPlan(Base):
    """생성된 여행 플랜."""

    __tablename__ = "travel_plan"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_session_id: Mapped[str] = mapped_column(String(255), index=True)
    input_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    clean_input: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    route_plan: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    candidate_pois: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    package: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="processing")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    feedbacks: Mapped[list["Feedback"]] = relationship(back_populates="plan")


class Feedback(Base):
    """사용자 피드백."""

    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plan_id: Mapped[int] = mapped_column(Integer, ForeignKey("travel_plan.id"))
    overall_rating: Mapped[int] = mapped_column(Integer)
    poi_clicks: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    poi_saves: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    poi_excludes: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    plan: Mapped["TravelPlan"] = relationship(back_populates="feedbacks")
