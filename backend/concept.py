from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models

router = APIRouter(prefix="/v1/concept", tags=["concept"])

# 개념 정리 보기
@router.get("/{chapter_id}")
def get_concept_summary(chapter_id: int, db: Session = Depends(get_db)):
    # chapter_id로 개념 정리 조회
    concept = db.query(models.Concept).filter(
        models.Concept.chapter_id == chapter_id
    ).first()

    if not concept:
        raise HTTPException(status_code=404, detail=f"Concept for chapter {chapter_id} not found")

    return {
        "contents": concept.concept
    }

# 개념 이해 완료
@router.post("/{chapter_id}")
def complete_concept_summary(chapter_id: int):
    return {"message": f"Complete concept summary for chapter {chapter_id}"}

