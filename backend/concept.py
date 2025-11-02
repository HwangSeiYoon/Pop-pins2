"""
Concept Router
개념 정리 보기, 개념 학습 완료
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
import schemas
import models
from database import get_db

router = APIRouter(prefix="/v1/concept", tags=["concept"])


@router.get("/{chapter_id}", response_model=schemas.ConceptResponse)
def get_concept_summary(chapter_id: int, db: Session = Depends(get_db)):
    """
    개념 정리 보기
    해당 챕터의 개념 정리 내용을 조회합니다.
    """
    # 챕터의 개념정리 조회
    concept = db.query(models.Concept).filter(models.Concept.chapter_id == chapter_id).first()

    if not concept:
        raise HTTPException(status_code=404, detail=f"Concept for chapter {chapter_id} not found")

    return schemas.ConceptResponse(
        title=concept.title or "",
        contents=concept.content or "",
        chapter_id=concept.chapter_id
    )


@router.patch("/{chapter_id}", status_code=204)
def complete_concept_summary(
    chapter_id: int,
    db: Session = Depends(get_db)
):
    """
    개념 학습 완료
    학습 완료로 상태를 변경합니다.
    URI의 chapter_id로 해당 챕터의 개념정리를 찾아 is_complete를 True로 설정합니다.
    """
    # 챕터의 개념정리 조회
    concept = db.query(models.Concept).filter(models.Concept.chapter_id == chapter_id).first()

    if not concept:
        raise HTTPException(status_code=404, detail=f"Concept for chapter {chapter_id} not found")

    # 완료 상태 업데이트
    concept.is_complete = True
    db.commit()
