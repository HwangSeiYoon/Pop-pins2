from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
import schemas
import models
from database import get_db
from kafka_producer import (
    send_chapter_created_event,
    send_concept_created_event,
    send_exercise_created_event
)
from socketio_manager import emit_concept_finish, emit_exercise_finish, emit_quiz_finish

router = APIRouter(prefix="/v1/chapter", tags=["chapter"])


# ============================================
# 기존 코드 (주석 처리됨)
# ============================================

# # 챕터 생성 (구버전)
# @router.post("/old", response_model=schemas.ChapterResponse)
# def create_chapter_old(chapter: schemas.ChapterCreate, db: Session = Depends(get_db)):
#     """새로운 챕터를 생성합니다. (구버전)"""
#     # 강의 존재 확인
#     course = db.query(models.Course).filter(models.Course.id == chapter.course_id).first()
#     if not course:
#         raise HTTPException(status_code=404, detail=f"Course {chapter.course_id} not found")
#
#     new_chapter = models.Chapter(
#         course_id=chapter.course_id,
#         title=chapter.title,
#         order_num=0  # TODO: 순서 자동 계산
#     )
#
#     db.add(new_chapter)
#     db.commit()
#     db.refresh(new_chapter)
#
#     # Kafka 이벤트 발행
#     send_chapter_created_event(
#         chapter_id=new_chapter.id,
#         course_id=new_chapter.course_id,
#         title=new_chapter.title
#     )
#
#     return schemas.ChapterResponse(
#         id=new_chapter.id,
#         course_id=new_chapter.course_id,
#         title=new_chapter.title,
#         content="",
#         created_at=new_chapter.created_at.isoformat()
#     )


# ============================================
# 새로운 API 명세에 따른 엔드포인트
# ============================================

# 챕터 생성 (N8N + Gemini 연동)
@router.post("/", response_model=schemas.ChapterCreateResponse)
def create_chapter(chapter: schemas.ChapterCreateRequest, db: Session = Depends(get_db)):
    """
    새로운 챕터를 생성하고 Kafka 이벤트를 발행합니다.
    N8N이 이벤트를 받아 Gemini에게 개념정리, 실습과제, 형성평가를 요청합니다.
    """
    try:
        # 강의 존재 확인
        course = db.query(models.Course).filter(models.Course.id == chapter.course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail=f"Course {chapter.course_id} not found")

        # 새 챕터 생성
        new_chapter = models.Chapter(
            course_id=chapter.course_id,
            title=chapter.title,
            description=chapter.description or "",
            order_num=0  # TODO: 순서 자동 계산
        )

        db.add(new_chapter)
        db.commit()
        db.refresh(new_chapter)

        # Kafka 이벤트 발행 - N8N이 이를 감지하고 Gemini 호출
        send_chapter_created_event(
            chapter_id=new_chapter.id,
            course_id=new_chapter.course_id,
            title=new_chapter.title
        )

        # 성공 응답
        return schemas.ChapterCreateResponse(
            key="chapter-create",
            chapterId=new_chapter.id,
            state="success"
        )

    except Exception as e:
        # 실패 응답
        db.rollback()
        return schemas.ChapterCreateResponse(
            key="chapter-create",
            chapterId=0,
            state="failure"
        )


# # 챕터 개념정리 생성 (구버전)
# @router.post("/{chapter_id}/concept/old", response_model=schemas.ConceptResponse)
# def create_concept_summary_old(chapter_id: int, concept_text: str, db: Session = Depends(get_db)):
#     """챕터의 개념정리를 생성합니다. (구버전)"""
#     # 챕터 존재 확인
#     chapter = db.query(models.Chapter).filter(models.Chapter.id == chapter_id).first()
#     if not chapter:
#         raise HTTPException(status_code=404, detail=f"Chapter {chapter_id} not found")
#
#     new_concept = models.Concept(
#         chapter_id=chapter_id,
#         concept=concept_text
#     )
#
#     db.add(new_concept)
#     db.commit()
#     db.refresh(new_concept)
#
#     # Kafka 이벤트 발행
#     send_concept_created_event(
#         concept_id=new_concept.id,
#         chapter_id=new_concept.chapter_id,
#         concept=new_concept.concept
#     )
#
#     return schemas.ConceptResponse(
#         id=new_concept.id,
#         chapter_id=new_concept.chapter_id,
#         concept=new_concept.concept
#     )


