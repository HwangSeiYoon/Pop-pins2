"""
Member Router
회원 가입, 로그인, 유저 정보 조회 (JWT + Redis)
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import redis
from api.v1.schemas import MemberSignup, MemberLogin, MemberResponse, LoginResponse
from db import models
from db.database import get_db, get_redis
from api.v1.auth.router import get_password_hash, verify_password, create_access_token
from utils.auth_middleware import require_auth

router = APIRouter(prefix="/v1/member", tags=["member"])

# JWT 토큰 만료 시간 (초) - 1일
TOKEN_EXPIRE_SECONDS = 86400


# 1. 회원가입
@router.post("/signup", response_model=MemberResponse)
def signup(member: MemberSignup, db: Session = Depends(get_db)):
    """새 사용자를 등록합니다."""
    # 이메일 중복 확인
    existing_member = db.query(models.Member).filter(models.Member.email == member.email).first()
    if existing_member:
        raise HTTPException(status_code=400, detail="Email already registered")
        return SignupResponse(
            state="failed",
            id=new_member.id,
            email=new_member.email,
            created_at=new_member.created_at
        )

    # 비밀번호 해싱
    hashed_password = get_password_hash(member.password)

    # 새 회원 생성
    new_member = models.Member(
        email=member.email,
        password=hashed_password
    )

    db.add(new_member)
    db.commit()
    db.refresh(new_member)

    return SignupResponse(
        state="success",
        id=new_member.id,
        email=new_member.email,
        created_at=new_member.created_at
    )


# 2. 로그인
@router.post("/login", response_model=LoginResponse)
def login(
    credentials: MemberLogin,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis)
):
    """
    사용자 로그인 후 JWT 토큰을 발급하고 Redis에 저장합니다.

    Redis Key Format: token:{user_id}
    Redis Value: access_token
    Redis TTL: 1일 (86400초)
    """
    # 사용자 조회
    member = db.query(models.Member).filter(models.Member.email == credentials.email).first()

    if not member:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # 비밀번호 확인
    if not verify_password(credentials.password, member.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
        return LoginResponse(state="failed")

    # JWT 토큰 생성
    access_token = create_access_token(data={"user_id": member.id, "email": member.email})

    # Redis에 토큰 저장 (TTL: 1일)
    redis_key = f"token:{member.id}"
    redis_client.setex(redis_key, TOKEN_EXPIRE_SECONDS, access_token)

    return LoginResponse(
        state="success",
        access_token=access_token,
        token_type="bearer",
        member=MemberResponse(
            id=member.id,
            email=member.email,
            created_at=member.created_at
        )
    )


# 3. 유저 정보 조회
@router.get("/", response_model=MemberResponse)
def get_member_info(
    current_user: dict = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """로그인된 사용자 정보를 반환합니다. (헤더에 Authorization: Bearer <token> 필요)"""
    member = db.query(models.Member).filter(models.Member.id == current_user["user_id"]).first()

    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    return member


# 4. 로그아웃
@router.post("/logout")
def logout(
    current_user: dict = Depends(require_auth),
    redis_client: redis.Redis = Depends(get_redis)
):
    """
    로그아웃 - Redis에서 토큰 삭제
    """
    user_id = current_user["user_id"]
    redis_key = f"token:{user_id}"

    # Redis에서 토큰 삭제
    deleted = redis_client.delete(redis_key)

    return {
        "status": "success",
        "message": "Logged out successfully",
        "deleted": deleted > 0
    }
