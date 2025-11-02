"""
Kafka 유틸리티 클래스
n8n 워크플로우 요청을 Kafka를 통해 비동기 처리
"""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
try:
    from confluent_kafka import Producer, Consumer, KafkaError
    KAFKA_AVAILABLE = True
except ImportError:
    # Fallback when Kafka is not available
    KAFKA_AVAILABLE = False
    Producer = None
    Consumer = None
    KafkaError = Exception
import uuid

logger = logging.getLogger(__name__)

class KafkaManager:
    """
    Kafka 메시지 관리 클래스
    n8n 워크플로우 요청을 Kafka를 통해 비동기 처리
    
    사용 예시:
        # 챕터 생성 시 컨셉 요청
        message_id = create_concept_request(
            user_id=current_user["user_id"],
            chapter_id=new_chapter.id,
            question="파이썬 기초 문법"
        )
    
    메시지 형식:
        {
            "message_id": "uuid",
            "timestamp": "2024-01-01T00:00:00",
            "workflow_type": "concept",
            "user_id": 123,
            "chapter_id": 456,
            "priority": "high",
            "data": {"question": "파이썬 기초"},
            "status": "pending"
        }
    
    토픽 구조:
        - n8n-requests: n8n으로 보낼 작업 요청
        - n8n-responses: n8n에서 받을 작업 결과  
        - concept-generation: 컨셉 생성 요청
        - exercise-generation: 연습문제 생성 요청
        - quiz-generation: 퀴즈 생성 요청
        - content-updates: 콘텐츠 업데이트 알림
    """
    
    # Kafka 토픽 정의
    TOPICS = {
        "N8N_REQUESTS": "n8n-requests",
        "N8N_RESPONSES": "n8n-responses",
        "CONCEPT_GENERATION": "concept-generation",
        "EXERCISE_GENERATION": "exercise-generation", 
        "QUIZ_GENERATION": "quiz-generation",
        "CONTENT_UPDATES": "content-updates"
    }
    
    def __init__(self):
        self.producer = None
        self.consumer = None
        self.kafka_config = {
            'bootstrap.servers': 'localhost:9092',
            'client.id': 'docgodai-backend'
        }
    
    def get_producer(self):
        """Kafka Producer 인스턴스 가져오기"""
        if not KAFKA_AVAILABLE:
            logger.warning("Kafka가 설치되지 않았습니다. 메시지를 로깅으로 대체합니다.")
            return None
            
        if self.producer is None:
            try:
                self.producer = Producer(self.kafka_config)
                logger.info("Kafka Producer 연결 성공")
            except Exception as e:
                logger.error(f"Kafka Producer 연결 실패: {e}")
                return None
        return self.producer
    
    def get_consumer(self, topics: List[str], group_id: str = "docgodai-backend"):
        """Kafka Consumer 인스턴스 가져오기"""
        if not KAFKA_AVAILABLE:
            logger.warning("Kafka가 설치되지 않았습니다.")
            return None
            
        try:
            consumer_config = {
                'bootstrap.servers': 'localhost:9092',
                'group.id': group_id,
                'auto.offset.reset': 'latest'
            }
            consumer = Consumer(consumer_config)
            consumer.subscribe(topics)
            logger.info(f"Kafka Consumer 생성 - Topics: {topics}, Group: {group_id}")
            return consumer
        except Exception as e:
            logger.error(f"Kafka Consumer 생성 실패: {e}")
            return None
    
    def send_n8n_request(self, 
                        workflow_type: str, 
                        user_id: int,
                        chapter_id: int,
                        data: Dict[str, Any],
                        priority: str = "normal") -> str:
        """
        n8n 워크플로우 요청 메시지 발송
        
        Args:
            workflow_type: 워크플로우 타입 (concept, exercise, quiz)
            user_id: 사용자 ID
            chapter_id: 챕터 ID
            data: 워크플로우에 전달할 데이터
            priority: 우선순위 (high, normal, low)
            
        Returns:
            str: 메시지 ID
        """
        message_id = str(uuid.uuid4())
        
        message = {
            "message_id": message_id,
            "timestamp": datetime.utcnow().isoformat(),
            "workflow_type": workflow_type,
            "user_id": user_id,
            "chapter_id": chapter_id,
            "priority": priority,
            "data": data,
            "status": "pending"
        }
        
        try:
            producer = self.get_producer()
            if producer is None:
                # Kafka 사용 불가 시 로깅으로 대체
                logger.info(f"[Kafka 미사용] 메시지 발송 - Type: {workflow_type}, "
                           f"User: {user_id}, Chapter: {chapter_id}, Message: {message}")
                return message_id
            
            # confluent-kafka 방식으로 메시지 발송
            producer.produce(
                topic=self.TOPICS["N8N_REQUESTS"],
                key=message_id,
                value=json.dumps(message, ensure_ascii=False, default=str)
            )
            producer.flush()
            
            logger.info(f"메시지 발송 성공 - Topic: {self.TOPICS['N8N_REQUESTS']}, "
                       f"Type: {workflow_type}, Chapter: {chapter_id}")
            
            return message_id
            
        except Exception as e:
            logger.error(f"Kafka 메시지 발송 실패: {e}")
            # Kafka 실패 시에도 서버가 중단되지 않도록 로깅만 하고 계속 진행
            logger.info(f"[Kafka 실패 대체] 메시지 - Type: {workflow_type}, "
                       f"User: {user_id}, Chapter: {chapter_id}")
            return message_id
    
    def send_concept_generation_request(self, user_id: int, chapter_id: int, question: str) -> str:
        """컨셉 생성 요청"""
        data = {
            "question": question,
            "type": "concept_generation"
        }
        return self.send_n8n_request("concept", user_id, chapter_id, data, "high")
    
    def send_exercise_generation_request(self, user_id: int, chapter_id: int, concept_content: str) -> str:
        """연습문제 생성 요청"""
        data = {
            "concept_content": concept_content,
            "type": "exercise_generation"
        }
        return self.send_n8n_request("exercise", user_id, chapter_id, data, "normal")
    
    def send_quiz_generation_request(self, user_id: int, chapter_id: int, 
                                   concept_content: str, exercise_content: str) -> str:
        """퀴즈 생성 요청"""
        data = {
            "concept_content": concept_content,
            "exercise_content": exercise_content,
            "type": "quiz_generation"
        }
        return self.send_n8n_request("quiz", user_id, chapter_id, data, "normal")
    
    def send_content_update_notification(self, content_type: str, content_id: int, 
                                       user_id: int, status: str, content: Optional[Dict] = None) -> str:
        """콘텐츠 업데이트 알림 발송"""
        message_id = str(uuid.uuid4())
        
        message = {
            "message_id": message_id,
            "timestamp": datetime.utcnow().isoformat(),
            "content_type": content_type,  # concept, exercise, quiz
            "content_id": content_id,
            "user_id": user_id,
            "status": status,  # completed, failed, in_progress
            "content": content or {}
        }
        
        try:
            producer = self.get_producer()
            if producer is None:
                logger.info(f"[Kafka 미사용] 콘텐츠 업데이트 알림 - Type: {content_type}, ID: {content_id}")
                return message_id
                
            producer.produce(
                topic=self.TOPICS["CONTENT_UPDATES"],
                key=f"{content_type}_{content_id}",
                value=json.dumps(message, ensure_ascii=False, default=str)
            )
            producer.flush()
            return message_id
        except Exception as e:
            logger.error(f"콘텐츠 업데이트 알림 발송 실패: {e}")
            logger.info(f"[Kafka 실패 대체] 콘텐츠 업데이트 - Type: {content_type}, ID: {content_id}")
            return message_id
    
    def close_connections(self):
        """Kafka 연결 종료"""
        if self.producer:
            self.producer.close()
            logger.info("Kafka Producer 연결 종료")
        if self.consumer:
            self.consumer.close()
            logger.info("Kafka Consumer 연결 종료")

