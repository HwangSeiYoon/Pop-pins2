"""
Kafka Producer
이벤트를 Kafka에 발행하여 N8N이 처리하도록 함
"""

import json
import os
from typing import Optional
from kafka import KafkaProducer
from kafka.errors import KafkaError

# Kafka 설정
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC_COURSE_GENERATE = "course-generate"
KAFKA_TOPIC_CHAPTER_CREATED = "chapter-created"
KAFKA_TOPIC_CONCEPT_CREATED = "concept-created"
KAFKA_TOPIC_EXERCISE_CREATED = "exercise-created"
KAFKA_TOPIC_QUIZ_CREATED = "quiz-created"
KAFKA_TOPIC_QUIZ_ANSWER_SUBMIT = "quiz-answer-submit"

# Kafka Producer 인스턴스 (싱글톤)
_producer: Optional[KafkaProducer] = None


def get_kafka_producer() -> KafkaProducer:
    """
    Kafka Producer 싱글톤 인스턴스 가져오기

    Returns:
        KafkaProducer 인스턴스
    """
    global _producer
    if _producer is None:
        _producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None,
            acks='all',  # 모든 replica가 메시지를 받을 때까지 대기
            retries=3,  # 재시도 횟수
            max_in_flight_requests_per_connection=1  # 순서 보장
        )
    return _producer


def send_course_generate_event(
    course_id: int,
    course_title: str,
    course_description: str,
    prompt: str,
    maxchapters: int,
    link: list,
    difficulty: str,
    owner_id: int
) -> bool:
    """
    강의 생성 이벤트 발행
    N8N이 이 이벤트를 받아서 Gemini에게 챕터 생성 요청

    Args:
        course_id: 코스 ID
        course_title: 코스 제목
        course_description: 코스 설명
        prompt: 사용자 프롬프트
        maxchapters: 최대 챕터 수
        link: 참고 링크 리스트
        difficulty: 난이도
        owner_id: 소유자 ID

    Returns:
        성공 여부
    """
    try:
        producer = get_kafka_producer()

        event_data = {
            "course_id": course_id,
            "courseTitle": course_title,
            "courseDescription": course_description,
            "prompt": prompt,
            "maxchapters": maxchapters,
            "link": link,
            "difficulty": difficulty,
            "owner_id": owner_id,
            "event_type": "course_generate"
        }

        future = producer.send(
            KAFKA_TOPIC_COURSE_GENERATE,
            key=f"course_{course_id}",
            value=event_data
        )

        # 메시지 전송 완료 대기 (타임아웃 5초)
        record_metadata = future.get(timeout=5)
        print(f"Sent course_generate event: {record_metadata.topic}:{record_metadata.partition}:{record_metadata.offset}")
        return True

    except KafkaError as e:
        print(f"Failed to send course_generate event: {e}")
        return False


def send_chapter_created_event(
    chapter_id: int,
    course_id: int,
    owner_id: int,
    course_title: str,
    course_description: str,
    chapter_title: str,
    chapter_description: str,
    course_prompt: str = ""
) -> bool:
    """
    챕터 생성 이벤트 발행
    N8N이 이 이벤트를 받아서 Gemini에게 concept, exercise, quiz 생성 요청

    Args:
        chapter_id: 챕터 ID
        course_id: 코스 ID
        owner_id: 소유자 ID
        course_title: 코스 제목
        course_description: 코스 설명
        chapter_title: 챕터 제목
        chapter_description: 챕터 설명
        course_prompt: 코스 프롬프트

    Returns:
        성공 여부
    """
    try:
        producer = get_kafka_producer()

        event_data = {
            "chapter_id": chapter_id,
            "course_id": course_id,
            "owner_id": owner_id,
            "course_title": course_title,
            "course_description": course_description,
            "chapter_title": chapter_title,
            "chapter_description": chapter_description,
            "course_prompt": course_prompt,
            "event_type": "chapter_created"
        }

        future = producer.send(
            KAFKA_TOPIC_CHAPTER_CREATED,
            key=f"chapter_{chapter_id}",
            value=event_data
        )

        # 메시지 전송 완료 대기 (타임아웃 5초)
        record_metadata = future.get(timeout=5)
        print(f"Sent chapter_created event: {record_metadata.topic}:{record_metadata.partition}:{record_metadata.offset}")
        return True

    except KafkaError as e:
        print(f"Failed to send chapter_created event: {e}")
        return False


