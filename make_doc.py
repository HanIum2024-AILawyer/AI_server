import os
from docx import Document
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.llms import Ollama

# Ollama LLM 초기화
llm = Ollama(model="mistral:latest")

# 프롬프트 템플릿 설정
lawsuit_prompt = PromptTemplate(
    input_variables=["case_description", "claim_amount"],
    template=(
        "다음 사건에 대한 사 건 서술과 청구 금액을 읽고, 사건명, 청구취지, 청구원인을 생성해줘. 반드시 한국어로만 답변해야 해.\n"
        "1. 사건명 (15자 이내). ~~의 소. 라고 출력해줘.\n"
        "2. 청구취지 항목은 다음과 같이 구성되어야 해. 1번 항목은 사건 서술과 청구 금액을 읽고 자동으로 생성하지만, "
        "2번과 3번 항목은 아래와 같이 고정된 문구를 사용해:\n"
        "1. {case_description}에 따라 피고는 원고에게 {claim_amount}원을 지급해야 한다.\n"
        "2. 소송비용은 피고가 부담한다.\n"
        "3. 제 1항은 가집행할 수 있다.\n"
        "이라는 판결을 구함.\n\n"
        "3. 청구원인 (육하원칙에 따라 사건 설명)\n\n"
        "사건 서술: {case_description}\n"
        "청구 금액: {claim_amount}\n"
        "---사건명 예시---\n"
        "대여금 청구의 소\n"
        "----------------\n"
    )
)

accusation_prompt = PromptTemplate(
    input_variables=["case_description", "claim_amount"],
    template=(
        "다음 사건에 대한 사건 서술과 청구 금액을 읽고, 고소장을 작성해줘. 반드시 한국어로만 작성해줘.\n"
        "1. 사건명 (15자 이내). 고소장으로 출력.\n"
        "2. 고소취지 항목은 다음과 같이 구성되어야 해. 1번 항목은 사건 서술과 청구 금액을 읽고 자동으로 생성하지만, "
        "2번과 3번 항목은 아래와 같이 고정된 문구를 사용해:\n"
        "1. {case_description}에 따라 피고소인은 원고에게 {claim_amount}원을 지급해야 한다.\n"
        "2. 소송비용은 피고소인이 부담한다.\n"
        "3. 제 1항은 가집행할 수 있다.\n"
        "이라는 판결을 구함.\n\n"
        "3. 범죄사실 및 고소이유 (육하원칙에 따라 사건 설명)\n\n"
        "사건 서술: {case_description}\n"
        "청구 금액: {claim_amount}\n"
        "---사건명 예시---\n"
        "사기죄 고소장\n"
        "----------------\n"
    )
)

def make_doc(input_data: dict):
    doc_type = input_data["doc_type"]
    claim_count = input_data["claim_count"]
    
    # 101: 소송장, 201: 고소장 분기 처리
    if doc_type == "101":
        # 소송장 템플릿 파일 로드 및 프롬프트 선택
        word_file_path = f"./datas/word/word_소송장_{claim_count}명.docx"
        prompt = lawsuit_prompt
    elif doc_type == "201":
        # 고소장 템플릿 파일 로드 및 프롬프트 선택
        word_file_path = f"./datas/word/word_고소장_{claim_count}명.docx"
        prompt = accusation_prompt
    else:
        raise ValueError(f"Invalid doc_type: {doc_type}")

    # 템플릿 파일이 존재하는지 확인
    if not os.path.exists(word_file_path):
        raise FileNotFoundError(f"Template file not found: {word_file_path}")

    doc = Document(word_file_path)

    # LLMChain을 사용해 AI 응답 생성
    llm_chain = LLMChain(llm=llm, prompt=prompt)
    generated_text = llm_chain.run(case_description=input_data["case_description"], claim_amount=input_data["claim_amount"])

    # 생성된 텍스트 파싱
    lines = generated_text.split("\n")
    case_name = lines[0].replace("사건명: ", "").strip()
    claim_purpose = lines[1].replace("청구취지: ", "").strip()
    claim_reason = lines[2].replace("청구원인: ", "").strip()

    # 텍스트 대체
    for paragraph in doc.paragraphs:
        paragraph.text = paragraph.text.replace("claim_name", case_name)
        paragraph.text = paragraph.text.replace("claim_purpose", claim_purpose)
        paragraph.text = paragraph.text.replace("claim_reason", claim_reason)

    # 수정된 문서를 파일로 저장
    output_file_name = "./output/new_document.docx"
    os.makedirs(os.path.dirname(output_file_name), exist_ok=True)  # 디렉토리가 없으면 생성
    doc.save(output_file_name)

    # 파일이 생성되었는지 확인
    if not os.path.exists(output_file_name):
        raise FileNotFoundError(f"Failed to create file: {output_file_name}")

    # AI가 생성한 코멘트를 반환 (원하는 경우 추가 가능)
    ai_comment = f"사건명: {case_name}, 청구취지: {claim_purpose}, 청구원인: {claim_reason}"

    return {"doc": output_file_name, "aiComment": ai_comment}
