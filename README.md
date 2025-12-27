# 박보검(양관식) 챗봇

드라마 '폭싹 속았수다'의 주인공 '양관식'(박보검)과 대화할 수 있는 챗봇입니다.

## 🚀 실행 방법

### 로컬에서 실행하기

1. 저장소 클론하기:
   ```bash
   git clone https://github.com/djchany/bogum-chat.git
   cd bogum-chat
   ```

2. 가상환경 설정 및 활성화 (Windows):
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. 필요한 패키지 설치:
   ```bash
   pip install -r requirements.txt
   ```

4. API 키 설정:
   `.streamlit/secrets.toml` 파일을 생성하고 다음 내용을 추가하세요:
   ```toml
   OPENROUTER_API_KEY = "여기에_당신의_OpenRouter_API_키를_입력하세요"
   ```

5. 앱 실행:
   ```bash
   streamlit run app.py
   ```

## 📝 주의사항
- 이 프로젝트는 OpenRouter API를 사용합니다. 사용 전에 [OpenRouter](https://openrouter.ai/)에서 API 키를 발급받아야 합니다.
- API 키는 반드시 안전하게 보관하시고, 절대 공개 저장소에 올리지 마세요.

## 📄 라이선스
이 프로젝트는 MIT 라이선스 하에 배포됩니다.
