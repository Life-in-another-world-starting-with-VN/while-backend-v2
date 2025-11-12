from sqlalchemy.orm import Session
from domain.entity.user import User, RefreshToken
from typing import Optional
from datetime import datetime


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, username: str, email: str, hashed_password: str) -> User:
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def save_refresh_token(self, user_id: int, token: str, expires_at: datetime) -> RefreshToken:
        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at
        )
        self.db.add(refresh_token)
        self.db.commit()
        self.db.refresh(refresh_token)
        return refresh_token

    def get_refresh_token(self, token: str) -> Optional[RefreshToken]:
        return self.db.query(RefreshToken).filter(RefreshToken.token == token).first()

    def delete_refresh_token(self, token: str) -> None:
        self.db.query(RefreshToken).filter(RefreshToken.token == token).delete()
        self.db.commit()

    def replace_refresh_token(self, old_token: str, user_id: int, new_token: str, expires_at: datetime) -> RefreshToken:
        """기존 토큰을 삭제하고 새 토큰을 저장하는 원자적 작업"""
        # 기존 토큰 삭제
        self.db.query(RefreshToken).filter(RefreshToken.token == old_token).delete()
        
        # 새 토큰 생성
        refresh_token = RefreshToken(
            user_id=user_id,
            token=new_token,
            expires_at=expires_at
        )
        self.db.add(refresh_token)
        
        # 한 번에 commit
        self.db.commit()
        self.db.refresh(refresh_token)
        return refresh_token
