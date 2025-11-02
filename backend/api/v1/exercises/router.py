"""
Exercise Router
실습 과제 조회 및 완료 처리
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import schemas
import models
from database import get_db
from datetime import datetime, timezone

router = APIRouter(prefix="/v1/exercise", tags=["exercise"])


# 1. 실습 과제 보기
@router.get("/{chapter_id}", response_model=schemas.ExerciseResponse)
def get_exercise(chapter_id: int, db: Session = Depends(get_db)):
    """해당 챕터의 실습 과제를 조회합니다."""
    # 챕터의 실습 과제 조회
    exercise = db.query(models.Exercise).filter(
        models.Exercise.chapter_id == chapter_id
    ).first()

    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    return exercise


# 2. 실습 과제 완료
@router.patch("/{chapter_id}", response_model=schemas.ExerciseUpdateResponse)
def update_exercise_completion(
    chapter_id: int,
    request: schemas.ExerciseUpdateRequest,
    db: Session = Depends(get_db)
):
    """실습 과제 완료 여부를 업데이트합니다."""
    # 챕터의 실습 과제 조회
    exercise = db.query(models.Exercise).filter(
        models.Exercise.chapter_id == chapter_id
    ).first()

    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    # is_complete 업데이트
    exercise.is_complete = request.is_complete
    exercise.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(exercise)

    return schemas.ExerciseUpdateResponse(
        chapter_id=chapter_id,
        is_complete=exercise.is_complete,
        updated_at=exercise.updated_at
    )
