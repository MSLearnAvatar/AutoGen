# AutoGen
AutoGen - Multi Agent
Fastapi
# AutoGen
AutoGen - Multi Agent
# AutoGen Multi-Agent Azure AI Avatar Chat

## 📋 개요

Azure OpenAI와 AutoGen을 활용한 지능형 멀티 에이전트 시스템입니다. 이 프로젝트는 Azure AI Avatar와 통합되어 실시간 음성 대화와 텍스트 응답을 동시에 제공하는 혁신적인 AI 채팅 시스템을 구현합니다.

## ✨ 주요 기능

- **멀티 에이전트 협업**: 계획 에이전트, 기술 작가, 스크립트 작가가 협력하여 최적화된 응답 생성
- **Azure AI Avatar 통합**: 실시간 음성 합성과 아바타 애니메이션
- **실시간 WebSocket 통신**: 빠른 응답과 원활한 사용자 경험
- **Azure Search 통합**: 벡터 데이터베이스를 활용한 정확한 정보 검색
- **이중 응답 시스템**: 상세한 텍스트 응답과 아바타용 요약 스크립트 동시 제공

## 🏗️ 시스템 아키텍처

```
사용자 질문
    ↓
Planning Agent (계획 수립)
    ↓
Technical Writer (상세 응답 생성)
    ↓
Script Writer (아바타용 스크립트 생성)
    ↓
Azure AI Avatar (음성 출력)
```

## 🛠️ 기술 스택

- **Backend**: FastAPI, Python 3.8+
- **AI Framework**: AutoGen, Azure OpenAI
- **실시간 통신**: WebSocket
- **음성/아바타**: Azure Speech Service, Azure AI Avatar
- **검색**: Azure Cognitive Search
- **Frontend**: HTML5, CSS3, JavaScript
- **배포**: Gunicorn, Uvicorn

## 📦 설치 및 설정

### 1. 저장소 클론

```bash
git clone https://github.com/your-username/autogen-multi-agent.git
cd autogen-multi-agent
```

### 2. 가상환경 생성 및 활성화

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate     # Windows
```

### 3. 종속성 설치

```bash
pip install -r requirements.txt
```

### 4. 환경변수 설정

`.env` 파일을 생성하고 다음 정보를 입력하세요:

```env
# Azure OpenAI 설정
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_MODEL=your_model_name
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/

# Azure Speech Service 설정
SPEECH_KEY=your_speech_key
SPEECH_REGION=your_region

# Azure Search 설정 (Autogen_Chat_data.py에서 사용)
AZURE_SEARCH_ENDPOINT=your_search_endpoint
AZURE_SEARCH_API_KEY=your_search_key
AZURE_SEARCH_INDEX=your_index_name
```

## 🚀 실행 방법

### 개발 환경

```bash
python app.py
```

### 프로덕션 환경

```bash
gunicorn app:app --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:3100
```

애플리케이션이 실행되면 `http://localhost:8000` (개발) 또는 `http://localhost:3100` (프로덕션)에서 접속할 수 있습니다.

## 📁 프로젝트 구조

```
autogen-multi-agent/
├── app.py                    # 메인 FastAPI 애플리케이션
├── Autogen_Chat_data.py      # Azure Search 통합 버전
├── requirements.txt          # Python 종속성
├── templates/
│   └── index.html           # 웹 인터페이스
├── static/
│   ├── css/
│   │   └── styles.css       # 스타일시트
│   └── js/
│       └── script.js        # 클라이언트 JavaScript
└── README.md                # 프로젝트 문서
```

## 🤖 에이전트 시스템

### Planning Agent (계획 에이전트)
- 복잡한 작업을 하위 작업으로 분해
- 다른 에이전트들에게 작업 할당
- 품질 체크리스트 기반 검증

### Technical Writer (기술 작가)
- Azure AI 및 기계학습 관련 전문 정보 제공
- 상세하고 기술적인 응답 생성
- 코드 예제 및 실용적 가이드 포함

### Script Writer (스크립트 작가)
- 아바타가 말하기 편한 형태로 내용 요약
- Markdown 문법 제거 및 자연스러운 대화체 변환
- 100자 내외의 간결한 스크립트 생성

## 🔧 주요 설정

### 아바타 설정
- **캐릭터**: Meg
- **스타일**: Business
- **배경색**: #FFFFFFFF
- **음성**: ko-KR-SunHiNeural

### 모델 설정
- **최대 턴 수**: 10
- **종료 조건**: "TERMINATE" 키워드 또는 최대 메시지 수 도달

## 🌐 API 엔드포인트

- `GET /`: 메인 웹 인터페이스
- `GET /health`: 서버 상태 확인
- `WebSocket /api/ws`: 실시간 채팅 통신

## 📱 사용 방법

1. 웹 브라우저에서 애플리케이션에 접속
2. "아바타 세션 시작" 버튼 클릭
3. 질문을 입력하고 전송
4. 텍스트 응답과 아바타 음성 응답을 동시에 확인

## ⚠️ 주의사항

- Azure 서비스 키가 올바르게 설정되었는지 확인하세요
- WebRTC를 지원하는 최신 브라우저를 사용하세요
- HTTPS 환경에서 아바타 기능이 최적으로 작동합니다

## 🤝 기여하기

1. 이 저장소를 포크하세요
2. 새로운 기능 브랜치를 생성하세요 (`git checkout -b feature/AmazingFeature`)
3. 변경사항을 커밋하세요 (`git commit -m 'Add some AmazingFeature'`)
4. 브랜치에 푸시하세요 (`git push origin feature/AmazingFeature`)
5. Pull Request를 생성하세요

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 지원

문제가 발생하거나 질문이 있으시면 [Issues](https://github.com/yplnaa/autogen-multi-agent/issues)에 등록해주세요.

## 🔄 버전 히스토리

- **v1.0.0**: 초기 릴리즈
  - 멀티 에이전트 시스템 구현
  - Azure AI Avatar 통합
  - WebSocket 실시간 통신

---