# 싱글톤 인스턴스
kafka_manager = KafkaManager()

# 편의 함수들
def send_to_n8n(workflow_type: str, user_id: int, chapter_id: int, data: Dict[str, Any]) -> str:
    """n8n 워크플로우 요청 발송 (편의 함수)"""
    return kafka_manager.send_n8n_request(workflow_type, user_id, chapter_id, data)

def notify_content_update(content_type: str, content_id: int, user_id: int, 
                         status: str, content: Optional[Dict] = None) -> str:
    """콘텐츠 업데이트 알림 (편의 함수)"""
    return kafka_manager.send_content_update_notification(
        content_type, content_id, user_id, status, content
    )

def create_concept_request(user_id: int, chapter_id: int, question: str) -> str:
    """컨셉 생성 요청 (편의 함수)"""
    return kafka_manager.send_concept_generation_request(user_id, chapter_id, question)

def create_exercise_request(user_id: int, chapter_id: int, concept_content: str) -> str:
    """연습문제 생성 요청 (편의 함수)"""
    return kafka_manager.send_exercise_generation_request(user_id, chapter_id, concept_content)

def create_quiz_request(user_id: int, chapter_id: int, concept_content: str, exercise_content: str) -> str:
    """퀴즈 생성 요청 (편의 함수)"""
    return kafka_manager.send_quiz_generation_request(user_id, chapter_id, concept_content, exercise_content)