# AI Travel Planner - Project Specification

> **목적**: 이 문서는 Claude Code가 프로젝트 구조 생성, 코드 스캐폴딩, 아키텍처 설계를 수행할 때 참조하는 **단일 진실 공급원(Single Source of Truth)**입니다.
> **현재 단계**: Phase 1 - MVP (코드 샘플 + 스캐폴딩)

---

## 1. 프로젝트 개요

사용자가 방문하고자 하는 관광지 목록을 입력하면:
1. 입력을 정규화하고 좌표/Place ID로 매핑
2. 최적 동선(TSP)을 산출
3. 동선 주변 카페/맛집 등 POI를 탐색
4. LLM Agent가 '여행 패키지'로 편집 (스토리텔링 + 추천 이유)
5. 지도 + 타임테이블 + 추천카드로 출력
6. 사용자 피드백으로 추천 품질 개선

---

## 2. 기술 스택

| 영역 | 기술 | 버전/비고 |
|------|------|-----------|
| Language | Python | 3.11+ |
| Web Framework | FastAPI | API 서버 |
| Frontend | Streamlit (MVP) → React (Phase 2) | MVP는 Streamlit |
| LLM Framework | LangChain + LangGraph | Agent 파이프라인 |
| LLM Provider | OpenAI / Anthropic | gpt-4o-mini (MVP), claude-sonnet-4-20250514 |
| Vector DB | PGVector (PostgreSQL) | RAG용 |
| Cache | Redis | POI/경로 캐싱 |
| Routing Engine | Google OR-Tools | TSP/VRP 최적화 |
| Map API | Google Maps Platform / Kakao Maps | Geocoding, Places, Directions |
| Database | PostgreSQL 16 | 메인 DB |
| Task Queue | Celery + Redis | 비동기 처리 (Phase 2) |
| Container | Docker + docker-compose | 로컬 개발 환경 |

---

## 3. 프로젝트 폴더 구조

