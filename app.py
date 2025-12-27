import streamlit as st
from openai import OpenAI
import json
import os
import re

# --- 1. 초기 설정 ---
st.set_page_config(page_title="박보검(양관식)과 대화", layout="wide")

# 깃허브에 올린 이미지의 Raw URL 주소
# (이 주소는 브라우저가 직접 이미지를 불러오기 때문에 절대 경로/상대 경로 오류가 없습니다)
PROFILE_IMAGE_URL = "https://raw.githubusercontent.com/djchany/bogum-chat/main/profile.jpg"

SAVE_DIR = "chat_history"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# API 키 설정
if "OPENROUTER_API_KEY" in st.secrets:
    api_key = st.secrets["OPENROUTER_API_KEY"]
else:
    api_key = st.sidebar.text_input("OpenRouter API Key 입력", type="password")

if not api_key:
    st.info("사이드바에 API Key를 입력하거나 Streamlit Secrets를 설정해주세요.")
    st.stop()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
    default_headers={
        "HTTP-Referer": "https://github.com/djchany/bogum-chat",
        "X-Title": "Bogum Chat"
    }
)

# --- 2. 캐릭터 프롬프트 ---
CHARACTER_PROMPT = """
당신은 드라마 '폭싹 속았수다'의 주인공 '양관식'입니다. 이름은 '박보검'으로 활동합니다.

[절대 규칙]
1. 당신은 오직 '한국어'와 '제주도 방언'으로만 대답합니다. 아랍어, 영어, 한자 등 외국어는 절대 사용하지 마세요.
2. 당신은 남성이며, 상대방은 짝사랑하는 친구 '제우리'입니다.
3. 소설을 쓰지 마세요. 상대방의 대사나 행동을 대신 작성하지 말고, 오직 당신의 반응만 출력하세요.
4. 행동 묘사는 반드시 괄호 ( )를 사용하고 10자 이내로 짧게 하세요.

[캐릭터 특징]
- 1950년대 제주도 소년의 순수함과 성실함.
- 말수가 적고 무뚝뚝하지만 속마음은 따뜻한 일편단심.
- 표준어를 쓰지만 배경이 제주도이므로 아주 가끔 누구나 알만한 제주도 방언을 사용한다.
"""

# --- 3. 유틸리티 함수 ---
def format_chat_text(text):
    # 괄호 지문 스타일링
    formatted = re.sub(
        r'(\s*\([^)]+\)\s*)', 
        r'<span class="action-text">\1</span>', 
        text
    )
    return formatted.replace("\n", "<br>")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_file" not in st.session_state:
    st.session_state.current_file = None

def save_chat(filename):
    if not filename.endswith(".json"): filename += ".json"
    filepath = os.path.join(SAVE_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(st.session_state.messages, f, ensure_ascii=False, indent=4)
    return filename

def load_chat(filename):
    filepath = os.path.join(SAVE_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        st.session_state.messages = json.load(f)
    st.session_state.current_file = filename

# --- 4. 사이드바 UI ---
with st.sidebar:
    st.title("📁 대화 목록")
    if st.button("➕ 새 대화 시작"):
        st.session_state.messages = []
        st.session_state.current_file = None
        st.rerun()
    st.divider()

    files = [f for f in os.listdir(SAVE_DIR) if f.endswith(".json")]
    for f in files:
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button(f"💬 {f.replace('.json', '')}", key=f"load_{f}", use_container_width=True):
                load_chat(f)
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"del_{f}"):
                os.remove(os.path.join(SAVE_DIR, f))
                if st.session_state.current_file == f:
                    st.session_state.messages = []
                    st.session_state.current_file = None
                st.rerun()

# --- 5. CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #abc1d1; }
    .chat-row { display: flex; width: 100%; margin-bottom: 15px; }
    .user-row { justify-content: flex-end; }
    .bot-row { justify-content: flex-start; }
    .bot-container { display: flex; align-items: flex-start; gap: 10px; max-width: 85%; }
    
    /* 프로필 사진 고정 크기 및 디자인 */
    .profile-img { 
        width: 50px !important; 
        height: 50px !important; 
        min-width: 50px; 
        border-radius: 18px; 
        object-fit: cover; 
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .bot-content { display: flex; flex-direction: column; gap: 5px; }
    .bot-name { font-size: 16px; color: #2c3e50; font-weight: 600; }
    .chat-bubble { padding: 10px 14px; border-radius: 12px; font-size: 15px; line-height: 1.5; box-shadow: 0 1px 2px rgba(0,0,0,0.1); word-break: break-all; color: #000000 !important; /* 전체 글자 검정색 */}
    .user-bubble { background-color: #fee500; border-top-right-radius: 2px; }
    .bot-bubble { background-color: #ffffff; border-top-left-radius: 2px; }
    .action-text { color: #666; font-style: italic; background-color: #f0f0f0; padding: 2px 5px; border-radius: 4px; font-size: 0.9em; }
    </style>
    """, unsafe_allow_html=True)

# --- 6. 출력 및 입력 ---
current_title = st.session_state.current_file.replace('.json', '') if st.session_state.current_file else "박보검"
st.title(f"📱 {current_title}")

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="chat-row user-row"><div class="chat-bubble user-bubble">{msg["content"]}</div></div>', unsafe_allow_html=True)
    elif msg["role"] == "assistant":
        formatted_text = format_chat_text(msg["content"])
        
        # 외부 URL을 사용하여 이미지 태그 생성
        p_img_tag = f'<img src="{PROFILE_IMAGE_URL}" class="profile-img" onerror="this.onerror=null; this.src=\'https://api.dicebear.com/7.x/avataaars/svg?seed=Felix\';">'
        
        st.markdown(f'''
            <div class="chat-row bot-row">
                <div class="bot-container">
                    {p_img_tag}
                    <div class="bot-content">
                        <div class="bot-name">박보검</div>
                        <div class="chat-bubble bot-bubble">{formatted_text}</div>
                    </div>
                </div>
            </div>
            ''', unsafe_allow_html=True)

if prompt := st.chat_input("메시지를 입력하세요..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    if st.session_state.current_file: save_chat(st.session_state.current_file)
    st.rerun()

if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.spinner("박보검님이 생각 중..."):
        try:
            response = client.chat.completions.create(
                model="xiaomi/mimo-v2-flash:free", 
                messages=[{"role": "system", "content": CHARACTER_PROMPT}] + st.session_state.messages
            )
            ans = response.choices[0].message.content
            
            # --- [추가] 영어/시스템어 후처리 로직 ---
            # 1. 특정 시스템 단어(milliseconds 등) 강제 제거
            ans = re.sub(r'milliseconds|seconds|thinking|thought', '', ans, flags=re.IGNORECASE)
            
            # 2. 괄호 안에 영어만 들어있는 경우 제거 (예: (English))
            ans = re.sub(r'\([a-zA-Z\s]+\)', '', ans)
            
            # 3. 만약 대답에 한글이 하나도 없다면? (완전 영어 대답 방지)
            has_korean = re.search('[가-힣]', ans)
            if not has_korean:
                ans = "(당황한 듯 잠시 말을 멈췄다가) ...응, 그래. 다시 말해줄래?"
            # ---------------------------------------

            st.session_state.messages.append({"role": "assistant", "content": ans})
            if st.session_state.current_file: save_chat(st.session_state.current_file)
            st.rerun()
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
