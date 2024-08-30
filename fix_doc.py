from docx import Document
from io import BytesIO

def fix_doc(sender_id: str, doc_file: BytesIO, db):
    # Word 문서 수정 로직
    doc = Document(doc_file)
    for paragraph in doc.paragraphs:
        if "placeholder" in paragraph.text:
            paragraph.text = paragraph.text.replace("placeholder", "fixed text")

    # 수정된 문서를 BytesIO에 저장
    output = BytesIO()
    doc.save(output)
    output.seek(0)

    return {
        "senderId": sender_id,
        "doc": output,  # 수정된 Word 문서
        "senderType": "AI"
    }
