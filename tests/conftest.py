import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.database import Base, get_db
from main import app

# 테스트용 인메모리 SQLite 데이터베이스
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    # 테이블 생성
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        # 테스트용 캐릭터 데이터 삽입
        from domain.entity.game import Character
        
        characters = [
            Character(
                name="아리아나",
                personality="밝고 활발한 성격. 항상 긍정적이고 주변 사람들을 웃게 만드는 것을 좋아한다."
            ),
            Character(
                name="유나",
                personality="조용하고 차분한 성격. 책을 좋아하며 깊이 있는 대화를 선호한다."
            ),
            Character(
                name="소라",
                personality="도도하지만 따뜻한 성격. 처음엔 차갑게 대하지만 친해지면 누구보다 다정하다."
            ),
        ]
        
        for char in characters:
            db.add(char)
        db.commit()
        
        yield db
    finally:
        db.close()
        # 테스트 후 테이블 삭제
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
