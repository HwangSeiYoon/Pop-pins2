# PopPins II - Sequence Diagram

**프로젝트**: PopPins II  
**문서 타입**: System Sequence Diagrams  
**버전**: 1.0  
**작성일**: 2025-11-22

---

## 1. 전체 시스템 플로우

### 1.1 학습 자료 생성 플로우

```mermaid
sequenceDiagram
    actor User as 👤 사용자
    participant UI as 🖥️ Frontend
    participant API as ⚙️ Backend
    participant RAG as 📚 RAG Engine
    participant AI as 🤖 Gemini
    
    User->>UI: 주제 입력
    UI->>User: 옵션 설정 화면
    User->>UI: 난이도/챕터 수 설정
    UI->>API: POST /generate-study-material
    
    API->>RAG: PDF 검색 (Top-3)
    RAG-->>API: 관련 문서
    API->>AI: 커리큘럼 생성
    AI-->>API: Course + Chapters
    
    loop 챕터별
        API->>RAG: 챕터 문서 검색
        RAG-->>API: 문서
        API->>AI: 개념/실습/퀴즈 생성
        AI-->>API: Content
    end
    
    API-->>UI: JSON 응답
    UI->>User: 결과 표시
```

---

## 2. 세부 플로우

### 2.1 RAG 문서 검색

```mermaid
sequenceDiagram
    participant API
    participant RAG as RAG Engine
    participant FAISS as FAISS DB
    participant Embed as Embedding
    
    API->>RAG: search_rag_context("파이썬 리스트", k=3)
    RAG->>Embed: 쿼리 임베딩
    Embed-->>RAG: Vector
    RAG->>FAISS: similarity_search(Vector, k=3)
    FAISS-->>RAG: Top-3 Documents
    RAG->>RAG: 컨텍스트 포맷팅
    RAG-->>API: "참고 자료 1: ...\n참고 자료 2: ..."
```

### 2.2 AI 콘텐츠 생성

```mermaid
sequenceDiagram
    participant API
    participant AI as Gemini AI
    
    API->>AI: generate_concept(query + RAG context)
    Note over AI: Prompt:<br/>1. RAG 컨텍스트<br/>2. 학습자 레벨<br/>3. 출력 형식
    AI->>AI: 개념 정리 생성 (1000~1200자)
    AI-->>API: JSON (title, description, contents)
    
    API->>AI: generate_exercise(query + RAG context)
    AI->>AI: 실습 3개 생성
    AI-->>API: JSON (title, description, contents)
    
    API->>AI: generate_quiz(query + RAG context)
    AI->>AI: 퀴즈 3개 생성
    AI-->>API: JSON (quizes: [...])
```

---

## 3. 사용자 시나리오별 플로우

### 3.1 빠른 학습 (수진의 사례)

```mermaid
sequenceDiagram
    actor 수진
    participant System
    
    수진->>System: "확률과 통계 기초" 입력
    수진->>System: 난이도: 초급, 3일 학습
    System->>수진: 커리큘럼 3챕터 생성 (30초)
    
    Note over 수진,System: Day 1
    수진->>System: 챕터 1 개념 읽기
    수진->>System: 실습 1-2 풀기
    System->>수진: 진도율 33%
    
    Note over 수진,System: Day 2
    수진->>System: 챕터 2-3 학습
    System->>수진: 진도율 100%
    
    Note over 수진,System: Day 3
    수진->>System: 전체 퀴즈 복습
    System->>수진: 학습 완료!
```

### 3.2 팀 학습 (민수의 사례)

```mermaid
sequenceDiagram
    actor 민수
    participant System
    actor 팀원
    
    민수->>System: "Delphi 기초" 입력
    민수->>System: 중급, 5챕터
    System->>민수: 커리큘럼 생성
    
    민수->>팀원: 학습 자료 공유
    
    par 병렬 학습
        팀원->>System: 챕터 1-2 학습
    and
        민수->>System: 챕터 3-5 학습
    end
    
    민수->>팀원: 주간 미팅으로 진도 체크
    System->>민수: 팀 학습 현황 표시
```

---

## 4. 에러 처리 플로우

### 4.1 생성 실패 처리

