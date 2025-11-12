from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from core.database import Base, engine
from presentation.auth_router import router as auth_router
from presentation.game_router import router as game_router

app = FastAPI(
    title="GSTAR API",
    description="GSTAR API Documentation",
    version="2.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    
    # 정적 파일 디렉토리 생성
    images_dir = Path("static/generated_images")
    images_dir.mkdir(parents=True, exist_ok=True)

# 정적 파일 서빙 설정
app.mount("/static", StaticFiles(directory="static"), name="static")

# 라우터 등록
app.include_router(auth_router)
app.include_router(game_router)


@app.get("/")
def root():
    return {"message": "GSTAR API Server is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