```
travel-planner/
├── README.md                    # 프로젝트 소개 및 실행 가이드
├── PROJECT_SPEC.md              # 이 문서
├── docker-compose.yml           # PostgreSQL, Redis, PGVector
├── .env.example                 # 환경변수 템플릿
├── pyproject.toml               # Python 의존성 (uv/poetry)
├── alembic.ini                  # DB 마이그레이션 설정
├── alembic/                     # 마이그레이션 스크립트
│
├── etl/                         # ── ETL 레이어 ──
│   ├── __init__.py
│   ├── README.md                # ETL 모듈 설명
│   ├── poi_collector.py         # 외부 API → POI DB 적재
│   ├── review_collector.py      # 리뷰 데이터 수집/요약
│   ├── embedding_builder.py     # POI 텍스트 → 벡터 임베딩 생성
│   ├── place_cache_updater.py   # Place 정보 주기적 캐시 갱신
│   └── scripts/
│       ├── seed_sample_data.py  # 샘플 데이터 시딩
│       └── run_etl_pipeline.py  # ETL 파이프라인 실행 스크립트
│
├── api/                         # ── API 레이어 ──
│   ├── __init__.py
│   ├── README.md                # API 모듈 설명
│   ├── main.py                  # FastAPI app 진입점
│   ├── config.py                # 환경변수/설정 관리
│   ├── dependencies.py          # FastAPI 의존성 주입
│   │
│   ├── routers/                 # 라우터 (엔드포인트 정의)
│   │   ├── __init__.py
│   │   ├── input.py             # POST /api/v1/plan/input
│   │   ├── route.py             # POST /api/v1/plan/route
│   │   ├── poi.py               # POST /api/v1/plan/poi
│   │   ├── package.py           # POST /api/v1/plan/package
│   │   ├── output.py            # GET  /api/v1/plan/{plan_id}
│   │   └── feedback.py          # POST /api/v1/plan/{plan_id}/feedback
│   │
│   ├── schemas/                 # Pydantic 모델 (Request/Response)
│   │   ├── __init__.py
│   │   ├── input_schema.py      # 사용자 입력 스키마
│   │   ├── route_schema.py      # 경로 최적화 스키마
│   │   ├── poi_schema.py        # POI 검색 스키마
│   │   ├── package_schema.py    # 패키지 출력 스키마
│   │   └── feedback_schema.py   # 피드백 스키마
│   │
│   ├── services/                # 비즈니스 로직 (핵심 처리)
│   │   ├── __init__.py
│   │   ├── input_service.py     # Stage 1-2: 입력 파싱 + 정규화
│   │   ├── route_service.py     # Stage 3: 경로 최적화
│   │   ├── poi_service.py       # Stage 4: 주변 POI 탐색
│   │   ├── package_service.py   # Stage 5: LLM 패키지 구성 (오케스트레이터)
│   │   ├── output_service.py    # Stage 6: 출력 생성
│   │   └── feedback_service.py  # Stage 7: 피드백 처리
│   │
│   ├── agents/                  # LLM Agent 정의 (LangGraph)
│   │   ├── __init__.py
│   │   ├── graph.py             # LangGraph StateGraph 정의
│   │   ├── state.py             # Agent 공유 State 스키마
│   │   ├── curator.py           # Curator Agent (POI 선별 + 슬롯 배치)
│   │   ├── storyteller.py       # Storyteller Agent (스토리/추천멘트)
│   │   ├── validator.py         # Validator Agent (규칙 기반 검증)
│   │   └── prompts/
│   │       ├── curator.py       # Curator 프롬프트 템플릿
│   │       ├── storyteller.py   # Storyteller 프롬프트 템플릿
│   │       └── validator.py     # Validator 프롬프트 템플릿
│   │
│   ├── external/                # 외부 API 클라이언트
│   │   ├── __init__.py
│   │   ├── google_places.py     # Google Places API 래퍼
│   │   ├── google_directions.py # Google Directions API 래퍼
│   │   ├── google_geocoding.py  # Google Geocoding API 래퍼
│   │   ├── kakao_local.py       # Kakao Local API 래퍼
│   │   └── base_client.py       # HTTP 클라이언트 베이스 (httpx)
│   │
│   └── db/                      # 데이터베이스
│       ├── __init__.py
│       ├── database.py          # SQLAlchemy async engine/session
│       ├── models.py            # ORM 모델 정의
│       └── repositories/
│           ├── __init__.py
│           ├── poi_repo.py      # POI CRUD
│           ├── plan_repo.py     # Plan CRUD
│           └── feedback_repo.py # Feedback CRUD
│
├── app/                         # ── APP 레이어 (Frontend) ──
│   ├── __init__.py
│   ├── README.md                # APP 모듈 설명
│   ├── streamlit_app.py         # Streamlit 메인 앱
│   ├── pages/
│   │   ├── 01_input.py          # 입력 페이지
│   │   ├── 02_result.py         # 결과 페이지 (지도 + 타임테이블)
│   │   └── 03_feedback.py       # 피드백 페이지
│   └── components/
│       ├── map_renderer.py      # 지도 렌더링 컴포넌트
│       ├── timeline.py          # 타임라인 컴포넌트
│       └── place_card.py        # 장소 추천카드 컴포넌트
│
├── core/                        # ── 공유 모듈 ──
│   ├── __init__.py
│   ├── constants.py             # 상수 정의
│   ├── exceptions.py            # 커스텀 예외
│   ├── logging_config.py        # 로깅 설정
│   └── utils/
│       ├── __init__.py
│       ├── geo.py               # 좌표 계산 유틸 (Haversine 등)
│       ├── time_utils.py        # 시간 파싱/변환 유틸
│       └── text.py              # 텍스트 정규화 유틸
│
└── tests/                       # ── 테스트 ──
    ├── __init__.py
    ├── conftest.py              # pytest fixtures
    ├── test_etl/
    ├── test_api/
    │   ├── test_services/
    │   ├── test_agents/
    │   └── test_routers/
    └── test_app/
```

---

## 4. 레이어별 책임 정의

### 4.1 ETL 레이어 (`etl/`)

**역할**: 외부 데이터를 수집·가공하여 내부 DB에 적재. 배치/스케줄 실행.

| 모듈 | 기능 | 입력 | 출력 |
|------|------|------|------|
| `poi_collector.py` | Google/Kakao Places API로 지역별 POI 수집 | 지역 목록 (시/구 단위) | `poi` 테이블 적재 |
| `review_collector.py` | POI별 리뷰 수집 및 LLM 요약 | POI ID 목록 | `review_summary` 테이블 |
| `embedding_builder.py` | POI 설명+리뷰 텍스트 → 벡터 임베딩 | `poi` + `review_summary` | `poi_embedding` 테이블 (PGVector) |
| `place_cache_updater.py` | 영업시간/폐업 여부 등 최신 정보 갱신 | `poi` 테이블 | `poi` 테이블 업데이트 |

