"""app.streamlit_app - Streamlit 메인 앱.

Usage::

    streamlit run app/streamlit_app.py
"""

import streamlit as st

st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("AI Travel Planner")
st.markdown("관광지를 입력하면 최적 동선과 주변 POI를 추천합니다.")

# 사이드바: API 서버 설정
st.sidebar.header("설정")
api_url = st.sidebar.text_input("API Server URL", value="http://localhost:8000")
st.session_state["api_url"] = api_url

# 서버 상태 확인
if st.sidebar.button("서버 연결 확인"):
    import httpx

    try:
        resp = httpx.get(f"{api_url}/health", timeout=5.0)
        if resp.status_code == 200:
            st.sidebar.success("서버 연결 성공")
        else:
            st.sidebar.error(f"서버 응답 오류: {resp.status_code}")
    except httpx.ConnectError:
        st.sidebar.error("서버에 연결할 수 없습니다")
    except Exception as e:
        st.sidebar.error(f"오류: {e}")

st.markdown("---")
st.markdown("👈 왼쪽 사이드바에서 페이지를 선택하세요.")
st.markdown(
    """
### 사용 방법
1. **입력 페이지**: 관광지, 날짜, 이동수단 등을 입력합니다
2. **결과 페이지**: 정규화된 입력 결과를 확인합니다

### API 엔드포인트
- `GET /health` — 서버 상태 확인
- `POST /api/v1/plan/input` — 입력 정규화
- `GET /docs` — Swagger UI (API 문서)
"""
)
