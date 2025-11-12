from pydantic import BaseModel, EmailStr, Field
from typing import Dict, List, Optional


# ============== Auth Schemas ==============
class SignupRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)


class SignupResponse(BaseModel):
    message: str


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str


class ReissueRequest(BaseModel):
    refresh_token: str


class ReissueResponse(BaseModel):
    access_token: str
    refresh_token: str


# ============== Game Schemas ==============
class CreateGameRequest(BaseModel):
    personality: str = Field(..., description="캐릭터 성격")
    genre: str = Field(..., description="게임 장르")
    playtime: int = Field(..., gt=0, description="플레이 시간 (분 단위)")


class SceneData(BaseModel):
    role: str
    scene_id: int
    type: str
    dialogue: Optional[str] = None
    selections: Dict[str, str] = {}
    character_filename: Optional[str] = None  # 캐릭터 이미지 파일명 (예: "1_smile.png")


class SessionData(BaseModel):
    session_id: int
    content: str
    scenes: List[SceneData]
    background_url: Optional[str] = None


class CreateGameResponse(BaseModel):
    game_id: int
    personality: str
    genre: str
    title: str
    playtime: int
    main_character_id: int
    main_character_name: str
    sessions: List[SessionData]


class EmotionData(BaseModel):
    angry: int = Field(..., ge=0, le=100)
    disgust: int = Field(..., ge=0, le=100)
    fear: int = Field(..., ge=0, le=100)
    happy: int = Field(..., ge=0, le=100)
    sad: int = Field(..., ge=0, le=100)
    surprise: int = Field(..., ge=0, le=100)
    neutral: int = Field(..., ge=0, le=100)


class NextSceneRequest(BaseModel):
    emotion: EmotionData
    time: int = Field(..., ge=0, description="현재 진행 시간 (초 단위)")


class NextSceneResponse(BaseModel):
    session_id: int
    content: str
    scenes: List[SceneData]
    background_url: Optional[str] = None