**실행 방식**:
```bash
# 샘플 데이터 시딩 (개발용)
python -m etl.scripts.seed_sample_data

# 전체 ETL 파이프라인
python -m etl.scripts.run_etl_pipeline --region "제주" --categories "cafe,restaurant"
```

### 4.2 API 레이어 (`api/`)

**역할**: 핵심 비즈니스 로직. 7-Stage 파이프라인의 실제 처리를 담당.

#### 4.2.1 API 엔드포인트 명세

```
POST /api/v1/plan/input
  - 사용자 입력 수신 + Stage 1-2 처리 (파싱, 정규화, 검증)
  - Request:  InputRequest (관광지 목록, 날짜, 이동수단, 선호)
  - Response: CleanInput (정규화된 Place ID 목록, 좌표, 검증 결과)

POST /api/v1/plan/route
  - Stage 3: 최적 경로 생성
  - Request:  RouteRequest (Place ID 목록, 시간 제약, 이동수단)
  - Response: RoutePlan (방문 순서, 구간별 이동시간, 도착/출발 시각)

POST /api/v1/plan/poi
  - Stage 4: 주변 POI 탐색
  - Request:  POIRequest (RoutePlan + 선호 카테고리)
  - Response: CandidatePOI[] (후보 POI 리스트 with 랭킹 점수)

POST /api/v1/plan/package
  - Stage 5: LLM 패키지 구성 (핵심)
  - Request:  PackageRequest (RoutePlan + CandidatePOI + 사용자 선호)
  - Response: PackageDraft (JSON - 최종 패키지)
  - SSE 스트리밍 지원: GET /api/v1/plan/package/stream/{task_id}

GET /api/v1/plan/{plan_id}
  - Stage 6: 최종 결과 조회
  - Response: FinalOutput (패키지 + 지도 데이터 + 타임테이블)

POST /api/v1/plan/{plan_id}/feedback
  - Stage 7: 피드백 수신
  - Request:  FeedbackRequest (별점, 클릭 로그, 제외 사유)

# === 통합 엔드포인트 (1~5 한 번에 실행) ===
POST /api/v1/plan/generate
  - Stage 1~5 일괄 실행
  - Request:  GenerateRequest (사용자 원본 입력)
  - Response: SSE 스트림 (단계별 진행 상태 + 최종 패키지)
```

#### 4.2.2 서비스 레이어 흐름

```
[사용자 입력]
    │
    ▼
input_service.py ─── Stage 1: 자연어 파싱 (LLM Function Calling)
    │                 Stage 2: Place ID 매핑, 좌표 검증, 중복 제거
    ▼
route_service.py ─── Stage 3: OR-Tools TSP 최적화
    │                 - Distance Matrix 계산 (Google Directions / OSRM)
    │                 - Time Window + Dwell Time 제약
    │                 - Multi-day 분할 (K-Means 클러스터링)
    ▼
poi_service.py ───── Stage 4: 주변 POI 탐색
    │                 - Radial Search (각 Stop 반경 300~800m)
    │                 - Route-corridor Search (경로 Buffer)
    │                 - 필터링 + 랭킹
    ▼
package_service.py ─ Stage 5: LLM Agent 파이프라인 (LangGraph)
    │                 - Curator Agent → Storyteller Agent → Validator Agent
    │                 - RAG 컨텍스트 주입
    ▼
output_service.py ── Stage 6: 최종 출력 포맷팅
    │
    ▼
[지도 + 타임테이블 + 추천카드]
```

### 4.3 APP 레이어 (`app/`)

**역할**: 사용자 인터페이스. MVP는 Streamlit, Phase 2에서 React 전환.

| 페이지 | 역할 |
|--------|------|
| `01_input.py` | 관광지 입력 (텍스트/지도 선택), 조건 설정, 선호 입력 |
| `02_result.py` | 지도(folium) + 타임테이블 + 추천카드 렌더링 |
| `03_feedback.py` | 별점, POI별 좋아요/제외, 의견 입력 |

---

## 5. 핵심 모듈 상세 설계

