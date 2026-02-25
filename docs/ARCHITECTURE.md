# AI Travel Planner - 프로젝트 아키텍처

> **작성일**: 2026-02-18
> **현재 단계**: Phase 1 - MVP (스캐폴딩)
> **목적**: 팀원 간 프로젝트 구조 및 설계 공유

---

## 1. 프로젝트 개요

사용자가 관광지 목록을 입력하면 **최적 동선 산출 → 주변 POI 탐색 → LLM Agent 패키지 편집 → 지도/타임테이블 출력**까지 수행하는 AI 여행 플래너입니다. 현재 **Phase 1 (MVP 스캐폴딩)** 단계이며, 대부분의 파일은 docstring 수준의 스텁 상태이고 `core/` 모듈만 실 구현이 완료되어 있습니다.

---

## 2. 기술 스택

| 영역 | 기술 | 비고 |
|------|------|------|
| Language | Python 3.11+ | |
| Web Framework | FastAPI + Uvicorn | API 서버 |
| Frontend (MVP) | Streamlit + Folium | Phase 2에서 React 전환 |
| LLM | LangChain + LangGraph | gpt-4o-mini (MVP), claude-sonnet |
| DB | PostgreSQL 16 + PGVector | 메인 DB + 벡터 검색 |
| Cache | Redis 7 | POI/경로 캐싱 |
| 경로 최적화 | Google OR-Tools | TSP/VRP |
| 외부 API | Google Maps Platform, Kakao Local | Geocoding, Places, Directions |
| HTTP Client | httpx | async 지원 |
| Container | Docker Compose | 로컬 개발 환경 |

---

## 3. 폴더 구조

```
project/
├── CLAUDE.md
├── PROJECT_SPEC.md                       # 단일 진실 공급원 (설계 문서)
├── ARCHITECTURE.md                       # 이 문서
├── AI_Travel_Planner_기술아키텍처_상세분석서.docx
│
└── travel-planner/                       # 메인 애플리케이션
    ├── pyproject.toml                    # 의존성 (hatchling 빌드)
    ├── docker-compose.yml                # PostgreSQL + Redis
    ├── .env.example                      # 환경변수 템플릿
    ├── alembic.ini + alembic/            # DB 마이그레이션
    │
    ├── core/          ← 공유 모듈 (구현 완료)
    ├── etl/           ← ETL 배치 레이어 (스텁)
    ├── api/           ← API 백엔드 레이어 (스텁)
    ├── app/           ← 프론트엔드 레이어 (스텁)
    └── tests/         ← 테스트 (스텁)
```

---

## 4. 레이어별 상세 구조

### 4.1 `core/` - 공유 모듈 (구현 완료)

모든 레이어가 공통으로 사용하는 상수, 예외, 유틸리티.

```
core/
├── constants.py        # StrEnum (POICategory, TransportMode 등)
│                       # 검색 반경, 체류시간, 식사시간대, 캐시 TTL, 랭킹 가중치
├── exceptions.py       # TravelPlannerError 계층 (7개 커스텀 예외)
├── logging_config.py   # 로깅 설정
└── utils/
    ├── geo.py          # 좌표 계산 (Haversine 등)
    ├── time_utils.py   # 시간 파싱/변환
    └── text.py         # 텍스트 정규화
```

**예외 계층:**

```
TravelPlannerError (최상위)
├── InvalidInputError        # 입력 검증
├── PlaceNotFoundError       # 장소 미발견
├── RouteOptimizationError   # 경로 최적화 실패
├── ExternalAPIError         # 외부 API 실패 (service, status_code 포함)
├── LLMResponseError         # LLM 응답 파싱 실패
├── PackageValidationError   # 패키지 검증 실패 (issues 리스트)
├── CacheError               # 캐시 연산 실패
└── DatabaseError            # DB 연산 실패
```

---

### 4.2 `etl/` - ETL 배치 레이어

외부 데이터를 수집/가공하여 DB에 적재하는 오프라인 파이프라인.

