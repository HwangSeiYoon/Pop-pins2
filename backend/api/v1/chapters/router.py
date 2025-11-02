"""
Chapter Router (단일 질문-학습 모드)
질문 등록 및 학습 페이지 조회
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional, List
from api.v1.schemas import schemas
from db.models import models
from db.database import get_db
from core.socketio_manager import (
    emit_chapter_processing_started,
    emit_concept_processing,
    emit_exercise_processing,
    emit_quiz_processing,
    emit_concept_completed,
    emit_exercise_completed,
    emit_quiz_completed,
    emit_all_completed
)

router = APIRouter(prefix="/v1/chapter", tags=["chapter"])


# 1. 질문 등록 (챕터 생성)
@router.post("/", response_model=schemas.ChapterCreateResponse)
async def create_chapter(chapter: schemas.ChapterCreate, db: Session = Depends(get_db)):
    """
    학생이 질문을 등록합니다.
    질문 1개 → Chapter 1개 → Concept 1개 + Exercise 1개 + Quiz 1개 (빈 값)

    Flow:
    1. 챕터 생성 (title = 질문)
    2. 빈 Concept, Exercise, Quiz 생성
    3. Socket.IO로 처리 시작 알림 발송
    4. Kafka로 AI 생성 요청 전송 (실제 Kafka 코드는 미구현)
    5. n8n이 AI 응답을 받아 webhook으로 전송
    """
    # 챕터 생성
    new_chapter = models.Chapter(
        owner_id=chapter.owner_id,
        title=chapter.title,
        description=chapter.description,
        status=models.StatusEnum.pending,
        is_active=True
    )
    db.add(new_chapter)
    db.flush()  # chapter.id 생성

    # 개념 정리 생성 (빈 값)
    new_concept = models.Concept(
        chapter_id=new_chapter.id,
        title=None,
        content=None,
        is_complete=False
    )
    db.add(new_concept)
    db.flush()

    # 실습 과제 생성 (빈 값)
    new_exercise = models.Exercise(
        chapter_id=new_chapter.id,
        question=None,
        answer=None,
        is_complete=False
    )
    db.add(new_exercise)
    db.flush()

    # 퀴즈 생성 (빈 값)
    new_quiz = models.Quiz(
        chapter_id=new_chapter.id,
        question=None,
        options=None,
        correct_answer=None,
        type=models.QuizTypeEnum.multiple
    )
    db.add(new_quiz)
    db.flush()

    db.commit()
    db.refresh(new_chapter)

    # Socket.IO 실시간 알림 발송 - 처리 시작
    await emit_chapter_processing_started(new_chapter.id, new_chapter.title)
    await emit_concept_processing(new_chapter.id, new_concept.id)
    await emit_exercise_processing(new_chapter.id, new_exercise.id)
    await emit_quiz_processing(new_chapter.id, 1)

    # TODO: Kafka로 AI 생성 요청 전송
    # send_to_kafka(chapter_id=new_chapter.id, title=new_chapter.title)

    return schemas.ChapterCreateResponse(
        chapter_id=new_chapter.id,
        concept_id=new_concept.id,
        exercise_id=new_exercise.id,
        quiz_id=new_quiz.id,
        status=new_chapter.status.value,
        created_at=new_chapter.created_at
    )


# 2. 단일 학습 페이지 조회 (한 번에 모든 데이터)
@router.get("/{chapter_id}/learning", response_model=schemas.SingleLearningPage)
def get_learning_page(chapter_id: int, db: Session = Depends(get_db)):
    """
    단일 학습 페이지 조회
    Chapter + Concept + Exercise + Quiz를 한 번에 조회

    프론트엔드는 이 API 한 번만 호출하면 모든 데이터를 받을 수 있습니다.
    """
    # 챕터 조회
    chapter = db.query(models.Chapter).filter(models.Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    # Concept 조회 (1:1)
    concept = db.query(models.Concept).filter(models.Concept.chapter_id == chapter_id).first()
    concept_dto = None
    if concept:
        concept_dto = schemas.ConceptDTO(
            id=concept.id,
            title=concept.title,
            content=concept.content,
            is_complete=concept.is_complete
        )

    # Exercise 조회 (1:1)
    exercise = db.query(models.Exercise).filter(models.Exercise.chapter_id == chapter_id).first()
    exercise_dto = None
    if exercise:
        exercise_dto = schemas.ExerciseDTO(
            id=exercise.id,
            question=exercise.question,
            is_complete=exercise.is_complete
        )

    # Quiz 조회 (1:1)
    quiz = db.query(models.Quiz).filter(models.Quiz.chapter_id == chapter_id).first()
    quiz_dto = None
    if quiz:
        # 옵션이 JSON 문자열인 경우 파싱
        options = None
        if quiz.options:
            import json
            if isinstance(quiz.options, str):
                options = json.loads(quiz.options)
            else:
                options = quiz.options

        quiz_dto = schemas.QuizDTO(
            id=quiz.id,
            question=quiz.question,
            options=options,
            type=quiz.type.value
        )

    return schemas.SingleLearningPage(
        chapter_id=chapter.id,
        title=chapter.title,
        description=chapter.description,
        status=chapter.status.value,
        concept=concept_dto,
        exercise=exercise_dto,
        quiz=quiz_dto
    )


# 3. 챕터 목록 조회
@router.get("/", response_model=List[schemas.ChapterListItem])
def get_chapters(
    skip: int = 0,
    limit: int = 20,
    owner_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    챕터 목록 조회 (학생의 질문 목록)
    """
    query = db.query(models.Chapter)

    if owner_id:
        query = query.filter(models.Chapter.owner_id == owner_id)

    chapters = query.order_by(models.Chapter.created_at.desc()).offset(skip).limit(limit).all()

    return [schemas.ChapterListItem.from_orm(chapter) for chapter in chapters]


