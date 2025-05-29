import streamlit as st
import json
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import FewShotChatMessagePromptTemplate
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_chroma import Chroma
load_dotenv()

st.set_page_config(
    page_title="This is Mainchat",
)

DATA_DIR = Path("data")
USER_PROFILE_PATH = DATA_DIR / "user_profiles.json"

def load_user_profile(user_id):
    with open(USER_PROFILE_PATH, "r", encoding="utf-8") as f:
        profiles = json.load(f)
        return profiles["users"][user_id]

def create_chain(user_profile):
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"""You are a friendly AI friend helping a student practice English conversation.
        The student's profile:
        - Age: {user_profile['age']}
        - Language Level: {user_profile['language_level']}
        
        Your role is to:
        1. Respond in a way appropriate for the student's age and language level
        2. Keep the conversation engaging and natural
        3. Provide gentle corrections if needed
        4. Be supportive and encouraging
        5. At the end of the conversation, please add a suitable emoji that matches the tone of the chat.""" ),
        ("human", "{question}")
    ])
    
    llm = ChatOpenAI(model_name="gpt-4", temperature=0.7)
    output_parser = StrOutputParser()
    return prompt | llm | output_parser


CHAT_LOG_PATH = DATA_DIR / "chat_logs.json"

def load_all_chat_logs():
    if CHAT_LOG_PATH.exists():
        with open(CHAT_LOG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        # 없을 경우 기본 구조 반환
        return {"users": {}}

def load_chat_log(user_id):
    all_logs = load_all_chat_logs()
    return all_logs["users"].get(user_id, None)

def save_chat_log(user_id, new_message):
    all_logs = load_all_chat_logs()
    existing = all_logs["users"].get(user_id, [])
    all_logs["users"][user_id] = existing + new_message

    with open(CHAT_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(all_logs, f, ensure_ascii=False, indent=2)

chroma = Chroma("fewshot_chat", OpenAIEmbeddings())

def create_chain_with_examples(user_profile, user_id):
    raw_examples = load_chat_log(user_id) or []

    examples = []
    for i in range(len(raw_examples) - 1):
        if raw_examples[i]["role"] == "human" and raw_examples[i + 1]["role"] == "assistant":
            examples.append({
                "input": raw_examples[i]["content"],
                "answer": raw_examples[i + 1]["content"]
            })

    example_prompt = ChatPromptTemplate.from_messages([
        ("human", "{input}"),
        ("ai", "{answer}")
    ])

    example_selector = SemanticSimilarityExampleSelector.from_examples(
        examples,               
        OpenAIEmbeddings(),     
        chroma,                 
        k=1                     
    )

    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_selector=example_selector,
        example_prompt=example_prompt,
        input_variables=["question"]
    )

    # selected = example_selector.select_examples({"question": "I want to be better"})
    # print(selected)

    full_prompt = ChatPromptTemplate.from_messages([
        ("system", f"""You are a friendly AI friend helping a student practice English conversation.
        The student's profile:
        - Age: {user_profile['age']}
        - Language Level: {user_profile['language_level']}

        Your role is to:
        1. Respond in a way appropriate for the student's age and language level
        2. Keep the conversation engaging and natural
        3. Provide gentle corrections if needed
        4. Be supportive and encouraging
        5. At the end of the conversation, please add a suitable emoji that matches the tone of the chat.
        """),        
    ]) + few_shot_prompt + ChatPromptTemplate.from_messages([
        ("human", "{question}")
    ])

    llm = ChatOpenAI(model_name="gpt-4", temperature=0.7)
    output_parser = StrOutputParser()

    return full_prompt | llm | output_parser

def main():
    if "user_id" not in st.session_state or not st.session_state.user_id:
        st.switch_page("main.py")
        return

    user_profile = load_user_profile(st.session_state.user_id)
    
    st.title(f"Welcome, {st.session_state.user_id} 🙂")
    st.markdown("---")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "What can I do help you? 🤔"
            }
        ]
    
    for message in st.session_state.messages:
        st.chat_message(message["role"]).write(message["content"])

    if prompt := st.chat_input("Type your message here..."):
        st.chat_message("user").write(prompt)

        st.session_state.messages.append({"role": "human", "content": prompt})
        
        raw_examples = load_chat_log(st.session_state.user_id) or []

        if len(raw_examples) <= 0:
            chain = create_chain(user_profile)
        else:
            chain = create_chain_with_examples(user_profile, st.session_state.user_id)
        
        context = {
            # "question": prompt
            # 이전까지의 두 쌍의 대화를 참조하도록 프롬프트 변경
            "question": f"Previous conversation: {st.session_state.messages[-4:]}\nUser's response: {prompt}\nPlease respond naturally and ask a follow-up question."
        }
        
        response = chain.invoke(context)
        
        st.session_state.messages.append({"role": "assistant", "content": response})

        save_chat_log(st.session_state.user_id, st.session_state.messages[-2:])

        st.rerun()

if __name__ == "__main__":
    main()