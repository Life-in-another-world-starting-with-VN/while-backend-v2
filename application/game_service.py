from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from fastapi import HTTPException, status

from domain.repository.game_repository import (
    CharacterRepository,
    GameRepository,
    SessionRepository,
    SceneRepository,
)
from application.background_generator import BackgroundGenerator
from application.llm_service import LLMService


class GameService:
    def __init__(self, db: Session):
        self.db = db
        self.character_repo = CharacterRepository(db)
        self.game_repo = GameRepository(db)
        self.session_repo = SessionRepository(db)
        self.scene_repo = SceneRepository(db)
        self.bg_generator = BackgroundGenerator()
        self.llm_service = LLMService()

    def create_new_game(
        self, user_id: int, personality: str, genre: str, playtime: int
    ) -> Dict:
        """새 게임 생성"""
        # 1. 모든 캐릭터 조회
        characters = self.character_repo.get_all_characters()
        if not characters:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No characters found in database",
            )

        characters_dict = [
            {"id": char.id, "name": char.name, "personality": char.personality}
            for char in characters
        ]

        # 2. LLM으로 게임 구조 생성
        game_structure = self.llm_service.generate_game_structure(
            personality=personality,
            genre=genre,
            playtime=playtime,
            characters=characters_dict,
        )

        # 3. 게임 생성
        game = self.game_repo.create_game(
            user_id=user_id,
            title=game_structure["title"],
            personality=personality,
            genre=genre,
            playtime=playtime,
        )

        # 4. 첫 세션 생성
        first_session_content = game_structure["first_session_content"]

        # 배경 이미지 생성
        try:
            background_url = self.bg_generator.create_background_image(
                first_session_content
            )
        except Exception as e:
            print(f"Background generation failed: {e}")
            background_url = "https://placeholder.com/background.jpg"

        session = self.session_repo.create_session(
            game_id=game.id,
            session_number=1,
            content=first_session_content,
            background_url=background_url,
        )

        # 5. 첫 씬 생성
        first_scene_data = game_structure["first_scene"]
        scene = self.scene_repo.create_scene(
            session_id=session.id,
            scene_number=1,
            role=first_scene_data["role"],
            scene_type=first_scene_data["type"],
            dialogue=first_scene_data.get("dialogue"),
            selections=first_scene_data.get("selections"),
        )

        # 6. 응답 구성
        return {
            "game_id": game.id,
            "personality": game.personality,
            "genre": game.genre,
            "title": game.title,
            "playtime": game.playtime,
            "sessions": [
                {
                    "session_id": session.id,
                    "content": session.content,
                    "scenes": [
                        {
                            "role": scene.role,
                            "scene_id": scene.id,
                            "type": scene.type,
                            "dialogue": scene.dialogue,
                            "selections": scene.selections or {},
                        }
                    ],
                    "background_url": session.background_url,
                }
            ],
        }

    def generate_next_scene(
        self,
        game_id: int,
        session_id: int,
        scene_id: int,
        emotion: Dict[str, int],
        elapsed_time: int,
    ) -> Dict:
        """다음 씬 생성"""
        # 1. 게임, 세션 조회
        game = self.game_repo.get_game_by_id(game_id)
        if not game:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Game not found"
            )

        session = self.session_repo.get_session_by_id(session_id)
        if not session or session.game_id != game_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
            )

        # 2. 캐릭터 정보 가져오기
        characters = self.character_repo.get_all_characters()
        characters_dict = [
            {"id": char.id, "name": char.name, "personality": char.personality}
            for char in characters
        ]

        # 3. 대화 히스토리 (현재 세션의 모든 씬)
        scenes = self.scene_repo.get_scenes_by_session(session_id)
        scene_history = [
            {
                "role": sc.role,
                "dialogue": sc.dialogue,
                "type": sc.type,
                "selections": sc.selections,
            }
            for sc in scenes
        ]

        # 4. 게임 컨텍스트
        game_context = {
            "title": game.title,
            "genre": game.genre,
            "personality": game.personality,
        }

        # 5. LLM으로 다음 씬 생성
        new_scene_data, session_ended, new_session_content = (
            self.llm_service.generate_next_scene(
                game_context=game_context,
                current_session_content=session.content,
                scene_history=scene_history,
                emotion=emotion,
                elapsed_time=elapsed_time,
                total_playtime=game.playtime,
                characters=characters_dict,
            )
        )

        # 6. 새 세션이 필요한 경우
        if session_ended and new_session_content:
            # 현재 세션 완료 표시
            self.session_repo.mark_session_completed(session_id)

            # 새 세션 생성
            latest_session = self.session_repo.get_latest_session(game_id)
            new_session_number = latest_session.session_number + 1

            # 배경 이미지 생성
            try:
                background_url = self.bg_generator.create_background_image(
                    new_session_content
                )
            except Exception as e:
                print(f"Background generation failed: {e}")
                background_url = "https://placeholder.com/background.jpg"

            new_session = self.session_repo.create_session(
                game_id=game_id,
                session_number=new_session_number,
                content=new_session_content,
                background_url=background_url,
            )

            # 새 세션의 첫 씬 생성
            new_scene = self.scene_repo.create_scene(
                session_id=new_session.id,
                scene_number=1,
                role=new_scene_data["role"],
                scene_type=new_scene_data["type"],
                dialogue=new_scene_data.get("dialogue"),
                selections=new_scene_data.get("selections"),
            )

            return {
                "session_id": new_session.id,
                "content": new_session.content,
                "scenes": [
                    {
                        "role": new_scene.role,
                        "scene_id": new_scene.id,
                        "type": new_scene.type,
                        "dialogue": new_scene.dialogue,
                        "selections": new_scene.selections or {},
                    }
                ],
                "background_url": new_session.background_url,
            }
        else:
            # 현재 세션에서 계속
            latest_scene = self.scene_repo.get_latest_scene(session_id)
            new_scene_number = latest_scene.scene_number + 1

            new_scene = self.scene_repo.create_scene(
                session_id=session_id,
                scene_number=new_scene_number,
                role=new_scene_data["role"],
                scene_type=new_scene_data["type"],
                dialogue=new_scene_data.get("dialogue"),
                selections=new_scene_data.get("selections"),
            )

            return {
                "session_id": session.id,
                "content": session.content,
                "scenes": [
                    {
                        "role": new_scene.role,
                        "scene_id": new_scene.id,
                        "type": new_scene.type,
                        "dialogue": new_scene.dialogue,
                        "selections": new_scene.selections or {},
                    }
                ],
                "background_url": session.background_url,
            }

    def generate_scene_after_selection(
        self,
        game_id: int,
        session_id: int,
        scene_id: int,
        selection_id: int,
        emotion: Dict[str, int],
        elapsed_time: int,
    ) -> Dict:
        """선택지 선택 후 다음 씬 생성"""
        # 1. 게임, 세션, 씬 조회
        game = self.game_repo.get_game_by_id(game_id)
        if not game:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Game not found"
            )

        session = self.session_repo.get_session_by_id(session_id)
        if not session or session.game_id != game_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
            )

        scene = self.scene_repo.get_scene_by_id(scene_id)
        if not scene or scene.session_id != session_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Scene not found"
            )

        # 2. 선택지 검증
        if scene.type != "selection" or not scene.selections:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This scene is not a selection type",
            )

        if str(selection_id) not in scene.selections:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid selection_id",
            )

        # 선택지 저장
        self.scene_repo.update_scene_selection(scene_id, selection_id)

        # 3. 캐릭터 정보 가져오기
        characters = self.character_repo.get_all_characters()
        characters_dict = [
            {"id": char.id, "name": char.name, "personality": char.personality}
            for char in characters
        ]

        # 4. 대화 히스토리
        scenes = self.scene_repo.get_scenes_by_session(session_id)
        scene_history = [
            {
                "role": sc.role,
                "dialogue": sc.dialogue,
                "type": sc.type,
                "selections": sc.selections,
            }
            for sc in scenes
        ]

        # 5. 게임 컨텍스트
        game_context = {
            "title": game.title,
            "genre": game.genre,
            "personality": game.personality,
        }

        # 6. 선택한 옵션
        selected_option = scene.selections[str(selection_id)]

        # 7. LLM으로 다음 씬 생성
        new_scene_data, session_ended, new_session_content = (
            self.llm_service.generate_scene_after_selection(
                game_context=game_context,
                current_session_content=session.content,
                scene_history=scene_history,
                selected_option=selected_option,
                emotion=emotion,
                elapsed_time=elapsed_time,
                total_playtime=game.playtime,
                characters=characters_dict,
            )
        )

        # 8. 새 세션이 필요한 경우
        if session_ended and new_session_content:
            # 현재 세션 완료 표시
            self.session_repo.mark_session_completed(session_id)

            # 새 세션 생성
            latest_session = self.session_repo.get_latest_session(game_id)
            new_session_number = latest_session.session_number + 1

            # 배경 이미지 생성
            try:
                background_url = self.bg_generator.create_background_image(
                    new_session_content
                )
            except Exception as e:
                print(f"Background generation failed: {e}")
                background_url = "https://placeholder.com/background.jpg"

            new_session = self.session_repo.create_session(
                game_id=game_id,
                session_number=new_session_number,
                content=new_session_content,
                background_url=background_url,
            )

            # 새 세션의 첫 씬 생성
            new_scene = self.scene_repo.create_scene(
                session_id=new_session.id,
                scene_number=1,
                role=new_scene_data["role"],
                scene_type=new_scene_data["type"],
                dialogue=new_scene_data.get("dialogue"),
                selections=new_scene_data.get("selections"),
            )

            return {
                "session_id": new_session.id,
                "content": new_session.content,
                "scenes": [
                    {
                        "role": new_scene.role,
                        "scene_id": new_scene.id,
                        "type": new_scene.type,
                        "dialogue": new_scene.dialogue,
                        "selections": new_scene.selections or {},
                    }
                ],
                "background_url": new_session.background_url,
            }
        else:
            # 현재 세션에서 계속
            latest_scene = self.scene_repo.get_latest_scene(session_id)
            new_scene_number = latest_scene.scene_number + 1

            new_scene = self.scene_repo.create_scene(
                session_id=session_id,
                scene_number=new_scene_number,
                role=new_scene_data["role"],
                scene_type=new_scene_data["type"],
                dialogue=new_scene_data.get("dialogue"),
                selections=new_scene_data.get("selections"),
            )

            return {
                "session_id": session.id,
                "content": session.content,
                "scenes": [
                    {
                        "role": new_scene.role,
                        "scene_id": new_scene.id,
                        "type": new_scene.type,
                        "dialogue": new_scene.dialogue,
                        "selections": new_scene.selections or {},
                    }
                ],
                "background_url": session.background_url,
            }