```mermaid
sequenceDiagram
    actor User
    participant UI
    participant API
    participant AI
    
    User->>UI: 주제 입력
    UI->>API: POST /generate-study-material
    
    alt AI 응답 실패
        API->>AI: generate_concept()
        AI-->>API: Error (Rate Limit)
        API-->>UI: 500 Error (detail: "생성 실패")
        UI->>User: ❌ 에러 메시지 + [재시도]
        User->>UI: [재시도] 클릭
        UI->>API: POST (retry)
    else JSON 파싱 실패
        API->>AI: generate_concept()
        AI-->>API: Invalid JSON
        API->>API: clean_json_response() 재시도
        alt 파싱 성공
            API-->>UI: 정상 응답
        else 파싱 최종 실패
            API-->>UI: 500 Error
        end
    end
```

### 4.2 RAG 검색 실패 처리

```mermaid
sequenceDiagram
    participant API
    participant RAG
    participant AI
    
    API->>RAG: search_rag_context()
    
    alt 벡터 DB 없음
        RAG-->>API: "" (빈 컨텍스트)
        API->>AI: Gemini만으로 생성 (RAG 없이)
    else 검색 오류
        RAG-->>API: Exception
        API->>API: 로깅
        API->>AI: Gemini만으로 생성
    end
    
    AI-->>API: 생성된 콘텐츠
```

---

## 5. 데이터 플로우

### 5.1 PDF → 벡터 DB

```mermaid
graph LR
    A[PDF 파일] --> B[PyPDFLoader]
    B --> C[텍스트 추출]
    C --> D[RecursiveTextSplitter]
    D --> E[Chunks<br/>1000자×200 overlap]
    E --> F[Gemini Embedding<br/>text-embedding-004]
    F --> G[FAISS 벡터 DB]
    G --> H[메타데이터<br/>file_name, source]
```

### 5.2 사용자 입력 → 학습 자료

```mermaid
graph TD
    A[사용자 입력] --> B{파싱}
    B --> C[topic]
    B --> D[difficulty]
    B --> E[max_chapters]
    
    C --> F[RAG 검색]
    D --> F
    F --> G[Gemini AI]
    G --> H[Course]
    G --> I[Concept]
    G --> J[Exercise]
    G --> K[Quiz]
    
    H --> L[StudyMaterialResponse]
    I --> L
    J --> L
    K --> L
    L --> M[JSON 응답]
```

---

## 6. 상태 다이어그램

### 6.1 학습 진행 상태

```mermaid
stateDiagram-v2
    [*] --> 주제입력
    주제입력 --> 생성중
    생성중 --> 커리큘럼확인
    
    커리큘럼확인 --> 챕터학습
    챕터학습 --> 개념읽기
    개념읽기 --> 실습풀기
    실습풀기 --> 퀴즈풀기
    
    퀴즈풀기 --> 이해도체크
    이해도체크 --> 다음챕터: 이해함
    이해도체크 --> 개념읽기: 이해 부족
    
    다음챕터 --> 챕터학습: 챕터 남음
    다음챕터 --> 학습완료: 모든 챕터 완료
    학습완료 --> [*]
```

### 6.2 API 요청 상태

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Generating: POST 요청
    
    Generating --> RAG_Search
    RAG_Search --> AI_Generate
    
    AI_Generate --> Parsing
    Parsing --> Success: JSON OK
    Parsing --> Retry: JSON Error
    
    Retry --> AI_Generate: 재시도 (3회)
    Retry --> Error: 최종 실패
    
    Success --> [*]
    Error --> [*]
```

---

## 7. 시스템 컨텍스트

```mermaid
C4Context
    title PopPins II System Context
    
    Person(user, "학습자", "파이썬 초~중급")
    System(poppins, "PopPins II", "AI 기반 PBL 생성")
    System_Ext(gemini, "Gemini AI", "LLM & Embedding")
    SystemDb(faiss, "FAISS DB", "벡터 저장소")
    
    Rel(user, poppins, "학습 주제 입력")
    Rel(poppins, gemini, "콘텐츠 생성 요청")
    Rel(poppins, faiss, "유사 문서 검색")
```

---

## 📚 참고 문서

- [통합 기획 문서](./pop_pins_ii_planning_document.md)
- [PRD](./pop_pins_ii_prd.md)
- [User Diagram](./pop_pins_ii_user_diagram.md)
- [Wireframe](./pop_pins_ii_wireframe.md)

---

**문서 버전**: 1.0  
**최종 수정일**: 2025-11-22  
**작성자**: 이진걸  
**상태**: 작성 완료
