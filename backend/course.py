"""
Course Router
강의 리스트 조회, 강의 생성, 강의 상세 보기
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import json
import schemas
import models
from database import get_db
from kafka_producer import send_course_generate_event

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


@router.post("/generate", response_model=schemas.CourseGenerateImmediateResponse)
def generate_course(
    request_data: schemas.CourseGenerateRequest,
    db: Session = Depends(get_db)
):
    """
    강의 생성 (비동기 처리)

    흐름:
    1. 즉시 응답 반환 (status: submitted)
    2. Kafka 이벤트 발행 → N8N → Gemini가 챕터 생성
    3. Webhook으로 결과 수신 → DB에 챕터 저장 → Socket.IO로 클라이언트에게 알림

    Returns:
        즉시 응답: { "status": "submitted", "message": "...", "course_id": int }
    """
    # 코스 생성 (link는 JSON으로 저장)
    new_course = models.Course(
        title=request_data.courseTitle,
        description=request_data.courseDescription,
        difficulty=request_data.difficulty,
        prompt=request_data.prompt,
        link=json.dumps(request_data.link),  # JSON 문자열로 저장
        owner_id=1  # TODO: 실제 owner_id 전달 필요
    )

    db.add(new_course)
    db.commit()
    db.refresh(new_course)

    # Kafka 이벤트 발행 (N8N이 받아서 Gemini 호출)
    send_course_generate_event(
        course_id=new_course.id,
        course_title=request_data.courseTitle,
        course_description=request_data.courseDescription,
        prompt=request_data.prompt,
        maxchapters=request_data.maxchapters,
        link=request_data.link,
        difficulty=request_data.difficulty,
        owner_id=1  # TODO: 실제 owner_id
    )

    # 즉시 응답 반환
    return schemas.CourseGenerateImmediateResponse(
        status="submitted",
        message="강의 생성 요청이 접수되었습니다. 챕터 생성 결과는 실시간으로 전송됩니다.",
        course_id=new_course.id
    )


@router.get("/{course_id}", response_model=schemas.CourseDetailResponse)
def get_course_detail(course_id: int, db: Session = Depends(get_db)):
    """
    강의 상세 보기
    특정 강의의 상세 정보와 챕터별 완료 상태를 조회합니다.
    """
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail=f"Course {course_id} not found")

    # 챕터 정보 조회
    chapters = db.query(models.Chapter).filter(models.Chapter.course_id == course_id).all()

    chapter_list = []
    for chapter in chapters:
        # Concept, Exercise, Quiz 조회
        concept = db.query(models.Concept).filter(models.Concept.chapter_id == chapter.id).first()
        exercise = db.query(models.Exercise).filter(models.Exercise.chapter_id == chapter.id).first()
        quizzes = db.query(models.Quiz).filter(models.Quiz.chapter_id == chapter.id).all()

        # is_created: concept, exercise, quiz가 모두 생성되었는지 (is_available=True)
        is_created = (
            concept and concept.is_available and
            exercise and exercise.is_available and
            len(quizzes) > 0 and all(q.is_available for q in quizzes)
        )

        # completionCount: is_complete=True인 항목 개수 (0~3)
        completion_count = 0
        if concept and concept.is_complete:
            completion_count += 1
        if exercise and exercise.is_complete:
            completion_count += 1
        # Quiz는 모든 퀴즈가 완료되어야 카운트
        if quizzes and all(q.is_complete for q in quizzes):
            completion_count += 1

        chapter_list.append(
            schemas.ChapterDetailForCourse(
                id=chapter.id,
                title=chapter.title,
                description=chapter.description or "",
                is_created=is_created,
                completionCount=completion_count
            )
        )

    return schemas.CourseDetailResponse(
        courseTitle=course.title,
        courseDescription=course.description or "",
        difficulty=course.difficulty.value if course.difficulty else "medium",
        chapters=chapter_list
    )
