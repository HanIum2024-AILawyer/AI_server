import os
from docx import Document
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.llms import Ollama

# Ollama LLM 초기화
llm = Ollama(model="mistral:latest")

# 프롬프트 템플릿 설정
prompt = PromptTemplate(
    input_variables=["case_description", "claim_amount"],
    template=(
        "다음 사건에 대한 사건 서술과 청구 금액을 읽고, 사건명, 청구취지, 청구원인을 생성해줘. 반드시 한국어로만 답변해야 해."
        "1. 사건명 (15자 이내). ~~의 소. 라고 출력해줘. "
        "2. 청구취지 (20자 이내로 간결하게, 청구하는 금액 명시. 아래 예시를 보고 2번 3번은 특별한 상황 제외하면 그대로 출력할 것.)"
        "3. 청구원인 (육하원칙에 따라 사건 설명)\n\n"
        "사건 서술: {case_description}\n"
        "청구 금액: {claim_amount}"
        "아래는 출력 예시야."
        "---사건명 예시---"
        "대여금 청구의 소"
        "----------------"
        "--청구취지 예시--"
        "1. 피고는 원고에게 55,000,000원 및 이에 대하여 소장부본 송달 다음 날부터 다 갚는 날까지 연 12%의 비율로 계산한 돈을 지급하라."
        "2. 소송비용은 피고가 부담한다."
        "3. 제1항은 가집행할 수 있다."
        "라는 판결을 구함."
        "----------------"
        "--청구원인 예시--"
        "1. 채권자와 채무자는 평상시 잘아는 사이로 채무자가 채권자에게 카드대금을 납부하여야 한다며 금 △,△△△,△△△원을 대여하여 주면 이틀정도 사용하고 갚는다고 하여 채권자는 △△△△. △△. △△. 채권자가 그동안 납부하던 보험에서 약관대출을 받아 △,△△△,△△△원을 현금으로 대여하여 주었고, △△△△. △△. △△. 에△,△△△,△△△원을 채무자의 통장으로 이체하여 주었습니다."
        "2. 그러나 채무자는 위 금원을 빌려간 이후 위 대여금을 지급하지 않아 채권자가 위 대여금에 대한 지급을 요구하자 조금만 더 기다려 달라면서 이자를 지급하여 주겠다고 하며 계속하여 조금씩의 이자를 현금으로 지급하더니 얼마 지나지 않아 이자 마저도 지급하지 아니하여 채권자는 채무자에게 위 대여금 전액의 상환을 요구하였으나, 채무자는 현재까지 이에 불응하고 있습니다."
        "3. 따라서 채권자는 채무자에게 위 금원의 지급을 수차에 걸쳐 지급하여 줄 것을 독촉하였으나 차일피일 기일만 지연하고 있고, 신청일 현재까지 하등의 이유없이 그 지급에 불응하고 있으므로 채권자는 신청취지와 같은 대여금과 소정의 손해금율에 의한 금원을 지급받고자 본 신청에 이른것입니다."
        "----------------"
    )
)

def make_doc(input_data: dict):
    # 피고 숫자에 맞는 Word 템플릿 파일 로드
    claim_count = input_data["claim_count"]  # API에서 받아오는 'claim_count'로 수정
    word_file_path = f"./datas/word/word_소송장_{claim_count}명.docx"
    
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
