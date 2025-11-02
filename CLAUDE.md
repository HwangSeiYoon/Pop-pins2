# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

**Hack-DOCGODAI**는 AI 기반 학습 플랫폼으로, 사용자가 코스를 생성하면 N8N과 Gemini가 자동으로 챕터별 학습 콘텐츠(개념정리, 실습과제, 형성평가)를 생성합니다.

### 주요 기술 스택
- **Backend**: FastAPI, SQLAlchemy, Socket.IO
- **Infrastructure**: Docker Compose (MySQL, Redis, Kafka, N8N)
- **AI Workflow**: N8N + Google Gemini
- **Message Queue**: Apache Kafka
- **Database**: MySQL
- **Cache**: Redis

## 프로젝트 구조

```
Hack-DOCGODAI/
├── backend/          # FastAPI 백엔드 애플리케이션
├── agent/            # N8N 워크플로우 JSON 파일들
├── infra/            # 인프라 설정 (Docker Compose)
└── lib/              # 공유 라이브러리
```

## 개발 환경 설정

### 인프라 시작

```bash
cd infra

# 필수 디렉토리 생성
mkdir -p volume-kafka volume-mysql volume-n8n volume-redis

# 인프라 컨테이너 시작 (MySQL, Redis, Kafka, N8N)
docker-compose up -d
```

### 인프라 포트

- **MySQL**: `3306:3306`
- **Redis**: `6379:6379`
- **Kafka**: `9092:9092`
- **N8N**: `5678:5678`

### 백엔드 실행

```bash
cd backend

# Python 가상환경 활성화 (이미 생성되어 있음)
source ../.venv/bin/activate  # Linux/Mac
# 또는 Windows:
# ..\.venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 개발 서버 시작
python main.py
# 또는
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

백엔드 서버: `http://localhost:8000`

## 아키텍처

### 핵심 데이터 흐름

```
1. 사용자가 코스 생성
   ↓
2. 백엔드가 Chapter 생성 → Kafka 이벤트 발행 ("chapter-created")
   ↓
3. N8N이 Kafka 이벤트 수신 → Gemini API 호출
   ↓
4. Gemini가 콘텐츠 생성 (개념정리/실습과제/퀴즈)
   ↓
5. N8N이 백엔드 Webhook 호출 → DB 저장 + Socket.IO 실시간 알림
   ↓
6. 클라이언트가 Socket.IO로 완료 알림 수신
```

### 백엔드 아키텍처 (FastAPI)

**레이어 구조:**
1. **API Routes** (`*.py` 라우터 파일들)
2. **Repository Pattern** (`backend/repository/` - CRUD 로직 분리)
3. **Database Models** (`backend/db/models.py` - SQLAlchemy ORM)
4. **External Integrations**
   - `kafka_producer.py` - Kafka 이벤트 발행
   - `socketio_manager.py` - Socket.IO 실시간 알림
   - `n8n_client.py` - N8N HTTP 호출 (필요 시)

**주요 라우터:**
- `member.py` - 회원가입, 로그인 (JWT 인증)
- `course.py` - 코스 생성/조회/리스트
- `chapter.py` - 챕터 생성/조회 + **Webhook 엔드포인트** (N8N → 백엔드)
- `concept.py` - 개념정리 조회/완료 처리
- `exercise.py` - 실습과제 조회/완료 처리
- `quiz.py` - 형성평가 조회/제출/채점
- `webhook.py` - N8N Webhook 통합 엔드포인트

### N8N 워크플로우 (agent/)

N8N에서 사용하는 JSON 워크플로우 파일들:

- `102-2. CourseMaker-2.json` - 코스 메이커
- `103-2. ConceptMaker-2.json` - 개념정리 생성
- `104-2. ExerciseMaker-2.json` - 실습과제 생성
- `105-1. Quizmaker.json` - 퀴즈 생성
- `106-2. QuizGrader.json` - 퀴즈 채점

이 워크플로우들은 N8N 웹 UI(`http://localhost:5678`)에서 import하여 사용합니다.

## 데이터베이스 모델

### 주요 엔티티 관계

```
Member (회원)
  ↓ 1:N
Course (코스)
  ↓ 1:N
Chapter (챕터)
  ↓ 1:N
  ├── Concept (개념정리)
  ├── Exercise (실습과제)
  └── Quiz (형성평가)
```

### 주요 필드

**Member**
- `id`, `email`, `password` (hashed)

**Course**
- `title`, `description`, `prompt`, `difficulty`
- `links` (JSON 배열, `json.dumps()` 사용)

**Chapter**
- `title`, `description`, `order_num`
- `course_id` (FK)

**Concept / Exercise / Quiz**
- `is_available` - Gemini 생성 완료 여부 (`True`일 때 사용자가 접근 가능)
- `is_complete` - 사용자 학습 완료 여부
- `content` - 학습 콘텐츠 (Gemini가 생성한 내용)

## Kafka 이벤트

### Kafka Topics

- `chapter-created` - 챕터 생성 시 발행
- `concept-created` - 개념정리 생성 요청
- `exercise-created` - 실습과제 생성 요청
- `quiz-created` - 퀴즈 생성 요청
- `quiz-answer-submit` - 퀴즈 답안 제출 (채점 요청)

