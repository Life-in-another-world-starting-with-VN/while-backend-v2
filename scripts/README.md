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

## 주의사항

- 스크립트 실행 전 `.env` 파일이 올바르게 설정되어 있는지 확인하세요
- 데이터베이스 연결이 필요한 스크립트는 DB가 실행 중이어야 합니다
