#!/usr/bin/env python3
"""
캐릭터 데이터 삽입 스크립트
"""
from core.database import SessionLocal
from domain.entity.game import Character


def insert_characters():
    db = SessionLocal()

    try:
        # 이미 캐릭터가 있는지 확인
        existing_count = db.query(Character).count()
        if existing_count > 0:
            print(f"이미 {existing_count}명의 캐릭터가 있습니다.")
            response = input("기존 캐릭터를 삭제하고 다시 생성하시겠습니까? (y/n): ")
            if response.lower() != 'y':
                print("취소되었습니다.")
                return

            db.query(Character).delete()
            db.commit()
            print("기존 캐릭터를 삭제했습니다.")

        # 3명의 캐릭터 생성
        characters = [
            Character(
                name="아리아나",
                personality="밝고 활발한 성격. 항상 긍정적이고 주변 사람들을 웃게 만드는 것을 좋아한다. 친구들에게 인기가 많으며 모든 일에 적극적으로 참여한다."
            ),
            Character(
                name="유나",
                personality="조용하고 차분한 성격. 책을 좋아하며 깊이 있는 대화를 선호한다. 겉으로는 냉정해 보이지만 속마음은 따뜻하고 세심하다."
            ),
            Character(
                name="소라",
                personality="도도하지만 따뜻한 성격. 처음엔 차갑게 대하지만 친해지면 누구보다 다정하다. 완벽주의자이며 자존심이 강하다."
            ),
        ]

        for char in characters:
            db.add(char)

        db.commit()

        print("\n✅ 캐릭터 데이터 삽입 완료!")
        print("\n생성된 캐릭터:")
        for char in characters:
            db.refresh(char)
            print(f"  - ID: {char.id}, 이름: {char.name}")
            print(f"    성격: {char.personality[:50]}...")
            print()

    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    insert_characters()