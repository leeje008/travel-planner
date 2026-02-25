"""api.dependencies - FastAPI 의존성 주입.

DB 세션, 외부 API 클라이언트 등의 의존성을 정의합니다.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from api.db.database import async_session_maker


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """트랜잭션 관리 DB 세션을 제공합니다.

    정상 완료 시 자동 commit, 예외 발생 시 자동 rollback.
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
