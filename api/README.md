# API Layer

FastAPI 기반 핵심 비즈니스 로직 서버입니다.

## 7-Stage Pipeline

| Stage | 서비스 | 엔드포인트 |
|-------|--------|-----------|
| 1-2 | `input_service.py` | `POST /api/v1/plan/input` |
| 3 | `route_service.py` | `POST /api/v1/plan/route` |
| 4 | `poi_service.py` | `POST /api/v1/plan/poi` |
| 5 | `package_service.py` | `POST /api/v1/plan/package` |
| 6 | `output_service.py` | `GET /api/v1/plan/{plan_id}` |
| 7 | `feedback_service.py` | `POST /api/v1/plan/{plan_id}/feedback` |

## 실행

```bash
uvicorn api.main:app --reload
```
