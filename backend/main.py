"""
FastAPI Main Application with Socket.IO (단일 질문-학습 모드)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio
import uvicorn

# Router imports (단일 모드: member, chapter, quiz만 사용)
from member import router as member_router
from chapter import router as chapter_router
from quiz import router as quiz_router

# Socket.IO
from socketio_manager import sio

# Database initialization
from database import engine, redis_client
import models

# Create database tables
models.Base.metadata.create_all(bind=engine)

print("✅ Database tables created successfully")

# FastAPI app
app = FastAPI(
    title="DOCGODAI Backend API (단일 모드)",
    description="질문 1개 → 학습 페이지 1개 (Concept + Exercise + Quiz 1개)",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers (단일 모드: 3개만 사용)
app.include_router(member_router)   # 회원가입, 로그인
app.include_router(chapter_router)  # 질문 등록, 학습 페이지 조회
app.include_router(quiz_router)     # 퀴즈 제출

# Socket.IO ASGI app 통합
socket_app = socketio.ASGIApp(sio, app)


@app.get("/api/v1/")
def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "DOCGODAI Backend API (단일 모드) is running",
        "mode": "single_question_learning",
        "version": "2.0.0"
    }


@app.get("/health")
def health_check():
    """Detailed health check"""
    # Redis 연결 확인
    redis_status = "connected"
    try:
        redis_client.ping()
    except Exception as e:
        redis_status = f"error: {str(e)}"

    return {
        "status": "ok",
        "database": "connected",
        "redis": redis_status,
        "socketio": "enabled",
        "api_version": "2.0.0"
    }

@app.post("/api/v1/user/me")
def 

if __name__ == "__main__":
    # Socket.IO와 함께 실행
    uvicorn.run(
        "main:socket_app",  # Socket.IO ASGI app 사용
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
