"""api.routers.input - POST /api/v1/plan/input 엔드포인트.

사용자 입력 수신 + Stage 1-2 처리 (파싱, 정규화, 검증).
"""

from fastapi import APIRouter

from api.schemas.input_schema import CleanInput, InputRequest
from api.services.input_service import parse_and_normalize

router = APIRouter(prefix="/plan", tags=["plan"])


@router.post("/input", response_model=CleanInput)
async def plan_input(request: InputRequest):
    """사용자 입력을 파싱하고 정규화된 CleanInput을 반환합니다."""
    return await parse_and_normalize(request)
