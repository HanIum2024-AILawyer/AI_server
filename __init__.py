from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from chat_message import chat_message
from chat_remove import chat_remove
from fix_doc import fix_doc
from make_doc import make_doc
from fastapi.responses import FileResponse
from io import BytesIO
from pydantic import BaseModel
from sqlite3 import connect, Connection
import threading
from contextlib import asynccontextmanager

# FastAPI 애플리케이션 생성
app = FastAPI()

# SQLite 연결을 위한 전역 변수
db_lock = threading.Lock()
db_path = "chat_history.db"

def init_db():
    with db_lock:
        conn = connect(db_path)
        with conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """)
        conn.close()

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

# 공통으로 사용할 요청 데이터 형식 정의
class ChatMessageRequest(BaseModel):
    room_Id: str
    content: str
    senderType: str

class ChatRemoveRequest(BaseModel):
    room_Id: str
    senderType: str

class FixDocRequest(BaseModel):
    room_Id: str
    senderType: str

class MakeDocRequest(BaseModel):
    room_Id: str
    senderType: str

# /ai/chat/message/ 엔드포인트
@app.post("/ai/chat/message/")
def handle_chat_message(request: ChatMessageRequest, db: Connection = Depends(get_db)):
    if request.senderType != "USER":
        raise HTTPException(status_code=400, detail="Invalid senderType. Must be 'USER'.")

    response = chat_message(request.room_Id, request.content, db)
    return response

# /ai/chat/remove/ 엔드포인트
@app.post("/ai/chat/remove/")
def handle_chat_remove(request: ChatRemoveRequest, db: Connection = Depends(get_db)):
    if request.senderType != "USER":
        raise HTTPException(status_code=400, detail="Invalid senderType. Must be 'USER'.")

    response = chat_remove(request.room_Id, db)
    return response

# /ai/doc/fix_doc/ 엔드포인트
@app.post("/ai/doc/fix_doc/")
async def handle_fix_doc(file: UploadFile = File(...), docId: str = "", senderType: str = "USER", db: Connection = Depends(get_db)):
    if senderType != "USER":
        raise HTTPException(status_code=400, detail="Invalid senderType. Must be 'USER'.")

    file_bytes = BytesIO(await file.read())
    response = fix_doc(docId, file_bytes, db)

    return FileResponse(response['doc'], media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document', filename="fixed_document.docx")

# /ai/doc/make_doc/ 엔드포인트
@app.post("/ai/doc/make_doc/")
def handle_make_doc(request: MakeDocRequest, db: Connection = Depends(get_db)):
    if request.senderType != "USER":
        raise HTTPException(status_code=400, detail="Invalid senderType. Must be 'USER'.")

    response = make_doc(request.docId, db)

    return FileResponse(response['doc'], media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document', filename="new_document.docx")
