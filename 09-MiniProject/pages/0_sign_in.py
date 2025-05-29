import streamlit as st
import json
from pathlib import Path

# 페이지 설정
st.set_page_config(
    page_title="Sign In",
    page_icon="🤖"
)

# 데이터 저장 경로 설정
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
USER_PROFILE_PATH = DATA_DIR / "user_profiles.json"

def load_user_profiles():
    if USER_PROFILE_PATH.exists():
        with open(USER_PROFILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"users": {}}

# 사용자 인증 함수: ID와 비밀번호가 맞는지 확인
def authenticate_user(username, password):
    profiles = load_user_profiles()  # 저장된 사용자 정보 불러오기

    # 입력한 ID가 사용자 목록에 있는 경우
    if username in profiles["users"]:
        # 해당 ID의 비밀번호가 일치하는지 확인
        if profiles["users"][username]["pw"] == password:
            return True  # 인증 성공

    return False  # 인증 실패

# 메인 페이지
def main():
    st.title("🤖 Welcome!")
    st.markdown("""
    To communicate with BOT, please sign up and sign in first.
    """)

    # 로그인 폼 영역 시작
    with st.form("login_form"):
        st.header("Login")  # 폼 제목 표시

        # 사용자로부터 ID와 비밀번호 입력 받기
        username = st.text_input("ID")
        password = st.text_input("Password", type="password")

        # 로그인 및 회원가입 버튼을 좌우로 나누어 배치
        col1, col2 = st.columns(2)
        with col1:
            login_submitted = st.form_submit_button("Login")  # 로그인 버튼
        with col2:
            # 회원가입 버튼 클릭 시 회원가입 페이지로 이동
            if st.form_submit_button("Sign Up"):
                st.switch_page("pages/1_sign_up.py")

        # 로그인 버튼이 눌렸을 때 실행
        if login_submitted:
            # ID나 비밀번호가 비어있는 경우
            if not username or not password:
                st.error("Please enter both username and password.")  # 입력 누락 에러 표시
            # 입력값이 모두 있고 인증에 성공한 경우
            elif authenticate_user(username, password):
                st.session_state.user_id = username          # 세션에 사용자 ID 저장
                st.session_state.logged_in = True            # 로그인 상태 설정
                st.success("Login successful!")              # 성공 메시지 표시
                st.switch_page("pages/3_main_chat.py")       # 채팅 페이지로 이동
            else:
                # 인증 실패 시 에러 메시지 표시
                st.error("Invalid username or password.\n\nIf you don't have an account, please sign up.")


# 앱 실행
if __name__ == "__main__":
    main() 