### 5.1 데이터베이스 모델 (`api/db/models.py`)

```python
# 주요 테이블 정의

class POI(Base):
    """관광지/카페/맛집 등 POI 정보"""
    __tablename__ = "poi"
    id: int                     # PK
    place_id: str               # Google Place ID (unique)
    name: str                   # 장소명
    category: str               # attraction | cafe | restaurant | etc
    latitude: float
    longitude: float
    address: str
    phone: str | None
    rating: float | None        # 평점 (1.0~5.0)
    review_count: int
    price_level: int | None     # 0~4 (Google 기준)
    opening_hours: JSON | None  # 영업시간 JSON
    is_active: bool             # 영업 중 여부
    updated_at: datetime

class POIEmbedding(Base):
    """POI 벡터 임베딩 (PGVector)"""
    __tablename__ = "poi_embedding"
    id: int
    poi_id: int                 # FK → poi.id
    content: str                # 임베딩 원본 텍스트
    embedding: Vector(1536)     # PGVector 컬럼
    metadata: JSON              # 카테고리, 지역 등 필터 메타

class TravelPlan(Base):
    """생성된 여행 플랜"""
    __tablename__ = "travel_plan"
    id: int
    user_session_id: str        # 사용자 세션 식별
    input_data: JSON            # 원본 입력
    clean_input: JSON           # 정규화된 입력
    route_plan: JSON            # 최적 경로
    candidate_pois: JSON        # 후보 POI 목록
    package: JSON               # 최종 패키지
    status: str                 # processing | completed | failed
    created_at: datetime

class Feedback(Base):
    """사용자 피드백"""
    __tablename__ = "feedback"
    id: int
    plan_id: int                # FK → travel_plan.id
    overall_rating: int         # 1~5
    poi_clicks: JSON            # {place_id: click_count}
    poi_saves: JSON             # [place_id, ...]
    poi_excludes: JSON          # [{place_id, reason}]
    comment: str | None
    created_at: datetime
```

### 5.2 Pydantic 스키마 (`api/schemas/`)

```python
# === input_schema.py ===

class SpotInput(BaseModel):
    """개별 관광지 입력"""
    name: str | None = None           # 장소명
    url: str | None = None            # 블로그/지도 URL
    place_id: str | None = None       # 이미 알고 있는 경우

class InputRequest(BaseModel):
    """Stage 1 입력 요청"""
    spots: list[SpotInput]            # 관광지 목록 (최소 2개)
    departure: str                     # 출발지 (주소 또는 좌표)
    arrival: str | None = None         # 도착지 (없으면 출발지 = 도착지)
    dates: list[str]                   # 여행 날짜 ["2026-03-01", "2026-03-02"]
    transport: Literal["walk", "transit", "drive"]
    preferences: Preferences | None = None

class Preferences(BaseModel):
    """사용자 선호"""
    categories: list[str] = ["cafe", "restaurant"]  # 관심 카테고리
    companion: Literal["solo", "couple", "family", "friends"] = "solo"
    budget: int | None = None          # 총 예산 (원)
    vibe: list[str] = []               # ["감성", "핫플", "조용한", "뷰맛집"]
    meal_preference: str | None = None # "한식", "일식" 등

class CleanInput(BaseModel):
    """Stage 2 정규화 결과"""
    spots: list[CleanSpot]
    departure: Coordinate
    arrival: Coordinate
    dates: list[date]
    transport: str
    preferences: Preferences
    warnings: list[str] = []           # 보정 사항 알림

class CleanSpot(BaseModel):
    place_id: str
    name: str
    latitude: float
    longitude: float
    opening_hours: dict | None
    confidence: float                  # 매핑 신뢰도 (0~1)


# === route_schema.py ===

class RoutePlan(BaseModel):
    """Stage 3 최적 경로"""
    days: list[DayRoute]
    total_travel_minutes: int
    total_distance_km: float

class DayRoute(BaseModel):
    day_number: int
    date: str
    stops: list[RouteStop]

class RouteStop(BaseModel):
    order: int
    place_id: str
    name: str
    arrival_time: str              # "09:30"
    departure_time: str            # "11:00"
    dwell_minutes: int
    transit_to_next: TransitInfo | None

class TransitInfo(BaseModel):
    mode: str
    duration_minutes: int
    distance_km: float
    polyline: str | None           # encoded polyline


# === package_schema.py ===

class TravelPackage(BaseModel):
    """Stage 5 최종 패키지"""
    package_id: str
    title: str                     # "제주 동쪽 해안 감성 여행"
    description: str               # 패키지 한 줄 설명
    theme: str                     # "healing" | "activity" | "gourmet" 등
    days: list[PackageDay]
    total_duration_hours: float
    total_distance_km: float
    estimated_budget: int | None
    metadata: PackageMetadata

class PackageDay(BaseModel):
    day_number: int
    date: str
    title: str                     # "성산일출봉에서 시작하는 아침"
    story: str                     # 하루 코스 스토리
    stops: list[PackageStop]

class PackageStop(BaseModel):
    order: int
    place_id: str
    name: str
    type: Literal["attraction", "cafe", "restaurant", "other"]
    arrival_time: str
    departure_time: str
    dwell_minutes: int
    recommendation_reason: str     # "현지인이 추천하는 흑돼지 맛집..."
    rating: float | None
    transit_to_next: TransitInfo | None
```

