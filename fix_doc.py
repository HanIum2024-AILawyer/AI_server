from docx import Document
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.llms import Ollama
import os
import re

# Ollama LLM 초기화
llm = Ollama(model="mistral:latest")

# 프롬프트 템플릿 설정
prompt = PromptTemplate(
    input_variables=["claim_text"],
    template="다음 내용을 법적 서류에 맞는 단어와 말투로 수정해줘: {claim_text}"
)

# '청구 취지' 또는 '청구 원인'을 찾는 함수 (띄어쓰기가 다를 경우도 고려)
def find_section(paragraphs, keywords):
    for i, paragraph in enumerate(paragraphs):
        if any(re.search(keyword, paragraph.text.replace(" ", "")) for keyword in keywords):
            return i
    return None

def fix_doc(file_path: str):
    # 파일을 Document 객체로 로드
    doc = Document(file_path)
    
    # 청구 취지와 청구 원인을 찾을 때 사용할 키워드 리스트
    claim_purpose_keywords = ["청구취지", "청구  취지", "청  구  취  지"]
    claim_reason_keywords = ["청구원인", "청구  원인", "청  구  원  인"]

    # 청구 취지 부분을 찾고 수정
    claim_purpose_index = find_section(doc.paragraphs, claim_purpose_keywords)
    if claim_purpose_index is not None:
        claim_purpose_text = doc.paragraphs[claim_purpose_index + 1].text
        if claim_purpose_text:
            claim_purpose_lines = claim_purpose_text.split("\n")
            modified_purpose_lines = []

            # 각 줄을 LLM을 통해 수정
            for line in claim_purpose_lines:
                if line.strip():
                    llm_chain = LLMChain(llm=llm, prompt=prompt)
                    modified_line = llm_chain.run(claim_text=line.strip())
                    modified_purpose_lines.append(modified_line)

            # 수정된 텍스트를 문서에 반영
            doc.paragraphs[claim_purpose_index + 1].text = "\n".join(modified_purpose_lines)

    # 청구 원인 부분을 찾고 수정
    claim_reason_index = find_section(doc.paragraphs, claim_reason_keywords)
    if claim_reason_index is not None:
        claim_reason_text = doc.paragraphs[claim_reason_index + 1].text
        if claim_reason_text:
            claim_reason_lines = claim_reason_text.split("\n")
            modified_reason_lines = []

            # 각 줄을 LLM을 통해 수정
            for line in claim_reason_lines:
                if line.strip():
                    llm_chain = LLMChain(llm=llm, prompt=prompt)
                    modified_line = llm_chain.run(claim_text=line.strip())
                    modified_reason_lines.append(modified_line)

            # 수정된 텍스트를 문서에 반영
            doc.paragraphs[claim_reason_index + 1].text = "\n".join(modified_reason_lines)

    # 수정된 문서를 파일 시스템에 저장
    modified_file_path = "fixed_document.docx"
    doc.save(modified_file_path)

    # 파일 경로를 반환
    return modified_file_path
