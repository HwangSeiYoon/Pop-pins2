# RAG Vector Generator 사용 매뉴얼

## 📖 빠른 시작 가이드

### 1단계: 설치
```bash
cd "RAG vector generator"
pip install -r requirements.txt
```

### 2단계: API 키 설정
`.env` 파일 생성:
```env
GEMINI_API_KEY=your-api-key-here
```

### 3단계: PDF 준비
`pdfs/` 폴더에 PDF 파일 복사

### 4단계: 실행
```bash
python python_textbook_rag_generator.py --db-name my_db --chunking-strategy semantic
```

---

## 🎓 사용 시나리오

### 시나리오 1: 파이썬 교육 RAG (기본)

```bash
# 1. PDF 준비
# pdfs/ 폴더에 파이썬 교재 PDF들 복사

# 2. 벡터 DB 생성
python python_textbook_rag_generator.py \
  --db-name python_textbook_db \
  --chunking-strategy semantic \
  --embedding-model gemini
```

**결과**: `vector_db/python_textbook_db/` 생성

---

### 시나리오 2: 의료 지식 베이스 구축

```bash
# 1. 의학 교재 PDF 준비
# pdfs/ 폴더에 의학 관련 PDF 복사

# 2. 벡터 DB 생성 (큰 청크 사용)
python python_textbook_rag_generator.py \
  --db-name medical_knowledge_db \
  --chunking-strategy semantic \
  --chunk-size 1500 \
  --embedding-model gemini
```

**활용**: 의료 상담 봇, 증상 검색 시스템

---

### 시나리오 3: 법률 문서 검색 시스템

```bash
# 1. 법률 문서 PDF 준비

# 2. 벡터 DB 생성
python python_textbook_rag_generator.py \
  --db-name legal_docs_db \
  --chunking-strategy recursive \
  --chunk-size 1500 \
  --chunk-overlap 300
```

**활용**: 판례 검색, 법률 조항 참조

---

### 시나리오 4: 회사 내부 문서 지식 베이스

```bash
# 1. 회사 문서 PDF 준비 (매뉴얼, 가이드 등)

# 2. 벡터 DB 생성
python python_textbook_rag_generator.py \
  --db-name company_docs_db \
  --source-dir /path/to/company/docs \
  --output-dir /path/to/output \
  --chunking-strategy semantic
```

**활용**: 직원 질의응답 시스템, 온보딩 자료

---

## 🛠️ 시나리오별 최적 설정

### 코드/기술 문서
```bash
--chunking-strategy recursive
--chunk-size 800
--chunk-overlap 150
```
이유: 코드 블록을 잘게 나누지 않기 위해

### 설명 중심 문서
```bash
--chunking-strategy semantic
--chunk-size 1200
```
이유: 의미 단위로 분할

### 법률/계약서
```bash
--chunking-strategy semantic
--chunk-size 1500
--chunk-overlap 300
```
이유: 긴 문단, 많은 중복 필요

---

## 🔄 일반적인 작업 흐름

### 새 프로젝트 시작

```bash
# 1. 폴더 생성 및 이동
mkdir my_rag_project
cd my_rag_project

# 2. RAG Generator 복사
cp -r /path/to/"RAG vector generator" .

# 3. 의존성 설치
cd "RAG vector generator"
pip install -r requirements.txt

# 4. .env 설정
echo "GEMINI_API_KEY=your-key" > .env

# 5. PDF 추가
mkdir pdfs
# PDF 파일들을 pdfs/에 복사

# 6. 벡터 DB 생성
python python_textbook_rag_generator.py --db-name my_db
```

### 기존 DB에 새 문서 추가

```bash
# 1. pdfs/ 폴더에 새 PDF 추가

# 2. 같은 명령 재실행
python python_textbook_rag_generator.py --db-name existing_db

# → 기존 파일은 자동으로 건너뛰고 새 파일만 처리
```

### 중단된 작업 재개

