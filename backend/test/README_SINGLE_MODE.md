# DOCGODAI Backend - 단일 질문-학습 모드

## 📌 개요

질문 1개 → 학습 페이지 1개로 간소화된 버전

```
질문 1개
  ↓
Chapter 1개
  ↓
Concept 1개 + Exercise 1개 + Quiz 1개
```

## 🎯 핵심 변경 사항

### 1. **데이터베이스 구조 변경** (models.py)

- **Course 모델 제거** - 중간 단계 제거, 질문이 곧 챕터
- **1:1 관계로 변경** - Chapter : Concept : Exercise : Quiz = 1:1:1:1
- **UNIQUE 제약 조건 추가** - `chapter_id`에 UNIQUE constraint
- **Status 필드 추가** - Chapter에 `status` (pending/completed) 추가
- **Nullable 필드** - AI가 채우기 전까지 빈 값 허용

### 2. **API 엔드포인트** (단순화)

#### Member (JWT + Redis)
- `POST /v1/member/signup` - 회원가입
- `POST /v1/member/login` - 로그인 (토큰 → Redis)
- `GET /v1/member/` - 내 정보 조회
- `POST /v1/member/logout` - 로그아웃 (Redis에서 토큰 삭제)

#### Chapter (질문 등록 및 학습)
- `POST /v1/chapter/` - 질문 등록 (챕터 생성)
- `GET /v1/chapter/{id}/learning` - **통합 학습 페이지 조회** (한 번에 모든 데이터)
- `GET /v1/chapter/` - 챕터 목록 조회

#### Webhook (n8n → Backend)
- `POST /v1/chapter/{id}/concept-finish` - 개념 정리 생성 완료
- `POST /v1/chapter/{id}/exercise-finish` - 실습 과제 생성 완료
- `POST /v1/chapter/{id}/quiz-finish` - 퀴즈 생성 완료

#### Quiz (제출)
- `POST /v1/quiz/{chapter_id}/submit` - 퀴즈 정답 제출

## 🔄 처리 흐름

```
1. 학생 질문 등록
POST /v1/chapter/
{
  "title": "파이썬 리스트와 튜플 차이가 뭐예요?",
  "description": "",
  "owner_id": 1
}

↓ 챕터 + 빈 Concept/Exercise/Quiz 생성
↓ Socket.IO: processing_started, concept_processing, exercise_processing, quiz_processing
↓
2. Kafka로 AI 생성 요청 (TODO: 실제 Kafka 코드 미구현)
↓
3. n8n이 AI로부터 콘텐츠 생성 후 Webhook 호출
POST /v1/chapter/{id}/concept-finish
POST /v1/chapter/{id}/exercise-finish
POST /v1/chapter/{id}/quiz-finish
↓
4. Socket.IO: concept_completed, exercise_completed, quiz_completed
↓
5. 모든 리소스 완료 시 Socket.IO: all_completed
↓
6. 학생이 학습 페이지 조회
GET /v1/chapter/{id}/learning
→ 한 번에 Concept + Exercise + Quiz 데이터 반환
↓
7. 퀴즈 제출
POST /v1/quiz/{chapter_id}/submit
{
  "answer": "불가능하다",
  "member_id": 1
}
```

## 📊 데이터베이스 테이블

### member
```sql
- id INT PK
- email VARCHAR(255) UNIQUE
- password VARCHAR(255)
- created_at DATETIME
- updated_at DATETIME
```

### chapter (질문 = 챕터)
```sql
- id INT PK
- owner_id INT FK → member.id
- title VARCHAR(255)  -- 질문
- description TEXT  -- AI가 생성한 요약
- status ENUM('pending', 'completed')
- is_active BOOLEAN
- created_at DATETIME
- updated_at DATETIME
```

### concept (1:1)
```sql
- id INT PK
- chapter_id INT FK UNIQUE → chapter.id
- title VARCHAR(255) NULLABLE
- content TEXT NULLABLE
- is_complete BOOLEAN
- created_at DATETIME
- updated_at DATETIME
```

### exercise (1:1)
```sql
- id INT PK
- chapter_id INT FK UNIQUE → chapter.id
- question TEXT NULLABLE
- answer TEXT NULLABLE
- is_complete BOOLEAN
- created_at DATETIME
- updated_at DATETIME
```

### quiz (1:1, 챕터당 1개)
```sql
- id INT PK
- chapter_id INT FK UNIQUE → chapter.id
- question TEXT NULLABLE
- options JSON NULLABLE
- correct_answer VARCHAR(255) NULLABLE
- explanation TEXT
- type ENUM('multiple', 'short', 'boolean')
- created_at DATETIME
- updated_at DATETIME
```

## 🚀 실행 방법

### 1. 환경 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 내용
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=docgodai

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

SECRET_KEY=your-secret-key-here
```

### 2. Docker Compose 실행

```bash
cd infra
docker-compose up -d
```

### 3. Python 의존성 설치

```bash
cd backend
pip install -r requirements.txt
```

### 4. 데이터베이스 초기화

```python
python init_db.py
```

### 5. 서버 실행

```bash
python main.py
```

서버: `http://localhost:8000`
API Docs: `http://localhost:8000/docs`

