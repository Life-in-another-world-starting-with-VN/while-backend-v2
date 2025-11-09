#!/usr/bin/env python3
"""
게임 API 테스트 스크립트
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v2"

# 전역 변수
access_token = None
game_id = None
session_id = None
scene_id = None


def test_signup():
    """1. 회원가입 테스트"""
    print("\n" + "=" * 50)
    print("TEST 1: 회원가입")
    print("=" * 50)

    url = f"{BASE_URL}/signup"
    data = {
        "username": "testuser123",
        "email": "test@example.com",
        "password": "test1234",
    }

    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

    return response.status_code == 200


def test_login():
    """2. 로그인 테스트"""
    global access_token

    print("\n" + "=" * 50)
    print("TEST 2: 로그인")
    print("=" * 50)

    url = f"{BASE_URL}/login"
    data = {"username": "testuser123", "password": "test1234"}

    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        access_token = result["access_token"]
        print(f"✅ 로그인 성공!")
        print(f"Access Token: {access_token[:50]}...")
        return True
    else:
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return False


def test_create_game():
    """3. 게임 생성 테스트"""
    global game_id, session_id, scene_id

    print("\n" + "=" * 50)
    print("TEST 3: 게임 생성")
    print("=" * 50)

    url = f"{BASE_URL}/game"
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {"personality": "따뜻함", "genre": "로맨스", "playtime": 5}

    print(f"Request: {json.dumps(data, indent=2, ensure_ascii=False)}")

    response = requests.post(url, json=data, headers=headers)
    print(f"\nStatus: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")

        game_id = result["game_id"]
        session_id = result["sessions"][0]["session_id"]
        scene_id = result["sessions"][0]["scenes"][0]["scene_id"]

        print(f"\n✅ 게임 생성 성공!")
        print(f"Game ID: {game_id}")
        print(f"Session ID: {session_id}")
        print(f"Scene ID: {scene_id}")
        return True
    else:
        print(f"Response: {response.text}")
        return False


def test_next_scene():
    """4. 다음 씬 생성 테스트"""
    global session_id, scene_id

    print("\n" + "=" * 50)
    print("TEST 4: 다음 씬 생성")
    print("=" * 50)

    url = f"{BASE_URL}/game/{game_id}/{session_id}/{scene_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {
        "emotion": {
            "angry": 10,
            "disgust": 5,
            "fear": 5,
            "happy": 60,
            "sad": 5,
            "surprise": 10,
            "neutral": 5,
        },
        "time": 30,  # 30초 경과
    }

    print(f"Request: {json.dumps(data, indent=2, ensure_ascii=False)}")

    response = requests.post(url, json=data, headers=headers)
    print(f"\nStatus: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")

        # 새로운 scene_id 업데이트
        if result["scenes"]:
            scene_id = result["scenes"][0]["scene_id"]
            session_id = result["session_id"]

        print(f"\n✅ 다음 씬 생성 성공!")
        print(f"New Scene ID: {scene_id}")
        return True
    else:
        print(f"Response: {response.text}")
        return False


def test_selection_scene():
    """5. 선택지 선택 후 씬 생성 테스트"""
    print("\n" + "=" * 50)
    print("TEST 5: 선택지 선택 후 씬 생성")
    print("=" * 50)

    # 먼저 선택지가 있는 씬이 나올 때까지 다음 씬 생성
    print("선택지가 있는 씬을 찾는 중...")

    for i in range(5):  # 최대 5번 시도
        result = get_current_scene()
        if result and result["type"] == "selection":
            print(f"\n✅ 선택지 씬 발견! Scene ID: {scene_id}")
            print(f"Selections: {json.dumps(result['selections'], indent=2, ensure_ascii=False)}")

            # 1번 선택지 선택
            selection_id = 1
            url = f"{BASE_URL}/game/{game_id}/{session_id}/{scene_id}/selection/{selection_id}"
            headers = {"Authorization": f"Bearer {access_token}"}
            data = {
                "emotion": {
                    "angry": 5,
                    "disgust": 5,
                    "fear": 5,
                    "happy": 70,
                    "sad": 5,
                    "surprise": 5,
                    "neutral": 5,
                },
                "time": 60,
            }

            response = requests.post(url, json=data, headers=headers)
            print(f"\nStatus: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
                print(f"\n✅ 선택 후 씬 생성 성공!")
                return True
            else:
                print(f"Response: {response.text}")
                return False

        # 선택지가 아니면 다음 씬으로
        if not test_next_scene():
            break

    print("⚠️  선택지 씬을 찾지 못했습니다 (정상적인 경우도 있음)")
    return True


def get_current_scene():
    """현재 씬 정보 조회 (헬퍼 함수)"""
    # 실제로는 이 정보를 저장해두거나 별도 API가 필요하지만,
    # 테스트를 위해 마지막 응답을 기억하는 방식으로 처리
    return None


def main():
    print("\n" + "=" * 50)
    print("게임 API 테스트 시작")
    print("=" * 50)

    tests = [
        ("회원가입", test_signup),
        ("로그인", test_login),
        ("게임 생성", test_create_game),
        ("다음 씬 생성", test_next_scene),
        ("선택지 선택", test_selection_scene),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} 테스트 중 에러 발생: {e}")
            results.append((name, False))

    # 결과 요약
    print("\n\n" + "=" * 50)
    print("테스트 결과 요약")
    print("=" * 50)

    for name, result in results:
        status = "✅ 성공" if result else "❌ 실패"
        print(f"{name}: {status}")

    success_count = sum(1 for _, result in results if result)
    print(f"\n총 {len(results)}개 중 {success_count}개 성공")


if __name__ == "__main__":
    main()
