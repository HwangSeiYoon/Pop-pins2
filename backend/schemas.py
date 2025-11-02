"""
Pydantic Schemas for Request/Response models
"""

from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime


# ============================================
# Member Schemas
# ============================================

class MemberSignup(BaseModel):
    email: EmailStr
    password: str


class MemberSignupResponse(BaseModel):
    id: int
    email: str
    created_at: datetime


class MemberLogin(BaseModel):
    email: EmailStr
    password: str


class MemberLoginResponse(BaseModel):
    access_token: str
    token_type: str
    member_id: int


class MemberInfoResponse(BaseModel):
    id: int
    email: str
    created_at: datetime


# ============================================
# Course Schemas
# ============================================

class CourseCreate(BaseModel):
    title: str
    description: str
    difficulty: str
    owner_id: int


class CourseResponse(BaseModel):
    id: int
    title: str
    description: str
    difficulty: str
    owner_id: int
    created_at: datetime


class ChapterBasic(BaseModel):
    id: int
    title: str


# 강의 상세 보기용 챕터 정보
class ChapterDetailForCourse(BaseModel):
    id: int
    title: str
    description: str
    is_created: bool  # concept, exercise, quiz가 모두 생성되었는지
    completionCount: int  # 개념정리, 실습과제, 형성평가 완료 개수 (0~3)


class CourseDetailResponse(BaseModel):
    courseTitle: str
    courseDescription: str
    difficulty: str
    chapters: List[ChapterDetailForCourse]


# 강의 생성 요청 (Gemini가 자동으로 챕터 생성)
class CourseGenerateRequest(BaseModel):
    courseTitle: str
    courseDescription: str
    prompt: str
    maxchapters: int
    link: List[str]
    difficulty: str


# 강의 생성 응답 (즉시 응답)
class CourseGenerateImmediateResponse(BaseModel):
    status: str  # "submitted"
    message: str
    course_id: int


# Gemini가 생성한 챕터 정보
class GeneratedChapterInfo(BaseModel):
    chapterId: int
    chapterTitle: str
    chapterDescription: str


# Gemini가 생성한 강의 전체 정보 (Webhook으로 받음)
class WebhookCourseGenerateResponse(BaseModel):
    course: dict  # {"id": int, "chapters": List[GeneratedChapterInfo]}


# ============================================
# Chapter Schemas
# ============================================

class ChapterCreate(BaseModel):
    course_id: int
    title: str
    description: str
    owner_id: int


class ChapterCreateResponse(BaseModel):
    chapter_id: int
    concept_id: int
    exercise_id: int
    quiz_slots: List[int]
    created_at: datetime


class ConceptStatus(BaseModel):
    id: int
    is_complete: bool


class ExerciseStatus(BaseModel):
    id: int
    is_complete: bool


class QuizSlot(BaseModel):
    slot_number: int
    status: str  # pending, completed

class ChapterDetailConcept(BaseModel):
    is_available: bool
    concept_description: list[str]
    is_complete: bool

class ChapterDetailExercise(BaseModel):
    is_available: bool
    exercise_description: list[str]
    is_complete: bool

class ChapterDetailQuiz(BaseModel):
    is_available: bool
    quiz_description: list[str]
    is_complete: bool

class ChapterDetailResponse(BaseModel):
    id: int
    concept: ChapterDetailConcept
    exercise: ChapterDetailExercise
    quiz: ChapterDetailQuiz


# ============================================
# Concept Schemas
# ============================================

class ConceptResponse(BaseModel):
    title: str
    contents: str
    chapter_id: int


class ConceptComplete(BaseModel):
    is_complete: bool


class ConceptCompleteResponse(BaseModel):
    chapter_id: int
    is_complete: bool
    updated_at: datetime


# ============================================
# Exercise Schemas
# ============================================


class ExerciseResponse(BaseModel):
    chapter_id: int
    title: str
    description: str
    contents: str


class ExerciseComplete(BaseModel):
    is_complete: bool


class ExerciseCompleteResponse(BaseModel):
    chapter_id: int
    is_complete: bool
    updated_at: datetime


# ============================================
# Quiz Schemas
# ============================================

class QuizItem(BaseModel):
    id: int
    title: str

class QuizContent(BaseModel):
    contents: list[QuizItem]

class QuizSubmit(BaseModel):
    id: int
    answer: str

class QuizSubmitContent(BaseModel):
    answers: list[QuizSubmit]


class QuizSubmitResponse(BaseModel):
    pass


class QuizComplete(BaseModel):
    status: str  # completed


class QuizCompleteResponse(BaseModel):
    chapter_id: int
    status: str
    updated_at: datetime


class QuizResultResponse(BaseModel):
    chapter_id: int
    correct_count: int
    total: int
    score: int
    accuracy: float


class QuizRestartResponse(BaseModel):
    chapter_id: int
    reset_status: bool
    updated_at: datetime


# ============================================
# N8N Webhook Schemas
# ============================================

# 개념 정리 생성 요청 (N8N Webhook)
class WebhookConceptRequest(BaseModel):
    courseTitle: str
    courseDescription: str
    chapterTitle: str
    chapterDescription: str


class WebhookConceptResponse(BaseModel):
    title: str
    description: str
    contents: str


# 실습 생성 요청 (N8N Webhook)
class WebhookExerciseRequest(BaseModel):
    courseTitle: str
    courseDescription: str
    chapterTitle: str
    chapterDescription: str


class WebhookExerciseResponse(BaseModel):
    title: str
    description: str
    contents: str  # md 파일


# 형성평가 생성 요청 (N8N Webhook)
class WebhookQuizRequest(BaseModel):
    courseTitle: str
    chapterTitle: str
    coursePrompt: str


class WebhookQuizItem(BaseModel):
    quiz: str


class WebhookQuizResponse(BaseModel):
    quizes: List[WebhookQuizItem]


# 퀴즈 정답 제출 요청 (N8N Webhook)
class WebhookAnswerQuizItem(BaseModel):
    quiz: str
    answer: str


class WebhookAnswerOutput(BaseModel):
    courseTitle: str
    courseDescription: str
    contents: List[WebhookAnswerQuizItem]


class WebhookAnswerRequest(BaseModel):
    output: WebhookAnswerOutput


class WebhookAnswerScore(BaseModel):
    id: int
    score: int
    correct_answer: str


class WebhookAnswerResponse(BaseModel):
    scores: List[WebhookAnswerScore]


# 퀴즈 채점 결과 Webhook (N8N → Backend)
class WebhookQuizGradingResult(BaseModel):
    chapter_id: int
    quiz_id: int
    slot_number: int
    member_id: int
    is_correct: bool
    score: int
    correct_answer: str
    explanation: Optional[str] = None