### 5.3 LLM Agent 파이프라인 (`api/agents/`)

#### State 정의 (`state.py`)

```python
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class PlannerState(TypedDict):
    """LangGraph Agent 공유 상태"""
    # 입력 데이터
    user_preferences: dict
    route_plan: dict              # Stage 3 결과
    candidate_pois: list[dict]    # Stage 4 결과

    # Agent 처리 결과
    curated_schedule: dict | None     # Curator 출력
    validation_result: dict | None    # Validator 출력
    story_content: dict | None        # Storyteller 출력
    final_package: dict | None        # 최종 패키지

    # 제어
    errors: list[str]
    retry_count: int
    messages: Annotated[list, add_messages]
```

#### Graph 정의 (`graph.py`)

```python
from langgraph.graph import StateGraph, END

def build_planner_graph():
    graph = StateGraph(PlannerState)

    # 노드 등록
    graph.add_node("curate", curate_node)
    graph.add_node("validate", validate_node)
    graph.add_node("storytell", storytell_node)
    graph.add_node("format_output", format_output_node)

    # 엣지 정의
    graph.set_entry_point("curate")
    graph.add_edge("curate", "validate")
    graph.add_conditional_edges(
        "validate",
        validation_router,      # 검증 통과 → storytell, 실패 → curate (재시도)
        {"pass": "storytell", "fail": "curate", "max_retry": END}
    )
    graph.add_edge("storytell", "format_output")
    graph.add_edge("format_output", END)

    return graph.compile()


def validation_router(state: PlannerState) -> str:
    if state["validation_result"]["is_valid"]:
        return "pass"
    if state["retry_count"] >= 2:
        return "max_retry"
    return "fail"
```

#### Curator Agent (`curator.py`)

```python
async def curate_node(state: PlannerState) -> dict:
    """
    역할: 후보 POI를 선별하고 일정표의 슬롯에 배치
    로직:
      1. 식사 시간대(11:30~13:30, 17:30~19:30)에 맛집 자동 배치
      2. 카페는 오후 2~4시 우선 배치
      3. 영업시간 내 방문 가능한 POI만 선별
      4. 동선 이탈 최소화 (경로 반경 내 POI 우선)
      5. LLM으로 최종 선별 판단 (선호도 + 밸런스 고려)
    """
    # Rule-based 사전 필터링
    filtered = apply_time_rules(state["route_plan"], state["candidate_pois"])
    filtered = apply_distance_filter(filtered, max_detour_meters=500)

    # LLM 최종 선별
    response = await llm.ainvoke(
        curator_prompt.format(
            route=state["route_plan"],
            candidates=filtered,
            preferences=state["user_preferences"]
        )
    )
    return {"curated_schedule": parse_curator_response(response)}
```

#### Storyteller Agent (`storyteller.py`)

```python
async def storytell_node(state: PlannerState) -> dict:
    """
    역할: 확정된 일정에 스토리와 추천 멘트를 부여
    로직:
      1. RAG로 각 장소의 상세 정보 검색
      2. 동행 유형에 맞는 톤/스타일 적용
      3. 하루 코스 전체 스토리라인 생성
      4. 각 POI별 추천 이유 생성 (리뷰 기반 하이라이트)
    """
    # RAG 컨텍스트 수집
    rag_context = await retrieve_poi_context(state["curated_schedule"])

    # LLM 스토리 생성
    response = await llm.ainvoke(
        storyteller_prompt.format(
            schedule=state["curated_schedule"],
            context=rag_context,
            companion=state["user_preferences"]["companion"],
        )
    )
    return {"story_content": parse_storyteller_response(response)}
```

