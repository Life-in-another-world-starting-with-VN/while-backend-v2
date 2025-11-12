# Scripts

프로젝트 유틸리티 스크립트 모음

## 파일 설명

### insert_characters.py
캐릭터 데이터를 데이터베이스에 삽입하는 스크립트

**사용법:**
```bash
python scripts/insert_characters.py
```

### check_models.py
데이터베이스 모델 및 테이블 구조를 확인하는 스크립트

**사용법:**
```bash
python scripts/check_models.py
```

### verify_all_images_16_9.py
생성된 이미지들의 비율이 16:9인지 검증하는 스크립트

**사용법:**
```bash
python scripts/verify_all_images_16_9.py
```

### add_main_character_to_games.py
게임 테이블에 main_character_id 컬럼을 추가하는 마이그레이션 스크립트

**사용법:**
```bash
python scripts/add_main_character_to_games.py
```

**설명:**
- 게임마다 메인 캐릭터를 고정하기 위한 컬럼 추가
- 기존 게임 데이터는 자동으로 첫 번째 캐릭터(ID=1)로 설정됨
- Foreign Key 제약조건 자동 추가

### add_character_fields_to_scenes.py
씬 테이블에 캐릭터 관련 필드를 추가하는 마이그레이션 스크립트

**사용법:**
```bash
python scripts/add_character_fields_to_scenes.py
```

## 주의사항

- 스크립트 실행 전 `.env` 파일이 올바르게 설정되어 있는지 확인하세요
- 데이터베이스 연결이 필요한 스크립트는 DB가 실행 중이어야 합니다
