"""
JWT 토큰 검증 미들웨어
Authorization 헤더의 JWT 토큰을 Redis와 대조하여 유효성 검증
"""

from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import redis
from core.config import settings
from db.database import get_redis
from typing import Optional, Dict, Any

# HTTP Bearer 토큰
security = HTTPBearer()

def verify_token(token: str, redis_client: redis.Redis) -> Dict[str, Any]:
    """
    JWT 토큰 검증 및 Redis 확인
    
    Args:
        token: JWT 토큰
        redis_client: Redis 클라이언트
        
    Returns:
        Dict: 토큰에서 추출한 사용자 정보
        
    Raises:
        HTTPException: 토큰이 유효하지 않거나 만료된 경우
    """
    try:
        # JWT 토큰 디코딩
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Redis에서 토큰 확인
        stored_token = redis_client.get(f"token:{user_id}")
        if not stored_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token not found or expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 토큰 일치 확인
        if stored_token.decode() != token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return {
            "user_id": int(user_id),
            "email": payload.get("email")
        }
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    redis_client: redis.Redis = Depends(get_redis)
) -> Dict[str, Any]:
    """
    현재 사용자 정보 가져오기
    Authorization 헤더에서 JWT 토큰을 추출하고 검증
    
    Args:
        credentials: HTTP Bearer 토큰
        redis_client: Redis 클라이언트
        
    Returns:
        Dict: 현재 사용자 정보
        
    Raises:
        HTTPException: 토큰이 유효하지 않은 경우
    """
    return verify_token(credentials.credentials, redis_client)

def get_optional_user(
    request: Request,
    redis_client: redis.Redis = Depends(get_redis)
) -> Optional[Dict[str, Any]]:
    """
    선택적 사용자 정보 가져오기 (토큰이 없어도 에러 발생하지 않음)
    
    Args:
        request: FastAPI Request 객체
        redis_client: Redis 클라이언트
        
    Returns:
        Optional[Dict]: 사용자 정보 (토큰이 없으면 None)
    """
    authorization = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    token = authorization.replace("Bearer ", "")
    try:
        return verify_token(token, redis_client)
    except HTTPException:
        return None

def require_auth(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    redis_client: redis.Redis = Depends(get_redis)
) -> Dict[str, Any]:
    """
    인증 필수 의존성
    모든 보호된 엔드포인트에서 사용
    
    Args:
        credentials: HTTP Bearer 토큰
        redis_client: Redis 클라이언트
        
    Returns:
        Dict: 현재 사용자 정보
        
    Raises:
        HTTPException: 토큰이 유효하지 않은 경우 401 에러
    """
    return get_current_user(credentials, redis_client)

def get_user_id_from_token(token: str, redis_client: redis.Redis) -> Optional[int]:
    """
    JWT 토큰에서 user_id 추출 (Redis 검증 포함)
    
    Args:
        token: JWT 토큰 문자열
        redis_client: Redis 클라이언트
        
    Returns:
        Optional[int]: 사용자 ID (토큰이 유효하지 않으면 None)
    """
    try:
        user_info = verify_token(token, redis_client)
        return user_info.get("user_id")
    except HTTPException:
        return None

def extract_user_id_from_header(authorization_header: str, redis_client: redis.Redis) -> Optional[int]:
    """
    Authorization 헤더에서 user_id 추출
    
    Args:
        authorization_header: "Bearer <token>" 형태의 헤더 값
        redis_client: Redis 클라이언트
        
    Returns:
        Optional[int]: 사용자 ID (헤더가 유효하지 않으면 None)
    """
    if not authorization_header or not authorization_header.startswith("Bearer "):
        return None
    
    token = authorization_header.replace("Bearer ", "")
    return get_user_id_from_token(token, redis_client)

def get_user_id_from_request(
    request: Request,
    redis_client: redis.Redis = Depends(get_redis)
) -> Optional[int]:
    """
    Request 객체에서 user_id 추출 (의존성 함수로 사용 가능)
    
    Args:
        request: FastAPI Request 객체
        redis_client: Redis 클라이언트
        
    Returns:
        Optional[int]: 사용자 ID (토큰이 없거나 유효하지 않으면 None)
    """
    authorization = request.headers.get("Authorization")
    return extract_user_id_from_header(authorization, redis_client)