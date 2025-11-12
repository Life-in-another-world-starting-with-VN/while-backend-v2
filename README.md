# GSTAR API v2

FastAPI와 MariaDB를 사용한 텍스트 기반 게임 API 서버

## 프로젝트 구조

```
while-backend-v2/
├── application/              # 비즈니스 로직 레이어
│   ├── auth_service.py       # 인증/인가 서비스
│   ├── game_service.py       # 게임 로직 서비스
│   ├── llm_service.py        # Gemini LLM 서비스
│   └── background_generator.py # fal.ai 배경 이미지 생성 서비스
├── core/                     # 핵심 설정 및 유틸리티
│   ├── config.py             # 환경 변수 설정
│   ├── database.py           # DB 연결 설정
│   ├── security.py           # JWT 및 보안 유틸리티
│   └── auth_dependency.py    # 인증 의존성
├── domain/                   # 도메인 레이어
│   ├── entity/               # 데이터베이스 엔티티
│   │   ├── user.py           # 사용자 엔티티
│   │   └── game.py           # 게임 엔티티
│   └── repository/           # 데이터 접근 레이어
│       ├── user_repository.py
│       └── game_repository.py
├── presentation/             # API 엔드포인트 레이어
│   ├── auth_router.py        # 인증 API
│   ├── game_router.py        # 게임 API
│   └── schemas.py            # Request/Response 스키마
├── tests/                    # 테스트 코드
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_game_api.py
│   ├── test_full_integration.py
│   └── test_integration_image_generation.py
├── scripts/                  # 유틸리티 스크립트
│   ├── insert_characters.py  # 캐릭터 데이터 삽입
│   ├── check_models.py       # 모델 확인
│   └── verify_all_images_16_9.py # 이미지 비율 검증
├── docs/                     # 문서
│   ├── API 명세서.html       # API 명세서
│   └── INTEGRATION_TEST_RESULTS.md # 통합 테스트 결과
├── static/                   # 정적 파일
│   └── generated_images/     # 생성된 이미지 저장
├── main.py                   # 애플리케이션 진입점
└── requirements.txt          # 의존성 패키지
```

## 기능

### 구현된 API

#### 1. 인증 API (`/api/v2/auth`)

- **회원가입** - `POST /api/v2/auth/signup`
  - username, email, password로 회원가입
  - 중복 확인 및 비밀번호 해싱

- **로그인** - `POST /api/v2/auth/login`
  - username, password로 로그인
  - JWT access_token과 refresh_token 발급

- **리프레시 토큰 재발급** - `POST /api/v2/auth/reissue`
  - refresh_token으로 새로운 access_token과 refresh_token 발급
  - 기존 refresh_token은 삭제되어 재사용 불가

#### 2. 게임 API (`/api/v2/game`)

- **게임 생성** - `POST /api/v2/game`
  - AI가 캐릭터를 선택하고 스토리 시작
  - Gemini LLM을 활용한 게임 시나리오 생성
  - fal.ai를 활용한 배경 이미지 자동 생성

- **다음 씬 생성** - `POST /api/v2/game/{game_id}/{session_id}/{scene_id}`
  - 사용자의 감정 데이터에 따른 스토리 진행
  - 동적인 선택지 생성
  - 게임 상태 및 진행 내역 저장

- **선택지 선택 후 씬 생성** - `POST /api/v2/game/{game_id}/{session_id}/{scene_id}/selection/{selection_id}`
  - 사용자의 선택에 따른 스토리 분기
  - 선택지 기반 게임 진행

## 설치 및 실행

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 다음 내용을 설정하세요:

```env
# 데이터베이스 설정
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/gstar_db

# JWT 인증 설정
JWT_SECRET_KEY=your-secret-key-here-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Gemini LLM 설정
GEMINI_TOKEN=your-gemini-api-key
GEMINI_MODEL=gemini-2.0-flash

# fal.ai 이미지 생성 설정
FAL_KEY=your-fal-api-key
FAL_URL=https://queue.fal.run/fal-ai/flux-pro/v1.1-ultra
IMAGE_SIZE=16:9
```

#### 환경 변수 설명

**데이터베이스**
- `DATABASE_URL`: MariaDB 연결 URL (형식: `mysql+pymysql://사용자명:비밀번호@호스트:포트/데이터베이스명`)