### Kafka 이벤트 발행 방법

```python
from kafka_producer import send_chapter_created_event

send_chapter_created_event(
    chapter_id=chapter.id,
    course_id=course.id,
    owner_id=current_user["user_id"],
    course_title=course.title,
    course_description=course.description,
    chapter_title=chapter.title,
    chapter_description=chapter.description
)
```

## Socket.IO 실시간 알림

### 클라이언트 룸 조인

클라이언트는 특정 챕터의 업데이트를 받기 위해 룸에 조인합니다:

```javascript
socket.emit('join_chapter', { chapter_id: 123 });
```

### 서버 → 클라이언트 이벤트

- `concept-finished` - 개념정리 생성 완료
- `exercise-finished` - 실습과제 생성 완료
- `quiz-finished` - 형성평가 생성 완료
- `quiz-graded` - 퀴즈 채점 완료
- `chapter-complete` - 챕터의 모든 콘텐츠 생성 완료

### Emit 방법 (백엔드)

```python
from socketio_manager import emit_concept_finish

await emit_concept_finish(
    chapter_id=chapter_id,
    data={
        "concept_id": concept.id,
        "chapter_id": chapter_id,
        "content": concept.content
    }
)
```

## Webhook 엔드포인트 (N8N → 백엔드)

N8N이 Gemini 작업 완료 후 호출하는 엔드포인트:

- `POST /v1/chapter/{chapter_id}/concept-finish`
- `POST /v1/chapter/{chapter_id}/exercise-finish`
- `POST /v1/chapter/{chapter_id}/quiz-finish`

**처리 흐름:**
1. Request Body에서 Gemini 생성 결과 파싱
2. DB에 저장 (`is_available=True` 설정)
3. Socket.IO로 클라이언트에 실시간 알림 전송

## 환경 변수

### Backend (.env)

```bash
# Database
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=your_database_name

# JWT
JWT_SECRET_KEY=your-secret-key-change-this-in-production

# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
```

### Infrastructure (infra/.env)

```bash
# N8N
N8N_IMAGE=n8nio/n8n:latest
N8N_PORT=5678

# MySQL
MYSQL_IMAGE=mysql:8.0
MYSQL_PORT=3306
MYSQL_ROOT_PASSWORD=rootpassword
MYSQL_DATABASE=learning_platform
MYSQL_USER=user
MYSQL_PASSWORD=password

# Kafka
KAFKA_IMAGE=bitnami/kafka:latest
KAFKA_PORT=9092

# Redis
REDIS_IMAGE=redis:7-alpine
REDIS_PORT=6379
```

## 주요 개발 패턴

### Repository 패턴 사용

**절대로 라우터에서 직접 `db.query()` 사용 금지.** 반드시 Repository를 통해 DB 작업 수행:

```python
from repository import ChapterRepository
from database import get_db

@router.post("/chapters")
def create_chapter(db: Session = Depends(get_db)):
    repo = ChapterRepository(db)
    chapter = repo.create({
        "title": "New Chapter",
        "course_id": 1
    })
    return chapter
```

### Kafka 이벤트 기반 비동기 처리

- 챕터 생성 시 Kafka 이벤트만 발행하고 **즉시 응답** (200 OK)
- N8N이 이벤트를 받아 Gemini 호출 (비동기)
- 완료되면 N8N이 Webhook 호출하여 결과 저장
- **클라이언트는 Socket.IO로 완료 알림을 실시간 수신**

### JWT 인증

```python
from auth import get_current_user

@router.post("/protected")
def protected_route(current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    email = current_user["email"]
    # ...
```

## 테스트

```bash
cd backend

# 모든 테스트 실행
pytest

# 특정 테스트 파일 실행
pytest test/test_api.py

# 상세 출력
pytest -v
```

## 주의사항

### message.txt 파일

`backend/message (1).txt` 파일은 API 명세 및 프로젝트 설명이 포함된 중요한 문서입니다. 영구 보존하고 참고하세요.

### 기존 코드 vs 새 코드

일부 라우터(`chapter.py` 등)에는 주석 처리된 구버전 코드가 존재합니다. 새 API 명세를 우선하되, 구버전 코드는 참고용으로 보존합니다.

### 멀티플랫폼 지원 (WSL)

현재 개발 환경은 WSL2에서 실행되므로 Windows 경로(`/mnt/c/...`)와 Linux 경로 혼용에 주의하세요.

### Socket.IO 엔드포인트

FastAPI에 Socket.IO를 마운트할 때 `/socket.io` 경로를 사용합니다:

```python
app.mount("/socket.io", socket_app)
```

클라이언트는 `http://localhost:8000/socket.io`로 연결합니다.

## 추가 참고 문서

- `backend/CLAUDE.md` - 백엔드 상세 가이드 (Repository 패턴, 모델 구조 등)
- `backend/schema.sql` - 데이터베이스 스키마 정의
- `infra/workflows/README.md` - 인프라 정보
- `agent/README.md` - N8N 워크플로우 정보
