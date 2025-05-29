import streamlit as st
import json
from pathlib import Path

st.set_page_config(
    page_title="Sign Up",
    page_icon="🤖",
)

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

USER_PROFILE_PATH = DATA_DIR / "user_profiles.json"

def init_user_profiles():
    if not USER_PROFILE_PATH.exists():
        with open(USER_PROFILE_PATH, "w", encoding="utf-8") as f:
            json.dump({"users": {}}, f, ensure_ascii=False, indent=4) 

def load_user_profiles():
    if USER_PROFILE_PATH.exists():
        with open(USER_PROFILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"users": {}}

def save_user_profile(user_id, profile_data):
    profiles = load_user_profiles()
    profiles["users"][user_id] = profile_data

    with open(USER_PROFILE_PATH, "w", encoding="utf-8") as f:
        json.dump(profiles, f, ensure_ascii=False, indent=4)

def main():
    with st.form("signup_form"):
        st.header("Create Your Account")
        
        id = st.text_input("ID")
        pw = st.text_input("Password", type="password")
        confirm_pw = st.text_input("Confirm Password", type="password")
        nationality = st.text_input("Nationality")
        age = st.number_input("Age", min_value=1, max_value=100, step=1, value=12)
        sex = st.selectbox("Sex", ["Male", "Female"])
        language_level = st.selectbox(
            "Language Level",
            ["Beginner", "Intermediate", "Advanced"]
        )

        col1, col2 = st.columns(2)
        with col1:
            signup_submitted = st.form_submit_button("Sign Up")
        with col2:
            if st.form_submit_button("Back to Login"):
                st.switch_page("main.py")

        # 'Sign Up' 버튼이 눌렸을 때 실행
        if signup_submitted:
            # 모든 입력값이 채워졌는지 확인
            if not all([id, pw, confirm_pw, nationality, age, sex, language_level]):
                st.error("Please fill in all required fields.")  # 하나라도 비었으면 에러 표시
            # 비밀번호와 비밀번호 확인이 일치하는지 확인
            elif pw != confirm_pw:
                st.error("Passwords do not match.")  # 비밀번호 불일치 시 에러 표시
            else:
                profiles = load_user_profiles()  # 기존 사용자 정보 불러오기

                # 이미 존재하는 ID인지 확인
                if id in profiles["users"]:
                    st.error("This ID is already taken.")  # 중복 ID 에러 표시
                else:
                    # 사용자 정보를 딕셔너리로 정리
                    profile_data = {
                        "id": id,
                        "pw": pw,
                        "nationality": nationality,
                        "age": age,
                        "sex": sex,
                        "language_level": language_level
                    }

                    # 사용자 정보 저장
                    save_user_profile(id, profile_data)

                    # 성공 메시지 표시 및 세션 상태 설정
                    st.success("Account created successfully!")
                    st.session_state.user_id = id
                    st.session_state.profile_setup = True

                    # 메인 페이지로 이동
                    st.switch_page("main.py")


if __name__ == "__main__":
    init_user_profiles()
    main()