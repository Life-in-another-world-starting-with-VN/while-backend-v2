# 캐릭터 일관성 업데이트

## 개요
게임 생성 시 선택된 캐릭터가 게임 전체에서 일관되게 사용되도록 시스템을 개선했습니다.

## 주요 변경사항

### 1. 데이터베이스 스키마 변경

#### Game 테이블
- **새 컬럼 추가**: `main_character_id` (INT, NOT NULL)
- **Foreign Key**: `characters(id)` 참조
- **목적**: 게임마다 메인 캐릭터를 고정

```sql
ALTER TABLE games 
ADD COLUMN main_character_id INT NOT NULL DEFAULT 1;

ALTER TABLE games 
ADD CONSTRAINT fk_games_main_character 
FOREIGN KEY (main_character_id) REFERENCES characters(id);
```

### 2. LLM 프롬프트 개선

#### 게임 생성 시 (`generate_game_structure`)
- LLM이 사용자가 원하는 성격과 가장 잘 맞는 캐릭터 1명을 선택
- 선택된 캐릭터 ID를 응답에 포함 (`main_character_id`)
- 첫 씬부터 메인 캐릭터가 등장

#### 씬 생성 시 (`generate_next_scene`, `generate_scene_after_selection`)
- **메인 캐릭터 고정 규칙 추가**:
  - 캐릭터가 등장하는 씬에서는 반드시 메인 캐릭터만 사용
  - 다른 캐릭터는 절대 등장시키지 않음
  - narrator는 사용 가능하지만, 캐릭터 대사는 항상 메인 캐릭터만

### 3. API 응답 개선

#### CreateGameResponse
새로운 필드 추가:
```json
{
  "game_id": 1,
  "title": "게임 제목",
  "personality": "성격",
  "genre": "장르",
  "playtime": 30,
  "main_character_id": 2,        // 새로 추가
  "main_character_name": "캐릭터명",  // 새로 추가
  "sessions": [...]
}
```

#### 씬 응답
- `character_filename` 필드가 항상 포함됨
- 형식: `"{character_id}.png"` 또는 `"{character_id}_{emotion}.png"`
- 예시: `"2.png"`, `"2_smile.png"`

### 4. 코드 변경

#### `domain/entity/game.py`
```python
class Game(Base):
    # ...
    main_character_id = Column(Integer, ForeignKey("characters.id"), nullable=False)
```

#### `domain/repository/game_repository.py`
```python
def create_game(
    self,
    user_id: int,
    title: str,
    personality: str,
    genre: str,
    playtime: int,
    main_character_id: int,  # 새 파라미터
) -> Game:
```

#### `application/game_service.py`
- 게임 생성 시 LLM이 선택한 메인 캐릭터 ID 저장
- 씬 생성 시 메인 캐릭터 ID를 LLM에 전달
- 응답에 메인 캐릭터 정보 포함

#### `application/llm_service.py`
- `generate_next_scene`에 `main_character_id` 파라미터 추가
- `generate_scene_after_selection`에 `main_character_id` 파라미터 추가
- 프롬프트에 메인 캐릭터 고정 규칙 추가

## 마이그레이션

### 실행 방법
```bash
python scripts/add_main_character_to_games.py
```

### 마이그레이션 내용
1. `games` 테이블에 `main_character_id` 컬럼 추가
2. Foreign Key 제약조건 추가
3. 기존 게임 데이터는 자동으로 첫 번째 캐릭터(ID=1)로 설정

## 동작 방식

### 게임 생성 플로우
1. 사용자가 원하는 성격, 장르, 플레이타임 입력
2. LLM이 모든 캐릭터 중 가장 적합한 캐릭터 1명 선택
3. 선택된 캐릭터를 게임의 메인 캐릭터로 저장
4. 첫 씬부터 메인 캐릭터가 등장

### 씬 생성 플로우
1. 게임의 `main_character_id`를 LLM에 전달
2. LLM은 해당 캐릭터만 사용하여 씬 생성
3. 응답에 `character_filename` 포함 (예: "2_smile.png")
4. 클라이언트는 파일명으로 캐릭터 이미지 표시

## 이점

1. **일관성**: 게임 전체에서 동일한 캐릭터가 등장
2. **명확성**: 캐릭터 파일명이 항상 포함되어 클라이언트 구현 간소화
3. **확장성**: 향후 멀티 캐릭터 지원 시 쉽게 확장 가능
4. **데이터 무결성**: Foreign Key로 데이터 일관성 보장

## 테스트 방법

### 1. 게임 생성 테스트
```bash
POST /api/game/create
{
  "personality": "밝고 활발한",
  "genre": "학원물",
  "playtime": 30
}
```

응답에서 `main_character_id`와 `main_character_name` 확인

### 2. 씬 생성 테스트
```bash
POST /api/game/{game_id}/session/{session_id}/scene/{scene_id}/next
{
  "emotion": {...},
  "time": 60
}
```

응답의 모든 씬에서 `character_filename`이 동일한 캐릭터 ID 사용 확인

## 주의사항

- 기존 게임 데이터는 자동으로 캐릭터 ID=1로 설정됨
- 새로 생성되는 게임부터 LLM이 자동으로 적합한 캐릭터 선택
- 캐릭터 이미지 파일은 `static/characters/` 디렉토리에 위치해야 함
