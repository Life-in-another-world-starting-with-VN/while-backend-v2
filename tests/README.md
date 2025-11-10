# API 테스트 문서

## 개요
모든 API 엔드포인트에 대한 자동화된 pytest 테스트가 구현되어 있습니다.

## 테스트 실행 방법

### 전체 테스트 실행
```bash
pytest tests/ -v
```

### 특정 테스트 파일 실행
```bash
# 인증 API 테스트
pytest tests/test_auth.py -v

# 게임 API 테스트
pytest tests/test_game_endpoints.py -v
```

### 특정 테스트 클래스 실행
```bash
pytest tests/test_auth.py::TestSignup -v
pytest tests/test_game_endpoints.py::TestCreateGame -v
```

## 테스트 커버리지

### 1. 인증 API (`test_auth.py`)

#### 회원가입 (POST `/api/v2/signup`)
- ✅ `test_signup_success` - 정상 회원가입
- ✅ `test_signup_duplicate_username` - 중복 username 처리
- ✅ `test_signup_duplicate_email` - 중복 email 처리
- ✅ `test_signup_invalid_email` - 잘못된 email 형식

#### 로그인 (POST `/api/v2/login`)
- ✅ `test_login_success` - 정상 로그인
- ✅ `test_login_wrong_password` - 잘못된 비밀번호
- ✅ `test_login_nonexistent_user` - 존재하지 않는 사용자

#### 토큰 재발급 (POST `/api/v2/reissue`)
- ✅ `test_reissue_success` - 정상 토큰 재발급
- ✅ `test_reissue_invalid_token` - 잘못된 토큰
- ✅ `test_reissue_with_access_token` - 액세스 토큰으로 재발급 시도

### 2. 게임 API (`test_game_endpoints.py`)

#### 게임 생성 (POST `/api/v2/game`)
- ✅ `test_create_game_success` - 정상 게임 생성
- ✅ `test_create_game_without_auth` - 인증 없이 생성 시도
- ✅ `test_create_game_invalid_playtime` - 잘못된 playtime 값
- ✅ `test_create_game_missing_fields` - 필수 필드 누락

#### 다음 씬 생성 (POST `/api/v2/game/{game_id}/{session_id}/{scene_id}`)
- ✅ `test_next_scene_success` - 정상 다음 씬 생성
- ✅ `test_next_scene_without_auth` - 인증 없이 생성 시도
- ✅ `test_next_scene_invalid_emotion_values` - 잘못된 감정 값
- ✅ `test_next_scene_negative_time` - 음수 시간 값
- ✅ `test_next_scene_invalid_game_id` - 존재하지 않는 game_id

#### 선택지 선택 후 씬 생성 (POST `/api/v2/game/{game_id}/{session_id}/{scene_id}/selection/{selection_id}`)
- ✅ `test_selection_scene_success` - 정상 선택지 선택
- ✅ `test_selection_scene_without_auth` - 인증 없이 선택 시도
- ✅ `test_selection_scene_invalid_selection_id` - 잘못된 선택지 ID

## 테스트 결과

```
총 22개 테스트 - 모두 통과 ✅

인증 API: 10개 테스트
게임 API: 12개 테스트
```

## 테스트 환경 설정

### Fixtures (`conftest.py`)

#### `db_session`
- 각 테스트마다 독립적인 데이터베이스 세션 제공
- 테스트 시작 시 테이블 생성 및 캐릭터 데이터 삽입
- 테스트 종료 시 테이블 삭제

#### `client`
- FastAPI TestClient 제공
- 데이터베이스 의존성 오버라이드

#### `authenticated_client` (`test_game_endpoints.py`)
- 회원가입 및 로그인이 완료된 클라이언트
- 인증이 필요한 게임 API 테스트에 사용

#### `game_context` (`test_game_endpoints.py`)
- 게임 생성 후 game_id, session_id, scene_id 제공
- 다음 씬 생성 테스트에 사용

#### `game_with_selection` (`test_game_endpoints.py`)
- 선택지가 있는 씬을 찾거나 생성
- 선택지 선택 테스트에 사용

## 주의사항

1. **캐릭터 데이터**: 테스트 실행 시 자동으로 3명의 캐릭터가 생성됩니다.
2. **API 호출**: 실제 Gemini API를 호출하므로 테스트 실행 시간이 다소 소요됩니다.
3. **환경 변수**: `.env` 파일에 필요한 API 키가 설정되어 있어야 합니다.

## 추가 테스트

### 이미지 생성 통합 테스트 (`test_full_integration.py`)
- Google AI 이미지 생성 기능 전체 플로우 테스트
- 스토리 → 키워드 → 이미지 생성 → 파일 저장 → URL 반환

### 기타 테스트
- `test_aspect_ratio.py` - 이미지 비율 검증
- `test_password.py` - 비밀번호 해싱 검증
- `test_gemini_flash_image.py` - Gemini 이미지 생성 API 테스트
