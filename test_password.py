#!/usr/bin/env python3
"""
비밀번호 해싱 및 검증 테스트 스크립트
"""
import sys
from core.security import get_password_hash, verify_password


def test_short_password():
    """짧은 비밀번호 테스트"""
    print("=" * 50)
    print("Test 1: 짧은 비밀번호")
    password = "test1234"
    print(f"원본 비밀번호: {password}")
    print(f"비밀번호 길이: {len(password.encode('utf-8'))} bytes")

    try:
        hashed = get_password_hash(password)
        print(f"해시 성공: {hashed[:50]}...")

        # 검증
        is_valid = verify_password(password, hashed)
        print(f"검증 결과: {is_valid}")

        # 잘못된 비밀번호 검증
        is_invalid = verify_password("wrong_password", hashed)
        print(f"잘못된 비밀번호 검증: {is_invalid}")

        assert is_valid == True, "올바른 비밀번호 검증 실패"
        assert is_invalid == False, "잘못된 비밀번호가 통과됨"
        print("✅ Test 1 통과")
        return True
    except Exception as e:
        print(f"❌ Test 1 실패: {e}")
        return False


def test_long_password():
    """긴 비밀번호 테스트 (72바이트 초과)"""
    print("\n" + "=" * 50)
    print("Test 2: 긴 비밀번호 (72바이트 초과)")
    password = "a" * 100  # 100자
    print(f"비밀번호 길이: {len(password.encode('utf-8'))} bytes")

    try:
        hashed = get_password_hash(password)
        print(f"해시 성공: {hashed[:50]}...")

        # 검증
        is_valid = verify_password(password, hashed)
        print(f"검증 결과: {is_valid}")

        assert is_valid == True, "긴 비밀번호 검증 실패"
        print("✅ Test 2 통과")
        return True
    except Exception as e:
        print(f"❌ Test 2 실패: {e}")
        return False


def test_korean_password():
    """한글 포함 비밀번호 테스트"""
    print("\n" + "=" * 50)
    print("Test 3: 한글 포함 비밀번호")
    password = "테스트비밀번호1234!@#$"
    print(f"원본 비밀번호: {password}")
    print(f"비밀번호 길이: {len(password.encode('utf-8'))} bytes")

    try:
        hashed = get_password_hash(password)
        print(f"해시 성공: {hashed[:50]}...")

        # 검증
        is_valid = verify_password(password, hashed)
        print(f"검증 결과: {is_valid}")

        assert is_valid == True, "한글 비밀번호 검증 실패"
        print("✅ Test 3 통과")
        return True
    except Exception as e:
        print(f"❌ Test 3 실패: {e}")
        return False


def test_very_long_korean_password():
    """매우 긴 한글 비밀번호 테스트"""
    print("\n" + "=" * 50)
    print("Test 4: 매우 긴 한글 비밀번호")
    password = "안녕하세요반갑습니다" * 10  # 한글은 UTF-8에서 3바이트
    print(f"비밀번호 길이: {len(password.encode('utf-8'))} bytes")

    try:
        hashed = get_password_hash(password)
        print(f"해시 성공: {hashed[:50]}...")

        # 검증
        is_valid = verify_password(password, hashed)
        print(f"검증 결과: {is_valid}")

        assert is_valid == True, "매우 긴 한글 비밀번호 검증 실패"
        print("✅ Test 4 통과")
        return True
    except Exception as e:
        print(f"❌ Test 4 실패: {e}")
        return False


def test_special_characters():
    """특수문자 포함 비밀번호 테스트"""
    print("\n" + "=" * 50)
    print("Test 5: 특수문자 포함 비밀번호")
    password = "P@ssw0rd!#$%^&*()_+-=[]{}|;:',.<>?/~`"
    print(f"원본 비밀번호: {password}")
    print(f"비밀번호 길이: {len(password.encode('utf-8'))} bytes")

    try:
        hashed = get_password_hash(password)
        print(f"해시 성공: {hashed[:50]}...")

        # 검증
        is_valid = verify_password(password, hashed)
        print(f"검증 결과: {is_valid}")

        assert is_valid == True, "특수문자 비밀번호 검증 실패"
        print("✅ Test 5 통과")
        return True
    except Exception as e:
        print(f"❌ Test 5 실패: {e}")
        return False


def main():
    print("비밀번호 해싱 및 검증 테스트 시작\n")

    results = []
    results.append(test_short_password())
    results.append(test_long_password())
    results.append(test_korean_password())
    results.append(test_very_long_korean_password())
    results.append(test_special_characters())

    print("\n" + "=" * 50)
    print(f"전체 테스트 결과: {sum(results)}/{len(results)} 통과")

    if all(results):
        print("✅ 모든 테스트 통과!")
        return 0
    else:
        print("❌ 일부 테스트 실패")
        return 1


if __name__ == "__main__":
    sys.exit(main())
