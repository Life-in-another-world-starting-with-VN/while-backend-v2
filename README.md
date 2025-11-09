# GSTAR API v2

FastAPI와 MariaDB를 사용한 인증/인가 API 서버

## 프로젝트 구조

```
gstar_v2/
├── application/          # 비즈니스 로직 레이어
│   └── auth_service.py
├── core/                 # 핵심 설정 및 유틸리티
│   ├── config.py
│   ├── database.py
│   └── security.py
├── domain/               # 도메인 레이어
│   ├── entity/           # 데이터베이스 엔티티
│   │   └── user.py
│   └── repository/       # 데이터 접근 레이어
│       └── user_repository.py
├── presentation/         # API 엔드포인트 레이어
│   ├── auth_router.py
│   └── schemas.py
├── tests/                # 테스트 코드
│   ├── conftest.py
│   └── test_auth.py
├── main.py               # 애플리케이션 진입점
└── requirements.txt      # 의존성 패키지
```

## 기능

### 구현된 API

1. **회원가입** - `POST /api/v2/signup`
   - username, email, password로 회원가입
   - 중복 확인 및 비밀번호 해싱

2. **로그인** - `POST /api/v2/login`
   - username, password로 로그인
   - JWT access_token과 refresh_token 발급

3. **리프레시 토큰 재발급** - `POST /api/v2/reissue`
   - refresh_token으로 새로운 access_token과 refresh_token 발급
   - 기존 refresh_token은 삭제되어 재사용 불가

## 설치 및 실행

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 다음 내용을 설정하세요:

```env
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/gstar_db
JWT_SECRET_KEY=your-secret-key-here-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### 3. 데이터베이스 설정

MariaDB에 데이터베이스를 생성하세요:

```sql
CREATE DATABASE gstar_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. 서버 실행

```bash
python main.py
```

서버는 `http://localhost:8000`에서 실행됩니다.

## API 문서

서버 실행 후 다음 URL에서 Swagger UI를 통해 API 문서를 확인할 수 있습니다:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 테스트

### 전체 테스트 실행

```bash
pytest tests/test_auth.py -v
```

### 테스트 커버리지

- 회원가입 성공
- 중복 username/email 검증
- 잘못된 이메일 형식 검증
- 로그인 성공
- 잘못된 비밀번호 검증
- 존재하지 않는 사용자 검증
- 리프레시 토큰 재발급 성공
- 잘못된 토큰 검증
- 액세스 토큰으로 재발급 시도 검증

## 보안

- 비밀번호는 bcrypt로 해싱되어 저장됩니다
- JWT 토큰 기반 인증 사용
- Access Token과 Refresh Token 분리
- Refresh Token은 DB에 저장되어 관리됩니다
- 사용된 Refresh Token은 재사용이 불가능합니다

## 기술 스택

- **Framework**: FastAPI
- **Database**: MariaDB (SQLAlchemy ORM)
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt (passlib)
- **Testing**: pytest
- **Python Version**: 3.6+
