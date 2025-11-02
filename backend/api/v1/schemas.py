"""
Pydantic 스키마 (단일 질문-학습 모드)
질문 1개 → Chapter 1개 → Concept 1개 + Exercise 1개 + Quiz 1개
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# ==================== Member 스키마 ====================

class SignupResponse(BaseModel):
    """회원가입 리스폰스"""
    state: str
    id: int
    email: str
    created_at: datetime

class MemberSignup(BaseModel):
    """회원가입 요청"""
    email: EmailStr
    password: str


class MemberLogin(BaseModel):
    """로그인 요청"""
    email: EmailStr
    password: str


class MemberResponse(BaseModel):
    """회원 정보 응답"""
    id: int
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    """로그인 응답"""
    state: str  # "success" or "failed"
    access_token: str
    token_type: str = "bearer"
    member: MemberResponse


# ==================== Chapter (질문) 스키마 ====================

class ChapterCreate(BaseModel):
    """질문 등록 (챕터 생성)"""
    title: str  # 학생이 질문한 내용
    description: Optional[str] = ""
    owner_id: int  # 로그인한 사용자 (나중에 JWT에서 추출)


class ChapterCreateResponse(BaseModel):
    """질문 등록 응답"""
    chapter_id: int
    concept_id: int
    exercise_id: int
    quiz_id: int
    status: str  # "pending"
    created_at: datetime


# ==================== 단일 학습 페이지 조회 스키마 ====================

class ConceptDTO(BaseModel):
    """개념 DTO"""
    id: int
    title: Optional[str] = None
    content: Optional[str] = None
    is_complete: bool

class ExerciseResponse(BaseModel):
    """실습 과제 응답"""
    id: int
    title: Optional[str] = None
    contents: Optional[str] = None
    is_complete: bool


class ExerciseWithChapterResponse(BaseModel):
    """챕터 정보를 포함한 실습 과제 응답"""
    chapter_id: int
    chapter_title: str
    chapter_contents: Optional[str] = None
    exercise: ExerciseResponse


class ExerciseDTO(BaseModel):
    """연습문제 DTO"""
    id: int
    question: Optional[str] = None
    is_complete: bool


class QuizDTO(BaseModel):
    """퀴즈 DTO (정답은 포함하지 않음)"""
    id: int
    question: Optional[str] = None
    options: Optional[List[str]] = None
    type: str


class SingleLearningPage(BaseModel):
    """단일 학습 페이지 (한 번에 모든 데이터 조회)"""
    chapter_id: int
    title: str
    description: Optional[str] = None
    status: str  # "pending" or "completed"
    concept: Optional[ConceptDTO] = None
    exercise: Optional[ExerciseDTO] = None
    quiz: Optional[QuizDTO] = None


# ==================== Quiz 제출 스키마 ====================

class QuizSubmit(BaseModel):
    """퀴즈 정답 제출"""
    answer: str
    member_id: int  # 나중에 JWT에서 추출 가능


class QuizSubmitResponse(BaseModel):
    """퀴즈 제출 응답"""
    is_correct: bool
    score: int
    explanation: Optional[str] = None


# ==================== N8N Webhook 스키마 ====================

class ConceptWebhook(BaseModel):
    """개념 정리 생성 완료 webhook (n8n → 백엔드)"""
    title: str
    content: str


class ExerciseWebhook(BaseModel):
    """실습 과제 생성 완료 webhook (n8n → 백엔드)"""
    question: str
    answer: str


class QuizWebhook(BaseModel):
    """퀴즈 생성 완료 webhook (n8n → 백엔드)"""
    question: str
    correct_answer: str
    options: Optional[List[str]] = None
    type: str = "multiple"


class WebhookResponse(BaseModel):
    """Webhook 응답 (공통)"""
    status: str
    message: str
    chapter_id: int


# ==================== 챕터 목록 조회 스키마 ====================

class ChapterListItem(BaseModel):
    """챕터 목록 항목"""
    id: int
    title: str
    description: Optional[str] = None
    status: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
