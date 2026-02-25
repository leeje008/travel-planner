"""app.pages.02_result - 결과 페이지.

정규화된 입력 결과 표시. 지도/타임라인은 후속 구현.
"""

import pandas as pd
import streamlit as st

st.header("정규화 결과")

if "clean_input" not in st.session_state:
    st.info("아직 결과가 없습니다. '입력' 페이지에서 먼저 일정을 생성하세요.")
    st.stop()

result = st.session_state["clean_input"]

# 경고 메시지 표시
if result.get("warnings"):
    st.subheader("경고 사항")
    for w in result["warnings"]:
        st.warning(w)

# 관광지 목록 테이블
st.subheader("관광지 목록")
spots_data = []
for spot in result["spots"]:
    spots_data.append(
        {
            "Place ID": spot["place_id"],
            "이름": spot["name"],
            "위도": spot["latitude"],
            "경도": spot["longitude"],
            "신뢰도": f"{spot['confidence']:.0%}",
        }
    )

if spots_data:
    df = pd.DataFrame(spots_data)
    st.dataframe(df, use_container_width=True)

# 여행 정보 요약
st.subheader("여행 정보")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("이동수단", result.get("transport", "-"))
with col2:
    st.metric("여행 일수", f"{len(result.get('dates', []))}일")
with col3:
    st.metric("관광지 수", f"{len(result.get('spots', []))}곳")

# 출발지 / 도착지
dep = result.get("departure", {})
arr = result.get("arrival", {})
st.markdown(
    f"**출발지**: ({dep.get('latitude', 0)}, {dep.get('longitude', 0)}) · "
    f"**도착지**: ({arr.get('latitude', 0)}, {arr.get('longitude', 0)})"
)

# 선호 설정
prefs = result.get("preferences", {})
if prefs:
    st.subheader("선호 설정")
    st.json(prefs)

# 원본 JSON 확인
with st.expander("원본 JSON 응답"):
    st.json(result)

# 원본 요청 확인
if "raw_input" in st.session_state:
    with st.expander("원본 요청 데이터"):
        st.json(st.session_state["raw_input"])
