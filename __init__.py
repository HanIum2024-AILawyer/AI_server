from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from chat_message import chat_message
from chat_remove import chat_remove
from fix_doc import fix_doc
from make_doc import make_doc  # make_doc 함수 사용
from fastapi.responses import FileResponse
from pydantic import BaseModel
import threading
from contextlib import asynccontextmanager
import os
from sqlite3 import connect, Connection
from docx import Document

# FastAPI 애플리케이션 생성
app = FastAPI()

# SQLite 연결을 위한 전역 변수 (chat 관련된 부분에서만 사용)
db_lock = threading.Lock()
db_path = "chat_history.db"

# 데이터베이스 초기화 함수 (chat 관련 테이블만 유지)
def init_db():
    with db_lock:
        conn = connect(db_path)
        with conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                roomId TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                senderType TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """)
        conn.close()

# FastAPI 애플리케이션 시작 시 DB 초기화
init_db()

def get_db():
    with db_lock:
        conn = connect(db_path)
        try:
            yield conn
        finally:
            conn.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 애플리케이션 시작 시 실행할 코드
    init_db()
    print("Database initialized")
    
    # 애플리케이션 실행
    yield
    
    # 애플리케이션 종료 시 실행할 코드
    print("Shutting down application")

app = FastAPI(lifespan=lifespan)

# 공통으로 사용할 요청 데이터 형식 정의 (채팅 관련)
class ChatMessageRequest(BaseModel):
    roomId: str
    content: str
    senderType: str

class ChatRemoveRequest(BaseModel):
    roomId: str

# 문서 생성 및 수정용 데이터 형식 정의
class MakeDocRequest(BaseModel):
    doc_type: str  # 101은 소송장, 201은 고소장, 답변서=102, 준비서면=103, 민사가 100번라인, 형사가 200번라인
    defendant_count: str  # 피고 숫자 (1 ~ 3)
    case_description: str  # 사건에 대한 서술
    claim_amount: str  # 피해 금액 또는 피해 규모


# /ai/chat/message/ 엔드포인트
@app.post("/ai/chat/message/")
def handle_chat_message(request: ChatMessageRequest, db: Connection = Depends(get_db)):
    if request.senderType != "USER":
        raise HTTPException(status_code=400, detail="Invalid senderType. Must be 'USER'.")

    response = chat_message(request.roomId, request.content, db)
    return response

# /ai/chat/remove/ 엔드포인트
@app.post("/ai/chat/remove/")
def handle_chat_remove(request: ChatRemoveRequest, db: Connection = Depends(get_db)):
    success = chat_remove(request.roomId, db)
    
    if not success:
        raise HTTPException(status_code=404, detail="No chat history found for the provided roomId.")
    
    return {"success": success}

# /ai/doc/fix_doc/ 엔드포인트
@app.post("/ai/doc/fix_doc/")
async def handle_fix_doc(file: UploadFile = File(...)):

    # 1. 업로드된 파일을 서버에 저장
    uploaded_file_name = "uploaded_document.docx"
    with open(uploaded_file_name, "wb") as f:
        f.write(await file.read())

    # 2. fix_doc 함수 호출하여 문서 수정
    modified_file_path = fix_doc(uploaded_file_name)

    # 3. 수정된 파일을 반환하고, 반환 후 파일 삭제
    try:
        return FileResponse(modified_file_path, 
                            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document', 
                            filename="fixed_document.docx")
    finally:
        # 원본 파일과 수정된 파일 모두 삭제
        if os.path.exists(uploaded_file_name):
            os.remove(uploaded_file_name)
        if os.path.exists(modified_file_path):
            os.remove(modified_file_path)


# /ai/doc/make_doc/ 엔드포인트 (파일 생성 및 반환 후 삭제)
@app.post("/ai/doc/make_doc/")
def handle_make_doc(request: MakeDocRequest):

    # make_doc 함수 호출하여 문서 생성
    file_name = make_doc(
        input_data={
            "defendant_count": request.defendant_count,
            "case_description": request.case_description,
            "claim_amount": request.claim_amount
        }
    )

    # 파일 반환 및 반환 후 삭제
    try:
        return FileResponse(file_name, 
                            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document', 
                            filename="./outputnew_document.docx")
    finally:
        pass
    #     if os.path.exists(file_name):
    #         os.remove(file_name)

