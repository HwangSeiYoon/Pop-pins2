# PopPins II - 시스템 아키텍처 문서

**프로젝트**: PopPins II (어딧세이 가제)  
**문서 타입**: Architecture Diagram & System Design  
**버전**: 1.0  
**작성일**: 2025-11-22  
**작성자**: 이진걸

---

## 📌 개요

PopPins II는 AI 기반 PBL(Problem-Based Learning) 학습 자료 자동 생성 플랫폼으로, **FastAPI Backend**, **Google Gemini AI**, **FAISS Vector DB**를 핵심으로 하는 3-Layer Architecture입니다.

---

## 🏗️ 전체 시스템 아키텍처

### High-Level Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        A[사용자]
        B[Frontend 웹앱<br/>React + Vite]
    end
    
    subgraph "Application Layer"
        C[FastAPI Backend<br/>Port: 8001]
        D[REST API Endpoints]
    end
    
    subgraph "AI & Data Layer"
        E[Google Gemini 2.5 Flash]
        F[FAISS Vector DB]
        G[PDF 교재]
    end
    
    A -->|HTTP Request| B
    B -->|API Call| D
    D --> C
    C -->|Generate Content| E
    C -->|Search Context| F
    F -.->|Index| G
    E -->|JSON Response| C
    C -->|Study Material| D
    D -->|API Response| B
    B -->|Display| A
    
    style B fill:#e1f5ff
    style C fill:#fff4e6
    style E fill:#f3e5f5
    style F fill:#e8f5e9
```

---

## 🔧 Component Architecture

### 1. Frontend Layer (🔄 예정)

**기술 스택**:
- React 18+
- Vite (빌드 도구)
- TailwindCSS (선택)
- Axios (HTTP 클라이언트)

**주요 컴포넌트**:
```
src/
├── components/
│   ├── TopicForm.jsx          # 주제 입력 폼
│   ├── LoadingSpinner.jsx     # 로딩 표시
│   ├── CourseViewer.jsx       # 커리큘럼 표시
│   ├── ConceptViewer.jsx      # 개념 정리 표시
│   ├── ExerciseViewer.jsx     # 실습 과제 표시
│   └── QuizViewer.jsx         # 퀴즈 표시
├── services/
│   └── api.js                 # API 호출 함수
└── App.jsx                    # 메인 앱
```

**상태**: 🔄 개발 예정

---

### 2. Backend Layer (✅ 완료)

**기술 스택**:
- FastAPI 0.104.0+
- Python 3.8+
- Uvicorn (ASGI 서버)
- Pydantic (데이터 검증)

**디렉토리 구조**:
```
app/
├── main_with_RAG.py          # 메인 애플리케이션
├── .env                       # 환경 변수
├── requirements.txt           # 의존성
└── vector_db/                 # FAISS 벡터 DB
    └── python_textbook_gemini_db/
```

**API 엔드포인트**:

| Method | Endpoint | 설명 | 상태 |
|--------|----------|------|------|
| POST | `/generate-study-material` | 학습 자료 생성 | ✅ |
| GET | `/` | API 정보 | ✅ |
| GET | `/health` | 서버 상태 확인 | ✅ |

**핵심 함수**:
- `initialize_rag_vector_db()`: FAISS 벡터 DB 초기화
- `search_rag_context()`: RAG 컨텍스트 검색
- `generate_course()`: 커리큘럼 생성
- `generate_concept()`: 개념 정리 생성
- `generate_exercise()`: 실습 과제 생성
- `generate_quiz()`: 퀴즈 생성

---

### 3. AI Engine Layer (✅ 완료)

#### Google Gemini 2.5 Flash

**설정**:
```python
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-exp",
    generation_config={
        "temperature": 0.7,
        "max_output_tokens": 8192,
    }
)
```

**역할별 프롬프트**:
- **CourseMaker**: 커리큘럼 설계 전문가
- **ConceptMaker**: 개념 정리 전문가 (1000~1200자, Markdown)
- **ExerciseMaker**: 실습 문제 출제자 (3개 문제)
- **QuizMaker**: 평가 문제 출제자 (3개 주관식)

**응답 형식**: JSON

---

### 4. Vector DB Layer (✅ 완료)

#### FAISS (Facebook AI Similarity Search)

**구성**:
```python
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004"
)
vector_store = FAISS.load_local(
    VECTOR_DB_PATH, 
    embeddings,
    allow_dangerous_deserialization=True
)
```

**문서 처리 파이프라인**:
```
PDF 파일
    ↓
PyPDFLoader (텍스트 추출)
    ↓
RecursiveCharacterTextSplitter
 - chunk_size: 1000
 - chunk_overlap: 200
    ↓
GoogleGenerativeAIEmbeddings
 - model: text-embedding-004
 - dimension: 768
    ↓
FAISS VectorStore 저장
    ↓
