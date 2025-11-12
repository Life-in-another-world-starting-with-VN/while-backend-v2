from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from domain.repository.user_repository import UserRepository
from core.security import get_password_hash, verify_password, create_access_token, create_refresh_token, decode_token
from core.config import get_settings

settings = get_settings()


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)

    def signup(self, username: str, email: str, password: str) -> dict:
        # 이미 존재하는 username 확인
        existing_user = self.user_repository.get_user_by_username(username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )

        # 이미 존재하는 email 확인
        existing_email = self.user_repository.get_user_by_email(email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # 비밀번호 해싱
        hashed_password = get_password_hash(password)

        # 사용자 생성
        user = self.user_repository.create_user(
            username=username,
            email=email,
            hashed_password=hashed_password
        )

        return {"message": "회원가입에 성공했습니다."}

    def login(self, username: str, password: str) -> dict:
        # 사용자 조회
        user = self.user_repository.get_user_by_username(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )

        # 비밀번호 검증
        if not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )

        # 액세스 토큰 생성
        access_token = create_access_token(data={"sub": str(user.id), "username": user.username})

        # 리프레시 토큰 생성
        refresh_token = create_refresh_token(data={"sub": str(user.id), "username": user.username})

        # 리프레시 토큰을 DB에 저장
        expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        self.user_repository.save_refresh_token(
            user_id=user.id,
            token=refresh_token,
            expires_at=expires_at
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }

    def reissue_token(self, refresh_token: str) -> dict:
        # 리프레시 토큰 검증
        try:
            payload = decode_token(refresh_token)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        # 토큰 타입 확인
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )

        # DB에서 리프레시 토큰 확인
        stored_token = self.user_repository.get_refresh_token(refresh_token)
        if not stored_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token not found"
            )

        # 토큰 만료 확인
        if stored_token.expires_at < datetime.utcnow():
            # 만료된 토큰 삭제
            self.user_repository.delete_refresh_token(refresh_token)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expired"
            )

        # 사용자 정보 조회
        user_id = int(payload.get("sub"))
        user = self.user_repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        # 새로운 액세스 토큰 생성
        new_access_token = create_access_token(data={"sub": str(user.id), "username": user.username})

        # 새로운 리프레시 토큰 생성
        new_refresh_token = create_refresh_token(data={"sub": str(user.id), "username": user.username})

        # 기존 토큰 삭제 및 새 토큰 저장 (원자적 작업)
        expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        self.user_repository.replace_refresh_token(
            old_token=refresh_token,
            user_id=user.id,
            new_token=new_refresh_token,
            expires_at=expires_at
        )

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token
        }
