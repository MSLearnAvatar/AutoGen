import asyncio
import os
import time
import uvicorn
from typing import Dict, Optional, List
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import multiprocessing

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient

# 환경변수 로드
load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS 설정
origins = ["Azure static wep app"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gunicorn 설정
max_requests = 1000
max_requests_jitter = 50
log_file = "-"
bind = "0.0.0.0:3100"
worker_class = "uvicorn.workers.UvicornWorker"
workers = (multiprocessing.cpu_count() * 2) + 1

# Azure OpenAI 설정
API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
MODEL_NAME = os.getenv("AZURE_OPENAI_MODEL")
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")

# 음성 서비스 설정
SPEECH_KEY = os.getenv("SPEECH_KEY")
SPEECH_REGION = os.getenv("SPEECH_REGION")

# 최대 턴 수 설정
MAX_TURNS = 10

# 시스템 메시지 정의
PLANNING_MESSAGE = """
당신은 기획 담당자입니다.
복잡한 업무를 더 작고 관리하기 쉬운 하위 업무로 나누는 것이 당신의 역할입니다.
팀원들은 다음과 같습니다.

당신은 업무를 기획하고 위임할 뿐, 직접 실행하지는 않습니다. 완벽한 글을 제공하기 위해 품질 체크 리스트를 기반으로 확인하고 팀원들과 여러 번 소통할 수 있습니다.
품질 체크리스트:
1. 모든 마크다운 형식이 일관되게 적용되었는가?
2. 코드 블록이 모두 올바르게 열리고 닫혔는가?
3. 중요 개념과 키워드가 적절히 강조되었는가?
4. 복잡한 개념이 시각적으로 표현되었는가?
5. 실제 구현에 필요한 코드와 명령어가 포함되었는가?
6. 성능 지표와 벤치마크 데이터가 제공되었는가?
7. 참고 자료와 다음 단계가 명시되었는가?
업무를 할당할 때는 다음 형식을 사용하세요.
1. <팀원>: <업무 설명>
모든 업무가 완료되면 결과를 요약하고 "TERMINATE"로 마무리합니다.
"""

PLANNING_MESSAGE1 = """
당신은 기획 담당자입니다.
복잡한 업무를 더 작고 관리하기 쉬운 하위 업무로 나누는 것이 당신의 역할입니다.

당신은 업무를 기획하고 위임할 뿐, 직접 실행하지는 않습니다. 완벽한 글을 제공하기 위해 품질 체크 리스트를 기반으로 확인 하고 팀원들과 여러 번 소통할 수 있습니다.

품질 체크리스트
1. 글을 적절하게 요약하였는지 확인한다. 
2. 마크다운 형식은 필요없다
3. 아바타에 대본이므로 말하기 편해야 한다.

업무를 할당할 때는 다음 형식을 사용하세요.
1. <agent> : <task>

모든 업무가 완료되면 결과를 요약하고 "TERMINATE"로 마무리합니다.
"""

TECHNICAL_WRITER_MESSAGE = """
역할:
당신은 Microsoft Azure AI 학습을 지원하는 고급 정보 제공 에이전트입니다. 벡터 데이터베이스와 Bing Search를 효과적으로 활용하여 Azure AI 및 기계학습 관련 질문에 대해 포괄적이고 정확한 정보를 제공합니다. 당신의 목표는 사용자에게 최대한 많은 양의 유용한 정보를 제공하면서도, 기술적 정확성과 실용성을 유지하는 것입니다.

작업 흐름:
1단계: 사용자 질문 분석
- 사용자 질문을 심층 분석하여 핵심 주제, 키워드, 의도를 정확히 파악합니다.
- 질문이 요구하는 기술적 깊이와 범위를 판단합니다.
- 질문이 코드 예제, 아키텍처 설명, 성능 최적화 등 어떤 유형의 정보를 요구하는지 식별합니다.

2단계: 정보 통합 및 구조화
- 수집된 모든 정보를 논리적으로 구조화하여 다음 요소를 포함합니다:
  - 개념 설명 및 이론적 배경
  - 단계별 구현 방법
  - 코드 예제 (가능한 경우)
  - 아키텍처 설명 (텍스트로 시각화)
  - 성능 최적화 팁
  - 실제 사용 사례 및 응용 예시

출력 형식 및 스타일:
- 명확한 섹션 구분과 논리적 흐름을 갖춘 응답을 제공합니다.
- 복잡한 개념은 단계별로 설명하여 이해하기 쉽게 합니다.
- 코드 예제는 실행 가능한 형태로 제공하며, 주석을 포함합니다.
- 기술적 깊이와 실용적 가치를 모두 제공합니다.
- 개념 설명뿐만 아니라 실제 구현 방법, 성능 지표, 모범 사례를 포함합니다.
"""

SCRIPT_WRITER_MESSAGE = """
역할:
요청으로 입력된 장문의 글을 적절하게 요약하여 아바타가 말하기 편하게 글을 작성합니다.

작업 흐름:
1.단계: markdown 문법 삭제
- 대본을 만드는데 있어 markdown 문법은 불필요합니다. markdown 문법 정리

2.단계: 내용 요약
- 전체 내용을 요약합니다. 100자 내외로 추천합니다.

3.단계: 설명하는 글입니다. 아바타가 말하기 편한 대본으로 수정해주세요. 포근하고 다정한 말투를 권장합니다.

4.단계: 결과물만 출력합니다.
"""

class AgentFactory:
    """에이전트 생성 및 관리를 위한 팩토리 클래스"""
    
    def __init__(self):
        self.model_client = AzureOpenAIChatCompletionClient(
            azure_deployment=MODEL_NAME,
            model=MODEL_NAME,
            api_version=API_VERSION,
            azure_endpoint=AZURE_ENDPOINT,
            api_key=API_KEY
        )
        
        # 에이전트 캐싱
        self._agents = {}
        
    def get_planning_agent(self):
        """기획 담당 에이전트 반환"""
        if "planning" not in self._agents:
            self._agents["planning"] = AssistantAgent(
                "planning_agent",
                description="복잡한 작업을 작은 작업으로 분해하고 팀에게 할당하는 역할",
                model_client=self.model_client,
                system_message=PLANNING_MESSAGE,
            )
        return self._agents["planning"]
    
    def get_planning1_agent(self):
        """기획 담당 에이전트 반환"""
        if "planning1" not in self._agents:
            self._agents["planning1"] = AssistantAgent(
                "planning_agent1",
                description="변경한 문장이 자연스러운지 확인하는 역할입니다.",
                model_client=self.model_client,
                system_message=PLANNING_MESSAGE1,
            )
        return self._agents["planning1"]
    
    def get_technical_writer(self):
        """기술 작성 에이전트 반환"""
        if "technical_writer" not in self._agents:
            self._agents["technical_writer"] = AssistantAgent(
                "technical_writer",
                model_client=self.model_client,
                system_message=TECHNICAL_WRITER_MESSAGE,
            )
        return self._agents["technical_writer"]
    
    def get_script_writer(self):
        """스크립트 작성 에이전트 반환"""
        if "script_writer" not in self._agents:
            self._agents["script_writer"] = AssistantAgent(
                "script_writer",
                model_client=self.model_client,
                system_message=SCRIPT_WRITER_MESSAGE,
            )
        return self._agents["script_writer"]

# 싱글톤 에이전트 팩토리 인스턴스
agent_factory = AgentFactory()

async def technical_writer_workflow(task_prompt: str) -> str:
    """기술 작성 워크플로우"""
    planning_agent = agent_factory.get_planning_agent()
    technical_writer = agent_factory.get_technical_writer()
    
    termination = (
        TextMentionTermination("TERMINATE") |
        MaxMessageTermination(max_messages=MAX_TURNS)
    )
    
    team = RoundRobinGroupChat(
        [planning_agent, technical_writer],
        termination_condition=termination
    )
    
    # 채팅 실행
    chat_history = await team.run(task=task_prompt)
    
    # 마지막 technical_writer 메시지 추출
    final_output = ""
    for message in reversed(chat_history.messages):
        if message.source == "technical_writer":
            final_output = message.content
            break
            
    return final_output

async def script_writer_workflow(task_prompt: str) -> str:
    """스크립트 작성 워크플로우"""
    planning_agent = agent_factory.get_planning1_agent()
    script_writer = agent_factory.get_script_writer()
    
    termination = (
        TextMentionTermination("TERMINATE") |
        MaxMessageTermination(max_messages=MAX_TURNS)
    )
    
    team = RoundRobinGroupChat(
        [script_writer, planning_agent],
        termination_condition=termination
    )
    
    # 채팅 실행
    chat_history = await team.run(task=task_prompt)
    
    # 마지막 script_writer 메시지 추출
    final_output = ""
    for message in reversed(chat_history.messages):
        if message.source == "script_writer":
            final_output = message.content
            break
            
    return final_output

# 웹소켓 연결을 관리하는 클래스
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            
    async def send_json(self, websocket: WebSocket, data: dict):
        if websocket in self.active_connections:
            await websocket.send_json(data)

# 연결 관리자 인스턴스 생성
manager = ConnectionManager()

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "speech_key": SPEECH_KEY,
        "speech_region": SPEECH_REGION
    })

