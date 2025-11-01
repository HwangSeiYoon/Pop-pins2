# from fastapi import APIRouter, HTTPException, Depends
# from sqlalchemy.orm import Session
# import schemas
# import models
# from database import get_db

# router = APIRouter(prefix="/v1/exercise", tags=["exercise"])

# @router.get("/{chapter_id}")
# def get_exercise(chapter_id: int, db: Session = Depends(get_db)):
#     """
#     특정 챕터의 실습 과제 내용을 반환합니다.
#     """
#     exercise = db.query(models.Exercise).filter(models.Exercise.chapter_id == chapter_id).first()
#     if not exercise:
#         raise HTTPException(status_code=404, detail=f"Exercise for chapter {chapter_id} not found")
    
#     return {"contents": exercise.subject_md}

# @router.post("/{chapter_id}")
# def complete_exercise(chapter_id: int, db: Session = Depends(get_db)):
#     """
#     특정 챕터의 실습 과제를 완료 처리합니다.
#     """
#     exercise = db.query(models.Exercise).filter(models.Exercise.chapter_id == chapter_id).first()
#     if not exercise:
#         raise HTTPException(status_code=404, detail=f"Exercise for chapter {chapter_id} not found")
    
#     exercise.is_complete = "true"  # Or True, depending on the column type
#     db.commit()
    
#     return {}

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import Dict

import schemas
import models
from database import get_db

router = APIRouter(prefix="/v1/exercise", tags=["exercise"])

@router.get("/{chapter_id}", response_model=Dict[str, str])
def get_exercise_content(chapter_id: int, db: Session = Depends(get_db)):
    """
    실습 과제 보기
    - Request: {}
    - Response: {"contents": string}
    """
    exercise = db.query(models.Exercise).filter(models.Exercise.chapter_id == chapter_id).first()
    if not exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="해당 챕터의 실습 과제를 찾을 수 없습니다.")
    
    return {"contents": exercise.subject_md}

@router.post("/{chapter_id}", status_code=status.HTTP_204_NO_CONTENT)
def mark_exercise_as_complete(chapter_id: int, db: Session = Depends(get_db)):
    """
    실습 과제 완료
    - Request: {}
    - Response: {}
    """
    exercise = db.query(models.Exercise).filter(models.Exercise.chapter_id == chapter_id).first()
    if not exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="해당 챕터의 실습 과제를 찾을 수 없습니다.")
    
    exercise.is_complete = True
    db.commit()
    
    return {}
