"""
Course Router
강의 CRUD 작업
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from utils.auth_middleware import require_auth
# from typing import List
# from api.v1.schemas import CourseListItem, CourseCreate, CourseResponse, CourseDetailResponse, ChapterSimple  # 스키마 없음
from db import models
from db.database import get_db

router = APIRouter(prefix="/v1/course", tags=["course"])


# 1. 강의 리스트 조회
@router.get("/")
def get_course_list(
    current_user: dict = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """등록된 모든 강의 목록을 조회합니다."""
    courses = db.query(models.Course).all()

    return [
        {
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "difficulty": course.difficulty,
            "owner_id": course.owner_id,
            "created_at": course.created_at.isoformat() if course.created_at else None
        }
        for course in courses
    ]


# 2. 강의 생성 (CourseMaker 지원)
@router.post("/")
def create_course(
    course_data: dict,
    current_user: dict = Depends(require_auth),  # JWT 인증 활성화
    db: Session = Depends(get_db)
):
    """
    새로운 강의를 생성합니다.
    
    CourseMaker에서 호출 시:
    {
        "title": "강의 제목",
        "description": "강의 설명", 
        "difficulty": "medium",
        "chapters": [
            {
                "chapterId": 1,
                "chapterTitle": "챕터 제목",
                "chapterDescription": "챕터 설명"
            },
            ...
        ]
    }
    """
    # 디버깅: 받은 데이터 로그 출력
    print(f"🔍 DEBUG - 받은 course_data: {course_data}")
    print(f"🔍 DEBUG - chapters 데이터: {course_data.get('chapters', [])}")
    print(f"🔍 DEBUG - chapters 타입: {type(course_data.get('chapters', []))}")
    print(f"🔍 DEBUG - chapters 길이: {len(course_data.get('chapters', []))}")
    # 1. 코스 생성
    new_course = models.Course(
        title=course_data.get("title", ""),
        description=course_data.get("description", ""),
        difficulty=course_data.get("difficulty", "medium"),
        owner_id=current_user["user_id"]  # JWT에서 추출한 사용자 ID 사용
    )

    db.add(new_course)
    db.flush()  # course.id 생성

    # 2. 챕터들 생성 (CourseMaker에서 전달된 경우)
    chapters_data = course_data.get("chapters", [])
    created_chapters = []
    
    print(f"📝 DEBUG - chapters_data 상세: {chapters_data}")
    
    for i, chapter_data in enumerate(chapters_data):
        print(f"📝 DEBUG - 챕터 {i+1}: {chapter_data}")
        print(f"📝 DEBUG - chapterTitle: {chapter_data.get('chapterTitle', 'N/A')}")
        print(f"📝 DEBUG - chapterDescription: {chapter_data.get('chapterDescription', 'N/A')}")
        
        new_chapter = models.Chapter(
            course_id=new_course.id,
            owner_id=current_user["user_id"],
            title=chapter_data.get("chapterTitle", ""),
            description=chapter_data.get("chapterDescription", ""),
            status=models.StatusEnum.pending,  # AI 콘텐츠 생성 대기
            is_active=True
        )
        db.add(new_chapter)
        db.flush()  # chapter.id 생성
        
        # 3. 각 챕터마다 빈 Concept, Exercise, Quiz 생성
        # Concept 생성 (빈 값)
        new_concept = models.Concept(
            chapter_id=new_chapter.id,
            title=None,
            content=None,
            is_complete=False
        )
        db.add(new_concept)
        
        # Exercise 생성 (빈 값)
        new_exercise = models.Exercise(
            chapter_id=new_chapter.id,
            title=None,
            contents=None,
            is_complete=False
        )
        db.add(new_exercise)
        
        # Quiz 생성 (빈 값)
        new_quiz = models.Quiz(
            chapter_id=new_chapter.id,
            question=None,
            options=None,
            correct_answer=None,
            type=models.QuizTypeEnum.multiple
        )
        db.add(new_quiz)
        
        created_chapters.append({
            "id": new_chapter.id,
            "title": new_chapter.title,
            "description": new_chapter.description,
            "status": new_chapter.status.value
        })

    db.commit()
    db.refresh(new_course)

    # TODO: 각 챕터에 대해 ConceptMaker, ExerciseMaker, QuizMaker 호출
    # for chapter in created_chapters:
    #     trigger_concept_maker(chapter["id"], new_course.title, new_course.description, chapter["title"], chapter["description"])
    #     trigger_exercise_maker(chapter["id"], ...)
    #     trigger_quiz_maker(chapter["id"], ...)

    return {
        "id": new_course.id,
        "title": new_course.title,
        "description": new_course.description,
        "difficulty": new_course.difficulty,
        "owner_id": new_course.owner_id,
        "created_at": new_course.created_at.isoformat() if new_course.created_at else None,
        "chapters": created_chapters
    }


# 3. 강의 상세 보기
@router.get("/{course_id}")
def get_course_detail(
    course_id: int,
    current_user: dict = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """특정 강의의 상세 정보를 조회합니다."""
    course = db.query(models.Course).filter(models.Course.id == course_id).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # 코스에 속한 챕터들 조회
    chapters = db.query(models.Chapter).filter(models.Chapter.course_id == course_id).all()
    
    chapters_data = [
        {
            "id": chapter.id,
            "title": chapter.title,
            "description": chapter.description,
            "status": chapter.status.value,
            "created_at": chapter.created_at.isoformat() if chapter.created_at else None
        }
        for chapter in chapters
    ]

    return {
        "course": {
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "difficulty": course.difficulty,
            "owner_id": course.owner_id,
            "created_at": course.created_at.isoformat() if course.created_at else None,
            "chapters": chapters_data
        }
    }