# # 챕터 형성평가(연습문제) 생성 (구버전)
# @router.post("/{chapter_id}/exercise/old", response_model=schemas.ExerciseResponse)
# def create_exercise_old(chapter_id: int, exercise: schemas.ExerciseCreate, db: Session = Depends(get_db)):
#     """챕터의 형성평가를 생성합니다. (구버전)"""
#     # 챕터 존재 확인
#     chapter = db.query(models.Chapter).filter(models.Chapter.id == chapter_id).first()
#     if not chapter:
#         raise HTTPException(status_code=404, detail=f"Chapter {chapter_id} not found")
#
#     new_exercise = models.Exercise(
#         chapter_id=chapter_id,
#         exercise=exercise.exercise,
#         is_correct=exercise.is_correct
#     )
#
#     db.add(new_exercise)
#     db.commit()
#     db.refresh(new_exercise)
#
#     # Kafka 이벤트 발행
#     send_exercise_created_event(
#         exercise_id=new_exercise.id,
#         chapter_id=new_exercise.chapter_id,
#         exercise=new_exercise.exercise,
#         is_correct=new_exercise.is_correct
#     )
#
#     return schemas.ExerciseResponse(
#         id=new_exercise.id,
#         chapter_id=new_exercise.chapter_id,
#         exercise=new_exercise.exercise,
#         is_correct=new_exercise.is_correct
#     )


# # 챕터 상세 조회 (구버전)
# @router.get("/{chapter_id}/old", response_model=schemas.ChapterResponse)
# def get_chapter_old(chapter_id: int, db: Session = Depends(get_db)):
#     """특정 챕터의 상세 정보를 반환합니다. (구버전)"""
#     chapter = db.query(models.Chapter).filter(models.Chapter.id == chapter_id).first()
#
#     if not chapter:
#         raise HTTPException(status_code=404, detail=f"Chapter {chapter_id} not found")
#
#     return schemas.ChapterResponse(
#         id=chapter.id,
#         course_id=chapter.course_id,
#         title=chapter.title,
#         content="",
#         created_at=chapter.created_at.isoformat()
#     )


# # 챕터의 개념정리 조회 (구버전)
# @router.get("/{chapter_id}/concept/old")
# def get_chapter_concepts_old(chapter_id: int, db: Session = Depends(get_db)):
#     """특정 챕터의 개념정리를 반환합니다. (구버전)"""
#     concepts = db.query(models.Concept).filter(models.Concept.chapter_id == chapter_id).all()
#     return {
#         "chapter_id": chapter_id,
#         "concepts": [{"id": c.id, "chapter_id": c.chapter_id, "concept": c.concept} for c in concepts]
#     }


# 챕터 상세 조회 (새 버전)
@router.get("/{chapter_id}", response_model=schemas.ChapterGetResponse)
def get_chapter(chapter_id: int, db: Session = Depends(get_db)):
    """
    특정 챕터의 상세 정보를 반환합니다.
    개념정리, 실습과제, 형성평가의 생성 여부 및 완료 여부를 포함합니다.
    """
    # 챕터 조회
    chapter = db.query(models.Chapter).filter(models.Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail=f"Chapter {chapter_id} not found")

    # 개념정리 조회
    concepts = db.query(models.Concept).filter(models.Concept.chapter_id == chapter_id).all()
    concept_descriptions = [c.concept for c in concepts] if concepts else []
    concept_is_complete = all(c.is_complete for c in concepts) if concepts else False
    concept_is_available = any(c.is_available for c in concepts) if concepts else False

    # 실습과제 조회
    exercises = db.query(models.Exercise).filter(models.Exercise.chapter_id == chapter_id).all()
    exercise_descriptions = [e.exercise for e in exercises] if exercises else []
    exercise_is_complete = all(e.is_complete for e in exercises) if exercises else False
    exercise_is_available = any(e.is_available for e in exercises) if exercises else False

    # 형성평가 조회
    quizzes = db.query(models.Quiz).filter(models.Quiz.chapter_id == chapter_id).all()
    quiz_descriptions = [q.question for q in quizzes] if quizzes else []
    quiz_is_complete = all(q.is_complete for q in quizzes) if quizzes else False
    quiz_is_available = any(q.is_available for q in quizzes) if quizzes else False

    return schemas.ChapterGetResponse(
        chapter=schemas.ChapterDetail(
            chapterDescription=chapter.description or "",
            concept=schemas.ConceptDetail(
                conceptDescription=concept_descriptions,
                isComplete=concept_is_complete
            ),
            exercise=schemas.ExerciseDetail(
                isAvailable=exercise_is_available,
                exerciseDescription=exercise_descriptions,
                isComplete=exercise_is_complete
            ),
            quiz=schemas.QuizDetail(
                quizDescription=quiz_descriptions,
                isAvailable=quiz_is_available,
                isComplete=quiz_is_complete
            )
        )
    )


