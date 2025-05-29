import streamlit as st  # Streamlit 라이브러리 불러오기

# 페이지 설정: 제목과 아이콘 지정 (사이드바 숨김 포함 가능)
st.set_page_config(
    page_title="Welcome!",  # 브라우저 탭 제목
    page_icon="🤖"          # 탭에 표시될 아이콘
)

# 앱을 실행하면 자동으로 로그인 페이지로 이동
st.switch_page("pages/0_sign_in.py")