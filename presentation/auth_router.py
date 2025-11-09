from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from core.database import get_db
from application.auth_service import AuthService
from presentation.schemas import (
    SignupRequest, SignupResponse,
    LoginRequest, LoginResponse,
    ReissueRequest, ReissueResponse
)

router = APIRouter(prefix="/api/v2", tags=["auth"])


@router.post("/signup", response_model=SignupResponse, status_code=status.HTTP_200_OK)
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    result = auth_service.signup(
        username=request.username,
        email=request.email,
        password=request.password
    )
    return result


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    result = auth_service.login(
        username=request.username,
        password=request.password
    )
    return result


@router.post("/reissue", response_model=ReissueResponse, status_code=status.HTTP_200_OK)
def reissue(request: ReissueRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    result = auth_service.reissue_token(refresh_token=request.refresh_token)
    return result
