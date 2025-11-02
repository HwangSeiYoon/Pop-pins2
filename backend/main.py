"""
FastAPI Main Application
Socket.IO와 통합된 메인 애플리케이션
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

# 라우터 import
import member
import course
import chapter
import concept
import exercise
import quiz
import webhook

# Socket.IO import
from socketio_manager import socket_app, sio

# Kafka producer import
from kafka_producer import close_kafka_producer


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    애플리케이션 시작/종료 시 실행되는 라이프사이클 이벤트
    """
    # 시작 시
    print("Starting FastAPI application...")
    yield
    # 종료 시
    print("Shutting down FastAPI application...")
    close_kafka_producer()


# FastAPI 앱 생성
app = FastAPI(
    title="AI Learning Platform API",
    description="N8N + Gemini + Kafka를 사용한 AI 기반 학습 플랫폼",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(member.router)
app.include_router(course.router)
app.include_router(chapter.router)
app.include_router(concept.router)
app.include_router(exercise.router)
app.include_router(quiz.router)
app.include_router(webhook.router)


@app.get("/")
def root():
    """
    헬스 체크 엔드포인트
    """
    return {
        "status": "ok",
        "message": "AI Learning Platform API is running",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    """
    상세 헬스 체크
    """
    return {
        "status": "healthy",
        "services": {
            "api": "running",
            "socket_io": "running",
            "kafka": "connected"
        }
    }


# Socket.IO를 FastAPI에 마운트
app.mount("/socket.io", socket_app)


if __name__ == "__main__":
    # 개발 서버 실행
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 개발 모드에서 자동 리로드
        log_level="info"
    )
