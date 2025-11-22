# PopPins II - 테스트 전략 (Test Strategy)

**프로젝트**: PopPins II (어딧세이 가제)  
**문서 타입**: Test Strategy & Quality Assurance  
**버전**: 1.0  
**작성일**: 2025-11-22  
**작성자**: 이진걸

---

## 📌 개요

PopPins II의 품질 보증(QA) 및 테스트 전략 문서입니다. **Backend API**, **AI 생성 품질**, **RAG 정확성**을 중심으로 단위 테스트, 통합 테스트, E2E 테스트 전략을 정의합니다.

---

## 🎯 테스트 목표

### Primary Goals

1. **기능 정확성**: API가 명세대로 동작
2. **AI 품질**: 생성된 학습 자료의 정확성 및 일관성
3. **RAG 신뢰성**: PDF 기반 컨텍스트 검색 정확도
4. **성능**: 응답 시간 1분 이내
5. **안정성**: 에러 없이 동작

### Quality Metrics

| 지표 | 목표 | 측정 방법 |
|------|------|----------|
| 단위 테스트 커버리지 | 80% 이상 | pytest-cov |
| API 응답 시간 | 60초 이내 | Locust 부하 테스트 |
| RAG 정확도 | 90% 이상 | 수동 검증 |
| JSON 파싱 성공률 | 95% 이상 | 로그 분석 |
| 크래시율 | 0% | 모니터링 |

---

## 🧪 테스트 피라미드

```
           ┌─────────────┐
           │   E2E (5%)  │  Frontend + Backend 통합
           ├─────────────┤
           │ Integration │  API + AI + RAG
           │   (25%)     │
           ├─────────────┤
           │   Unit      │  개별 함수 테스트
           │   (70%)     │
           └─────────────┘
```

---

## 1️⃣ Unit Tests (단위 테스트)

### 1.1 대상 함수

| 함수명 | 목적 | 테스트 케이스 수 |
|--------|------|-----------------|
| `initialize_rag_vector_db()` | FAISS DB 초기화 | 3 |
| `search_rag_context()` | RAG 검색 | 5 |
| `clean_json_response()` | JSON 파싱 | 7 |
| `generate_course()` | 커리큘럼 생성 | 4 |
| `generate_concept()` | 개념 정리 생성 | 4 |
| `generate_exercise()` | 실습 생성 | 4 |
| `generate_quiz()` | 퀴즈 생성 | 4 |

### 1.2 테스트 케이스 예시

#### `clean_json_response()` 테스트

```python
import pytest
from main_with_RAG import clean_json_response

def test_clean_json_basic():
    """기본 JSON 파싱"""
    text = '```json\n{"key": "value"}\n```'
    result = clean_json_response(text)
    assert result == '{"key": "value"}'

def test_clean_json_no_markers():
    """마커 없는 JSON"""
    text = '{"key": "value"}'
    result = clean_json_response(text)
    assert result == '{"key": "value"}'

def test_clean_json_multiple_markers():
    """여러 마커 제거"""
    text = '```\n```json\n{"key": "value"}\n```\n```'
    result = clean_json_response(text)
    assert result == '{"key": "value"}'

def test_clean_json_empty():
    """빈 문자열"""
    text = ''
    result = clean_json_response(text)
    assert result == ''
```

#### `search_rag_context()` 테스트

```python
def test_rag_search_basic(mock_vector_db):
    """기본 RAG 검색"""
    query = "파이썬 리스트"
    docs = search_rag_context(query, k=3)
    
    assert len(docs) <= 3
    assert all(isinstance(doc, str) for doc in docs)

def test_rag_search_empty_query():
    """빈 쿼리 처리"""
    docs = search_rag_context("", k=3)
    assert docs == []

def test_rag_search_db_not_initialized():
    """DB 미초기화 상태"""
    global vector_store
    vector_store = None
    docs = search_rag_context("test", k=3)
    assert docs == []
```

### 1.3 Coverage Target

- **목표**: 80% 이상
- **도구**: pytest-cov

```bash
pytest --cov=main_with_RAG --cov-report=html
```

---

## 2️⃣ Integration Tests (통합 테스트)