# ============================================
# Webhook 엔드포인트 (N8N이 호출)
# ============================================

# N8N Gemini 개념정리 완료 Webhook
@router.post("/{chapter_id}/concept-finish", response_model=schemas.WebhookConceptFinish)
async def concept_finish_webhook(
    chapter_id: int,
    webhook_data: schemas.WebhookConceptFinish,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    N8N이 Gemini로부터 개념정리 생성 완료 후 호출하는 Webhook입니다.
    """
    try:
        # 챕터 존재 확인
        chapter = db.query(models.Chapter).filter(models.Chapter.id == chapter_id).first()
        if not chapter:
            raise HTTPException(status_code=404, detail=f"Chapter {chapter_id} not found")

        # Gemini가 생성한 개념정리 데이터 저장
        if webhook_data.state == "success" and webhook_data.conceptData:
            for concept_text in webhook_data.conceptData:
                new_concept = models.Concept(
                    chapter_id=chapter_id,
                    concept=concept_text,
                    is_available=True,  # 생성 완료
                    is_complete=False   # 아직 학습 안 함
                )
                db.add(new_concept)

            db.commit()

        # Socket.IO로 클라이언트에 실시간 알림
        await emit_concept_finish(
            chapter_id=chapter_id,
            state=webhook_data.state,
            concept_data=webhook_data.conceptData
        )

        return webhook_data

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# N8N Gemini 실습과제 완료 Webhook
@router.post("/{chapter_id}/exercise-finish", response_model=schemas.WebhookExerciseFinish)
async def exercise_finish_webhook(
    chapter_id: int,
    webhook_data: schemas.WebhookExerciseFinish,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    N8N이 Gemini로부터 실습과제 생성 완료 후 호출하는 Webhook입니다.
    """
    try:
        # 챕터 존재 확인
        chapter = db.query(models.Chapter).filter(models.Chapter.id == chapter_id).first()
        if not chapter:
            raise HTTPException(status_code=404, detail=f"Chapter {chapter_id} not found")

        # Gemini가 생성한 실습과제 데이터 저장
        if webhook_data.state == "success" and webhook_data.exerciseData:
            for exercise_text in webhook_data.exerciseData:
                new_exercise = models.Exercise(
                    chapter_id=chapter_id,
                    exercise=exercise_text,
                    is_correct=False,   # 기본값
                    is_available=True,  # 생성 완료
                    is_complete=False   # 아직 완료 안 함
                )
                db.add(new_exercise)

            db.commit()

        # Socket.IO로 클라이언트에 실시간 알림
        await emit_exercise_finish(
            chapter_id=chapter_id,
            state=webhook_data.state,
            exercise_data=webhook_data.exerciseData
        )

        return webhook_data

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# N8N Gemini 형성평가 완료 Webhook
@router.post("/{chapter_id}/quiz-finish", response_model=schemas.WebhookQuizFinish)
async def quiz_finish_webhook(
    chapter_id: int,
    webhook_data: schemas.WebhookQuizFinish,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    N8N이 Gemini로부터 형성평가 생성 완료 후 호출하는 Webhook입니다.
    """
    try:
        # 챕터 존재 확인
        chapter = db.query(models.Chapter).filter(models.Chapter.id == chapter_id).first()
        if not chapter:
            raise HTTPException(status_code=404, detail=f"Chapter {chapter_id} not found")

        # Gemini가 생성한 퀴즈 데이터 저장
        if webhook_data.state == "success" and webhook_data.quizData:
            for quiz_text in webhook_data.quizData:
                new_quiz = models.Quiz(
                    chapter_id=chapter_id,
                    question=quiz_text,
                    question_type="서술형",  # 기본값 (Gemini가 타입도 보내면 수정 가능)
                    answer="",  # 기본값
                    is_available=True,  # 생성 완료
                    is_complete=False   # 아직 완료 안 함
                )
                db.add(new_quiz)

            db.commit()

        # Socket.IO로 클라이언트에 실시간 알림
        await emit_quiz_finish(
            chapter_id=chapter_id,
            state=webhook_data.state,
            quiz_data=webhook_data.quizData
        )

        return webhook_data

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

