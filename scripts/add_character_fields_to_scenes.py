#!/usr/bin/env python3
"""
Scene 테이블에 character_id와 emotion 컬럼 추가
"""
from core.database import SessionLocal, engine
from sqlalchemy import text


def add_character_fields():
    """Scene 테이블에 character_id와 emotion 컬럼 추가"""
    
    with engine.connect() as conn:
        try:
            # character_id 컬럼 추가
            conn.execute(text("""
                ALTER TABLE scenes 
                ADD COLUMN character_id INTEGER NULL
            """))
            print("✅ character_id 컬럼 추가 완료")
        except Exception as e:
            if "Duplicate column name" in str(e) or "duplicate column" in str(e):
                print("⚠️  character_id 컬럼이 이미 존재합니다")
            else:
                print(f"❌ character_id 컬럼 추가 실패: {e}")
        
        try:
            # emotion 컬럼 추가
            conn.execute(text("""
                ALTER TABLE scenes 
                ADD COLUMN emotion VARCHAR(20) NULL
            """))
            print("✅ emotion 컬럼 추가 완료")
        except Exception as e:
            if "Duplicate column name" in str(e) or "duplicate column" in str(e):
                print("⚠️  emotion 컬럼이 이미 존재합니다")
            else:
                print(f"❌ emotion 컬럼 추가 실패: {e}")
        
        conn.commit()
        print("\n✅ 마이그레이션 완료!")


if __name__ == "__main__":
    add_character_fields()