```
etl/
├── poi_collector.py         # Google/Kakao API → POI 테이블 적재
├── review_collector.py      # 리뷰 수집 + LLM 요약
├── embedding_builder.py     # POI 텍스트 → 벡터 임베딩 (PGVector)
├── place_cache_updater.py   # 영업시간/폐업 여부 갱신
└── scripts/
    ├── seed_sample_data.py  # 개발용 샘플 시딩
    └── run_etl_pipeline.py  # 파이프라인 실행 진입점
```

---

### 4.3 `api/` - API 백엔드 레이어 (핵심)

7-Stage 파이프라인을 처리하는 FastAPI 서버. **Router → Service → Agent/External/DB** 3계층 구조.

```
api/
├── main.py              # FastAPI app 진입점
├── config.py            # pydantic-settings 환경변수 관리
├── dependencies.py      # FastAPI DI (세션, 클라이언트 등)
│
├── routers/             # 엔드포인트 정의
│   ├── input.py         # POST /api/v1/plan/input
│   ├── route.py         # POST /api/v1/plan/route
│   ├── poi.py           # POST /api/v1/plan/poi
│   ├── package.py       # POST /api/v1/plan/package
│   ├── output.py        # GET  /api/v1/plan/{plan_id}
│   └── feedback.py      # POST /api/v1/plan/{plan_id}/feedback
│
├── schemas/             # Pydantic Request/Response 모델
│   ├── input_schema.py  # InputRequest, CleanInput, Preferences
│   ├── route_schema.py  # RoutePlan, DayRoute, RouteStop
│   ├── poi_schema.py    # CandidatePOI
│   ├── package_schema.py # TravelPackage, PackageDay, PackageStop
│   └── feedback_schema.py
│
├── services/            # 비즈니스 로직 (Stage별)
│   ├── input_service.py     # Stage 1-2: 입력 파싱 + 정규화
│   ├── route_service.py     # Stage 3: OR-Tools TSP 최적화
│   ├── poi_service.py       # Stage 4: 반경/경로 기반 POI 탐색 + 랭킹
│   ├── package_service.py   # Stage 5: LLM Agent 오케스트레이션
│   ├── output_service.py    # Stage 6: 최종 출력 포맷팅
│   └── feedback_service.py  # Stage 7: 피드백 수집
│
├── agents/              # LLM Agent (LangGraph)
│   ├── state.py         # PlannerState (TypedDict 공유 상태)
│   ├── graph.py         # StateGraph: Curate → Validate → Storytell → Format
│   ├── curator.py       # POI 선별 + 슬롯 배치
│   ├── storyteller.py   # 스토리/추천멘트 생성 (RAG)
│   ├── validator.py     # 규칙 기반 검증 (시간충돌, 영업시간 등)
│   └── prompts/         # 각 Agent 프롬프트 템플릿
│       ├── curator.py
│       ├── storyteller.py
│       └── validator.py
│
├── external/            # 외부 API 클라이언트
│   ├── base_client.py       # httpx AsyncClient + Redis 캐싱 베이스
│   ├── google_places.py     # 장소 검색, 주변 검색, 상세 조회
│   ├── google_directions.py # 경로/이동시간 조회
│   ├── google_geocoding.py  # 주소 ↔ 좌표 변환
│   └── kakao_local.py       # Kakao Local API
│
└── db/                  # 데이터베이스
    ├── database.py      # SQLAlchemy async engine/session
    ├── models.py        # ORM: POI, POIEmbedding, TravelPlan, Feedback
    └── repositories/    # CRUD 레포지토리
        ├── poi_repo.py
        ├── plan_repo.py
        └── feedback_repo.py
```

---

### 4.4 `app/` - 프론트엔드 (Streamlit MVP)

```
app/
├── streamlit_app.py     # 메인 앱
├── pages/
│   ├── 01_input.py      # 관광지 입력 + 조건 설정
│   ├── 02_result.py     # 지도(folium) + 타임테이블 + 추천카드
│   └── 03_feedback.py   # 별점, 좋아요/제외, 의견
└── components/
    ├── map_renderer.py  # Folium 지도 렌더링
    ├── timeline.py      # 타임라인 컴포넌트
    └── place_card.py    # 장소 추천카드
```

---

### 4.5 `tests/` - 테스트