```bash
# Checkpointing 덕분에 자동으로 이어서 진행
python python_textbook_rag_generator.py --db-name my_db
```

---

## 💡 고급 팁

### 팁 1: 속도 vs 품질 조절

**최고 품질 (느림)**:
```bash
python python_textbook_rag_generator.py \
  --chunking-strategy semantic \
  --rpm-limit 500
```

**균형 (권장)**:
```bash
python python_textbook_rag_generator.py \
  --chunking-strategy semantic \
  --rpm-limit 1440
```

**빠른 생성**:
```bash
python python_textbook_rag_generator.py \
  --chunking-strategy recursive
```

### 팁 2: 메모리 최적화

메모리가 부족한 경우:
```bash
python python_textbook_rag_generator.py \
  --batch-size 50 \
  --chunk-size 500
```

### 팁 3: 다국어 문서

한국어+영어 혼합:
```bash
python python_textbook_rag_generator.py \
  --embedding-model gemini  # Gemini가 다국어 우수
```

### 팁 4: 대량 문서 처리

1000개 이상 PDF:
```bash
# 밤새 실행
nohup python python_textbook_rag_generator.py \
  --db-name large_db \
  --rpm-limit 1000 > output.log 2>&1 &
```

---

## 📊 모니터링 및 검증

### 생성 진행 상황 확인

터미널 출력 확인:
```
PDF 처리 중: document1.pdf
  → 150 페이지에서 450 개 청크 생성
💾 체크포인트 저장 완료 (1/38, 2.6%)
```

### 메타데이터 확인

```bash
# JSON 파일 열기
cat vector_db/my_db_metadata.json

# 또는 Python으로
python -c "import json; print(json.load(open('vector_db/my_db_metadata.json')))"
```

### 벡터 DB 테스트

```python
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004",
    google_api_key=os.getenv("GEMINI_API_KEY")
)

vector_store = FAISS.load_local(
    "./vector_db/my_db",
    embeddings,
    allow_dangerous_deserialization=True
)

# 테스트 검색
results = vector_store.similarity_search("test query", k=3)
print(f"검색 결과: {len(results)}개")
for doc in results:
    print(f"- {doc.metadata['file_name']}: {doc.page_content[:100]}")
```

---

## ⚠️ 주의사항

### 1. API Quota 관리

**Gemini 무료 티어**:
- 1500 RPM (분당 요청 수)
- 하루 최대 ~30,000 요청

**안전한 설정**:
```bash
--rpm-limit 1440  # 96% 사용 (안전 마진 4%)
```

### 2. 민감 정보

**주의**: PDF에 개인정보나 기밀이 포함되어 있다면:
- 로컬 모델 사용 고려
- API 키를 Git에 커밋하지 않기
- `.env` 파일을 `.gitignore`에 추가

### 3. 저작권

PDF 파일의 저작권을 확인하세요. 상업적 사용 시 라이선스 검토 필요.

---

## 🆘 문제 해결

### 문제 1: "No PDF files found"

**해결**:
```bash
# pdfs/ 폴더 확인
ls pdfs/

# PDF 파일이 있는지 확인
# 없으면 PDF 파일을 pdfs/에 복사
```

### 문제 2: "API quota exceeded"

**해결**:
```bash
# 1. RPM limit 낮추기
python python_textbook_rag_generator.py --rpm-limit 500

# 2. 24시간 대기 후 재실행 (checkpointing으로 이어서 진행)
```

### 문제 3: "Memory error"

**해결**:
```bash
python python_textbook_rag_generator.py \
  --batch-size 30 \
  --chunk-size 500
```

### 문제 4: Semantic Chunking이 너무 느림

**해결**:
```bash
# Recursive chunking으로 전환
python python_textbook_rag_generator.py \
  --chunking-strategy recursive
```

---

## 📞 추가 도움말

- **이슈 리포트**: GitHub Issues
- **문서**: `README.md` 참고
- **프로젝트 문서**: `../README.md`, `../RAG_UPDATE_LOG.md`

---

**Happy Building! 🚀**
