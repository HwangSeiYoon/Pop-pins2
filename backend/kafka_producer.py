"""
Kafka Producer
메인 애플리케이션에서 사용하는 Kafka Producer 래퍼
"""

from utils.kafka_manager import kafka_manager

def close_kafka_producer():
    """Kafka Producer 연결 종료"""
    kafka_manager.close_connections()

# 편의 함수들을 re-export
from utils.kafka_manager import (
    send_to_n8n,
    notify_content_update,
    create_concept_request,
    create_exercise_request,
    create_quiz_request
)