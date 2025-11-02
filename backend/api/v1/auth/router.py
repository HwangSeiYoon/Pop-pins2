"""
JWT 인증 유틸리티
회원가입, 로그인, 토큰 검증 기능 제공
"""

from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
import redis
import json

# 환경 변수
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24시간

# 비밀번호 해싱
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer 토큰
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    평문 비밀번호와 해시된 비밀번호 비교

    Args:
        plain_password: 평문 비밀번호
        hashed_password: 해시된 비밀번호

    Returns:
        bool: 일치 여부
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    비밀번호 해싱

    Args:
        password: 평문 비밀번호

    Returns:
        str: 해시된 비밀번호
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    JWT 액세스 토큰 생성

    Args:
        data: 토큰에 포함할 데이터
        expires_delta: 만료 시간

    Returns:
        str: JWT 토큰
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    # Redis에 JWT 데이터 저장
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    user_id = data.get("user_id")
    if user_id:
        # user_id를 키로 사용하여 JWT payload 데이터 저장
        redis_key = f"user:{user_id}:session"
        redis_value = json.dumps({
            "token": encoded_jwt
        })
        # 만료 시간과 동일하게 24시간 설정
        r.setex(redis_key, ACCESS_TOKEN_EXPIRE_MINUTES * 60, redis_value)

    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    JWT 토큰 디코딩

    Args:
        token: JWT 토큰

    Returns:
        dict: 디코딩된 데이터 또는 None
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    현재 로그인한 사용자 정보 가져오기 (Dependency)

    Args:
        credentials: HTTP Bearer 토큰

    Returns:
        dict: 사용자 정보

    Raises:
        HTTPException: 인증 실패 시
    """
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("user_id")
    email = payload.get("email")

    if user_id is None or email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "user_id": user_id,
        "email": email,
        "name": payload.get("name")
    }


# Optional: 인증이 선택적인 경우
def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[dict]:
    """
    현재 로그인한 사용자 정보 가져오기 (선택적)

    Args:
        credentials: HTTP Bearer 토큰 (없을 수 있음)

    Returns:
        dict: 사용자 정보 또는 None
    """
    if credentials is None:
        return None

    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        return None

    return {
        "user_id": payload.get("user_id"),
        "email": payload.get("email"),
        "name": payload.get("name")
    }
