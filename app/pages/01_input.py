"""app.pages.01_input - 입력 페이지.

관광지 입력 (텍스트/지도 선택), 조건 설정, 선호 입력 화면.
"""

from datetime import date, timedelta

import httpx
import streamlit as st

st.header("여행 입력")

# API URL
api_url = st.session_state.get("api_url", "http://localhost:8000")

# 관광지 입력
st.subheader("관광지 목록")
spots_text = st.text_area(
    "방문할 관광지를 한 줄에 하나씩 입력하세요 (최소 2개)",
    placeholder="경복궁\n남산타워\n북촌한옥마을",
    height=150,
)

# 출발지 / 도착지
col1, col2 = st.columns(2)
with col1:
    departure = st.text_input("출발지", value="서울역")
with col2:
    arrival = st.text_input("도착지 (비우면 출발지와 동일)", value="")

# 날짜 선택
st.subheader("여행 날짜")
col_start, col_end = st.columns(2)
with col_start:
    start_date = st.date_input("시작일", value=date.today())
with col_end:
    end_date = st.date_input("종료일", value=date.today() + timedelta(days=1))

# 이동수단
transport = st.selectbox(
    "이동수단",
    options=["transit", "walk", "drive"],
    format_func=lambda x: {"transit": "대중교통", "walk": "도보", "drive": "자차"}[x],
)

# 선호 설정
st.subheader("선호 설정")
col_cat, col_comp = st.columns(2)
with col_cat:
    categories = st.multiselect(
        "관심 카테고리",
        options=["cafe", "restaurant", "shopping", "culture", "nature", "nightlife"],
        default=["cafe", "restaurant"],
        format_func=lambda x: {
            "cafe": "카페",
            "restaurant": "맛집",
            "shopping": "쇼핑",
            "culture": "문화/역사",
            "nature": "자연",
            "nightlife": "야경/나이트",
        }[x],
    )
with col_comp:
    companion = st.selectbox(
        "동행 유형",
        options=["solo", "couple", "family", "friends"],
        format_func=lambda x: {
            "solo": "혼자",
            "couple": "커플",
            "family": "가족",
            "friends": "친구",
        }[x],
    )

budget = st.number_input("총 예산 (원, 0이면 무제한)", min_value=0, step=10000, value=0)
meal_preference = st.text_input("식사 선호 (예: 한식, 일식)", value="")

# 일정 생성 버튼
st.markdown("---")
if st.button("일정 생성", type="primary", use_container_width=True):
    # 관광지 파싱
    spot_names = [s.strip() for s in spots_text.strip().split("\n") if s.strip()]

    if len(spot_names) < 2:
        st.error("관광지를 최소 2개 이상 입력해주세요.")
    else:
        # 날짜 목록 생성
        dates = []
        current = start_date
        while current <= end_date:
            dates.append(current.isoformat())
            current += timedelta(days=1)

        # 요청 payload
        payload = {
            "spots": [{"name": name} for name in spot_names],
            "departure": departure,
            "arrival": arrival if arrival else None,
            "dates": dates,
            "transport": transport,
            "preferences": {
                "categories": categories,
                "companion": companion,
                "budget": budget if budget > 0 else None,
                "vibe": [],
                "meal_preference": meal_preference if meal_preference else None,
            },
        }

        with st.spinner("입력을 정규화하는 중..."):
            try:
                resp = httpx.post(
                    f"{api_url}/api/v1/plan/input",
                    json=payload,
                    timeout=30.0,
                )
                if resp.status_code == 200:
                    st.session_state["clean_input"] = resp.json()
                    st.session_state["raw_input"] = payload
                    st.success("입력 정규화 완료! '결과' 페이지에서 확인하세요.")
                else:
                    st.error(f"API 오류 ({resp.status_code}): {resp.text}")
            except httpx.ConnectError:
                st.error(
                    f"서버에 연결할 수 없습니다 ({api_url}). "
                    "서버가 실행 중인지 확인하세요."
                )
            except Exception as e:
                st.error(f"요청 오류: {e}")

# 이전 결과가 있으면 간략히 표시
if "clean_input" in st.session_state:
    st.markdown("---")
    st.info(
        f"마지막 정규화 결과: "
        f"{len(st.session_state['clean_input']['spots'])}개 관광지, "
        f"{len(st.session_state['clean_input']['warnings'])}개 경고"
    )