**JWT 인증**
- `JWT_SECRET_KEY`: JWT 토큰 서명에 사용할 비밀 키 (보안을 위해 복잡한 문자열 사용 권장)
- `JWT_ALGORITHM`: JWT 알고리즘 (기본값: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Access Token 만료 시간 (분)
- `REFRESH_TOKEN_EXPIRE_DAYS`: Refresh Token 만료 시간 (일)

**Gemini LLM**
- `GEMINI_TOKEN`: Google Gemini API 키 (https://ai.google.dev/ 에서 발급)
- `GEMINI_MODEL`: 사용할 Gemini 모델명 (예: gemini-2.0-flash, gemini-pro 등)

**fal.ai 이미지 생성**
- `FAL_KEY`: fal.ai API 키 (https://fal.ai/ 에서 발급)
- `FAL_URL`: fal.ai 이미지 생성 엔드포인트 URL
- `IMAGE_SIZE`: 생성할 이미지 비율 (16:9, 4:3, 1:1 등)

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
# 인증 테스트
pytest tests/test_auth.py -v

# 게임 API 테스트
pytest tests/test_game_api.py -v

# 이미지 생성 통합 테스트
pytest tests/test_integration_image_generation.py -v

# 전체 통합 테스트
pytest tests/test_full_integration.py -v

# 모든 테스트 실행
pytest tests/ -v
```

### 테스트 커버리지

**인증 테스트**
- 회원가입 성공
- 중복 username/email 검증
- 잘못된 이메일 형식 검증
- 로그인 성공
- 잘못된 비밀번호 검증
- 존재하지 않는 사용자 검증
- 리프레시 토큰 재발급 성공
- 잘못된 토큰 검증
- 액세스 토큰으로 재발급 시도 검증

**게임 API 테스트**
- 게임 생성 및 첫 씬 생성
- 다음 씬 생성
- 선택지 선택 후 씬 생성
- 배경 이미지 생성 검증

**통합 테스트**
- 전체 게임 플로우 테스트
- 이미지 생성 및 저장 검증
- 16:9 비율 검증

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
- **LLM**: Google Gemini API
- **Image Generation**: fal.ai (Flux Pro v1.1 Ultra)
- **Testing**: pytest
- **Python Version**: 3.12+

## 주요 특징

- **Clean Architecture**: 계층형 아키텍처로 유지보수성 향상
  - Presentation Layer: API 엔드포인트 및 스키마
  - Application Layer: 비즈니스 로직
  - Domain Layer: 엔티티 및 리포지토리
  - Core Layer: 공통 유틸리티 및 설정

- **AI 통합**:
  - Gemini LLM을 활용한 동적 스토리 생성
  - fal.ai (Flux Pro)를 통한 고품질 배경 이미지 생성
  - 사용자 감정 데이터 기반 실시간 게임 진행

- **보안**:
  - JWT 기반 인증/인가
  - bcrypt 비밀번호 해싱
  - Refresh Token 관리로 보안 강화

## API 키 발급 안내

### Google AI Studio API (Gemini)
1. https://aistudio.google.com/ 접속
2. Google 계정으로 로그인
3. 좌측 메뉴에서 "Get API key" 클릭
4. "Create API key" 버튼 클릭
5. 기존 Google Cloud 프로젝트 선택 또는 새 프로젝트 생성
6. 생성된 API 키 복사
7. `.env` 파일의 `GEMINI_TOKEN`에 설정

**참고사항:**
- API 키는 안전하게 보관하고 공개 저장소에 커밋하지 마세요
- 무료 할당량 및 요금제는 https://ai.google.dev/pricing 에서 확인하세요

### fal.ai API (이미지 생성)
1. https://fal.ai/ 접속
2. 계정 생성 및 로그인
3. Dashboard에서 "API Keys" 메뉴 선택
4. "Create new key" 버튼 클릭
5. 생성된 API 키 복사
6. `.env` 파일의 `FAL_KEY`에 설정

**참고사항:**
- Flux Pro v1.1 Ultra 모델을 사용하여 고품질 16:9 배경 이미지 생성
- 요금제 및 크레딧 정보는 https://fal.ai/pricing 에서 확인하세요
