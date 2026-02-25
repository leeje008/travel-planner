# AI Travel Planner

AI 기반 여행 일정 최적화 및 POI 추천 시스템입니다.

## 주요 기능

- **최적 동선 산출**: Google OR-Tools 기반 TSP 경로 최적화
- **주변 POI 탐색**: 경로 주변 카페/맛집 등 자동 탐색 및 랭킹
- **LLM Agent 패키지**: LangGraph 기반 스토리텔링 + 추천 이유 생성
- **지도/타임테이블**: Folium 지도 + 타임라인 시각화
- **피드백 수집**: 사용자 피드백으로 추천 품질 개선

## 기술 스택

| 분류 | 기술 | 버전 |
|------|------|------|
| Language | Python | 3.11+ |
| Framework | FastAPI | 0.133.0 |
| Server | Uvicorn / Gunicorn | 0.41.0 / 25.1.0 |
| Database | PostgreSQL 16 (PGVector) | pgvector 0.4.2 |
| ORM | SQLAlchemy (async) | 2.0.47 |
| DB Driver | asyncpg | 0.31.0 |
| Migration | Alembic | 1.18.4 |
| Cache | Redis | 7.2.0 |
| LLM | LangChain + LangGraph | 1.2.10 / 1.0.9 |
| LLM Provider | OpenAI / Anthropic | langchain-openai 1.1.10 |
| Routing | Google OR-Tools | 9.15.6755 |
| HTTP Client | httpx | 0.28.1 |
| Validation | Pydantic | 2.12.5 |
| Geo | Shapely / Polyline | 2.1.2 / 2.0.4 |
| Frontend (MVP) | Streamlit + Folium | 1.54.0 / 0.20.0 |
| Package Manager | uv | - |
| Container | Docker + docker-compose | - |

## 프로젝트 구조

```
travel-planner/
├── api/                    # FastAPI 백엔드 (핵심)
│   ├── routers/            # API 엔드포인트 정의
│   ├── schemas/            # Pydantic Request/Response 모델
│   ├── services/           # 비즈니스 로직 (7-Stage Pipeline)
│   ├── agents/             # LLM Agent (LangGraph)
│   │   └── prompts/        # 프롬프트 템플릿
│   ├── external/           # 외부 API 클라이언트
│   └── db/                 # 데이터베이스 (ORM, Repository)
├── app/                    # Streamlit 프론트엔드
│   ├── pages/              # 입력 / 결과 / 피드백 페이지
│   └── components/         # 지도, 타임라인, 추천카드
├── core/                   # 공유 모듈
│   ├── constants.py        # Enum, 상수
│   ├── exceptions.py       # 커스텀 예외 계층
│   └── utils/              # 좌표계산, 시간, 텍스트 유틸
├── etl/                    # ETL 배치 파이프라인
│   └── scripts/            # 시딩, 파이프라인 실행
├── tests/                  # 테스트
├── docs/                   # 설계 문서
│   ├── PROJECT_SPEC.md     # 기술 명세서
│   └── ARCHITECTURE.md     # 아키텍처 문서
└── alembic/                # DB 마이그레이션
```

## 시작하기

### 환경 설정

```bash
# 가상환경 생성 및 활성화
uv venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 의존성 설치
uv sync
```

### 환경 변수

`.env.example`을 참고하여 `.env` 파일을 생성합니다:

```bash
cp .env.example .env
```

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/travel_planner
REDIS_URL=redis://localhost:6379/0

# External APIs
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
KAKAO_REST_API_KEY=your_kakao_rest_api_key

# LLM
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.3
```

### 인프라 실행

```bash
docker-compose up -d
```

PostgreSQL 16 (PGVector) + Redis 7 + API 서버가 실행됩니다.

### DB 마이그레이션

```bash
alembic upgrade head
```

### API 서버 실행 (로컬 개발)

```bash
uv run uvicorn api.main:app --reload
```

서버가 `http://localhost:8000`에서 실행됩니다.