#### Validator Agent (`validator.py`)

```python
async def validate_node(state: PlannerState) -> dict:
    """
    역할: 패키지의 논리적 정합성을 규칙 기반으로 검증
    검증 항목:
      1. 시간 충돌: 체류시간 + 이동시간 > 다음 슬롯 시작시간?
      2. 영업시간: 배치 시간이 영업시간 내?
      3. 동선 일관성: POI가 경로에서 허용 반경 초과?
      4. 예산 제약: 총 예상 비용 ≤ 사용자 예산?
      5. 식사/카페 배치: 적절한 시간대?
      6. 중복 검증: 동일 POI 중복 배치?
    """
    issues = []
    schedule = state["curated_schedule"]

    # 규칙 기반 검증 (LLM 불필요)
    issues += check_time_conflicts(schedule)
    issues += check_opening_hours(schedule)
    issues += check_route_consistency(schedule, state["route_plan"])
    issues += check_budget(schedule, state["user_preferences"])
    issues += check_meal_timing(schedule)
    issues += check_duplicates(schedule)

    return {
        "validation_result": {
            "is_valid": len(issues) == 0,
            "issues": issues
        },
        "retry_count": state["retry_count"] + (1 if issues else 0)
    }
```

### 5.4 경로 최적화 (`api/services/route_service.py`)

```python
from ortools.constraint_solver import routing_enums_pb2, pywrapcp

async def optimize_route(spots: list[CleanSpot], transport: str,
                         time_windows: dict | None = None) -> RoutePlan:
    """
    Stage 3: TSP with Time Windows
    알고리즘:
      - spots ≤ 10: CP-SAT Exact Solver
      - spots 11~25: Guided Local Search Metaheuristic
      - spots ≥ 26: Cluster-First (K-Means), Route-Second
    """
    n = len(spots)

    # 1. Distance/Time Matrix 계산
    matrix = await build_time_matrix(spots, transport)

    # 2. OR-Tools Routing Model 설정
    manager = pywrapcp.RoutingIndexManager(n, 1, 0)  # 1 vehicle, depot=0
    routing = pywrapcp.RoutingModel(manager)

    def time_callback(from_idx, to_idx):
        from_node = manager.IndexToNode(from_idx)
        to_node = manager.IndexToNode(to_idx)
        return matrix[from_node][to_node]

    transit_idx = routing.RegisterTransitCallback(time_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_idx)

    # 3. Time Window 제약 추가
    if time_windows:
        routing.AddDimension(transit_idx, 30, 720, False, "Time")
        time_dim = routing.GetDimensionOrDie("Time")
        for i, spot in enumerate(spots):
            if spot.place_id in time_windows:
                tw = time_windows[spot.place_id]
                idx = manager.NodeToIndex(i)
                time_dim.CumulVar(idx).SetRange(tw["start"], tw["end"])

    # 4. 솔버 실행
    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    params.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    params.time_limit.FromSeconds(5 if n <= 10 else 15)

    solution = routing.SolveWithParameters(params)
    return parse_solution(solution, routing, manager, spots, matrix)
```

### 5.5 주변 POI 탐색 (`api/services/poi_service.py`)

