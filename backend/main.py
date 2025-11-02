"""
FastAPI Main Application
Socket.IO와 통합된 메인 애플리케이션
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

# 라우터 import (api/v1 구조 사용)
from api.v1.members import router as members_router
from api.v1.courses import router as courses_router
from api.v1.chapters import router as chapters_router
from api.v1.concepts import router as concepts_router
from api.v1.exercises import router as exercises_router
from api.v1.quizzes import router as quizzes_router
# from api.v1.webhooks import router as webhooks_router  # TODO: webhook router 구현 필요

# Socket.IO import
from core.socketio_manager import socket_app, sio

# Kafka producer import
from kafka_producer import close_kafka_producer


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    애플리케이션 시작/종료 시 실행되는 라이프사이클 이벤트
    """
    # 시작 시
    print("Starting FastAPI application...")
    
    # 데이터베이스 초기화
    try:
        from db.database import init_db
        init_db()
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Database initialization failed: {e}")
    
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
app.include_router(members_router.router)
app.include_router(courses_router.router)
app.include_router(chapters_router.router)
app.include_router(concepts_router.router)
app.include_router(exercises_router.router)
app.include_router(quizzes_router.router)
# app.include_router(webhooks_router.router)  # TODO: webhook router 구현 필요

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
