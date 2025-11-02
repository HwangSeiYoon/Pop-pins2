"""
Webhook Router
N8N이 Gemini 결과를 받아서 백엔드로 전송하는 Webhook 수신 엔드포인트
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
import schemas
import models
from database import get_db
from socketio_manager import emit_concept_finish, emit_exercise_finish, emit_quiz_finish, emit_quiz_graded, emit_course_generated

router = APIRouter(prefix="/webhook", tags=["webhook"])


@router.post("/course-generate-finish")
async def course_generate_finish_webhook(
    course_data: schemas.WebhookCourseGenerateResponse,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    강의 생성 완료 Webhook
    N8N이 Gemini로부터 챕터 정보를 받아서 이 엔드포인트로 전송

    흐름:
    1. 클라이언트가 강의 생성 요청 → Kafka 이벤트 발행
    2. N8N이 Kafka 이벤트 수신 → Gemini에게 챕터 생성 요청
    3. Gemini 완료 → N8N이 이 Webhook 호출
    4. DB에 챕터 저장 후 Socket.IO로 클라이언트에게 실시간 알림

    Args:
        course_data: Gemini가 생성한 챕터 정보
    """
    try:
        course_id = course_data.course.get("id")
        chapters_data = course_data.course.get("chapters", [])

        # 코스 조회
        course = db.query(models.Course).filter(models.Course.id == course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail=f"Course {course_id} not found")

        # 챕터 생성
        created_chapters = []
        for chapter_info in chapters_data:
            # 챕터 생성
            new_chapter = models.Chapter(
                course_id=course_id,
                title=chapter_info.get("chapterTitle"),
                description=chapter_info.get("chapterDescription"),
                order_num=chapter_info.get("chapterId"),
                owner_id=course.owner_id
            )
            db.add(new_chapter)
            db.flush()  # ID 생성

            # Concept, Exercise, Quiz 빈 레코드 생성 (is_available=False)
            concept = models.Concept(
                chapter_id=new_chapter.id,
                is_available=False,
                is_complete=False
            )
            exercise = models.Exercise(
                chapter_id=new_chapter.id,
                is_available=False,
                is_complete=False
            )
            db.add(concept)
            db.add(exercise)

            # 퀴즈 3개 생성
            for i in range(1, 4):
                quiz = models.Quiz(
                    chapter_id=new_chapter.id,
                    is_available=False,
                    is_complete=False
                )
                db.add(quiz)

            created_chapters.append({
                "chapter_id": new_chapter.id,
                "chapter_title": new_chapter.title,
                "chapter_description": new_chapter.description
            })

        db.commit()

        # Socket.IO로 클라이언트에게 실시간 알림
        await emit_course_generated(
            course_id=course_id,
            data={
                "course_id": course_id,
                "chapters": created_chapters,
                "status": "completed",
                "message": f"{len(created_chapters)}개의 챕터가 생성되었습니다."
            }
        )

        return {
            "status": "success",
            "message": f"{len(created_chapters)} chapters created successfully",
            "course_id": course_id,
            "chapters": created_chapters
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/concept-finish")
async def concept_finish_webhook(
    concept_data: schemas.WebhookConceptResponse,
    chapter_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    개념 정리 생성 완료 Webhook
    N8N이 Gemini로부터 개념정리를 받아서 이 엔드포인트로 전송

    Args:
        concept_data: Gemini가 생성한 개념정리 데이터
        chapter_id: 챕터 ID (query parameter)
    """
    try:
        # 챕터의 개념정리 찾기
        concept = db.query(models.Concept).filter(
            models.Concept.chapter_id == chapter_id
        ).first()

        if not concept:
            raise HTTPException(status_code=404, detail=f"Concept for chapter {chapter_id} not found")

        # Gemini가 생성한 데이터로 업데이트
        concept.title = concept_data.title
        concept.content = concept_data.contents
        db.commit()

        # Socket.IO로 클라이언트에게 실시간 알림
        await emit_concept_finish(
            chapter_id=chapter_id,
            data={
                "chapter_id": chapter_id,
                "concept_id": concept.id,
                "title": concept_data.title,
                "status": "completed"
            }
        )

        return {"status": "success", "message": "Concept updated successfully"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/exercise-finish")
async def exercise_finish_webhook(
    exercise_data: schemas.WebhookExerciseResponse,
    chapter_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    실습 과제 생성 완료 Webhook
    N8N이 Gemini로부터 실습과제를 받아서 이 엔드포인트로 전송

    Args:
        exercise_data: Gemini가 생성한 실습과제 데이터
        chapter_id: 챕터 ID (query parameter)
    """
    try:
        # 챕터의 실습과제 찾기
        exercise = db.query(models.Exercise).filter(
            models.Exercise.chapter_id == chapter_id
        ).first()

        if not exercise:
            raise HTTPException(status_code=404, detail=f"Exercise for chapter {chapter_id} not found")

        # Gemini가 생성한 데이터로 업데이트
        exercise.question = exercise_data.title
        exercise.answer = exercise_data.contents
        db.commit()

        # Socket.IO로 클라이언트에게 실시간 알림
        await emit_exercise_finish(
            chapter_id=chapter_id,
            data={
                "chapter_id": chapter_id,
                "exercise_id": exercise.id,
                "title": exercise_data.title,
                "status": "completed"
            }
        )

        return {"status": "success", "message": "Exercise updated successfully"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/quiz-finish")
async def quiz_finish_webhook(
    quiz_data: schemas.WebhookQuizResponse,
    chapter_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    형성평가 생성 완료 Webhook
    N8N이 Gemini로부터 퀴즈를 받아서 이 엔드포인트로 전송

    Args:
        quiz_data: Gemini가 생성한 퀴즈 데이터
        chapter_id: 챕터 ID (query parameter)
    """
    try:
        # 챕터의 퀴즈들 찾기
        quizzes = db.query(models.Quiz).filter(
            models.Quiz.chapter_id == chapter_id
        ).limit(3).all()

        if not quizzes:
            raise HTTPException(status_code=404, detail=f"Quizzes for chapter {chapter_id} not found")

        # Gemini가 생성한 데이터로 업데이트 (최대 3개)
        quiz_ids = []
        for i, quiz_item in enumerate(quiz_data.quizes[:3]):
            if i < len(quizzes):
                quizzes[i].question = quiz_item.quiz
                quiz_ids.append(quizzes[i].id)
                # correct_answer는 나중에 정답 제출 시 Gemini가 채점하면서 설정

        db.commit()

        # Socket.IO로 클라이언트에게 실시간 알림
        await emit_quiz_finish(
            chapter_id=chapter_id,
            data={
                "chapter_id": chapter_id,
                "quiz_ids": quiz_ids,
                "quiz_count": len(quiz_data.quizes),
                "status": "completed"
            }
        )

        return {"status": "success", "message": f"{len(quiz_data.quizes)} quizzes updated successfully"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/answer-finish")
async def answer_finish_webhook(
    grading_result: schemas.WebhookQuizGradingResult,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    퀴즈 채점 완료 Webhook
    N8N이 Gemini로부터 채점 결과를 받아서 이 엔드포인트로 전송

    흐름:
    1. 클라이언트가 퀴즈 답안 제출 → Kafka 이벤트 발행
    2. N8N이 Kafka 이벤트 수신 → Gemini에게 채점 요청
    3. Gemini 채점 완료 → N8N이 이 Webhook 호출
    4. DB 업데이트 후 Socket.IO로 클라이언트에게 실시간 알림

    Args:
        grading_result: Gemini 채점 결과
    """
    try:
        # 퀴즈 조회
        quiz = db.query(models.Quiz).filter(models.Quiz.id == grading_result.quiz_id).first()
        if not quiz:
            raise HTTPException(status_code=404, detail=f"Quiz {grading_result.quiz_id} not found")

        # 정답 업데이트 (Gemini가 판단한 정답)
        quiz.correct_answer = grading_result.correct_answer
        if grading_result.explanation:
            quiz.explanation = grading_result.explanation
        db.commit()

        # TODO: QuizSubmission 테이블에 제출 기록 저장
        # quiz_submission = models.QuizSubmission(
        #     quiz_id=grading_result.quiz_id,
        #     member_id=grading_result.member_id,
        #     user_answer=user_answer,
        #     is_correct=grading_result.is_correct,
        #     score=grading_result.score,
        #     graded_at=datetime.utcnow()
        # )
        # db.add(quiz_submission)
        # db.commit()

        # Socket.IO로 클라이언트에게 실시간 채점 결과 알림
        await emit_quiz_graded(
            chapter_id=grading_result.chapter_id,
            data={
                "chapter_id": grading_result.chapter_id,
                "quiz_id": grading_result.quiz_id,
                "slot_number": grading_result.slot_number,
                "member_id": grading_result.member_id,
                "is_correct": grading_result.is_correct,
                "score": grading_result.score,
                "correct_answer": grading_result.correct_answer,
                "explanation": grading_result.explanation or "설명이 없습니다.",
                "status": "graded"
            }
        )

        return {
            "status": "success",
            "message": "Quiz grading result processed successfully",
            "is_correct": grading_result.is_correct,
            "score": grading_result.score
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
