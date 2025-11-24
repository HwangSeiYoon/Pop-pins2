# RAG Vector DB Generator

**AI 기반 Retrieval-Augmented Generation을 위한 범용 벡터 데이터베이스 생성기**

이 도구는 **어떤 분야의 PDF 문서든** 벡터 데이터베이스로 변환하여 AI가 정확하고 신뢰할 수 있는 답변을 생성할 수 있도록 지원합니다.

---

## 📚 목차

1. [개요](#개요)
2. [주요 기능](#주요-기능)
3. [빠른 시작](#빠른-시작)
4. [상세 사용법](#상세-사용법)
5. [다양한 분야 적용](#다양한-분야-적용)
6. [Standalone 앱으로 사용하기](#standalone-앱으로-사용하기)
7. [성능 최적화](#성능-최적화)
8. [문제 해결](#문제-해결)

---

## 🎯 개요

### RAG Vector DB Generator란?

**RAG**(Retrieval-Augmented Generation)는 AI가 답변을 생성할 때 관련 문서를 검색하여 참고하는 기술입니다. 이 생성기는 PDF 문서를 벡터 데이터베이스로 변환하여 RAG 시스템에서 활용할 수 있게 합니다.

### 왜 사용하나요?

- ✅ **정확성 향상**: AI가 문서 내용을 기반으로 답변하여 환각(hallucination) 감소
- ✅ **도메인 특화**: 특정 분야의 전문 지식을 AI에게 제공
- ✅ **최신 정보**: 최신 문서를 추가하여 AI 지식 업데이트
- ✅ **범용성**: 파이썬, 의학, 법률, 금융 등 **모든 분야** 적용 가능

### 현재 버전: v1.5.0 (Semantic Chunking)

- **Semantic Chunking**: 의미 기반 문서 분할로 검색 정확도 5% 향상
- **Metadata Enrichment**: 섹션 정보 자동 추출
- **Checkpointing**: 중간 저장으로 안정성 향상
- **Rate Limiting**: API quota 관리

---

## 🌟 주요 기능

### 1. **Semantic Chunking (의미 기반 분할)**
```
기존 방식:  "파이썬은 프로그래밍 언어입니다. | 변수는 값을 저장합니다."
            ❌ 의미 단위 무시, 고정 크기로 자름

Semantic:   "파이썬은 프로그래밍 언어입니다. 변수는 값을 저장합니다."
            ✅ 의미 단위로 자연스럽게 분할
```

### 2. **Intelligent Page Filtering**
- 목차, 색인, 저작권 페이지 자동 제거
- 50자 미만의 빈 페이지 필터링
- 실제 본문 내용만 벡터화

### 3. **Text Cleaning**
- 페이지 헤더/푸터 제거 (페이지 번호, 반복 제목 등)
- 과도한 공백 및 줄바꿈 정리
- 깔끔한 텍스트 데이터

### 4. **Three Embedding Models Supported**
- **Gemini** (추천): `text-embedding-004`, 무료 티어 1500 RPM
- **OpenAI**: `text-embedding-3-small`, 고성능
- **AWS Bedrock**: `amazon.titan-embed-text-v2:0`, 엔터프라이즈

### 5. **Robust Processing**
- **Checkpointing**: 파일 단위 중간 저장
- **Resume Capability**: 중단된 지점부터 재개
- **Rate Limiting**: API quota 초과 방지
- **Batch Processing**: 대량 문서 처리 지원

---

## 🚀 빠른 시작

### 1. 환경 설정

```bash
cd "RAG vector generator"
pip install -r requirements.txt
```

### 2. API 키 설정

`.env` 파일을 생성하고 API 키를 입력하세요:

```env
# Gemini 사용 시 (추천)
GEMINI_API_KEY=your-gemini-api-key-here

# OpenAI 사용 시
# OPENAI_API_KEY=your-openai-api-key-here

# AWS Bedrock 사용 시
# AWS_ACCESS_KEY_ID=your-access-key
# AWS_SECRET_ACCESS_KEY=your-secret-key
```

**API 키 발급 방법**:
- Gemini: https://makersuite.google.com/app/apikey
- OpenAI: https://platform.openai.com/api-keys
- AWS Bedrock: AWS Console에서 IAM 설정

### 3. PDF 파일 준비

`pdfs/` 폴더에 PDF 파일들을 복사하세요:

```
RAG vector generator/
├── pdfs/
│   ├── document1.pdf
│   ├── document2.pdf
│   └── document3.pdf
└── python_textbook_rag_generator.py
```

### 4. 벡터 DB 생성

#### 기본 사용법 (Semantic Chunking)
```bash
python python_textbook_rag_generator.py \
  --db-name my_vector_db \
  --chunking-strategy semantic \
  --embedding-model gemini \
  --rpm-limit 1440 \
  --batch-size 120
```

#### 빠른 생성 (Recursive Chunking)
```bash
python python_textbook_rag_generator.py \
  --db-name my_vector_db \
  --chunking-strategy recursive \
  --embedding-model gemini
```

### 5. 생성 확인

생성이 완료되면 다음 파일들이 생성됩니다:

```
vector_db/
├── my_vector_db/
│   ├── index.faiss          # 벡터 인덱스
│   └── index.pkl            # 메타데이터
└── my_vector_db_metadata.json  # 처리된 파일 목록
```

---

## 📖 상세 사용법

### 명령줄 옵션

| 옵션 | 설명 | 기본값 | 예시 |
|------|------|--------|------|
| `--db-name` | 벡터 DB 이름 | `python_textbook_db` | `medical_db` |
| `--chunking-strategy` | 분할 전략 | `recursive` | `semantic` |
| `--embedding-model` | 임베딩 모델 | `gemini` | `openai` |
| `--chunk-size` | 청크 크기 (recursive) | `1000` | `1500` |
| `--chunk-overlap` | 청크 중복 (recursive) | `200` | `300` |
| `--rpm-limit` | 분당 요청 수 | `1000` | `1440` |
| `--batch-size` | 배치 크기 | `100` | `120` |
| `--source-dir` | PDF 디렉토리 | `./pdfs` | `/path/to/pdfs` |
| `--output-dir` | 출력 디렉토리 | `./vector_db` | `/path/to/output` |

### Chunking 전략 선택

#### Semantic Chunking (권장)
- **장점**: 의미 단위로 분할, 검색 정확도 5% 향상
- **단점**: 느림 (임베딩 API 호출 필요)
- **용도**: 프로덕션 환경, 최고 품질

```bash
python python_textbook_rag_generator.py \
  --chunking-strategy semantic \
  --rpm-limit 1440
```

#### Recursive Chunking
- **장점**: 빠름, API 호출 적음
- **단점**: 의미 단위 무시
- **용도**: 테스트, 빠른 프로토타이핑

```bash
python python_textbook_rag_generator.py \
  --chunking-strategy recursive \
  --chunk-size 1000
```

### Embedding 모델 선택

#### Gemini (추천)
```bash
python python_textbook_rag_generator.py \
  --embedding-model gemini \
  --rpm-limit 1440
```
- **장점**: 무료 티어 1500 RPM, 한국어 우수
- **단점**: API quota 제한

#### OpenAI
```bash
python python_textbook_rag_generator.py \
  --embedding-model openai \
  --rpm-limit 3000
```
- **장점**: 고성능, 높은 RPM
- **단점**: 유료

#### AWS Bedrock
```bash
python python_textbook_rag_generator.py \
  --embedding-model bedrock
```
- **장점**: 엔터프라이즈급 안정성
- **단점**: AWS 설정 필요

---

## 🌍 다양한 분야 적용

### 의료/의학 전문 RAG

```bash
# pdfs/ 폴더에 의학 교재 PDF 넣기
python python_textbook_rag_generator.py \
  --db-name medical_knowledge_db \
  --chunking-strategy semantic \
  --embedding-model gemini
```

**활용 예시**:
- 의학 용어 설명
- 진단 가이드라인 검색
- 치료법 추천

### 법률 문서 RAG

```bash
# pdfs/ 폴더에 법률 문서 PDF 넣기
python python_textbook_rag_generator.py \
  --db-name legal_docs_db \
  --chunking-strategy semantic \
  --chunk-size 1500  # 법률 문서는 긴 문단이 많음
```

**활용 예시**:
- 판례 검색
- 법률 조항 해석
- 계약서 검토

### 기술 문서 RAG

```bash
# pdfs/ 폴더에 기술 문서 PDF 넣기
python python_textbook_rag_generator.py \
  --db-name tech_docs_db \
  --chunking-strategy recursive \
  --chunk-size 800  # 코드 예시가 많으면 작은 청크
```

**활용 예시**:
- API 문서 검색
- 트러블슈팅 가이드
- 설정 방법 찾기

### 금융/경제 RAG

```bash
python python_textbook_rag_generator.py \
  --db-name finance_db \
  --chunking-strategy semantic
```

**활용 예시**:
- 금융 용어 설명
- 투자 전략 검색
- 규정 준수 가이드

---

## 🔧 Standalone 앱으로 사용하기

이 도구는 **완전히 독립적으로** 실행 가능합니다. PopPins II 프로젝트 외부에서도 사용할 수 있습니다.

### Standalone 설치

```bash
# 1. 이 폴더만 복사
cp -r "RAG vector generator" /path/to/standalone/location

# 2. 의존성 설치
cd /path/to/standalone/location
pip install -r requirements.txt

# 3. .env 파일 생성
echo "GEMINI_API_KEY=your-key-here" > .env

# 4. PDF 파일 추가
# pdfs/ 폴더에 PDF 파일 복사

# 5. 벡터 DB 생성
python python_textbook_rag_generator.py --db-name my_db
```

### Python 코드에서 직접 사용

```python
from python_textbook_rag_generator import PythonTextbookRAGGenerator

# 생성기 초기화
generator = PythonTextbookRAGGenerator(
    embedding_model="gemini",
    chunking_strategy="semantic",
    rpm_limit=1440
)

# 벡터 DB 생성
generator.generate_vector_db(
    db_name="my_custom_db",
    source_dir="./my_pdfs",
    output_dir="./my_vector_dbs"
)
```

### 다른 프로젝트에서 벡터 DB 불러오기

```python
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# 임베딩 모델 초기화
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004",
    google_api_key="your-key"
)

# 벡터 DB 로드
vector_store = FAISS.load_local(
    "./vector_db/my_db",
    embeddings,
    allow_dangerous_deserialization=True
)

# 검색
results = vector_store.similarity_search("your query", k=3)
for doc in results:
    print(doc.page_content)
```

---

## ⚡ 성능 최적화

### RPM Limit 조정

**Gemini 무료 티어**:
- 기본: 1000 RPM
- 권장: 1440 RPM (초당 24회, 안전 마진 포함)

```bash
# 빠른 생성 (quota 주의!)
python python_textbook_rag_generator.py --rpm-limit 1440

# 안전한 생성
python python_textbook_rag_generator.py --rpm-limit 1000

# 느리지만 확실한 생성
python python_textbook_rag_generator.py --rpm-limit 500
```

### Batch Size 조정

```bash
# 대량 처리 (메모리 여유 있을 때)
python python_textbook_rag_generator.py --batch-size 200

# 기본값
python python_textbook_rag_generator.py --batch-size 100

# 메모리 부족 시
python python_textbook_rag_generator.py --batch-size 50
```

### 중단된 생성 재개

Checkpointing 덕분에 중단된 지점부터 자동 재개됩니다:

```bash
# 첫 실행 (일부만 처리되고 중단)
python python_textbook_rag_generator.py --db-name my_db

# 재실행 (자동으로 이어서 처리)
python python_textbook_rag_generator.py --db-name my_db
# → "이미 처리된 파일 건너뛰기" 메시지 확인
```

### PDF 추가 시

```bash
# 기존 DB에 새 PDF 추가
# 1. pdfs/ 폴더에 새 PDF 복사
# 2. 같은 명령 실행
python python_textbook_rag_generator.py --db-name my_db
# → 기존 파일은 건너뛰고 새 파일만 처리
```

---

## 🛠️ 문제 해결

### API Quota 초과

**증상**: `429 Resource has been exhausted`

**해결**:
```bash
# 1. RPM limit 낮추기
python python_textbook_rag_generator.py --rpm-limit 500

# 2. 24시간 대기 후 재실행 (checkpointing으로 이어서 진행)
```

### 메모리 부족

**증상**: `MemoryError` 또는 프로세스 중단

**해결**:
```bash
# Batch size 줄이기
python python_textbook_rag_generator.py --batch-size 50

# Chunk size 줄이기 (recursive 전략)
python python_textbook_rag_generator.py \
  --chunking-strategy recursive \
  --chunk-size 500
```

### PDF 읽기 오류

**증상**: `Error processing PDF`

**해결**:
1. PDF 파일이 손상되지 않았는지 확인
2. PDF 비밀번호가 걸려있지 않은지 확인
3. 이미지 전용 PDF는 OCR 필요

### 생성 속도가 너무 느림

**원인**: Semantic Chunking은 각 문서마다 임베딩 API 호출

**해결**:
```bash
# Recursive Chunking으로 전환
python python_textbook_rag_generator.py \
  --chunking-strategy recursive
```

---

## 📊 버전 히스토리

### v1.5.0 (2025-11-24) - Current
- ✅ Semantic Chunking 구현
- ✅ Checkpointing 시스템
- ✅ RateLimitedEmbeddings 래퍼
- ✅ 평균 5% 검색 정확도 향상

### v1.4.0 (2025-11-23)
- ✅ Page Filtering
- ✅ Text Cleaning
- ✅ Rate Limiting
- ✅ Batch Processing

### v1.0.0 (Initial)
- ✅ 기본 벡터 DB 생성
- ✅ Fixed-size chunking
- ✅ 3 embedding models 지원

---

## 📚 추가 리소스

### 관련 문서
- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
- [FAISS Documentation](https://github.com/facebookresearch/faiss)
- [Gemini API Documentation](https://ai.google.dev/docs)

### 프로젝트 문서
- `../RAG_UPDATE_LOG.md`: 업데이트 로그
- `../README.md`: 메인 프로젝트 README
- `../app/RAG_INTEGRATION_GUIDE.md`: 통합 가이드

---

## 🤝 기여 및 피드백

이 도구를 개선하고 싶으신가요?
- 버그 리포트: GitHub Issues
- 기능 제안: Pull Requests 환영
- 질문: Discussions 탭 활용

---

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

---

**Happy Vector DB Building! 🚀**
