# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

이 프로젝트는 AI 기반 학습 플랫폼의 FastAPI 백엔드입니다. 사용자가 코스를 생성하면 N8N과 Gemini가 자동으로 챕터별 개념정리, 실습과제, 형성평가를 생성합니다.

## Architecture

### 핵심 흐름
1. **코스 생성** → Kafka 이벤트 발행
2. **챕터 생성** → Kafka 이벤트 발행 → N8N이 Gemini 호출
3. **Gemini 완료** → N8N이 Webhook으로 결과 전송 → DB 저장 및 Socket.IO로 클라이언트 알림

### Database Layer (Repository Pattern)

**구조:**
- `models.py` - SQLAlchemy ORM 모델 정의
- `database.py` - DB 연결 설정 및 세션 관리
- `repository/` - CRUD 작업을 담당하는 Repository 패턴
  - `base_repository.py` - 모든 기본 CRUD 작업 (create, get, update, delete, count)
  - `member_repository.py` - 회원 관리
  - `course_repository.py` - 코스 관리
  - `chapter_repository.py` - 챕터 관리
  - `concept_repository.py` - 개념정리 관리
  - `exercise_repository.py` - 실습과제 관리
  - `quiz_repository.py` - 퀴즈/형성평가 관리

**Repository 사용 방법:**
```python
from repository import MemberRepository
from database import get_db

@router.post("/members")
def create_member(db: Session = Depends(get_db)):
    repo = MemberRepository(db)
    member = repo.create({"email": "test@test.com", "password": "hashed"})
    return member
```

각 Repository는 BaseRepository를 상속받아 공통 CRUD 작업을 제공하며, 모델별 특화 메서드를 추가로 구현합니다.

### API Routes Layer

**라우터 파일들:**
- `course.py` - 코스 생성, 조회, 리스트
- `chapter.py` - 챕터 생성, 조회 및 **Webhook 엔드포인트** (N8N이 호출)
- `concept.py` - 개념정리 조회 및 완료 처리
- `exercise.py` - 실습과제 조회 및 완료 처리

### External Integrations

**Kafka:**
- `kafka_producer.py` (존재 가정) - 이벤트 발행
  - `send_course_created_event()`
  - `send_chapter_created_event()`
  - `send_concept_created_event()`
  - `send_exercise_created_event()`

**Socket.IO:**
- `socketio_manager.py` (존재 가정) - 실시간 클라이언트 알림
  - `emit_concept_finish()`
  - `emit_exercise_finish()`
  - `emit_quiz_finish()`

### Webhook 처리 (chapter.py)

N8N이 Gemini 작업 완료 후 호출하는 엔드포인트:
- `POST /v1/chapter/{chapter_id}/concept-finish` - 개념정리 완료
- `POST /v1/chapter/{chapter_id}/exercise-finish` - 실습과제 완료
- `POST /v1/chapter/{chapter_id}/quiz-finish` - 형성평가 완료

각 Webhook은:
1. DB에 생성된 데이터 저장 (`is_available=True` 설정)
2. Socket.IO로 클라이언트에 실시간 알림 전송

## Key Models

### Member
- 회원 정보 (id, email, password)
- Course, Chapter, Concept, Exercise, Quiz의 owner

### Course
- 코스 정보 (title, description, prompt, difficulty)
- JSON 형태로 link 배열 저장 (`json.dumps()` 사용)
- member_id로 소유자 참조

### Chapter
- 챕터 정보 (title, description, order_num)
- course_id로 코스 참조
- Concept, Exercise, Quiz를 포함

### Concept, Exercise, Quiz
- 각각 개념정리, 실습과제, 형성평가
- `is_available` - Gemini 생성 완료 여부
- `is_complete` - 사용자 학습 완료 여부

## Database Schema

데이터베이스 스키마는 `ㅁㅁ.sql` 파일에 정의되어 있으며, 이를 기반으로 `models.py`가 생성되었습니다.

**주요 관계:**
- Member 1:N Course
- Course 1:N Chapter
- Chapter 1:N (Concept, Exercise, Quiz)

## Authentication

`auth.py`에서 JWT 기반 인증 제공:
- `get_password_hash()` - 비밀번호 해싱
- `verify_password()` - 비밀번호 검증
- `create_access_token()` - JWT 토큰 생성
- `get_current_user()` - FastAPI Dependency로 현재 사용자 가져오기

**사용 예시:**
```python
@router.post("/protected")
def protected_route(current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    email = current_user["email"]
```

## Environment Variables

`database.py`에서 사용하는 환경 변수:
- `DB_USER` (기본값: root)
- `DB_PASSWORD` (기본값: "")
- `DB_HOST` (기본값: localhost)
- `DB_PORT` (기본값: 3306)
- `DB_NAME` (기본값: your_database_name)

`auth.py`에서 사용:
- `JWT_SECRET_KEY` (기본값: your-secret-key-change-this-in-production)

## Important Notes

### Repository 패턴 사용
- **반드시** Repository를 통해 DB 작업 수행
- 라우터에서 직접 `db.query(models.Model)`보다 Repository 사용 권장
- 새로운 쿼리 로직은 Repository에 메서드로 추가

### 기존 코드 vs 새 코드
- `chapter.py`에는 주석 처리된 구버전 코드가 존재
- 새 API 명세에 따른 엔드포인트를 우선 사용
- 구버전 코드는 참고용으로 보존

### Kafka + N8N + Gemini 워크플로우
- 챕터 생성 시 Kafka 이벤트만 발행하고 즉시 응답
- N8N이 이벤트를 받아 Gemini 호출 (비동기)
- 완료되면 N8N이 Webhook 호출하여 결과 저장

### Socket.IO 실시간 알림
- Webhook 처리 시 `emit_*_finish()` 함수 호출 필수
- 클라이언트가 생성 완료를 실시간으로 받을 수 있음