```python
async def search_nearby_pois(route_plan: RoutePlan,
                              preferences: Preferences) -> list[CandidatePOI]:
    """
    Stage 4: 주변 POI 탐색
    전략:
      1. Stop-based Radial Search: 각 관광지 반경 300~800m
      2. Route-corridor Search: 구간 경로 Buffer 내 POI
      3. 결과 합산 → 필터링 → 랭킹
    """
    all_candidates = []

    for day in route_plan.days:
        for stop in day.stops:
            # Radial Search
            radius = get_dynamic_radius(stop, preferences.transport)
            pois = await google_places.nearby_search(
                lat=stop.latitude, lng=stop.longitude,
                radius=radius,
                types=preferences.categories
            )
            all_candidates.extend(pois)

        # Route-corridor Search (구간별)
        for i in range(len(day.stops) - 1):
            polyline = day.stops[i].transit_to_next.polyline
            if polyline:
                corridor_pois = await search_along_route(
                    polyline, buffer_meters=300,
                    types=preferences.categories
                )
                all_candidates.extend(corridor_pois)

    # 중복 제거 + 필터링 + 랭킹
    unique = deduplicate_by_place_id(all_candidates)
    filtered = apply_filters(unique, preferences)
    ranked = rank_pois(filtered, preferences)

    return ranked[:20]  # 상위 20개 반환


def rank_pois(pois: list, preferences: Preferences) -> list:
    """
    랭킹 수식:
    score = w1·rating + w2·log(review_count) + w3·(1/distance) + w4·category_match
    가중치는 사용자 선호에 따라 동적 조절
    """
    w1, w2, w3, w4 = 0.3, 0.2, 0.3, 0.2
    for poi in pois:
        poi.score = (
            w1 * (poi.rating or 0) / 5.0 +
            w2 * math.log(poi.review_count + 1) / 10.0 +
            w3 * (1.0 / max(poi.distance_meters, 50)) * 500 +
            w4 * (1.0 if poi.category in preferences.categories else 0.0)
        )
    return sorted(pois, key=lambda p: p.score, reverse=True)
```

### 5.6 외부 API 클라이언트 (`api/external/`)

```python
# === base_client.py ===
class BaseAPIClient:
    """공통 HTTP 클라이언트 (httpx 기반)"""
    def __init__(self, base_url: str, api_key: str):
        self.client = httpx.AsyncClient(
            base_url=base_url,
            timeout=10.0,
            headers={"Accept": "application/json"}
        )
        self.api_key = api_key
        self.cache = RedisCache()

    async def get(self, path: str, params: dict, cache_ttl: int = 3600):
        cache_key = f"{path}:{hash(frozenset(params.items()))}"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached
        response = await self.client.get(path, params={**params, "key": self.api_key})
        response.raise_for_status()
        data = response.json()
        await self.cache.set(cache_key, data, ttl=cache_ttl)
        return data


# === google_places.py ===
class GooglePlacesClient(BaseAPIClient):
    """Google Places API 래퍼"""

    async def text_search(self, query: str) -> list[dict]:
        """장소명 → Place ID 매핑"""
        data = await self.get("/maps/api/place/textsearch/json",
                              {"query": query, "language": "ko"})
        return data.get("results", [])

    async def nearby_search(self, lat: float, lng: float,
                            radius: int, types: list[str]) -> list[dict]:
        """반경 내 POI 검색"""
        data = await self.get("/maps/api/place/nearbysearch/json", {
            "location": f"{lat},{lng}",
            "radius": radius,
            "type": "|".join(types),
            "language": "ko"
        })
        return data.get("results", [])

    async def place_details(self, place_id: str) -> dict:
        """Place ID → 상세 정보"""
        data = await self.get("/maps/api/place/details/json", {
            "place_id": place_id,
            "fields": "name,formatted_address,geometry,opening_hours,"
                      "rating,user_ratings_total,price_level,photos",
            "language": "ko"
        }, cache_ttl=86400)  # 24시간 캐시
        return data.get("result", {})
```

---

## 6. 환경 설정

### 6.1 환경변수 (`.env.example`)

```env
# === Database ===
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/travel_planner
REDIS_URL=redis://localhost:6379/0

# === External APIs ===
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
KAKAO_REST_API_KEY=your_kakao_rest_api_key

# === LLM ===
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
LLM_MODEL=gpt-4o-mini           # MVP 기본 모델
LLM_TEMPERATURE=0.3

# === App ===
APP_ENV=development
LOG_LEVEL=DEBUG
```

### 6.2 Docker Compose (`docker-compose.yml`)

```yaml
services:
  db:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_DB: travel_planner
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  pgdata:
```

### 6.3 Python 의존성 (`pyproject.toml` 핵심)

