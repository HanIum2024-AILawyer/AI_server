# chat_remove.py

from sqlite3 import Connection

def chat_remove(roomId: str, db: Connection) -> bool:
    cursor = db.cursor()

    # 1. roomId와 일치하는 모든 대화 기록 삭제
    cursor.execute("DELETE FROM chat_history WHERE roomId = ?", (roomId,))
    
    # 2. 변경사항 커밋
    db.commit()

    # 3. 삭제된 행의 수를 반환하여 성공 여부를 확인
    deleted_rows = cursor.rowcount

    # 4. 성공 여부를 반환
    return deleted_rows > 0

