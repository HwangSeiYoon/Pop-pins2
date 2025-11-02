"""
Concept Router
개념 정리 조회 및 완료 처리
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import schemas
import models
from database import get_db
from datetime import datetime, timezone

router = APIRouter(prefix="/v1/concept", tags=["concept"])


# 1. 개념 정리 보기
@router.get("/{chapter_id}", response_model=schemas.ConceptResponse)
def get_concept(chapter_id: int, db: Session = Depends(get_db)):
    """해당 챕터의 개념 정리 내용을 조회합니다."""
    # 챕터의 개념 정리 조회
    concept = db.query(models.Concept).filter(
        models.Concept.chapter_id == chapter_id
    ).first()

    if not concept:
        raise HTTPException(status_code=404, detail="Concept not found")

    return concept


# 2. 개념 학습 완료
@router.patch("/{chapter_id}", response_model=schemas.ConceptUpdateResponse)
def update_concept_completion(
    chapter_id: int,
    request: schemas.ConceptUpdateRequest,
    db: Session = Depends(get_db)
):
    """학습 완료로 상태를 변경합니다."""
    # 챕터의 개념 정리 조회
    concept = db.query(models.Concept).filter(
        models.Concept.chapter_id == chapter_id
    ).first()

    if not concept:
        raise HTTPException(status_code=404, detail="Concept not found")

    # is_complete 업데이트
    concept.is_complete = request.is_complete
    concept.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(concept)

    return schemas.ConceptUpdateResponse(
        chapter_id=chapter_id,
        is_complete=concept.is_complete,
        updated_at=concept.updated_at
    )