```toml
[project]
name = "travel-planner"
version = "0.1.0"
requires-python = ">=3.11"

dependencies = [
    # Web
    "fastapi>=0.115",
    "uvicorn[standard]>=0.30",
    # LLM
    "langchain>=0.3",
    "langgraph>=0.2",
    "langchain-openai>=0.2",
    "langchain-anthropic>=0.3",
    # DB
    "sqlalchemy[asyncio]>=2.0",
    "asyncpg>=0.30",
    "pgvector>=0.3",
    "alembic>=1.14",
    # Routing
    "ortools>=9.10",
    # HTTP
    "httpx>=0.28",
    # Cache
    "redis>=5.0",
    # Geo
    "shapely>=2.0",
    "polyline>=2.0",
    # Frontend (MVP)
    "streamlit>=1.40",
    "folium>=0.18",
    "streamlit-folium>=0.23",
    # Utils
    "pydantic>=2.9",
    "pydantic-settings>=2.6",
    "python-dotenv>=1.0",
]

[project.optional-dependencies]
dev = ["pytest>=8.0", "pytest-asyncio>=0.24", "ruff>=0.8"]
```

---

## 7. 단계별 구현 가이드 (Claude Code용)

### Phase 1: 스캐폴딩 + 코드 샘플

> Claude Code에게 요청할 작업 순서

```
Step 1: 프로젝트 초기화
- 위 폴더 구조 생성
- pyproject.toml, docker-compose.yml, .env.example 생성
- core/ 모듈 (constants, exceptions, utils) 구현

Step 2: DB 설정
- SQLAlchemy 모델 정의 (api/db/models.py)
- Alembic 초기 마이그레이션 생성
- docker-compose up으로 PostgreSQL + PGVector 확인

Step 3: 외부 API 클라이언트
- base_client.py (httpx + Redis 캐싱)
- google_places.py, google_directions.py, google_geocoding.py
- 각 클라이언트 단위 테스트

Step 4: 서비스 레이어 (Stage 1~4)
- input_service.py → Place ID 매핑 + 검증
- route_service.py → OR-Tools TSP (기본 버전, 시간창 없이)
- poi_service.py → Radial Search + 랭킹

Step 5: LLM Agent (Stage 5)
- state.py, graph.py 정의
- curator.py + prompts/curator.py
- storyteller.py + prompts/storyteller.py
- validator.py + prompts/validator.py
- LangGraph 통합 테스트

Step 6: API 라우터
- FastAPI 라우터 연결
- Pydantic 스키마 검증
- /api/v1/plan/generate 통합 엔드포인트

Step 7: Streamlit MVP
- 입력 폼 → API 호출 → 결과 렌더링
- folium 지도 + 타임라인 표시
```

### Phase 1에서 스킵해도 되는 것

- Multi-day 분할 알고리즘 (1일 여행만 지원)
- Route-corridor Search (Radial Search만)
- RAG (직접 컨텍스트 주입으로 대체)
- PDF 내보내기
- 피드백 학습 (수집만)
- Celery 비동기 처리
- A/B 테스트

---

## 8. 코딩 컨벤션

```
- Python: ruff 포매터/린터 사용
- Type Hints: 모든 함수에 타입 힌트 필수
- Async: DB/HTTP 호출은 모두 async/await
- Error Handling: 커스텀 예외 + FastAPI exception handler
- Logging: structlog 또는 logging_config.py의 표준 로거
- 테스트: pytest + pytest-asyncio, 서비스 레이어 중심
- Docstring: 모든 서비스 함수에 역할/입력/출력 명시
- 환경변수: pydantic-settings의 BaseSettings 사용
- Import 순서: stdlib → third-party → local (ruff가 자동 정렬)
```

---

## 9. 참고 - Pipeline Stage ↔ 코드 매핑 요약

| Stage | 이름 | 서비스 | Agent | 라우터 | 스키마 |
|-------|------|--------|-------|--------|--------|
| 1 | 사용자 입력 | `input_service.py` | - | `input.py` | `input_schema.py` |
| 2 | 입력 정규화 | `input_service.py` | - | `input.py` | `input_schema.py` |
| 3 | 경로 생성 | `route_service.py` | - | `route.py` | `route_schema.py` |
| 4 | 주변 탐색 | `poi_service.py` | - | `poi.py` | `poi_schema.py` |
| 5 | LLM 패키지 | `package_service.py` | `curator` `storyteller` `validator` | `package.py` | `package_schema.py` |
| 6 | 출력 | `output_service.py` | - | `output.py` | `package_schema.py` |
| 7 | 피드백 | `feedback_service.py` | - | `feedback.py` | `feedback_schema.py` |
