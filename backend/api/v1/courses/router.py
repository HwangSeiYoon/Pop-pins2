"""
Course Router
강의 CRUD 작업
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import schemas
import models
from database import get_db

router = APIRouter(prefix="/v1/course", tags=["course"])


# 1. 강의 리스트 조회
@router.get("/", response_model=List[schemas.CourseListItem])
def get_course_list(db: Session = Depends(get_db)):
    """등록된 모든 강의 목록을 조회합니다."""
    courses = db.query(models.Course).all()
    return courses


# 2. 강의 생성
@router.post("/", response_model=schemas.CourseResponse)
def create_course(course: schemas.CourseCreate, db: Session = Depends(get_db)):
    """새로운 강의를 생성합니다."""
    new_course = models.Course(
        title=course.title,
        description=course.description,
        difficulty=course.difficulty,
        owner_id=course.owner_id
    )

    db.add(new_course)
    db.commit()
    db.refresh(new_course)

    return new_course


# 3. 강의 상세 보기
@router.get("/{course_id}", response_model=schemas.CourseDetailResponse)
def get_course_detail(course_id: int, db: Session = Depends(get_db)):
    """특정 강의의 상세 정보를 조회합니다."""
    course = db.query(models.Course).filter(models.Course.id == course_id).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # 챕터 리스트 구성
    chapters = [
        schemas.ChapterSimple(id=chapter.id, title=chapter.title)
        for chapter in course.chapters
    ]

    return schemas.CourseDetailResponse(
        id=course.id,
        title=course.title,
        description=course.description or "",
        difficulty=course.difficulty.value if hasattr(course.difficulty, 'value') else course.difficulty,
        chapters=chapters
    )
