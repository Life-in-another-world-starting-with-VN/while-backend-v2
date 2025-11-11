"""
게임 테이블에 main_character_id 컬럼 추가 마이그레이션 스크립트
"""
import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from core.database import engine, SessionLocal


def migrate():
    """main_character_id 컬럼 추가"""
    db = SessionLocal()
    
    try:
        # 1. 컬럼이 이미 존재하는지 확인 (MySQL)
        result = db.execute(text("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'games' 
            AND COLUMN_NAME = 'main_character_id'
        """))
        column_exists = result.fetchone()[0] > 0
        
        if column_exists:
            print("✓ main_character_id 컬럼이 이미 존재합니다.")
            return
        
        # 2. 컬럼 추가 (기본값 1로 설정 - 첫 번째 캐릭터)
        print("main_character_id 컬럼 추가 중...")
        db.execute(text("""
            ALTER TABLE games 
            ADD COLUMN main_character_id INT NOT NULL DEFAULT 1
        """))
        
        # 3. Foreign Key 제약조건 추가
        print("Foreign Key 제약조건 추가 중...")
        db.execute(text("""
            ALTER TABLE games 
            ADD CONSTRAINT fk_games_main_character 
            FOREIGN KEY (main_character_id) REFERENCES characters(id)
        """))
        
        db.commit()
        print("✓ main_character_id 컬럼이 성공적으로 추가되었습니다.")
        
        # 4. 기존 게임 데이터 확인
        result = db.execute(text("SELECT COUNT(*) FROM games"))
        game_count = result.fetchone()[0]
        print(f"✓ 기존 게임 {game_count}개에 main_character_id=1이 설정되었습니다.")
        
    except Exception as e:
        print(f"✗ 마이그레이션 실패: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("=== 게임 테이블 마이그레이션 시작 ===")
    migrate()
    print("=== 마이그레이션 완료 ===")
