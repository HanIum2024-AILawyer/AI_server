# db.py
from sqlite3 import connect
import threading

# SQLite 연결을 위한 전역 변수
db_lock = threading.Lock()
db_path = "chat_history.db"

def get_db():
    with db_lock:
        conn = connect(db_path)
        try:
            yield conn
        finally:
            conn.close()