```
tests/
├── conftest.py              # pytest fixtures
├── test_etl/                # ETL 단위 테스트
├── test_api/
│   ├── test_services/       # 서비스 레이어 테스트
│   ├── test_agents/         # LLM Agent 테스트
│   └── test_routers/        # API 엔드포인트 테스트
└── test_app/                # 프론트엔드 테스트
```

---

## 5. 데이터 흐름 (7-Stage Pipeline)

```
[사용자 입력]
     │
     ▼ Stage 1-2: input_service
  입력 파싱 → Place ID 매핑 → 좌표 검증 → CleanInput
     │
     ▼ Stage 3: route_service
  Distance Matrix → OR-Tools TSP → RoutePlan (최적 방문 순서)
     │
     ▼ Stage 4: poi_service
  Radial Search(반경) + Route-corridor → 필터 → 랭킹 → CandidatePOI[]
     │
     ▼ Stage 5: package_service → LangGraph Agent Pipeline
  ┌─────────────────────────────────────────────────┐
  │  Curator ──→ Validator ──→ Storyteller ──→ Format│
  │    (선별)   ↙ (실패시 재시도)   (스토리)   (출력) │
  │           ←──┘ (max 2회)                        │
  └─────────────────────────────────────────────────┘
     │
     ▼ Stage 6: output_service
  TravelPackage (JSON) → 지도 + 타임테이블 + 추천카드
     │
     ▼ Stage 7: feedback_service
  별점 + 클릭 로그 + 제외 사유 수집 → DB 저장
```

---

## 6. LLM Agent 파이프라인 상세

### Agent 흐름 (LangGraph StateGraph)

```
[Entry] → Curate → Validate ─── pass ──→ Storytell → Format Output → [END]
                      │                        ▲
                      └── fail (retry < 2) ────┘
                      └── max_retry ──────────→ [END]
```

| Agent | 역할 | 방식 |
|-------|------|------|
| **Curator** | 후보 POI 선별 + 시간대별 슬롯 배치 | Rule-based 필터 + LLM 최종 선별 |
| **Validator** | 일정 논리 검증 (시간충돌, 영업시간, 동선, 예산, 중복) | 순수 Rule-based (LLM 미사용) |
| **Storyteller** | 하루 코스 스토리라인 + POI별 추천 이유 생성 | RAG 컨텍스트 + LLM |

### 공유 상태 (PlannerState)

```python
PlannerState = {
    # 입력
    "user_preferences": dict,
    "route_plan": dict,
    "candidate_pois": list[dict],
    # Agent 출력
    "curated_schedule": dict | None,
    "validation_result": dict | None,
    "story_content": dict | None,
    "final_package": dict | None,
    # 제어
    "errors": list[str],
    "retry_count": int,
    "messages": list,
}
```

---

## 7. 인프라 구성

```
┌──────────────────────────────────────────────────┐
│                 Docker Compose                    │
│                                                   │
│  ┌───────────────────┐  ┌──────────────────────┐ │
│  │ PostgreSQL 16      │  │ Redis 7              │ │
│  │ + PGVector         │  │ (캐시/세션)          │ │
│  │ :5432              │  │ :6379                │ │
│  └─────────┬─────────┘  └──────────┬───────────┘ │
└────────────┼───────────────────────┼─────────────┘
             │                       │
      ┌──────┴──────┐        ┌──────┴──────┐
      │  FastAPI    │────────│ Redis Cache  │
      │  (Uvicorn)  │        └─────────────┘
      └──────┬──────┘
             │
      ┌──────┴──────┐
      │  Streamlit  │
      │  Frontend   │
      └─────────────┘

외부 연동:
  ├── Google Maps Platform (Places, Directions, Geocoding)
  ├── Kakao Local API
  └── OpenAI / Anthropic LLM API
```

---

## 8. API 엔드포인트 명세

| Method | Endpoint | Stage | 설명 |
|--------|----------|-------|------|
| `POST` | `/api/v1/plan/input` | 1-2 | 사용자 입력 수신 + 파싱/정규화/검증 |
| `POST` | `/api/v1/plan/route` | 3 | 최적 경로 생성 (TSP) |
| `POST` | `/api/v1/plan/poi` | 4 | 주변 POI 탐색 + 랭킹 |
| `POST` | `/api/v1/plan/package` | 5 | LLM 패키지 구성 |
| `GET`  | `/api/v1/plan/package/stream/{task_id}` | 5 | SSE 스트리밍 |
| `GET`  | `/api/v1/plan/{plan_id}` | 6 | 최종 결과 조회 |
| `POST` | `/api/v1/plan/{plan_id}/feedback` | 7 | 피드백 수신 |
| `POST` | `/api/v1/plan/generate` | 1-5 | **통합 엔드포인트** (일괄 실행, SSE) |

