# chat_message.py

from sqlite3 import Connection
from datetime import datetime
from langchain_community.llms import Ollama  # Ollama의 LLM 불러오기
from langchain.chains import SimpleSequentialChain  # LangChain의 간단한 체인 사용

def chat_message(room_id: str, content: str, db: Connection):
    cursor = db.cursor()

    # 1. room_id가 데이터베이스에 이미 존재하는지 확인
    cursor.execute("SELECT COUNT(*) FROM chat_history WHERE room_id = ?", (room_id,))
    exists = cursor.fetchone()[0] > 0

    # 2. room_id가 처음 보는 것이라면 새로운 행을 추가
    if not exists:
        cursor.execute("""
            INSERT INTO chat_history (room_id, message, timestamp) 
            VALUES (?, ?, ?)
        """, (room_id, content, datetime.now()))
        db.commit()

    # 3. Ollama에서 LLM 불러오기
    llm = Ollama(model_name="mistral:latest")  # Ollama 모델 이름을 지정해야 합니다.

    # 4. LangChain을 사용해 AI 응답 생성
    # 여기서는 간단한 체인을 사용해 사용자 입력을 LLM에 전달하고 응답을 받습니다.
    chain = SimpleSequentialChain(llm)
    response_content = chain.run(content)  # 사용자 입력을 LLM에 전달

    # 5. 생성된 응답을 데이터베이스에 저장
    cursor.execute("""
        INSERT INTO chat_history (room_id, message, timestamp) 
        VALUES (?, ?, ?)
    """, ("AI", response_content, datetime.now()))
    db.commit()

    # 6. 응답 반환
    return {"room_id": "AI", "content": response_content}