Similarity Search (Top-K=3)
```

**메타데이터**:
- `file_name`: 파일명
- `source_file`: 파일 경로
- `page`: 페이지 번호

---

## 📊 Data Flow Architecture

### Request Processing Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant FastAPI
    participant RAG
    participant Gemini
    
    User->>Frontend: 학습 주제 입력
    Frontend->>FastAPI: POST /generate-study-material
    
    Note over FastAPI: 1. CourseMaker
    FastAPI->>RAG: 커리큘럼 참고 검색
    RAG-->>FastAPI: 관련 문서 (Top-K=3)
    FastAPI->>Gemini: 커리큘럼 생성 요청
    Gemini-->>FastAPI: Course JSON
    
    loop 각 챕터마다
        Note over FastAPI: 2. ConceptMaker
        FastAPI->>RAG: 개념 설명 검색
        RAG-->>FastAPI: 관련 문서
        FastAPI->>Gemini: 개념 정리 생성
        Gemini-->>FastAPI: Concept Markdown
        
        Note over FastAPI: 3. ExerciseMaker
        FastAPI->>RAG: 실습 예제 검색
        RAG-->>FastAPI: 관련 문서
        FastAPI->>Gemini: 실습 문제 생성
        Gemini-->>FastAPI: Exercise Markdown
        
        Note over FastAPI: 4. QuizMaker
        FastAPI->>RAG: 핵심 개념 검색
        RAG-->>FastAPI: 관련 문서
        FastAPI->>Gemini: 퀴즈 생성
        Gemini-->>FastAPI: Quiz JSON
    end
    
    FastAPI-->>Frontend: StudyMaterialResponse
    Frontend-->>User: 학습 자료 표시
```

---

## 🗄️ Database Architecture (⏳ 계획)

### ERD 기반 설계

향후 PostgreSQL 도입 시 사용할 테이블:

```
Member (사용자)
    ↓ 1:N
Course (강좌)
    ↓ 1:N
Chapter (챕터)
    ↓ 1:N
├── Concept (개념)
├── Exercise (실습)
└── Quiz (퀴즈)
    ↓ 1:N
Result (학습 결과)
```

**상태**: ⏳ MVP 이후 구현 예정

---

## 🔐 Security Architecture

### 현재 보안 구성 (✅)

1. **API Key 관리**:
   ```env
   GEMINI_API_KEY=your-api-key  # .env 파일
   ```

2. **환경 변수 분리**:
   - `.env` 파일 사용
   - `.gitignore`에 추가

3. **입력 검증**:
   - Pydantic 모델로 타입 검증
   - HTTPException 에러 처리

### 향후 보안 강화 (⏳)

- JWT 토큰 기반 인증
- CORS 정책 세분화
- Rate Limiting
- API Key 로테이션

---

## 🚀 Deployment Architecture (⏳ 계획)

### GCP 기반 배포 아키텍처

```mermaid
graph LR
    A[사용자] -->|HTTPS| B[Cloud Load Balancer]
    B --> C[Cloud Run<br/>FastAPI Container]
    C --> D[Vertex AI<br/>Gemini API]
    C --> E[Cloud Storage<br/>Vector DB]
    C --> F[Cloud SQL<br/>PostgreSQL]
    
    style C fill:#fff4e6
    style D fill:#f3e5f5
    style E fill:#e8f5e9
    style F fill:#e3f2fd
```

**주요 서비스**:
- **Cloud Run**: 컨테이너 배포 (FastAPI)
- **Vertex AI**: Gemini API 호스팅
- **Cloud Storage**: FAISS 벡터 DB 저장
- **Cloud SQL**: PostgreSQL 관리형 DB

**상태**: ⏳ 향후 계획

---

## 📈 Scalability Considerations

### 수평 확장 전략

1. **Backend Scaling**:
   - Cloud Run 자동 스케일링
   - Stateless 설계

2. **Vector DB Scaling**:
   - FAISS → Pinecone/Weaviate 마이그레이션 검토
   - 분산 벡터 검색

3. **Caching Strategy**:
   - Redis 캐시 도입
   - 동일 주제 재생성 방지

---

## 🔍 Monitoring & Logging (⏳)

### 계획된 모니터링 구성

- **Application Monitoring**: Cloud Monitoring
- **Error Tracking**: Sentry
- **API Logging**: FastAPI 로그 → Cloud Logging
- **Performance Metrics**: 응답 시간, 처리량

---

## 📚 Technology Stack Summary

| Layer | Technology | Version | Status |
|-------|-----------|---------|--------|
| Frontend | React + Vite | 18+ | 🔄 예정 |
| Backend | FastAPI | 0.104+ | ✅ 완료 |
| AI | Google Gemini | 2.5 Flash | ✅ 완료 |
| Embedding | text-embedding-004 | - | ✅ 완료 |
| Vector DB | FAISS | CPU | ✅ 완료 |
| Database | PostgreSQL | 14+ | ⏳ 계획 |
| Deployment | GCP Cloud Run | - | ⏳ 계획 |

---

## 🎯 Architecture Principles

1. **단순성 우선**: MVP는 최소 구성 요소로 시작
2. **모듈화**: 각 AI 생성기 독립적 설계
3. **확장성**: 컴포넌트 추가/변경 용이
4. **신뢰성**: RAG로 PDF 기반 정확성 확보
5. **성능**: 챕터당 10-30초 생성 목표

---

**문서 버전**: 1.0  
**최종 수정일**: 2025-11-22  
**상태**: 현재 아키텍처 문서화 완료  
**다음 단계**: Frontend 개발, DB 통합