---

## 9. DB 모델 (ERD 요약)

```
┌─────────────┐     ┌──────────────────┐     ┌──────────────┐
│     POI      │     │   TravelPlan     │     │   Feedback   │
├─────────────┤     ├──────────────────┤     ├──────────────┤
│ id (PK)     │     │ id (PK)          │     │ id (PK)      │
│ place_id    │     │ user_session_id   │     │ plan_id (FK) │──→ TravelPlan
│ name        │     │ input_data (JSON) │     │ overall_rating│
│ category    │     │ clean_input (JSON)│     │ poi_clicks   │
│ lat / lng   │     │ route_plan (JSON) │     │ poi_saves    │
│ rating      │     │ candidate_pois   │     │ poi_excludes │
│ review_count│     │ package (JSON)    │     │ comment      │
│ price_level │     │ status           │     │ created_at   │
│ opening_hours│    │ created_at       │     └──────────────┘
│ is_active   │     └──────────────────┘
└──────┬──────┘
       │ 1:1
┌──────┴──────┐
│ POIEmbedding │
├─────────────┤
│ id (PK)     │
│ poi_id (FK) │
│ content     │
│ embedding   │  ← Vector(1536), PGVector
│ metadata    │
└─────────────┘
```

---

## 10. 현재 구현 상태

| 모듈 | 상태 | 비고 |
|------|------|------|
| `core/constants.py` | **구현 완료** | Enum, 상수값 정의됨 |
| `core/exceptions.py` | **구현 완료** | 7개 커스텀 예외 계층 |
| `core/utils/` | 스텁 | docstring만 존재 |
| `core/logging_config.py` | 스텁 | docstring만 존재 |
| `api/main.py` | 스텁 | FastAPI app 미구현 |
| `api/config.py` | 스텁 | BaseSettings 미구현 |
| `api/db/models.py` | 스텁 | ORM 모델 미구현 |
| `api/db/database.py` | 스텁 | engine/session 미구현 |
| `api/agents/` | 스텁 | LangGraph 미구현 |
| `api/routers/` | 스텁 | 엔드포인트 미구현 |
| `api/schemas/` | 스텁 | Pydantic 모델 미구현 |
| `api/services/` | 스텁 | 비즈니스 로직 미구현 |
| `api/external/` | 스텁 | API 클라이언트 미구현 |
| `etl/` | 스텁 | ETL 파이프라인 미구현 |
| `app/` | 스텁 | Streamlit UI 미구현 |
| `tests/` | 스텁 | conftest + `__init__.py`만 존재 |
| `docker-compose.yml` | **구현 완료** | PGVector + Redis 정의 |
| `pyproject.toml` | **구현 완료** | 전체 의존성 정의 |
| `alembic/` | **부분 구현** | 설정만 존재, 마이그레이션 없음 |

---

## 11. 다음 구현 단계 (Phase 1 로드맵)

```
Step 1: [완료] 프로젝트 초기화 - 폴더 구조, pyproject.toml, docker-compose, core/
Step 2: [다음] DB 설정 - SQLAlchemy 모델 구현, Alembic 마이그레이션
Step 3: 외부 API 클라이언트 - base_client, google_places, directions, geocoding
Step 4: 서비스 레이어 (Stage 1~4) - input, route, poi
Step 5: LLM Agent (Stage 5) - LangGraph 파이프라인
Step 6: API 라우터 - FastAPI 엔드포인트 연결
Step 7: Streamlit MVP - 입력 → API 호출 → 결과 렌더링
```

### Phase 1에서 스킵 항목

- Multi-day 분할 알고리즘 (1일 여행만 지원)
- Route-corridor Search (Radial Search만)
- RAG (직접 컨텍스트 주입으로 대체)
- PDF 내보내기, 피드백 학습, Celery 비동기, A/B 테스트