### 6. Socket.IO 테스트

```bash
open socket_client_example.html
```

## 🧪 API 테스트 예제

### 1. 회원가입
```bash
curl -X POST http://localhost:8000/v1/member/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "password": "password123"
  }'
```

### 2. 로그인
```bash
curl -X POST http://localhost:8000/v1/member/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "password": "password123"
  }'
```

Response:
```json
{
  "access_token": "eyJ0eXAi...",
  "token_type": "bearer",
  "member": {
    "id": 1,
    "email": "student@example.com",
    "created_at": "2025-11-02T12:00:00"
  }
}
```

### 3. 질문 등록
```bash
curl -X POST http://localhost:8000/v1/chapter/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "파이썬 리스트와 튜플 차이가 뭐예요?",
    "description": "",
    "owner_id": 1
  }'
```

Response:
```json
{
  "chapter_id": 1,
  "concept_id": 1,
  "exercise_id": 1,
  "quiz_id": 1,
  "status": "pending",
  "created_at": "2025-11-02T12:00:00"
}
```

### 4. 학습 페이지 조회 (통합)
```bash
curl http://localhost:8000/v1/chapter/1/learning
```

Response:
```json
{
  "chapter_id": 1,
  "title": "파이썬 리스트와 튜플 차이가 뭐예요?",
  "description": "가변/불변 구조에 대한 설명",
  "status": "completed",
  "concept": {
    "id": 1,
    "title": "리스트 vs 튜플",
    "content": "리스트는 mutable...",
    "is_complete": true
  },
  "exercise": {
    "id": 1,
    "question": "리스트를 튜플로 변환하는 코드를 작성하세요",
    "is_complete": true
  },
  "quiz": {
    "id": 1,
    "question": "튜플은 수정이 가능한가요?",
    "options": ["가능하다", "불가능하다"],
    "type": "multiple"
  }
}
```

### 5. 퀴즈 제출
```bash
curl -X POST http://localhost:8000/v1/quiz/1/submit \
  -H "Content-Type: application/json" \
  -d '{
    "answer": "불가능하다",
    "member_id": 1
  }'
```

Response:
```json
{
  "is_correct": true,
  "score": 100,
  "explanation": "튜플은 불변 자료형입니다"
}
```

## 🔌 Socket.IO 이벤트

### 클라이언트 → 서버
- `join_chapter` - 챕터 룸 참여 `{chapter_id: 1}`
- `leave_chapter` - 챕터 룸 나가기 `{chapter_id: 1}`

### 서버 → 클라이언트
- `chapter_processing_started` - 챕터 생성 시작
- `concept_processing` - 개념 정리 AI 생성 중
- `exercise_processing` - 실습 과제 AI 생성 중
- `quiz_processing` - 퀴즈 AI 생성 중
- `concept_completed` - 개념 정리 완료
- `exercise_completed` - 실습 과제 완료
- `quiz_completed` - 퀴즈 완료
- `all_completed` - 모든 콘텐츠 생성 완료

## 📝 Redis 키 구조

```
token:{user_id}  →  JWT access_token (TTL: 86400초 = 1일)
```

## 🔧 주요 파일

```
backend/
├── main.py                     # FastAPI 앱 + Socket.IO 통합
├── models.py                   # SQLAlchemy 모델 (단일 모드)
├── schemas.py                  # Pydantic 스키마
├── database.py                 # DB + Redis 연결
├── member.py                   # 회원 관리 (JWT + Redis)
├── chapter.py                  # 질문 등록 + 학습 페이지 조회 + Webhook
├── quiz.py                     # 퀴즈 제출
├── socketio_manager.py         # Socket.IO 이벤트 관리
├── auth.py                     # JWT 인증
├── init_db.py                  # DB 초기화
├── socket_client_example.html  # Socket.IO 테스트 클라이언트
└── README_SINGLE_MODE.md       # 이 문서
```

## ⚠️ TODO (Kafka/n8n 통합)

현재 Kafka 코드는 주석으로만 남겨두고 실제 구현되지 않았습니다.

```python
# chapter.py:91
# TODO: Kafka로 AI 생성 요청 전송
# send_to_kafka(chapter_id=new_chapter.id, title=new_chapter.title)
```

Kafka 통합 시 구현해야 할 부분:
1. Kafka Producer 설정
2. 챕터 생성 이벤트 발송
3. n8n에서 Kafka Consumer로 이벤트 수신
4. AI 처리 후 Webhook으로 응답

## 🎉 완료!

이제 단일 질문-학습 모드로 간소화된 백엔드가 완성되었습니다!

- **단순한 구조**: 질문 1개 = 학습 페이지 1개
- **통합 조회 API**: 한 번의 요청으로 모든 데이터 조회
- **실시간 알림**: Socket.IO로 AI 생성 진행 상황 추적
- **JWT + Redis**: 토큰 기반 인증 + Redis 세션 관리
