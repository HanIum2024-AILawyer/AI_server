from sqlite3 import Connection
from datetime import datetime
from langchain_community.llms import Ollama  # Ollama의 LLM 불러오기
from langchain.chains import LLMChain  # LLMChain 사용
from langchain.prompts import PromptTemplate
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings  # 사용할 임베딩 라이브러리
from text_processing import initial_chroma_db


# Ollama LLM을 함수 밖에서 초기화하여 처음에 한 번만 실행
# 로컬에서 mistral:latest 모델을 불러오기
llm = Ollama(model="mistral:latest")

# ChromaDB 초기화
vector_store = initial_chroma_db()

# 대화의 문맥을 설정하는 프롬프트 템플릿
prompt = PromptTemplate(
    input_variables=["history", "input"],
    template=(
        "너는 한국어로 대답해야 해. 영어 표기가 자연스러울 경우에만 영어 단어를 입력하고, "
        "최대한 한국어로 대답해 줘.\n"
        "너는 법률 변호사야. 나는 너에게 법률 상담을 할 거고, "
        "너는 법률 변호사로서 나에게 전문적이고 정확한 법적 자문을 제공해야 해.\n"
        "이것은 사용자와 AI 사이의 대화야. 지금까지의 대화:\n{history}\n"
        "사용자: {input}\nAI:"
    )
)

# 주제 추출을 위한 프롬프트 템플릿 설정
topic_prompt = PromptTemplate(
    input_variables=["content"],
    template=(
        "다음 텍스트에서 법적 주제를 추출해줘:\n"
        "{content}\n"
        "주제:"
    )
)

# 주제를 기반으로 문서를 검색하는 함수
def search_documents(topic: str):
    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    results = retriever.get_relevant_documents(topic)
    return results

# 전체 RAG 시스템을 chat_message에 통합
def chat_message(roomId: str, content: str, db: Connection):
    cursor = db.cursor()

    # 1. roomId를 사용하여 이전 대화 기록을 가져오기
    cursor.execute("SELECT content FROM chat_history WHERE roomId = ? ORDER BY timestamp ASC", (roomId,))
    previous_messages = cursor.fetchall()

    # 이전 대화 내용들을 하나의 텍스트로 연결
    conversation_history = "\n".join([msg[0] for msg in previous_messages])

    # 2. 주제 추출
    topic_prompt_chain = LLMChain(llm=llm, prompt=topic_prompt)
    topic = topic_prompt_chain.run(content=content).strip()

    # 3. 추출된 주제를 사용하여 ChromaDB에서 문서 검색
    documents = search_documents(topic)

    # 검색된 문서의 내용
    document_context = "\n".join([doc.page_content for doc in documents])

    # 4. LLMChain을 사용하여 응답 생성
    full_prompt = (
        f"다음 문서를 참고하여 질문에 답변해줘:\n"
        f"질문: {content}\n"
        f"참고 문서:\n{document_context}\n"
        "답변:"
    )
    llm_chain = LLMChain(llm=llm, prompt=full_prompt)
    response_content = llm_chain.run(history=conversation_history, input=content)

    # 5. 새로운 대화 기록을 데이터베이스에 저장
    cursor.execute("""
        INSERT INTO chat_history (roomId, content, senderType, timestamp) 
        VALUES (?, ?, ?, ?)
    """, (roomId, content, "USER", datetime.now()))

    cursor.execute("""
        INSERT INTO chat_history (roomId, content, senderType, timestamp) 
        VALUES (?, ?, ?, ?)
    """, (roomId, response_content, "AI", datetime.now()))

    db.commit()

    # 6. 응답 반환
    return {
        "roomId": roomId,
        "content": response_content, 
        "senderType": "AI",
        "topic": topic
    }
