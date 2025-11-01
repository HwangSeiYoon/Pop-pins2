from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import schemas
import models
from database import get_db
from kafka_producer import send_course_created_event
from auth import get_current_user
import json

router = APIRouter(prefix="/v1/course", tags=["course"])

# 강의 리스트 조회
@router.get("/", response_model=schemas.CourseListResponse)
def get_course_list(db: Session = Depends(get_db)):
    """모든 강의 리스트를 반환합니다."""
    courses = db.query(models.Course).all()

    course_items = [
        schemas.CourseItem(
            courseId=course.id,
            courseTitle=course.courseTitle,
            courseDescription=course.courseDescription or "",
            total=len(course.chapters) if course.chapters else 0,
            complete=0  # TODO: 완료된 챕터 수 계산 로직 추가
        )
        for course in courses
    ]
    return schemas.CourseListResponse(courses=course_items)


# 강의 생성
@router.post("/", response_model=schemas.CourseCreateResponse)
def create_course(
    course: schemas.CourseCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """새로운 강의를 생성합니다."""
    # link 배열을 JSON 문자열로 변환
    link_json = json.dumps(course.link)

    new_course = models.Course(
        member_id=current_user["user_id"],
        courseTitle=course.courseTitle,
        courseDescription=course.courseDescription,
        prompt=course.prompt,
        maxchapters=course.maxchapters,
        link=link_json,
        difficulty=course.difficulty
    )

    db.add(new_course)
    db.commit()
    db.refresh(new_course)

    # Kafka 이벤트 발행
    send_course_created_event(
        course_id=new_course.id,
        name=new_course.courseTitle,
        description=new_course.courseDescription or "",
        member_id=current_user["user_id"]
    )

    # 챕터 리스트 생성 (현재는 빈 배열, 나중에 AI로 생성)
    chapters = []

    return schemas.CourseCreateResponse(
        course={
            "id": new_course.id,
            "chapters": chapters
        }
    )

# 강의 상세 조회
@router.get("/{course_id}")
def get_course(course_id: int, db: Session = Depends(get_db)):
    """특정 강의의 상세 정보를 반환합니다."""
    course = db.query(models.Course).filter(models.Course.id == course_id).first()

    if not course:
        raise HTTPException(status_code=404, detail=f"Course {course_id} not found")

    # link를 JSON 파싱 (문자열로 저장되어 있으면)
    link_list = []
    if course.link:
        try:
            link_list = json.loads(course.link)
        except:
            link_list = []

    # 챕터 정보 가져오기
    chapter_items = []
    if course.chapters:
        for chapter in course.chapters:
            chapter_items.append({
                "chapterId": chapter.id,
                "chapterTitle": chapter.title,
                "chapterDescription": getattr(chapter, 'description', ''),
                "isGenerated": "completed",  # TODO: 실제 생성 상태 로직 추가
                "isCompleted": False  # TODO: 실제 진행 여부 로직 추가
            })

    return {
        "courseTitle": course.courseTitle,
        "courseDescription": course.courseDescription or "",
        "prompt": course.prompt or "",
        "maxchapters": course.maxchapters or 0,
        "link": link_list,
        "difficulty": course.difficulty or 0,
        "chapters": chapter_items
    }