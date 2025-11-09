from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from core.database import get_db
from core.auth_dependency import get_current_user
from application.game_service import GameService
from presentation.schemas import (
    CreateGameRequest,
    CreateGameResponse,
    NextSceneRequest,
    NextSceneResponse,
)

router = APIRouter(prefix="/api/v2", tags=["game"])


@router.post("/game", response_model=CreateGameResponse, status_code=status.HTTP_200_OK)
def create_game(
    request: CreateGameRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    새 게임 생성

    - **personality**: 캐릭터 성격
    - **genre**: 게임 장르
    - **playtime**: 플레이 시간 (분 단위)
    """
    game_service = GameService(db)
    result = game_service.create_new_game(
        user_id=current_user["user_id"],
        personality=request.personality,
        genre=request.genre,
        playtime=request.playtime,
    )
    return result


@router.post(
    "/game/{game_id}/{session_id}/{scene_id}",
    response_model=NextSceneResponse,
    status_code=status.HTTP_200_OK,
)
def generate_next_scene(
    game_id: int,
    session_id: int,
    scene_id: int,
    request: NextSceneRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    다음 씬 생성

    - **game_id**: 게임 ID
    - **session_id**: 현재 세션 ID
    - **scene_id**: 현재 씬 ID
    - **emotion**: 사용자 얼굴 감정 데이터
    - **time**: 현재 진행 시간 (초 단위)
    """
    game_service = GameService(db)
    result = game_service.generate_next_scene(
        game_id=game_id,
        session_id=session_id,
        scene_id=scene_id,
        emotion=request.emotion.dict(),
        elapsed_time=request.time,
    )
    return result


@router.post(
    "/game/{game_id}/{session_id}/{scene_id}/selection/{selection_id}",
    response_model=NextSceneResponse,
    status_code=status.HTTP_200_OK,
)
def generate_scene_after_selection(
    game_id: int,
    session_id: int,
    scene_id: int,
    selection_id: int,
    request: NextSceneRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    선택지 선택 후 다음 씬 생성

    - **game_id**: 게임 ID
    - **session_id**: 현재 세션 ID
    - **scene_id**: 현재 씬 ID (선택지가 있는 씬)
    - **selection_id**: 선택한 선택지 번호
    - **emotion**: 사용자 얼굴 감정 데이터
    - **time**: 현재 진행 시간 (초 단위)
    """
    game_service = GameService(db)
    result = game_service.generate_scene_after_selection(
        game_id=game_id,
        session_id=session_id,
        scene_id=scene_id,
        selection_id=selection_id,
        emotion=request.emotion.dict(),
        elapsed_time=request.time,
    )
    return result
