from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
import pandas as pd

# 텍스트 스플리터 함수
def split_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return text_splitter.split_text(text)

# 텍스트 임베딩 함수
def embed_texts(text_chunks, vector_store):
    # 임베딩된 텍스트를 기존 벡터 스토어에 추가
    vector_store.add_texts(text_chunks)

# ChromaDB 초기화 함수
def initial_chroma_db():
    # 임베딩을 위한 ChromaDB 초기화 (모든 CSV 파일에서 데이터를 추가할 수 있도록 함)
    embeddings = OpenAIEmbeddings()
    vector_store = Chroma(collection_name="legal_documents", embedding_function=embeddings)

    # 처리할 CSV 파일 경로 리스트와 해당 파일의 컬럼명
    csv_files = [
        {'file': './datas/law/건축관련법.csv', 'column': '건축'},
        {'file': './datas/law/소방관련법.csv', 'column': '소방'},
        {'file': './datas/law/의료관련법.csv', 'column': '의료'}
    ]
    
    # 각 CSV 파일에 대해 반복 처리
    for file_info in csv_files:
        # CSV 파일 로드 및 텍스트 추출
        df = pd.read_csv(file_info['file'])
        texts = df[file_info['column']].tolist()  # 해당 CSV 파일의 컬럼명으로 텍스트 추출

        # 텍스트 스플리팅 및 임베딩
        text_chunks = split_text(" ".join(texts))  # 모든 텍스트를 결합하여 스플리팅
        embed_texts(text_chunks, vector_store)  # 임베딩하고 ChromaDB에 저장
    
    return vector_store  # 모든 CSV 파일을 처리한 후 최종 벡터 스토어 반환