### 2.1 API 엔드포인트 테스트

#### POST /generate-study-material

**테스트 시나리오**:

```python
import pytest
from fastapi.testclient import TestClient
from main_with_RAG import app

client = TestClient(app)

def test_generate_study_material_success():
    """정상 학습 자료 생성"""
    response = client.post("/generate-study-material", json={
        "topic": "파이썬 리스트",
        "difficulty": "초급",
        "max_chapters": 2
    })
    
    assert response.status_code == 200
    data = response.json()
    
    # Course 구조 검증
    assert "course" in data
    assert "id" in data["course"]
    assert "chapters" in data["course"]
    assert len(data["course"]["chapters"]) == 2
    
    # Chapters 구조 검증
    assert "chapters" in data
    for chapter_content in data["chapters"]:
        assert "chapter" in chapter_content
        assert "concept" in chapter_content
        assert "exercise" in chapter_content
        assert "quiz" in chapter_content

def test_generate_study_material_invalid_difficulty():
    """잘못된 난이도 입력"""
    response = client.post("/generate-study-material", json={
        "topic": "파이썬",
        "difficulty": "invalid",  # 잘못된 값
        "max_chapters": 3
    })
    
    assert response.status_code == 422  # Validation Error

def test_generate_study_material_empty_topic():
    """빈 주제 입력"""
    response = client.post("/generate-study-material", json={
        "topic": "",
        "max_chapters": 3
    })
    
    assert response.status_code == 422

def test_generate_study_material_timeout():
    """타임아웃 처리 (30분 주제)"""
    # Mock으로 처리하거나 실제 타임아웃 테스트
    pass
```

#### GET /health

```python
def test_health_endpoint():
    """Health Check"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
```

### 2.2 RAG + AI 통합 테스트

```python
def test_rag_integration_with_gemini():
    """RAG 검색 + Gemini 생성"""
    query = "파이썬 함수"
    rag_docs = search_rag_context(query, k=3)
    
    # Gemini에 컨텍스트 전달
    prompt = f"다음 자료를 참고하여 개념을 설명:\n{rag_docs}"
    # ... Gemini 호출
    
    # 응답 검증
    assert len(rag_docs) > 0
```

---

## 3️⃣ E2E Tests (End-to-End 테스트)

### 3.1 시나리오 기반 테스트

#### 시나리오 1: "수진의 단기 학습"

```python
def test_e2e_sujin_scenario():
    """
    사용자: 수진 (대학생)
    목표: "파이썬 확률과 통계" 2시간 학습
    """
    # Step 1: 주제 입력
    response = client.post("/generate-study-material", json={
        "topic": "파이썬 확률과 통계 기초",
        "difficulty": "초급",
        "max_chapters": 2,
        "course_description": "2시간 안에 핵심 개념 학습"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    # Step 2: 커리큘럼 확인
    assert len(data["course"]["chapters"]) == 2
    
    # Step 3: 개념 정리 검증
    for chapter in data["chapters"]:
        concept = chapter["concept"]
        assert "contents" in concept
        assert len(concept["contents"]) >= 1000  # 최소 1000자
        
    # Step 4: 실습 과제 검증
    for chapter in data["chapters"]:
        exercise = chapter["exercise"]
        assert "contents" in exercise
        assert "문제" in exercise["contents"] or "Problem" in exercise["contents"]
        
    # Step 5: 퀴즈 검증
    for chapter in data["chapters"]:
        quiz = chapter["quiz"]
        assert len(quiz["quizes"]) == 3
```

#### 시나리오 2: "민수의 팀 리스킬링"

```python
def test_e2e_minsu_scenario():
    """
    사용자: 민수 (직장인)
    목표: Delphi 팀 교육 자료 생성
    """
    response = client.post("/generate-study-material", json={
        "topic": "Delphi 레거시 시스템 유지보수",
        "difficulty": "중급",
        "max_chapters": 5
    })
    
    assert response.status_code == 200
    data = response.json()
    
    # 실무 중심 검증
    assert len(data["course"]["chapters"]) == 5
    
    # 실습 문제가 실무 중심인지 확인
    for chapter in data["chapters"]:
        exercise = chapter["exercise"]["contents"]
        assert "실무" in exercise or "프로젝트" in exercise
```

