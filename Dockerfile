# 베이스 이미지 (Ubuntu 기반)
FROM ubuntu:20.04

# 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    curl \
    sudo \
    && apt-get clean

# Ollama 설치 스크립트 다운로드 및 실행
RUN curl -o- https://ollama.com/download.sh | bash

# Ollama가 설치된 경로를 PATH에 추가
ENV PATH="/root/.ollama/bin:${PATH}"

# Ollama 모델 다운로드 (Mistral 모델)
RUN ollama pull mistral

# Python 및 필요한 라이브러리 설치
RUN apt-get install -y python3.8 python3-pip

# FastAPI 관련 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# FastAPI 실행 (uvicorn)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8081"]
