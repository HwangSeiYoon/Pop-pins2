"""
Quiz Router (단일 퀴즈 제출)
챕터당 퀴즈 1개, 정답 제출 및 채점
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from api.v1.schemas import QuizSubmit, QuizSubmitResponse
from db import models
from db.database import get_db

router = APIRouter(prefix="/v1/quiz", tags=["quiz"])


@router.post("/{chapter_id}/submit", response_model=QuizSubmitResponse)
def submit_quiz(
    chapter_id: int,
    submission: QuizSubmit,
    db: Session = Depends(get_db)
):
    """
    퀴즈 정답 제출 및 채점

    Flow:
    1. chapter_id로 퀴즈 조회 (1:1 관계)
    2. 정답 비교
    3. 점수 계산 (맞으면 100점, 틀리면 0점)
    4. 결과 반환 (is_correct, score, explanation)
    """
    # 챕터 존재 확인
    chapter = db.query(models.Chapter).filter(models.Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    # 퀴즈 조회 (1:1)
    quiz = db.query(models.Quiz).filter(models.Quiz.chapter_id == chapter_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    # 퀴즈가 아직 생성되지 않았으면 에러
    if not quiz.question or not quiz.correct_answer:
        raise HTTPException(status_code=400, detail="Quiz is not ready yet")

    # 정답 확인 (대소문자 무시)
    user_answer = submission.answer.strip()
    correct_answer = quiz.correct_answer.strip()

    is_correct = user_answer.lower() == correct_answer.lower()
    score = 100 if is_correct else 0

    return QuizSubmitResponse(
        is_correct=is_correct,
        score=score,
        explanation=quiz.explanation
    )
