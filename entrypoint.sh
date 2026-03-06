#!/bin/sh
set -e

# DB 연결 대기
# Railway는 postgresql:// 형식을 제공하므로 asyncpg/postgres:// 변환 처리
echo "Waiting for database..."
MAX_RETRIES=30
RETRY=0
until python -c "
import psycopg2, os
url = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/travel_planner')
sync_url = url.replace('+asyncpg', '').replace('postgres://', 'postgresql://')
psycopg2.connect(sync_url)
" 2>/dev/null; do
    RETRY=$((RETRY + 1))
    if [ "$RETRY" -ge "$MAX_RETRIES" ]; then
        echo "Database connection failed after $MAX_RETRIES retries."
        exit 1
    fi
    echo "Waiting for database... ($RETRY/$MAX_RETRIES)"
    sleep 1
done
echo "Database ready."

# alembic 마이그레이션 적용
alembic upgrade head

# 애플리케이션 시작
exec "$@"
