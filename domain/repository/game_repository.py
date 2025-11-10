from sqlalchemy.orm import Session
from domain.entity.game import Character, Game, Session as GameSession, Scene
from typing import List, Optional


class CharacterRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_characters(self) -> List[Character]:
        """모든 캐릭터 조회"""
        return self.db.query(Character).all()

    def get_character_by_id(self, character_id: int) -> Optional[Character]:
        """ID로 캐릭터 조회"""
        return self.db.query(Character).filter(Character.id == character_id).first()

    def create_character(self, name: str, personality: str) -> Character:
        """캐릭터 생성"""
        character = Character(name=name, personality=personality)
        self.db.add(character)
        self.db.commit()
        self.db.refresh(character)
        return character


class GameRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_game(
        self,
        user_id: int,
        title: str,
        personality: str,
        genre: str,
        playtime: int,
    ) -> Game:
        """새 게임 생성"""
        game = Game(
            user_id=user_id,
            title=title,
            personality=personality,
            genre=genre,
            playtime=playtime,
        )
        self.db.add(game)
        self.db.commit()
        self.db.refresh(game)
        return game

    def get_game_by_id(self, game_id: int) -> Optional[Game]:
        """ID로 게임 조회"""
        return self.db.query(Game).filter(Game.id == game_id).first()

    def get_games_by_user(self, user_id: int) -> List[Game]:
        """사용자의 모든 게임 조회"""
        return self.db.query(Game).filter(Game.user_id == user_id).all()

    def update_game(self, game: Game) -> Game:
        """게임 업데이트"""
        self.db.commit()
        self.db.refresh(game)
        return game


class SessionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_session(
        self,
        game_id: int,
        session_number: int,
        content: str,
        background_url: Optional[str] = None,
    ) -> GameSession:
        """새 세션 생성"""
        session = GameSession(
            game_id=game_id,
            session_number=session_number,
            content=content,
            background_url=background_url,
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_session_by_id(self, session_id: int) -> Optional[GameSession]:
        """ID로 세션 조회"""
        return self.db.query(GameSession).filter(GameSession.id == session_id).first()

    def get_sessions_by_game(self, game_id: int) -> List[GameSession]:
        """게임의 모든 세션 조회"""
        return (
            self.db.query(GameSession)
            .filter(GameSession.game_id == game_id)
            .order_by(GameSession.session_number)
            .all()
        )

    def get_latest_session(self, game_id: int) -> Optional[GameSession]:
        """게임의 가장 최근 세션 조회"""
        return (
            self.db.query(GameSession)
            .filter(GameSession.game_id == game_id)
            .order_by(GameSession.session_number.desc())
            .first()
        )

    def update_session(self, session: GameSession) -> GameSession:
        """세션 업데이트"""
        self.db.commit()
        self.db.refresh(session)
        return session

    def mark_session_completed(self, session_id: int) -> GameSession:
        """세션을 완료 상태로 표시"""
        session = self.get_session_by_id(session_id)
        if session:
            session.is_completed = 1
            return self.update_session(session)
        return None


class SceneRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_scene(
        self,
        session_id: int,
        scene_number: int,
        role: str,
        scene_type: str,
        dialogue: Optional[str] = None,
        selections: Optional[dict] = None,
        character_id: Optional[int] = None,
        emotion: Optional[str] = None,
    ) -> Scene:
        """새 씬 생성"""
        scene = Scene(
            session_id=session_id,
            scene_number=scene_number,
            role=role,
            type=scene_type,
            dialogue=dialogue,
            selections=selections,
            character_id=character_id,
            emotion=emotion,
        )
        self.db.add(scene)
        self.db.commit()
        self.db.refresh(scene)
        return scene

    def get_scene_by_id(self, scene_id: int) -> Optional[Scene]:
        """ID로 씬 조회"""
        return self.db.query(Scene).filter(Scene.id == scene_id).first()

    def get_scenes_by_session(self, session_id: int) -> List[Scene]:
        """세션의 모든 씬 조회"""
        return (
            self.db.query(Scene)
            .filter(Scene.session_id == session_id)
            .order_by(Scene.scene_number)
            .all()
        )

    def get_latest_scene(self, session_id: int) -> Optional[Scene]:
        """세션의 가장 최근 씬 조회"""
        return (
            self.db.query(Scene)
            .filter(Scene.session_id == session_id)
            .order_by(Scene.scene_number.desc())
            .first()
        )

    def update_scene_selection(self, scene_id: int, selected_option: int) -> Scene:
        """씬의 선택지 업데이트"""
        scene = self.get_scene_by_id(scene_id)
        if scene:
            scene.selected_option = selected_option
            self.db.commit()
            self.db.refresh(scene)
        return scene

    def get_all_scenes_in_game(self, game_id: int) -> List[Scene]:
        """게임의 모든 씬 조회 (대화 히스토리 용)"""
        return (
            self.db.query(Scene)
            .join(GameSession)
            .filter(GameSession.game_id == game_id)
            .order_by(GameSession.session_number, Scene.scene_number)
            .all()
        )