def send_concept_created_event(
    concept_id: int,
    chapter_id: int,
    title: str,
    content: str
) -> bool:
    """
    개념정리 생성 이벤트 발행

    Args:
        concept_id: 개념정리 ID
        chapter_id: 챕터 ID
        title: 제목
        content: 내용

    Returns:
        성공 여부
    """
    try:
        producer = get_kafka_producer()

        event_data = {
            "concept_id": concept_id,
            "chapter_id": chapter_id,
            "title": title,
            "content": content,
            "event_type": "concept_created"
        }

        future = producer.send(
            KAFKA_TOPIC_CONCEPT_CREATED,
            key=f"concept_{concept_id}",
            value=event_data
        )

        record_metadata = future.get(timeout=5)
        print(f"Sent concept_created event: {record_metadata.topic}:{record_metadata.partition}:{record_metadata.offset}")
        return True

    except KafkaError as e:
        print(f"Failed to send concept_created event: {e}")
        return False


def send_exercise_created_event(
    exercise_id: int,
    chapter_id: int,
    question: str,
    answer: str
) -> bool:
    """
    실습과제 생성 이벤트 발행

    Args:
        exercise_id: 실습과제 ID
        chapter_id: 챕터 ID
        question: 문제
        answer: 답변

    Returns:
        성공 여부
    """
    try:
        producer = get_kafka_producer()

        event_data = {
            "exercise_id": exercise_id,
            "chapter_id": chapter_id,
            "question": question,
            "answer": answer,
            "event_type": "exercise_created"
        }

        future = producer.send(
            KAFKA_TOPIC_EXERCISE_CREATED,
            key=f"exercise_{exercise_id}",
            value=event_data
        )

        record_metadata = future.get(timeout=5)
        print(f"Sent exercise_created event: {record_metadata.topic}:{record_metadata.partition}:{record_metadata.offset}")
        return True

    except KafkaError as e:
        print(f"Failed to send exercise_created event: {e}")
        return False


def send_quiz_created_event(
    quiz_ids: list,
    chapter_id: int,
    questions: list
) -> bool:
    """
    퀴즈 생성 이벤트 발행

    Args:
        quiz_ids: 퀴즈 ID 리스트
        chapter_id: 챕터 ID
        questions: 문제 리스트

    Returns:
        성공 여부
    """
    try:
        producer = get_kafka_producer()

        event_data = {
            "quiz_ids": quiz_ids,
            "chapter_id": chapter_id,
            "questions": questions,
            "event_type": "quiz_created"
        }

        future = producer.send(
            KAFKA_TOPIC_QUIZ_CREATED,
            key=f"quiz_chapter_{chapter_id}",
            value=event_data
        )

        record_metadata = future.get(timeout=5)
        print(f"Sent quiz_created event: {record_metadata.topic}:{record_metadata.partition}:{record_metadata.offset}")
        return True

    except KafkaError as e:
        print(f"Failed to send quiz_created event: {e}")
        return False


def send_quiz_answer_submit_event(
    chapter_id: int,
    quiz_id: int,
    slot_number: int,
    member_id: int,
    course_title: str,
    course_description: str,
    quiz_question: str,
    user_answer: str
) -> bool:
    """
    퀴즈 정답 제출 이벤트 발행
    N8N이 이를 받아서 Gemini로 채점 요청

    Args:
        chapter_id: 챕터 ID
        quiz_id: 퀴즈 ID
        slot_number: 슬롯 번호
        member_id: 회원 ID
        course_title: 코스 제목
        course_description: 코스 설명
        quiz_question: 퀴즈 문제
        user_answer: 사용자 답변

    Returns:
        성공 여부
    """
    try:
        producer = get_kafka_producer()

        event_data = {
            "chapter_id": chapter_id,
            "quiz_id": quiz_id,
            "slot_number": slot_number,
            "member_id": member_id,
            "course_title": course_title,
            "course_description": course_description,
            "quiz_question": quiz_question,
            "user_answer": user_answer,
            "event_type": "quiz_answer_submit"
        }

        future = producer.send(
            KAFKA_TOPIC_QUIZ_ANSWER_SUBMIT,
            key=f"quiz_answer_{quiz_id}_{member_id}",
            value=event_data
        )

        record_metadata = future.get(timeout=5)
        print(f"Sent quiz_answer_submit event: {record_metadata.topic}:{record_metadata.partition}:{record_metadata.offset}")
        return True

    except KafkaError as e:
        print(f"Failed to send quiz_answer_submit event: {e}")
        return False


def close_kafka_producer():
    """
    Kafka Producer 종료
    애플리케이션 종료 시 호출
    """
    global _producer
    if _producer is not None:
        _producer.flush()
        _producer.close()
        _producer = None
        print("Kafka producer closed")