### Streamlit 앱 실행

```bash
uv run streamlit run app/streamlit_app.py
```

## MVP 테스트 워크플로우

기능 변경 후 3가지 방법으로 테스트할 수 있습니다.

### 1. pytest 자동 테스트

DB/외부 API 없이 바로 실행 가능합니다.

```bash
# 전체 테스트 실행
uv run pytest -v

# 특정 모듈만
uv run pytest tests/test_api/test_routers/test_input.py -v

# 커버리지 포함
uv run pytest --cov=api tests/
```

### 2. Swagger UI (API 직접 테스트)

```bash
# API 서버 실행
uv run uvicorn api.main:app --reload --port 8000
```

브라우저에서 `http://localhost:8000/docs`를 열면 Swagger UI에서 각 엔드포인트를 직접 테스트할 수 있습니다.

**테스트 예시** — `POST /api/v1/plan/input`:
```json
{
  "spots": [{"name": "경복궁"}, {"name": "남산타워"}],
  "departure": "서울역",
  "dates": ["2026-03-01", "2026-03-02"],
  "transport": "transit",
  "preferences": {
    "categories": ["cafe", "restaurant"],
    "companion": "couple"
  }
}
```

### 3. Streamlit MVP (시각적 테스트)

API 서버가 실행 중인 상태에서:

```bash
# Streamlit 앱 실행
uv run streamlit run app/streamlit_app.py
```

`http://localhost:8501`에서 입력 폼을 통해 API를 호출하고 결과를 시각적으로 확인할 수 있습니다.

| 페이지 | 기능 |
|--------|------|
| 메인 | 서버 연결 확인, 사용법 안내 |
| 입력 | 관광지/날짜/이동수단/선호 입력 → API 호출 |
| 결과 | 정규화된 관광지 테이블, 경고 사항, JSON 응답 확인 |

### 개발 흐름 요약

```
코드 수정 → pytest 자동 테스트 → 서버 실행 → Swagger/Streamlit 확인
```

```bash
# 1. 테스트 실행
uv run pytest -v

# 2. 서버 실행 (터미널 1)
uv run uvicorn api.main:app --reload --port 8000

# 3. Streamlit 실행 (터미널 2)
uv run streamlit run app/streamlit_app.py
```

## 개발

### 코드 품질

```bash
# 린트 검사
uv run ruff check api/ core/ etl/ app/

# 린트 자동 수정
uv run ruff check --fix api/ core/ etl/ app/

# 포맷팅
uv run ruff format api/ core/ etl/ app/
```

### 의존성 관리

```bash
# 의존성 추가
uv add package-name

# 개발 의존성 추가
uv add --group dev package-name

# 동기화
uv sync
```

## Docker

```bash
# 빌드
docker build -t travel-planner .

# 실행
docker run -p 8000:8000 travel-planner

# docker-compose (DB + Redis + API)
docker-compose up -d
```

## API 엔드포인트

### 7-Stage Pipeline

| Method | Endpoint | Stage | 설명 |
|--------|----------|-------|------|
| `POST` | `/api/v1/plan/input` | 1-2 | 사용자 입력 수신 + 파싱/정규화 |
| `POST` | `/api/v1/plan/route` | 3 | 최적 경로 생성 (TSP) |
| `POST` | `/api/v1/plan/poi` | 4 | 주변 POI 탐색 + 랭킹 |
| `POST` | `/api/v1/plan/package` | 5 | LLM 패키지 구성 |
| `GET` | `/api/v1/plan/{plan_id}` | 6 | 최종 결과 조회 |
| `POST` | `/api/v1/plan/{plan_id}/feedback` | 7 | 피드백 수신 |

### 아키텍처

```
Router (API Endpoint)
    ↓
Service (비즈니스 로직)
    ↓ Stage 5
Agent (LangGraph: Curator → Validator → Storyteller)
    ↓
Repository (데이터 접근)
    ↓
Database
```

## 라이선스

MIT
