"""
Course Router
강의 리스트 조회, 강의 생성, 강의 상세 보기
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import schemas
import models
from database import get_db

router = APIRouter(prefix="/v1/course", tags=["course"])


@router.get("/", response_model=List[schemas.CourseResponse])
def get_course_list(db: Session = Depends(get_db)):
    """
    강의 리스트 조회
    등록된 모든 강의 목록을 조회합니다.
    """
    courses = db.query(models.Course).all()

    return [
        schemas.CourseResponse(
            id=course.id,
            title=course.title,
            description=course.description or "",
            difficulty=course.difficulty.value if course.difficulty else "medium",
            owner_id=course.owner_id,
            created_at=course.created_at
        )
        for course in courses
    ]


@router.post("/", response_model=schemas.CourseResponse)
def create_course(course: schemas.CourseCreate, db: Session = Depends(get_db)):
    """
    강의 생성
    새로운 강의를 생성합니다.
    """
    new_course = models.Course(
        title=course.title,
        description=course.description,
        difficulty=course.difficulty,
        owner_id=course.owner_id
    )

    db.add(new_course)
    db.commit()
    db.refresh(new_course)

    return schemas.CourseResponse(
        id=new_course.id,
        title=new_course.title,
        description=new_course.description or "",
        difficulty=new_course.difficulty.value if new_course.difficulty else "medium",
        owner_id=new_course.owner_id,
        created_at=new_course.created_at
    )


@router.get("/{course_id}", response_model=schemas.CourseDetailResponse)
def get_course_detail(course_id: int, db: Session = Depends(get_db)):
    """
    강의 상세 보기
    특정 강의의 상세 정보를 조회합니다.
    """
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail=f"Course {course_id} not found")

    # 챕터 정보 조회
    chapters = db.query(models.Chapter).filter(models.Chapter.course_id == course_id).all()
    chapter_list = [
        schemas.ChapterBasic(id=chapter.id, title=chapter.title)
        for chapter in chapters
    ]

    return schemas.CourseDetailResponse(
        id=course.id,
        title=course.title,
        description=course.description or "",
        difficulty=course.difficulty.value if course.difficulty else "medium",
        chapters=chapter_list
    )
