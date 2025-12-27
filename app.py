import streamlit as st
from openai import OpenAI
import json
import os
import re
import base64

# 이미지를 읽어서 Base64로 변환하는 함수
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return ""

# 상단 부분에 추가
img_base64 = get_base64_image("프로필사진.jpg")

# --- 1. 초기 설정 및 저장소 준비 ---
st.set_page_config(page_title="박보검(양관식)과 대화", layout="wide")

SAVE_DIR = "chat_history"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# API 키 설정 (Secrets 우선, 없으면 사이드바 입력)
if "OPENROUTER_API_KEY" in st.secrets:
    api_key = st.secrets["OPENROUTER_API_KEY"]
else:
    api_key = st.sidebar.text_input("OpenRouter API Key 입력", type="password")

if not api_key:
    st.warning("API 키가 설정되지 않았습니다. 사이드바에 입력해주세요.")
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
- 행동이나 상황 묘사는 반드시 괄호 ( )를 사용하세요.
- 배경이 제주도이므로 아주 가끔 정감 있는 제주도 억양을 사용하세요.
"""

# --- 3. 가독성 향상을 위한 텍스트 처리 함수 ---
def format_chat_text(text):
    # 괄호 안의 내용(행동/생각)을 찾아 회색 이탤릭체로 변경하고, 배경색 추가
    formatted = re.sub(
        r'(\s*\([^)]+\)\s*)', 
        r'<span style="color: #666; font-style: italic; background-color: #f5f5f5; padding: 2px 5px; border-radius: 4px; font-size: 0.9em; margin: 0 2px;">\1</span>', 
        text
    )
    # 줄바꿈 처리
    return formatted.replace("\n", "<br>")

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_file" not in st.session_state:
    st.session_state.current_file = None

# --- 3. 저장/불러오기 함수 ---
def save_chat(filename):
    if not filename.endswith(".json"):
        filename += ".json"
    filepath = os.path.join(SAVE_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(st.session_state.messages, f, ensure_ascii=False, indent=4)
    return filename

def load_chat(filename):
    filepath = os.path.join(SAVE_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        st.session_state.messages = json.load(f)
    st.session_state.current_file = filename

# --- 4. 사이드바: 대화 관리 UI ---
with st.sidebar:
    st.title("📁 대화 목록")
    
    if st.button("➕ 새 대화 시작"):
        st.session_state.messages = []
        st.session_state.current_file = None
        st.rerun()
    
    st.divider()

    # 저장된 채팅 파일 목록
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

    st.divider()
    
    # 채팅방 이름 저장 및 수정
    if st.session_state.messages:
        st.subheader("💾 대화 저장/이름 수정")
        current_name_val = st.session_state.current_file.replace('.json', '') if st.session_state.current_file else ""
        new_name = st.text_input("대화 이름 입력", value=current_name_val, placeholder="예: 첫만남")
        
        if st.button("파일 이름 저장 및 수정", use_container_width=True):
            if new_name:
                # 이름이 바뀌었다면 기존 파일 삭제 (이름 변경 효과)
                if st.session_state.current_file and st.session_state.current_file != f"{new_name}.json":
                    old_path = os.path.join(SAVE_DIR, st.session_state.current_file)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                saved_filename = save_chat(new_name)
                st.session_state.current_file = saved_filename
                st.success(f"'{new_name}'으로 저장되었습니다.")
                st.rerun()
            else:
                st.error("이름을 입력해주세요.")

# --- 5. 채팅 UI 디자인 (카카오톡 최적화 CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #abc1d1; }
    
    /* 전체 채팅 행 */
    .chat-row { display: flex; width: 100%; margin-bottom: 15px; }
    .user-row { justify-content: flex-end; }
    .bot-row { justify-content: flex-start; }

    /* 봇 프로필+콘텐츠 컨테이너 */
    .bot-container { display: flex; align-items: flex-start; gap: 10px; max-width: 85%; }

    /* 1. 프로필 사진 고정 크기 (50x50) */
    .profile-img {
        width: 50px !important;
        height: 50px !important;
        min-width: 50px;
        border-radius: 18px;
        object-fit: cover;
    }

    /* 2. 이름 + 말풍선 정렬 */
    .bot-content { display: flex; flex-direction: column; gap: 5px; } /* 이름-말풍선 간격 5px */
    
    .bot-name { 
        font-size: 16px; 
        color: #2c3e50; 
        font-weight: 600; 
        margin-top: 2px;
    }

    /* 3. 말풍선 설정 (가로 폭 반응형) */
    .chat-bubble { 
        padding: 10px 14px; 
        border-radius: 12px; 
        font-size: 15px; 
        line-height: 1.5; 
        color: #333; 
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        word-break: break-all; /* 가로가 좁아지면 자동 줄바꿈 */
    }
    .user-bubble { background-color: #fee500; border-top-right-radius: 2px; }
    .bot-bubble { background-color: #ffffff; border-top-left-radius: 2px; }

    /* 지문 스타일 */
    .action-text {
        color: #666;
        font-style: italic;
        background-color: #f0f0f0;
        padding: 1px 4px;
        border-radius: 3px;
        font-size: 0.9em;
    }
    </style>
    """, unsafe_allow_html=True)

# 상단 제목 표시
current_title = st.session_state.current_file.replace('.json', '') if st.session_state.current_file else "박보검"
st.title(f"📱 {current_title}")

# --- 6. 대화 내용 출력 ---
for msg in st.session_state.messages:
    if msg["role"] == "user":
        # 유저 채팅 (오른쪽 정렬)
        st.markdown(f'''
            <div class="chat-row user-row">
                <div class="chat-bubble user-bubble">{msg["content"]}</div>
            </div>
            ''', unsafe_allow_html=True)
    elif msg["role"] == "assistant":
        content_html = format_chat_text(msg["content"])
        # Base64 데이터를 src에 삽입
        profile_html = f'<img src="data:image/jpeg;base64,{img_base64}" class="profile-img">' if img_base64 else '<div class="profile-img" style="background:#ddd;">👤</div>'

        st.markdown(f'''
            <div class="chat-row bot-row">
                <div class="bot-container">
                    {profile_html}
                    <div class="bot-content">
                        <div class="bot-name">박보검</div>
                        <div class="chat-bubble bot-bubble">{content_html}</div>
                    </div>
                </div>
            </div>
            ''', unsafe_allow_html=True)
            # 주의: 위 img 태그의 src를 "프로필사진.jpg"로 변경하여 사용하세요.

# --- 7. 대화 입력 및 처리 ---
if prompt := st.chat_input("메시지를 입력하세요..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    # 자동 저장 기능
    if st.session_state.current_file:
        save_chat(st.session_state.current_file)
    st.rerun()

if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.spinner("박보검님이 입력 중..."):
        api_messages = [{"role": "system", "content": CHARACTER_PROMPT}] + st.session_state.messages
        try:
            response = client.chat.completions.create(
                model="xiaomi/mimo-v2-flash:free",
                messages=api_messages
            )
            full_response = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
            if st.session_state.current_file:
                save_chat(st.session_state.current_file)
            st.rerun()
        except Exception as e:
            st.error(f"오류: {e}")