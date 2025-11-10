from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base


class Character(Base):
    """캐릭터 테이블 - 3명의 사전 정의된 캐릭터"""
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    personality = Column(Text, nullable=False)  # 특징 or 성격
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Game(Base):
    """게임 테이블"""
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)  # LLM이 생성한 게임 제목
    personality = Column(String(100), nullable=False)  # 캐릭터 성격
    genre = Column(String(100), nullable=False)  # 게임 장르
    playtime = Column(Integer, nullable=False)  # 분 단위 플레이 시간
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    sessions = relationship("Session", back_populates="game", cascade="all, delete-orphan")


class Session(Base):
    """세션 테이블 - 한 장소 단위의 장면"""
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False, index=True)
    session_number = Column(Integer, nullable=False)  # 세션 순서 (1, 2, 3...)
    content = Column(Text, nullable=False)  # 세션 설명 (예: "학교 복도에서 1번 캐릭터를 만나...")
    background_url = Column(String(500), nullable=True)  # 배경 이미지 URL
    is_completed = Column(Integer, default=0, nullable=False)  # 0: 진행중, 1: 완료
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    game = relationship("Game", back_populates="sessions")
    scenes = relationship("Scene", back_populates="session", cascade="all, delete-orphan")


class Scene(Base):
    """씬 테이블 - 각 대사 or 선택지"""
    __tablename__ = "scenes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False, index=True)
    scene_number = Column(Integer, nullable=False)  # 씬 순서 (1, 2, 3...)
    role = Column(String(100), nullable=False)  # 누가 말하는지 (캐릭터명, "user", "narrator")
    type = Column(String(20), nullable=False)  # "dialogue" or "selection"
    dialogue = Column(Text, nullable=True)  # type=dialogue일 때 대사 내용
    selections = Column(JSON, nullable=True)  # type=selection일 때 선택지 {"1": "...", "2": "..."}
    selected_option = Column(Integer, nullable=True)  # 사용자가 선택한 옵션 번호 (선택지인 경우)
    character_id = Column(Integer, nullable=True)  # 캐릭터 ID (캐릭터가 말하는 경우)
    emotion = Column(String(20), nullable=True)  # 캐릭터 표정 (anger, blush, embarrassed, laugh, sad, smile, surprise, thinking, worry, 기본)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    session = relationship("Session", back_populates="scenes")
