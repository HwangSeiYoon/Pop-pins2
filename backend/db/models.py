"""
SQLAlchemy 데이터베이스 모델 (단일 질문-학습 모드)
질문 1개 → Chapter 1개 → Concept 1개 + Exercise 1개 + Quiz 1개
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class StatusEnum(str, enum.Enum):
    """처리 상태 열거형"""
    pending = "pending"
    completed = "completed"


class DifficultyEnum(str, enum.Enum):
    """난이도 열거형"""
    easy = "easy"
    medium = "medium"
    hard = "hard"


class QuizTypeEnum(str, enum.Enum):
    """퀴즈 유형 열거형"""
    multiple = "multiple"
    short = "short"
    boolean = "boolean"


class Member(Base):
    """회원 모델"""
    __tablename__ = "member"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships - 단일 모드에서는 member -> chapter만 관리
    chapters = relationship("Chapter", back_populates="owner", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Member(id={self.id}, email={self.email})>"


class Chapter(Base):
    """챕터 모델 (단일 모드: 질문 1개 = 챕터 1개)"""
    __tablename__ = "chapter"

    id = Column(Integer, primary_key=True, autoincrement=True)
    owner_id = Column(Integer, ForeignKey("member.id"), nullable=False)
    title = Column(String(255), nullable=False)  # 학생이 입력한 질문
    description = Column(Text, nullable=True)  # AI가 생성한 요약/설명
    status = Column(Enum(StatusEnum), default=StatusEnum.pending)  # AI 생성 상태
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = relationship("Member", back_populates="chapters")
    concept = relationship("Concept", back_populates="chapter", cascade="all, delete-orphan", uselist=False)  # 1:1
    exercise = relationship("Exercise", back_populates="chapter", cascade="all, delete-orphan", uselist=False)  # 1:1
    quiz = relationship("Quiz", back_populates="chapter", cascade="all, delete-orphan", uselist=False)  # 1:1

    def __repr__(self):
        return f"<Chapter(id={self.id}, title={self.title}, owner_id={self.owner_id}, status={self.status})>"


class Concept(Base):
    """개념 모델 (1:1 관계)"""
    __tablename__ = "concept"
    __table_args__ = (
        UniqueConstraint('chapter_id', name='uq_chapter_concept'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    chapter_id = Column(Integer, ForeignKey("chapter.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=True)  # AI가 생성
    content = Column(Text, nullable=True)  # AI가 생성 (초기값 빈 문자열)
    is_complete = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    chapter = relationship("Chapter", back_populates="concept")

    def __repr__(self):
        return f"<Concept(id={self.id}, chapter_id={self.chapter_id}, is_complete={self.is_complete})>"


class Exercise(Base):
    """연습문제 모델 (1:1 관계)"""
    __tablename__ = "exercise"
    __table_args__ = (
        UniqueConstraint('chapter_id', name='uq_chapter_exercise'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    chapter_id = Column(Integer, ForeignKey("chapter.id", ondelete="CASCADE"), nullable=False)
    question = Column(Text, nullable=True)  # AI가 생성
    answer = Column(Text, nullable=True)  # AI가 생성
    is_complete = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    chapter = relationship("Chapter", back_populates="exercise")

    def __repr__(self):
        return f"<Exercise(id={self.id}, chapter_id={self.chapter_id}, is_complete={self.is_complete})>"


class Quiz(Base):
    """퀴즈 모델 (1:1 관계, 챕터당 1개만)"""
    __tablename__ = "quiz"
    __table_args__ = (
        UniqueConstraint('chapter_id', name='uq_chapter_quiz'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    chapter_id = Column(Integer, ForeignKey("chapter.id", ondelete="CASCADE"), nullable=False)
    question = Column(Text, nullable=True)  # AI가 생성
    options = Column(JSON, nullable=True)  # AI가 생성
    correct_answer = Column(String(255), nullable=True)  # AI가 생성
    explanation = Column(Text, nullable=True)
    type = Column(Enum(QuizTypeEnum), default=QuizTypeEnum.multiple)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    chapter = relationship("Chapter", back_populates="quiz")

    def __repr__(self):
        return f"<Quiz(id={self.id}, chapter_id={self.chapter_id}, type={self.type})>"
