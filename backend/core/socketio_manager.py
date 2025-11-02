"""
Socket.IO Manager
실시간 이벤트 전송을 위한 Socket.IO 관리
"""

import socketio
import logging

logger = logging.getLogger(__name__)

# Socket.IO 서버 생성 (ASGI mode for FastAPI)
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',  # 프로덕션에서는 특정 도메인으로 제한
    logger=True,
    engineio_logger=True
)


@sio.event
async def connect(sid, environ):
    """클라이언트 연결 시"""
    logger.info(f"Client connected: {sid}")
    await sio.emit('connection_established', {'status': 'connected'}, room=sid)


@sio.event
async def disconnect(sid):
    """클라이언트 연결 해제 시"""
    logger.info(f"Client disconnected: {sid}")


@sio.event
async def join_chapter(sid, data):
    """특정 챕터 룸에 참여"""
    chapter_id = data.get('chapter_id')
    if chapter_id:
        room = f"chapter_{chapter_id}"
        await sio.enter_room(sid, room)
        logger.info(f"Client {sid} joined room: {room}")
        await sio.emit('joined_chapter', {'chapter_id': chapter_id}, room=sid)


@sio.event
async def leave_chapter(sid, data):
    """챕터 룸에서 나가기"""
    chapter_id = data.get('chapter_id')
    if chapter_id:
        room = f"chapter_{chapter_id}"
        await sio.leave_room(sid, room)
        logger.info(f"Client {sid} left room: {room}")


# ==================== 이벤트 전송 함수들 ====================

async def emit_chapter_processing_started(chapter_id: int, title: str):
    """챕터 생성 시작 알림 (DB 저장 완료, AI 처리 시작 전)"""
    room = f"chapter_{chapter_id}"
    await sio.emit('chapter_processing_started', {
        'chapter_id': chapter_id,
        'title': title,
        'status': 'processing_started',
        'message': f'챕터 "{title}" 생성이 시작되었습니다. AI가 콘텐츠를 생성 중입니다...'
    }, room=room)
    logger.info(f"Emitted chapter_processing_started to room {room}")


async def emit_concept_processing(chapter_id: int, concept_id: int):
    """개념 정리 AI 처리 시작 알림 (Kafka 요청 전송됨)"""
    room = f"chapter_{chapter_id}"
    await sio.emit('concept_processing', {
        'chapter_id': chapter_id,
        'concept_id': concept_id,
        'status': 'processing',
        'message': '개념 정리를 AI가 생성 중입니다...'
    }, room=room)
    logger.info(f"Emitted concept_processing to room {room}")


async def emit_exercise_processing(chapter_id: int, exercise_id: int):
    """실습 과제 AI 처리 시작 알림 (Kafka 요청 전송됨)"""
    room = f"chapter_{chapter_id}"
    await sio.emit('exercise_processing', {
        'chapter_id': chapter_id,
        'exercise_id': exercise_id,
        'status': 'processing',
        'message': '실습 과제를 AI가 생성 중입니다...'
    }, room=room)
    logger.info(f"Emitted exercise_processing to room {room}")


async def emit_quiz_processing(chapter_id: int, quiz_count: int):
    """퀴즈 AI 처리 시작 알림 (Kafka 요청 전송됨)"""
    room = f"chapter_{chapter_id}"
    await sio.emit('quiz_processing', {
        'chapter_id': chapter_id,
        'quiz_count': quiz_count,
        'status': 'processing',
        'message': f'형성평가 {quiz_count}개를 AI가 생성 중입니다...'
    }, room=room)
    logger.info(f"Emitted quiz_processing to room {room}")


async def emit_concept_completed(chapter_id: int, concept_id: int):
    """개념 정리 완료 알림 (n8n webhook에서 호출)"""
    room = f"chapter_{chapter_id}"
    await sio.emit('concept_completed', {
        'chapter_id': chapter_id,
        'concept_id': concept_id,
        'status': 'completed',
        'message': '개념 정리가 완료되었습니다!'
    }, room=room)
    logger.info(f"Emitted concept_completed to room {room}")


async def emit_exercise_completed(chapter_id: int, exercise_id: int):
    """실습 과제 완료 알림 (n8n webhook에서 호출)"""
    room = f"chapter_{chapter_id}"
    await sio.emit('exercise_completed', {
        'chapter_id': chapter_id,
        'exercise_id': exercise_id,
        'status': 'completed',
        'message': '실습 과제가 완료되었습니다!'
    }, room=room)
    logger.info(f"Emitted exercise_completed to room {room}")


async def emit_quiz_completed(chapter_id: int, quiz_count: int):
    """퀴즈 완료 알림 (n8n webhook에서 호출)"""
    room = f"chapter_{chapter_id}"
    await sio.emit('quiz_completed', {
        'chapter_id': chapter_id,
        'quiz_count': quiz_count,
        'status': 'completed',
        'message': f'형성평가 {quiz_count}개가 완료되었습니다!'
    }, room=room)
    logger.info(f"Emitted quiz_completed to room {room}")


async def emit_all_completed(chapter_id: int):
    """모든 콘텐츠 생성 완료 알림 (모든 webhook 완료 후)"""
    room = f"chapter_{chapter_id}"
    await sio.emit('all_completed', {
        'chapter_id': chapter_id,
        'status': 'all_completed',
        'message': '모든 콘텐츠 생성이 완료되었습니다!'
    }, room=room)
    logger.info(f"Emitted all_completed to room {room}")


async def emit_progress_update(chapter_id: int, progress: int, message: str):
    """진행 상황 업데이트 (선택적 사용)"""
    room = f"chapter_{chapter_id}"
    await sio.emit('progress_update', {
        'chapter_id': chapter_id,
        'progress': progress,  # 0-100
        'message': message
    }, room=room)
    logger.info(f"Emitted progress_update to room {room}: {progress}%")