### 3.2 Performance E2E

```python
import time

def test_e2e_performance():
    """전체 프로세스 성능 테스트"""
    start_time = time.time()
    
    response = client.post("/generate-study-material", json={
        "topic": "파이썬 클래스",
        "max_chapters": 3
    })
    
    end_time = time.time()
    duration = end_time - start_time
    
    assert response.status_code == 200
    assert duration < 60  # 1분 이내
```

---

## 4️⃣ AI Quality Tests (AI 품질 테스트)

### 4.1 생성 품질 검증

```python
def test_concept_quality():
    """개념 정리 품질 검증"""
    response = client.post("/generate-study-material", json={
        "topic": "파이썬 리스트 컴프리헨션",
        "max_chapters": 5
    })
    
    concept = response.json()["chapters"][0]["concept"]
    
    # 1. 분량 검증
    assert len(concept["contents"]) >= 1000
    assert len(concept["contents"]) <= 1500
    
    # 2. Markdown 형식 검증
    assert "##" in concept["contents"] or "#" in concept["contents"]
    
    # 3. 코드 블록 포함 검증
    assert "```python" in concept["contents"]

def test_exercise_quality():
    """실습 문제 품질 검증"""
    response = client.post("/generate-study-material", json={
        "topic": "파이썬 함수",
        "max_chapters": 1
    })
    
    exercise = response.json()["chapters"][0]["exercise"]
    
    # 문제 수 검증 (기본 → 응용 → 확장)
    contents = exercise["contents"]
    assert contents.count("문제") >= 3 or contents.count("Problem") >= 3

def test_quiz_quality():
    """퀴즈 품질 검증"""
    response = client.post("/generate-study-material", json={
        "topic": "파이썬 변수",
        "max_chapters": 1
    })
    
    quiz = response.json()["chapters"][0]["quiz"]
    
    # 문제 수 검증
    assert len(quiz["quizes"]) == 3
    
    # 각 문제가 비어있지 않은지 검증
    for q in quiz["quizes"]:
        assert len(q["quiz"]) > 0
```

### 4.2 RAG 정확성 테스트

```python
def test_rag_accuracy():
    """RAG로 검색된 문서가 관련성 있는지 수동 검증"""
    topic = "파이썬 리스트"
    docs = search_rag_context(topic, k=3)
    
    # 검색된 문서에 키워드 포함 여부
    combined_text = " ".join(docs)
    assert "리스트" in combined_text or "list" in combined_text
```

---

## 5️⃣ Regression Tests (회귀 테스트)

### 5.1 Golden Master Testing

**목적**: AI 출력 일관성 검증

```python
import json

GOLDEN_MASTERS = {
    "파이썬 리스트_초급": "tests/golden/list_beginner.json",
    "파이썬 함수_중급": "tests/golden/function_intermediate.json"
}

def test_golden_master_list_beginner():
    """골든 마스터 테스트: 리스트 초급"""
    response = client.post("/generate-study-material", json={
        "topic": "파이썬 리스트",
        "difficulty": "초급",
        "max_chapters": 2
    })
    
    result = response.json()
    
    # 구조 일관성 검증 (내용 자체는 다를 수 있음)
    with open(GOLDEN_MASTERS["파이썬 리스트_초급"]) as f:
        golden = json.load(f)
    
    assert result["course"].keys() == golden["course"].keys()
    assert len(result["chapters"]) == len(golden["chapters"])
```

---

## 6️⃣ Load Tests (부하 테스트)

### 6.1 Locust 부하 테스트

```python
# locustfile.py
from locust import HttpUser, task, between

class PopPinsUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def generate_study_material(self):
        self.client.post("/generate-study-material", json={
            "topic": "파이썬 기초",
            "difficulty": "초급",
            "max_chapters": 2
        })
    
    @task(3)  # 3배 더 자주 호출
    def health_check(self):
        self.client.get("/health")
