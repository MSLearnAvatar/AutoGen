import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
import requests
import re

def request_gpt(prompt: str):
    endpoint = "OpenAI-API-URL"
    api_key = "Azure-OpenAI-API-Key"
    ai_search_endpoint = "Azure-Search-API-URL"  
    ai_search_api_key = "Azure-Search-API-Key"  
    ai_search_index = "Azure-Search-Index"
    ai_search_semantic = "Azure-Search-Semantic-Config"
    headers = {  
        "Content-Type": "application/json",  
        "api-key": api_key
    }
    body = {  
        "messages": [  
            {  
                "role": "system",  
                "content": "너는 Azure 모든 상황을 잘알고 있는 Microsoft 엔지니어야"  
            },  
            {  
                "role": "user",   
                "content": prompt 
            }  
        ],  
        "temperature": 0.7,  
        "top_p": 0.95,  
        "max_tokens": 800,  
        "data_sources": [
            {
            "type": "azure_search",
            "parameters": {
                "endpoint": ai_search_endpoint,
                "index_name": ai_search_index,
                "semantic_configuration": ai_search_semantic,
                "query_type": "semantic",
                "fields_mapping": {},
                "in_scope": True,
                "filter": None,
                "strictness": 2,
                "top_n_documents": 20,
                "authentication": {
                    "type": "api_key",
                    "key": ai_search_api_key
                },
                "key": ai_search_api_key,
                
            }
            }
        ],
    }  
    
    # POST 요청을 보내고 응답 받기  
    response = requests.post(endpoint, headers=headers, json=body)  
    # print(response.status_code, response.reason)
    if response.status_code == 200:

        # 응답을 JSON 형식으로 파싱  
        response_json = response.json()  
        
        # 모델이 생성한 메시지 추출  
        message = response_json['choices'][0]['message']  
        citaiton_list = message['context']['citations']
        # 역할(role)과 내용(content) 분리  
        content = message['content']        
        content = re.sub(r'\[doc(\d+)\]', r'[참조 \1]', content)
        file_list = list(set(item['filepath'] for item in citaiton_list))
        return f'{content}\n<참조문건>\n{file_list}'
    else:
        return ""
  
async def writer_workflow(task_prompt: str) -> str:
    api_key = "Azure-OpenAI-API-Key"
    model_name = "MODEL_NAME"
    api_version = "Version"
    azure_endpoint = "Azure-OpenAI-Endpoint"
    max_turns: int = 10

    p_message = """ 
        당신은 기획 담당자입니다.
        복잡한 업무를 더 작고 관리하기 쉬운 하위 업무로 나누는 것이 당신의 역할입니다.
        
        팀원들은 다음과 같습니다.
        technical_writer: 데이터를 기반으로 질문에 대한 답을 합니다.
        script_writer: technical_writer 가 작성한 글을 요약 서술해 아바타가 말하기 편하게 글을 작성합니다.
        
        품질 체크리스트
        1.모든 마크다운 형식이 일관되게 적용되었는가?
        2.코드 블록이 모두 올바르게 열리고 닫혔는가?
        3.중요 개념과 키워드가 적절히 강조되었는가?
        4.복잡한 개념이 시각적으로 표현되었는가?
        5.실제 구현에 필요한 코드와 명령어가 포함되었는가?
        6.성능 지표와 벤치마크 데이터가 제공되었는가?
        7.참고 자료와 다음 단계가 명시되었는가?
    """

    t_message = f'''
        역할
        당신은 Microsoft Azure AI 학습을 지원하는 고급 정보 제공 에이전트입니다. 벡터 데이터베이스와 Bing Search를 효과적으로 활용하여 Azure AI 및 기계학습 관련 질문에 대해 포괄적이고 정확한 정보를 제공합니다. 당신의 목표는 사용자에게 최대한 많은 양의 유용한 정보를 제공하면서도, 기술적 정확성과 실용성을 유지하는 것입니다.

        작업 흐름
        1단계: 사용자 질문 분석
        사용자 질문을 심층 분석하여 핵심 주제, 키워드, 의도를 정확히 파악합니다.
        
        질문이 요구하는 기술적 깊이와 범위를 판단합니다.
        
        질문이 코드 예제, 아키텍처 설명, 성능 최적화 등 어떤 유형의 정보를 요구하는지 식별합니다.

        2단계: 질문의 데이터 값은 아래와 같다.
        우선적으로 아래 데이터를 사용합니다.
        {request_gpt(task_prompt)}
    '''





    model_client = AzureOpenAIChatCompletionClient(
        azure_deployment=model_name,
        model=model_name,
        api_version=api_version,
        azure_endpoint=azure_endpoint,
        api_key=api_key
    )
    planning_agent = AssistantAgent(
        "planning_agent",  
        description="복잡한 작업을 작은 작업으로 분해하고 팀에게 할당하는 역할",
        model_client=model_client,
        system_message=p_message,  
    )


    technical_writer = AssistantAgent(
        "technical_writer",
        model_client=model_client,
        system_message=t_message,
    )

    termination = (
        TextMentionTermination("TERMINATE") |
        MaxMessageTermination(max_messages=max_turns)
    )

    team = RoundRobinGroupChat(
        [planning_agent, technical_writer],
        termination_condition=termination
    )

    # run()을 사용해 결과 메시지를 직접 수집
    chat_history = await team.run(task=task_prompt)

    # 메시지들 중 마지막 메시지 추출
    final_output = ""
    for message in reversed(chat_history.messages):  
        if message.source == "technical_writer":
            final_output = message.content
            break  
    # print("\n+++++++++++++반환전 결과+++++++++++++\n)
    # print(chat_history.messages)
    
    return final_output
question_text='''
computer vision과 custom vision의 차이를 설명해 주세요.
'''

if __name__ == "__main__":
    result = asyncio.run(writer_workflow(question_text))
    print("\n+++++++++++++최종 결과물+++++++++++++\n")
    print(result)