# ==================== N8N Webhook 엔드포인트 ====================

@router.post("/{chapter_id}/concept-finish", response_model=schemas.WebhookResponse)
async def concept_finish_webhook(
    chapter_id: int,
    data: schemas.ConceptWebhook,
    db: Session = Depends(get_db)
):
    """
    개념 정리 생성 완료 webhook (n8n → 백엔드)
    """
    chapter = db.query(models.Chapter).filter(models.Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    concept = db.query(models.Concept).filter(models.Concept.chapter_id == chapter_id).first()
    if not concept:
        raise HTTPException(status_code=404, detail="Concept not found")

    # AI가 생성한 데이터로 업데이트
    concept.title = data.title
    concept.content = data.content
    concept.is_complete = True

    db.commit()
    db.refresh(concept)

    # Socket.IO로 완료 알림 발송
    await emit_concept_completed(chapter_id, concept.id)

    # 모든 리소스 완료 확인
    await check_and_emit_all_completed(chapter_id, db)

    return schemas.WebhookResponse(
        status="success",
        message="개념 정리가 성공적으로 저장되었습니다",
        chapter_id=chapter_id
    )


@router.post("/{chapter_id}/exercise-finish", response_model=schemas.WebhookResponse)
async def exercise_finish_webhook(
    chapter_id: int,
    data: schemas.ExerciseWebhook,
    db: Session = Depends(get_db)
):
    """
    실습 과제 생성 완료 webhook (n8n → 백엔드)
    """
    chapter = db.query(models.Chapter).filter(models.Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    exercise = db.query(models.Exercise).filter(models.Exercise.chapter_id == chapter_id).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    # AI가 생성한 데이터로 업데이트
    exercise.question = data.question
    exercise.answer = data.answer
    exercise.is_complete = True

    db.commit()
    db.refresh(exercise)

    # Socket.IO로 완료 알림 발송
    await emit_exercise_completed(chapter_id, exercise.id)

    # 모든 리소스 완료 확인
    await check_and_emit_all_completed(chapter_id, db)

    return schemas.WebhookResponse(
        status="success",
        message="실습 과제가 성공적으로 저장되었습니다",
        chapter_id=chapter_id
    )


@router.post("/{chapter_id}/quiz-finish", response_model=schemas.WebhookResponse)
async def quiz_finish_webhook(
    chapter_id: int,
    data: schemas.QuizWebhook,
    db: Session = Depends(get_db)
):
    """
    퀴즈 생성 완료 webhook (n8n → 백엔드)
    """
    chapter = db.query(models.Chapter).filter(models.Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    quiz = db.query(models.Quiz).filter(models.Quiz.chapter_id == chapter_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    # AI가 생성한 데이터로 업데이트
    quiz.question = data.question
    quiz.correct_answer = data.correct_answer
    quiz.type = data.type

    if data.options:
        import json
        quiz.options = json.dumps(data.options)

    db.commit()
    db.refresh(quiz)

    # Socket.IO로 완료 알림 발송
    await emit_quiz_completed(chapter_id, 1)

    # 모든 리소스 완료 확인
    await check_and_emit_all_completed(chapter_id, db)

    return schemas.WebhookResponse(
        status="success",
        message="퀴즈가 성공적으로 저장되었습니다",
        chapter_id=chapter_id
    )


async def check_and_emit_all_completed(chapter_id: int, db: Session):
    """
    모든 리소스(개념, 실습, 퀴즈)가 완료되었는지 확인하고,
    모두 완료되었으면 all_completed 이벤트 발송 + 챕터 상태 업데이트
    """
    # 개념 정리 완료 확인
    concept = db.query(models.Concept).filter(
        models.Concept.chapter_id == chapter_id,
        models.Concept.is_complete == True
    ).first()

    # 실습 과제 완료 확인
    exercise = db.query(models.Exercise).filter(
        models.Exercise.chapter_id == chapter_id,
        models.Exercise.is_complete == True
    ).first()

    # 퀴즈 완료 확인
    quiz = db.query(models.Quiz).filter(
        models.Quiz.chapter_id == chapter_id
    ).first()
    quiz_complete = quiz and quiz.question is not None

    # 모두 완료되었으면 all_completed 이벤트 발송
    if concept and exercise and quiz_complete:
        # 챕터 상태 업데이트
        chapter = db.query(models.Chapter).filter(models.Chapter.id == chapter_id).first()
        if chapter:
            chapter.status = models.StatusEnum.completed
            db.commit()

        await emit_all_completed(chapter_id)
