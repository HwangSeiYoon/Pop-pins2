"""
Chapter Router
챕터 생성, 챕터 상세 보기
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
import schemas
import models
from database import get_db
from kafka_producer import send_chapter_created_event

router = APIRouter(prefix="/v1/chapter", tags=["chapter"])


@router.post("/", response_model=schemas.ChapterCreateResponse)
def create_chapter(
    chapter: schemas.ChapterCreate,
    db: Session = Depends(get_db)
):
    """
    챕터 생성
    새 챕터를 생성하고, 아래 세 가지 리소스를 동시에 생성합니다:
    - 개념 정리(concept)
    - 실습 과제(exercise)
    - 형성평가(quiz: 3개 slot)
    """
    # 강의 존재 확인
    course = db.query(models.Course).filter(models.Course.id == chapter.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail=f"Course {chapter.course_id} not found")

    # 챕터 생성
    new_chapter = models.Chapter(
        course_id=chapter.course_id,
        owner_id=chapter.owner_id,
        title=chapter.title,
        description=chapter.description,
        is_active=True,
        order_index=0  # TODO: 순서 자동 계산
    )
    db.add(new_chapter)
    db.commit()
    db.refresh(new_chapter)

    # Concept 생성 (빈 상태, N8N + Gemini가 채움)
    new_concept = models.Concept(
        chapter_id=new_chapter.id,
        owner_id=chapter.owner_id,
        title=f"{chapter.title} - 개념정리",
        content="",  # Gemini가 채울 예정
        is_complete=False
    )
    db.add(new_concept)
    db.commit()
    db.refresh(new_concept)

    # Exercise 생성 (빈 상태, N8N + Gemini가 채움)
    new_exercise = models.Exercise(
        chapter_id=new_chapter.id,
        owner_id=chapter.owner_id,
        question="",  # Gemini가 채울 예정
        answer="",
        difficulty="medium",
        is_complete=False
    )
    db.add(new_exercise)
    db.commit()
    db.refresh(new_exercise)

    # Quiz 3개 슬롯 생성 (빈 상태, N8N + Gemini가 채움)
    for slot_num in range(1, 4):
        new_quiz = models.Quiz(
            chapter_id=new_chapter.id,
            owner_id=chapter.owner_id,
            question="",  # Gemini가 채울 예정
            correct_answer="",
            type="multiple"  # 기본값
        )
        db.add(new_quiz)
    db.commit()

    # Kafka 이벤트 발행 - N8N이 이를 받아서 Gemini 호출
    send_chapter_created_event(
        chapter_id=new_chapter.id,
        course_id=course.id,
        owner_id=chapter.owner_id,
        course_title=course.title,
        course_description=course.description or "",
        chapter_title=chapter.title,
        chapter_description=chapter.description,
        course_prompt=""  # TODO: Course에서 prompt 필드 추가 필요
    )

    return schemas.ChapterCreateResponse(
        chapter_id=new_chapter.id,
        concept_id=new_concept.id,
        exercise_id=new_exercise.id,
        quiz_slots=[1, 2, 3],
        created_at=new_chapter.created_at
    )


@router.get("/{chapter_id}", response_model=schemas.ChapterDetailResponse)
def get_chapter_detail(chapter_id: int, db: Session = Depends(get_db)):
    """
    챕터 상세 보기
    챕터의 개요 및 관련 리소스 상태를 조회합니다.
    """
    # 챕터 조회
    chapter = db.query(models.Chapter).filter(models.Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail=f"Chapter {chapter_id} not found")

    # Concept 조회
    concepts = db.query(models.Concept).filter(models.Concept.chapter_id == chapter_id).all()
    if concepts:
        concept = concepts[0]
        concept_status = schemas.ConceptStatus(
            id=concept.id,
            is_complete=concept.is_complete or False
        )
    else:
        concept_status = schemas.ConceptStatus(id=0, is_complete=False)

    # Exercise 조회
    exercises = db.query(models.Exercise).filter(models.Exercise.chapter_id == chapter_id).all()
    if exercises:
        exercise = exercises[0]
        exercise_status = schemas.ExerciseStatus(
            id=exercise.id,
            is_complete=exercise.is_complete or False
        )
    else:
        exercise_status = schemas.ExerciseStatus(id=0, is_complete=False)

    # Quiz 조회 (3개 슬롯)
    quizzes = db.query(models.Quiz).filter(models.Quiz.chapter_id == chapter_id).limit(3).all()
    quiz_statuses = []
    for i in range(1, 4):
        if i <= len(quizzes):
            # TODO: 실제 완료 상태 확인 필요
            quiz_statuses.append(schemas.QuizSlot(slot_number=i, status="pending"))
        else:
            quiz_statuses.append(schemas.QuizSlot(slot_number=i, status="pending"))

    c = db.query(models.Concept).filter(models.Chapter.id == chapter_id).first()

    conceptNull = False
    if not c:
        conceptNull = True
    concept = schemas.ChapterDetailConcept(
        is_available=conceptNull,

    )

    return schemas.ChapterDetailResponse(
        id=chapter.id,
        title=chapter.title,
        description=chapter.description or "",
        is_active=chapter.is_active or True,
        concept=concept_status,
        exercise=exercise_status,
        quiz=quiz_statuses
    )
