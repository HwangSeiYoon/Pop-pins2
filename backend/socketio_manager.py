"""
Socket.IO Manager
실시간 클라이언트 알림을 위한 Socket.IO 관리
"""

import socketio
from typing import Optional, Dict, Any

# Socket.IO 서버 인스턴스 (ASGI 모드)
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',  # CORS 설정 (프로덕션에서는 특정 도메인으로 제한)
    logger=True,
    engineio_logger=True
)

# Socket.IO ASGI 앱
socket_app = socketio.ASGIApp(
    sio,
    socketio_path='/socket.io'
)


# ============================================
# Socket.IO 이벤트 핸들러
# ============================================

@sio.event
async def connect(sid, environ):
    """
    클라이언트 연결 시
    """
    print(f"Client connected: {sid}")


@sio.event
async def disconnect(sid):
    """
    클라이언트 연결 해제 시
    """
    print(f"Client disconnected: {sid}")


@sio.event
async def join_chapter(sid, data):
    """
    특정 챕터 룸에 조인
    클라이언트가 특정 챕터의 업데이트를 받기 위해 호출

    Args:
        data: {"chapter_id": int}
    """
    chapter_id = data.get('chapter_id')
    if chapter_id:
        room = f"chapter_{chapter_id}"
        await sio.enter_room(sid, room)
        print(f"Client {sid} joined room: {room}")
        await sio.emit('joined', {'room': room}, room=sid)


@sio.event
async def leave_chapter(sid, data):
    """
    특정 챕터 룸에서 나가기

    Args:
        data: {"chapter_id": int}
    """
    chapter_id = data.get('chapter_id')
    if chapter_id:
        room = f"chapter_{chapter_id}"
        await sio.leave_room(sid, room)
        print(f"Client {sid} left room: {room}")


@sio.event
async def join_course(sid, data):
    """
    특정 코스 룸에 조인
    클라이언트가 특정 코스의 업데이트를 받기 위해 호출

    Args:
        data: {"course_id": int}
    """
    course_id = data.get('course_id')
    if course_id:
        room = f"course_{course_id}"
        await sio.enter_room(sid, room)
        print(f"Client {sid} joined room: {room}")
        await sio.emit('joined', {'room': room}, room=sid)


@sio.event
async def leave_course(sid, data):
    """
    특정 코스 룸에서 나가기

    Args:
        data: {"course_id": int}
    """
    course_id = data.get('course_id')
    if course_id:
        room = f"course_{course_id}"
        await sio.leave_room(sid, room)
        print(f"Client {sid} left room: {room}")


# ============================================
# Emit 함수들 (서버에서 클라이언트로 전송)
# ============================================

async def emit_concept_finish(chapter_id: int, data: Dict[str, Any]):
    """
    개념 정리 생성 완료 알림

    Args:
        chapter_id: 챕터 ID
        data: 전송할 데이터
    """
    room = f"chapter_{chapter_id}"
    await sio.emit('concept-finished', data, room=room)
    print(f"Emitted concept-finished to room: {room}")


async def emit_exercise_finish(chapter_id: int, data: Dict[str, Any]):
    """
    실습 과제 생성 완료 알림

    Args:
        chapter_id: 챕터 ID
        data: 전송할 데이터
    """
    room = f"chapter_{chapter_id}"
    await sio.emit('exercise-finished', data, room=room)
    print(f"Emitted exercise-finished to room: {room}")


async def emit_quiz_finish(chapter_id: int, data: Dict[str, Any]):
    """
    형성평가 생성 완료 알림

    Args:
        chapter_id: 챕터 ID
        data: 전송할 데이터
    """
    room = f"chapter_{chapter_id}"
    await sio.emit('quiz-finished', data, room=room)
    print(f"Emitted quiz-finished to room: {room}")


async def emit_quiz_graded(chapter_id: int, data: Dict[str, Any]):
    """
    퀴즈 채점 완료 알림
    사용자가 퀴즈 답안을 제출한 후 Gemini 채점 결과를 실시간으로 전송

    Args:
        chapter_id: 챕터 ID
        data: 전송할 데이터 (quiz_id, slot_number, is_correct, score, explanation 등)
    """
    room = f"chapter_{chapter_id}"
    await sio.emit('quiz-graded', data, room=room)
    print(f"Emitted quiz-graded to room: {room}")


async def emit_course_generated(course_id: int, data: Dict[str, Any]):
    """
    강의 생성 완료 알림
    Gemini가 챕터를 생성한 후 실시간으로 결과 전송

    Args:
        course_id: 코스 ID
        data: 전송할 데이터 (course_id, chapters 등)
    """
    room = f"course_{course_id}"
    await sio.emit('course-generated', data, room=room)
    print(f"Emitted course-generated to room: {room}")


async def emit_chapter_complete(chapter_id: int, data: Dict[str, Any]):
    """
    챕터의 모든 콘텐츠 생성 완료 알림
    (concept, exercise, quiz 모두 완료)

    Args:
        chapter_id: 챕터 ID
        data: 전송할 데이터
    """
    room = f"chapter_{chapter_id}"
    await sio.emit('chapter-complete', data, room=room)
    print(f"Emitted chapter-complete to room: {room}")


# ============================================
# 유틸리티 함수
# ============================================

async def get_connected_clients(room: Optional[str] = None) -> int:
    """
    연결된 클라이언트 수 조회

    Args:
        room: 특정 룸의 클라이언트 수 (None이면 전체)

    Returns:
        클라이언트 수
    """
    if room:
        clients = sio.manager.get_participants(namespace='/', room=room)
        return len(clients)
    else:
        # 전체 연결된 클라이언트
        return len(sio.manager.rooms.get('/', {}).keys())
