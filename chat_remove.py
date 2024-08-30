def chat_remove(sender_id: str, db):
    # 특정 sender_id의 모든 채팅 기록을 삭제
    with db:
        db.execute("""
        DELETE FROM chat_history WHERE sender_id = ?
        """, (sender_id,))
        success = db.total_changes > 0

    return {
        "senderId": sender_id,
        "success": success,
        "senderType": "AI"
    }
