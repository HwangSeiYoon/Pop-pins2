# 파이썬 교재 PDF RAG 벡터 생성기

파이썬 교재 PDF 파일들을 읽어 임베딩하여 FAISS 벡터 데이터베이스에 저장하는 standalone 도구입니다.

## 📋 기능

- 📄 PDF 파일 자동 처리
- 🔄 기존 벡터 DB에 새 문서 추가 지원
- 🚫 중복 처리 방지 (이미 처리된 파일 자동 스킵)
- 🔌 유연한 임베딩 모델 지원 (Gemini, OpenAI, AWS Bedrock)
- 📊 처리 상태 메타데이터 관리
- 🎯 Standalone 동작 (독립적으로 실행 가능)

## 📦 설치

### 1. 필요한 패키지 설치

```bash
# 기본 패키지 설치
pip install -r requirements.txt

# 사용할 임베딩 모델 선택에 따라 추가 설치
# Gemini 사용 시 (기본값)
pip install langchain-google-genai

# OpenAI 사용 시
pip install langchain-openai

# AWS Bedrock 사용 시
pip install boto3 langchain-aws
```

### 2. 환경 변수 설정

#### 방법 1: .env 파일 사용 (권장)

스크립트 디렉토리에 `.env` 파일을 생성하고 API 키를 설정하세요:

```bash
# .env 파일 생성
# Windows (PowerShell)
New-Item -Path ".env" -ItemType File

# Linux/Mac
touch .env
```

`.env` 파일 내용:
```env
# Gemini 사용 시 (GEMINI_API_KEY 또는 GOOGLE_API_KEY 둘 다 지원)
GEMINI_API_KEY=your-google-api-key
# 또는
GOOGLE_API_KEY=your-google-api-key
```

또는 다른 모델 사용 시:
```env
# Gemini 사용 시
GEMINI_API_KEY=your-google-api-key
# 또는 GOOGLE_API_KEY=your-google-api-key

# OpenAI 사용 시
OPENAI_API_KEY=your-openai-api-key

# AWS Bedrock 사용 시
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_DEFAULT_REGION=ap-northeast-2
```

스크립트는 자동으로 `.env` 파일을 로드합니다.

#### 방법 2: 환경 변수 직접 설정

#### Gemini 사용 시 (권장)
```bash
# Windows (PowerShell) - GEMINI_API_KEY 또는 GOOGLE_API_KEY 둘 다 지원
$env:GEMINI_API_KEY="your-google-api-key"
# 또는
$env:GOOGLE_API_KEY="your-google-api-key"

# Windows (CMD)
set GEMINI_API_KEY=your-google-api-key
# 또는
set GOOGLE_API_KEY=your-google-api-key

# Linux/Mac
export GEMINI_API_KEY="your-google-api-key"
# 또는
export GOOGLE_API_KEY="your-google-api-key"
```

#### OpenAI 사용 시
```bash
# Windows (PowerShell)
$env:OPENAI_API_KEY="your-openai-api-key"

# Windows (CMD)
set OPENAI_API_KEY=your-openai-api-key

# Linux/Mac
export OPENAI_API_KEY="your-openai-api-key"
```

#### AWS Bedrock 사용 시
```bash
# Windows (PowerShell)
$env:AWS_ACCESS_KEY_ID="your-access-key-id"
$env:AWS_SECRET_ACCESS_KEY="your-secret-access-key"
$env:AWS_DEFAULT_REGION="ap-northeast-2"

# Linux/Mac
export AWS_ACCESS_KEY_ID="your-access-key-id"
export AWS_SECRET_ACCESS_KEY="your-secret-access-key"
export AWS_DEFAULT_REGION="ap-northeast-2"
```

## 🚀 사용 방법

### 1. PDF 파일 준비

먼저 `pdfs` 디렉토리를 생성하고 파이썬 교재 PDF 파일들을 넣어주세요:

```bash
# 디렉토리 생성
mkdir pdfs

# PDF 파일들을 pdfs 폴더에 복사
# 예: pdfs/python_basics.pdf, pdfs/python_advanced.pdf 등
```

### 2. 명령줄 인터페이스

#### 기본 사용 (Gemini 임베딩, 기본 경로)
```bash
python python_textbook_rag_generator.py
```

#### OpenAI 임베딩 사용
```bash
python python_textbook_rag_generator.py --embedding-model openai
```

#### 커스텀 소스 디렉토리 지정
```bash
python python_textbook_rag_generator.py --source-dir "C:/path/to/your/pdfs"
```

#### 커스텀 출력 디렉토리 지정
```bash
python python_textbook_rag_generator.py --output-dir "C:/path/to/output"
```

#### DB 이름 지정
```bash
python python_textbook_rag_generator.py --db-name "my_python_db"
```

#### API 키 직접 지정
```bash
python python_textbook_rag_generator.py --api-key "your-api-key"
```

#### 청크 크기 조정
```bash
python python_textbook_rag_generator.py --chunk-size 1500 --chunk-overlap 300
```

#### 모든 옵션 함께 사용
```bash
python python_textbook_rag_generator.py \
    --db-name "python_textbook_db" \
    --source-dir "./pdfs" \
    --output-dir "./vector_db" \
    --embedding-model gemini \
    --chunk-size 1000 \
    --chunk-overlap 200
```

### 3. Python 코드에서 사용

```python
from python_textbook_rag_generator import PythonTextbookRAGGenerator

# 생성기 초기화 (Gemini 사용)
generator = PythonTextbookRAGGenerator(
    embedding_model="gemini",
    chunk_size=1000,
    chunk_overlap=200
)

# 벡터 DB 생성
generator.generate_vector_db(
    db_name="python_textbook_db",
    source_dir="./pdfs",      # 선택사항
    output_dir="./vector_db"   # 선택사항
)
```