```

**실행**:
```bash
locust -f locustfile.py --host=http://localhost:8001
```

**목표**:
- 동시 사용자: 10명
- 평균 응답 시간: 30초 이하
- 에러율: 0%

---

## 7️⃣ Security Tests (보안 테스트)

### 7.1 Input Validation

```python
def test_sql_injection_attempt():
    """SQL Injection 시도"""
    response = client.post("/generate-study-material", json={
        "topic": "'; DROP TABLE courses; --",
        "max_chapters": 3
    })
    
    # 에러 없이 처리되어야 함 (Pydantic 검증)
    assert response.status_code in [200, 422]

def test_xss_attempt():
    """XSS 시도"""
    response = client.post("/generate-study-material", json={
        "topic": "<script>alert('XSS')</script>",
        "max_chapters": 3
    })
    
    assert response.status_code in [200, 422]
```

---

## 8️⃣ Test Data Management

### 8.1 Fixtures

```python
# conftest.py
import pytest
from fastapi.testclient import TestClient
from main_with_RAG import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def sample_request():
    return {
        "topic": "파이썬 테스트",
        "difficulty": "초급",
        "max_chapters": 2
    }

@pytest.fixture
def mock_vector_db(monkeypatch):
    def mock_search(query, k):
        return ["Mock document 1", "Mock document 2", "Mock document 3"]
    
    monkeypatch.setattr("main_with_RAG.search_rag_context", mock_search)
```

### 8.2 Mock Data

```json
// tests/data/sample_course.json
{
  "course": {
    "id": 1,
    "chapters": [
      {
        "chapterId": 1,
        "chapterTitle": "리스트 기초",
        "chapterDescription": "파이썬 리스트의 기본 개념"
      }
    ]
  },
  "chapters": [
    {
      "chapter": {},
      "concept": {},
      "exercise": {},
      "quiz": {}
    }
  ]
}
```

---

## 📊 Test Execution Plan

### Phase 1: MVP 테스트 (현재)

- ✅ 수동 API 테스트 (Postman/cURL)
- ✅ 기본 동작 검증

### Phase 2: 자동화 테스트 구축 (⏳)

**Week 1**:
- [ ] Unit Tests 작성 (70% coverage)
- [ ] Integration Tests (API 엔드포인트)
- [ ] CI/CD 파이프라인 설정

**Week 2**:
- [ ] E2E Tests (주요 시나리오 2개)
- [ ] AI Quality Tests
- [ ] Load Tests (Locust)

### Phase 3: 지속적 테스트 (⏳)

- [ ] 매 PR마다 자동 테스트 실행
- [ ] Nightly Regression Tests
- [ ] Weekly Performance Tests

---

## 🔧 Test Tools

| 도구 | 용도 | 상태 |
|------|------|------|
| pytest | Unit/Integration Tests | ✅ 설치됨 |
| pytest-cov | 코드 커버리지 | ⏳ 예정 |
| FastAPI TestClient | API Tests | ✅ 내장 |
| Locust | Load Tests | ⏳ 예정 |
| Postman | 수동 API 테스트 | ✅ 사용 중 |

---

## 🎯 Success Criteria

### Definition of Done (테스트 통과 기준)

- [x] 모든 API 엔드포인트 정상 응답
- [ ] Unit Test Coverage 80% 이상
- [ ] Integration Tests 100% 통과
- [ ] E2E Tests (2개 시나리오) 100% 통과
- [ ] 부하 테스트 통과 (10명 동시 사용자)
- [ ] 보안 테스트 통과
- [ ] Regression Tests 100% 통과

---

## 📝 Appendix

### A. Test Command Reference

```bash
# 모든 테스트 실행
pytest

# Coverage 포함
pytest --cov=main_with_RAG --cov-report=html

# 특정 테스트만 실행
pytest tests/test_api.py::test_generate_study_material_success

# Verbose 모드
pytest -v

# 빠른 실패 (첫 실패 시 중단)
pytest -x

# 부하 테스트
locust -f locustfile.py --host=http://localhost:8001 --users=10 --spawn-rate=2
```

### B. CI/CD Integration (GitHub Actions)

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest --cov=main_with_RAG --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

---

**문서 버전**: 1.0  
**최종 수정일**: 2025-11-22  
**상태**: 전략 수립 완료, 자동화 테스트 구축 대기  
**다음 단계**: Unit Tests 작성 시작
