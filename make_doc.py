from docx import Document
from io import BytesIO

def make_doc(sender_id: str, db):
    # 새로운 Word 문서 생성 로직
    doc = Document()
    doc.add_paragraph("This is a new document created by AI.")
    
    # 생성된 문서를 BytesIO에 저장
    output = BytesIO()
    doc.save(output)
    output.seek(0)
    
    return {
        "senderId": sender_id,
        "doc": output,  # 새로 생성된 Word 문서
        "senderType": "AI"
    }