## 📁 기본 경로

- **소스 디렉토리**: `./pdfs/` (스크립트와 같은 디렉토리의 pdfs 폴더)
- **출력 디렉토리**: `./vector_db/` (스크립트와 같은 디렉토리의 vector_db 폴더)

## 📂 파일 구조

```
RAG vector generator/
├── python_textbook_rag_generator.py  # 메인 스크립트
├── requirements.txt                   # 패키지 의존성
├── README.md                          # 이 파일
├── .env                               # 환경 변수 파일 (API 키 설정)
├── pdfs/                              # PDF 파일들을 넣을 디렉토리
│   ├── python_basics.pdf
│   ├── python_advanced.pdf
│   └── ...
└── vector_db/                         # 벡터 DB 저장 디렉토리
    ├── python_textbook_db/            # 벡터 DB 파일들
    │   ├── index.faiss
    │   └── index.pkl
    └── python_textbook_db_metadata.json  # 처리된 파일 메타데이터
```

## 🔄 중복 처리 방지

스크립트는 각 PDF 파일의 해시값과 파일 메타데이터를 저장하여 이미 처리된 파일을 자동으로 건너뜁니다. 파일이 수정된 경우에만 다시 처리됩니다.

## ⚙️ 설정 옵션

### 임베딩 모델

- **gemini** (기본값): Google Gemini Embedding API 사용
- **openai**: OpenAI Embedding API 사용
- **bedrock**: AWS Bedrock Titan Embedding 사용

### 청크 설정

- **chunk_size**: 텍스트를 나눌 청크의 크기 (기본값: 1000자)
- **chunk_overlap**: 청크 간 겹치는 문자 수 (기본값: 200자)

교재의 특성에 따라 조정 가능:
- 짧은 예제가 많은 경우: `chunk_size=800, chunk_overlap=150`
- 긴 설명이 많은 경우: `chunk_size=1500, chunk_overlap=300`

## ❌ 에러 처리

스크립트는 명확한 에러 메시지를 제공합니다:

- **API 키 누락**: 환경 변수 또는 `.env` 파일 설정 안내
- **패키지 누락**: 필요한 패키지 설치 안내
- **파일 없음**: 파일 경로 확인 안내
- **벡터 DB 로드 실패**: 새로 생성 또는 문제 해결 안내

### API 키 관련 문제 해결

API 키 오류가 발생하면:
1. `.env` 파일이 스크립트와 같은 디렉토리에 있는지 확인
2. `.env` 파일에 올바른 환경 변수명이 있는지 확인:
   - Gemini: `GEMINI_API_KEY` 또는 `GOOGLE_API_KEY`
   - OpenAI: `OPENAI_API_KEY`
   - AWS Bedrock: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
3. 환경 변수를 직접 설정했는지 확인
4. `.env` 파일에 공백이나 따옴표가 없는지 확인 (예: `GEMINI_API_KEY=your-key` 형식)

## 📝 예제 출력

정상적으로 작동하면 다음과 같은 출력을 볼 수 있습니다:

```
============================================================
파이썬 교재 PDF 벡터 데이터베이스 생성 시작
  DB 이름: python_textbook_db
  소스 디렉토리: C:\...\RAG vector generator\pdfs
  출력 디렉토리: C:\...\RAG vector generator\vector_db
============================================================
발견된 PDF 파일 수: 5
새로 처리할 파일 수: 5
새로운 벡터 DB 생성
PDF 처리 중: python_basics.pdf
  → 120 페이지에서 350 개 청크 생성
PDF 처리 중: python_advanced.pdf
  → 200 페이지에서 580 개 청크 생성
...
벡터 DB에 1500 개 청크 추가 중...
벡터 DB 업데이트 완료
벡터 DB 저장 완료: C:\...\vector_db\python_textbook_db
메타데이터 저장 완료: C:\...\vector_db\python_textbook_db_metadata.json
============================================================
벡터 데이터베이스 생성 완료!
============================================================
✅ 작업이 성공적으로 완료되었습니다!
```

## 🔍 벡터 DB 사용하기

생성된 벡터 DB는 다음과 같이 사용할 수 있습니다:

```python
import os
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# 임베딩 모델 초기화 (생성 시 사용한 것과 동일해야 함)
# GEMINI_API_KEY 또는 GOOGLE_API_KEY 둘 다 지원
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=api_key
)

# 벡터 DB 로드
vector_store = FAISS.load_local(
    "./vector_db/python_textbook_db",
    embeddings,
    allow_dangerous_deserialization=True
)

# 유사 문서 검색
query = "파이썬 리스트와 튜플의 차이점은?"
docs = vector_store.similarity_search(query, k=3)

for doc in docs:
    print(f"출처: {doc.metadata['file_name']}")
    print(f"내용: {doc.page_content[:200]}...")
    print("-" * 50)
```

## 💡 팁

1. **대량의 PDF 처리**: 많은 PDF 파일을 처리할 때는 시간이 오래 걸릴 수 있습니다. 중단되더라도 이미 처리된 파일은 건너뛰므로 다시 실행하면 됩니다.

2. **청크 크기 조정**: 교재의 특성에 맞게 청크 크기를 조정하면 검색 품질이 향상될 수 있습니다.

3. **임베딩 모델 선택**: 
   - Gemini: 무료 할당량이 넉넉하고 한국어 지원이 좋음
   - OpenAI: 높은 품질이지만 비용 발생
   - Bedrock: AWS 인프라 사용 시 적합

4. **메타데이터 확인**: `*_metadata.json` 파일을 확인하면 처리된 파일 목록과 청크 수를 확인할 수 있습니다.

## 📄 라이선스

이 도구는 교육 목적으로 자유롭게 사용할 수 있습니다.