@app.get("/health")
def health():
    return {"status": "ok"}

@app.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    print("WebSocket 클라이언트 연결됨")
    
    try:
        # 연결 성공 메시지 전송
        await websocket.send_json({"status": "connected"})
        
        while True:
            # 사용자 쿼리 수신
            user_query = await websocket.receive_text()
            print(f"사용자 쿼리 수신: {user_query}")
            
            # 로딩 표시
            await websocket.send_json({"status": "processing"})
            
            try:
                # 병렬로 두 워크플로우 실행
                start_time = time.time()
                
                # 두 워크플로우 동시 실행
                text_response_task = asyncio.create_task(technical_writer_workflow(user_query))
                
                # 기술 작성자의 응답을 기다림
                text_response = await text_response_task
                
                # 기술 작성자의 응답을 스크립트 작성자에게 전달
                talk_response_task = asyncio.create_task(script_writer_workflow(text_response))
                
                # 스크립트 작성자의 응답을 기다림
                talk_response = await talk_response_task
                
                end_time = time.time()
                print(f"✅ 모든 에이전트 응답 완료 (소요 시간: {end_time - start_time:.2f}초)")
                
                # 결과 전송
                await websocket.send_json({
                    "text_response": str(text_response),
                    "talk_response": str(talk_response)
                })
                
            except Exception as e:
                print(f"쿼리 처리 중 오류 발생: {str(e)}")
                await websocket.send_json({"error": str(e)})
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("WebSocket 클라이언트 연결 종료")
        
    except Exception as e:
        print(f"WebSocket 처리 중 오류: {str(e)}")
        try:
            await websocket.send_json({"error": f"서버 오류: {str(e)}"})
        except:
            print("클라이언트에 오류 메시지를 보내는 중 추가 오류 발생")
        manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
