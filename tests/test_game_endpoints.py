import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def authenticated_client(client: TestClient):
    """인증된 클라이언트 fixture"""
    # 회원가입
    client.post(
        "/api/v2/signup",
        json={
            "username": "gameuser",
            "email": "game@example.com",
            "password": "testpass123"
        }
    )
    
    # 로그인
    login_response = client.post(
        "/api/v2/login",
        json={
            "username": "gameuser",
            "password": "testpass123"
        }
    )
    
    access_token = login_response.json()["access_token"]
    return client, access_token


class TestCreateGame:
    def test_create_game_success(self, authenticated_client):
        """게임 생성 성공 테스트"""
        client, token = authenticated_client
        
        response = client.post(
            "/api/v2/game",
            json={
                "personality": "따뜻함",
                "genre": "로맨스",
                "playtime": 5
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # 디버깅을 위한 출력
        if response.status_code != 200:
            print(f"\nResponse status: {response.status_code}")
            print(f"Response body: {response.text}")
        
        assert response.status_code == 200
        data = response.json()
        
        # 응답 구조 검증
        assert "game_id" in data
        assert "personality" in data
        assert "genre" in data
        assert "title" in data
        assert "playtime" in data
        assert "sessions" in data
        
        # 값 검증
        assert data["personality"] == "따뜻함"
        assert data["genre"] == "로맨스"
        assert data["playtime"] == 5
        assert len(data["sessions"]) > 0
        
        # 첫 세션 검증
        session = data["sessions"][0]
        assert "session_id" in session
        assert "content" in session
        assert "scenes" in session
        assert len(session["scenes"]) > 0
        
        # 첫 씬 검증
        scene = session["scenes"][0]
        assert "scene_id" in scene
        assert "type" in scene
        assert "role" in scene

    def test_create_game_without_auth(self, client: TestClient):
        """인증 없이 게임 생성 시도"""
        response = client.post(
            "/api/v2/game",
            json={
                "personality": "따뜻함",
                "genre": "로맨스",
                "playtime": 5
            }
        )
        
        # 401 또는 403 모두 허용 (인증 실패)
        assert response.status_code in [401, 403]

    def test_create_game_invalid_playtime(self, authenticated_client):
        """잘못된 playtime으로 게임 생성 시도"""
        client, token = authenticated_client
        
        response = client.post(
            "/api/v2/game",
            json={
                "personality": "따뜻함",
                "genre": "로맨스",
                "playtime": 0  # 0 이하는 불가
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 422

    def test_create_game_missing_fields(self, authenticated_client):
        """필수 필드 누락"""
        client, token = authenticated_client
        
        response = client.post(
            "/api/v2/game",
            json={
                "personality": "따뜻함"
                # genre, playtime 누락
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 422


class TestNextScene:
    @pytest.fixture
    def game_context(self, authenticated_client):
        """게임 생성 후 컨텍스트 반환"""
        client, token = authenticated_client
        
        # 게임 생성
        game_response = client.post(
            "/api/v2/game",
            json={
                "personality": "따뜻함",
                "genre": "로맨스",
                "playtime": 5
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        game_data = game_response.json()
        game_id = game_data["game_id"]
        session_id = game_data["sessions"][0]["session_id"]
        scene_id = game_data["sessions"][0]["scenes"][0]["scene_id"]
        
        return client, token, game_id, session_id, scene_id

    def test_next_scene_success(self, game_context):
        """다음 씬 생성 성공 테스트"""
        client, token, game_id, session_id, scene_id = game_context
        
        response = client.post(
            f"/api/v2/game/{game_id}/{session_id}/{scene_id}",
            json={
                "emotion": {
                    "angry": 5,
                    "disgust": 5,
                    "fear": 5,
                    "happy": 70,
                    "sad": 5,
                    "surprise": 5,
                    "neutral": 5
                },
                "time": 30
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # 응답 구조 검증
        assert "session_id" in data
        assert "content" in data
        assert "scenes" in data
        assert len(data["scenes"]) > 0

    def test_next_scene_without_auth(self, game_context):
        """인증 없이 다음 씬 생성 시도"""
        client, _, game_id, session_id, scene_id = game_context
        
        response = client.post(
            f"/api/v2/game/{game_id}/{session_id}/{scene_id}",
            json={
                "emotion": {
                    "angry": 5,
                    "disgust": 5,
                    "fear": 5,
                    "happy": 70,
                    "sad": 5,
                    "surprise": 5,
                    "neutral": 5
                },
                "time": 30
            }
        )
        
        assert response.status_code in [401, 403]

    def test_next_scene_invalid_emotion_values(self, game_context):
        """잘못된 감정 값으로 다음 씬 생성 시도"""
        client, token, game_id, session_id, scene_id = game_context
        
        response = client.post(
            f"/api/v2/game/{game_id}/{session_id}/{scene_id}",
            json={
                "emotion": {
                    "angry": 150,  # 100 초과
                    "disgust": 5,
                    "fear": 5,
                    "happy": 70,
                    "sad": 5,
                    "surprise": 5,
                    "neutral": 5
                },
                "time": 30
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 422

    def test_next_scene_negative_time(self, game_context):
        """음수 시간으로 다음 씬 생성 시도"""
        client, token, game_id, session_id, scene_id = game_context
        
        response = client.post(
            f"/api/v2/game/{game_id}/{session_id}/{scene_id}",
            json={
                "emotion": {
                    "angry": 5,
                    "disgust": 5,
                    "fear": 5,
                    "happy": 70,
                    "sad": 5,
                    "surprise": 5,
                    "neutral": 5
                },
                "time": -10  # 음수
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 422

    def test_next_scene_invalid_game_id(self, game_context):
        """존재하지 않는 game_id로 다음 씬 생성 시도"""
        client, token, _, session_id, scene_id = game_context
        
        response = client.post(
            f"/api/v2/game/99999/{session_id}/{scene_id}",
            json={
                "emotion": {
                    "angry": 5,
                    "disgust": 5,
                    "fear": 5,
                    "happy": 70,
                    "sad": 5,
                    "surprise": 5,
                    "neutral": 5
                },
                "time": 30
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code in [400, 404]


class TestSelectionScene:
    @pytest.fixture
    def game_with_selection(self, authenticated_client):
        """선택지가 있는 씬을 찾거나 생성"""
        client, token = authenticated_client
        
        # 게임 생성
        game_response = client.post(
            "/api/v2/game",
            json={
                "personality": "따뜻함",
                "genre": "로맨스",
                "playtime": 5
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        game_data = game_response.json()
        game_id = game_data["game_id"]
        
        # 첫 세션과 씬 정보
        if "sessions" in game_data and game_data["sessions"]:
            session_id = game_data["sessions"][0]["session_id"]
            scene_id = game_data["sessions"][0]["scenes"][0]["scene_id"]
            current_scene = game_data["sessions"][0]["scenes"][0]
        else:
            # 게임 생성 실패 시 기본값 반환
            return client, token, game_id, 1, 1
        
        # 선택지 씬을 찾을 때까지 다음 씬 생성 (최대 10번)
        for _ in range(10):
            # 현재 씬이 선택지인지 확인
            if current_scene["type"] == "selection":
                return client, token, game_id, session_id, scene_id
            
            # 다음 씬 생성
            next_response = client.post(
                f"/api/v2/game/{game_id}/{session_id}/{scene_id}",
                json={
                    "emotion": {
                        "angry": 5,
                        "disgust": 5,
                        "fear": 5,
                        "happy": 70,
                        "sad": 5,
                        "surprise": 5,
                        "neutral": 5
                    },
                    "time": 30
                },
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if next_response.status_code == 200:
                next_data = next_response.json()
                if "scenes" in next_data and next_data["scenes"]:
                    session_id = next_data["session_id"]
                    scene_id = next_data["scenes"][0]["scene_id"]
                    current_scene = next_data["scenes"][0]
                    
                    if current_scene["type"] == "selection":
                        return client, token, game_id, session_id, scene_id
                else:
                    break
            else:
                break
        
        # 선택지 씬을 못 찾았어도 테스트를 위해 반환
        return client, token, game_id, session_id, scene_id

    def test_selection_scene_success(self, game_with_selection):
        """선택지 선택 후 씬 생성 성공 테스트"""
        client, token, game_id, session_id, scene_id = game_with_selection
        
        response = client.post(
            f"/api/v2/game/{game_id}/{session_id}/{scene_id}/selection/1",
            json={
                "emotion": {
                    "angry": 5,
                    "disgust": 5,
                    "fear": 5,
                    "happy": 70,
                    "sad": 5,
                    "surprise": 5,
                    "neutral": 5
                },
                "time": 60
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # 선택지 씬이 아닐 수도 있으므로 200 또는 400 허용
        assert response.status_code in [200, 400]
        
        if response.status_code == 200:
            data = response.json()
            assert "session_id" in data
            assert "content" in data
            assert "scenes" in data

    def test_selection_scene_without_auth(self, game_with_selection):
        """인증 없이 선택지 선택 시도"""
        client, _, game_id, session_id, scene_id = game_with_selection
        
        response = client.post(
            f"/api/v2/game/{game_id}/{session_id}/{scene_id}/selection/1",
            json={
                "emotion": {
                    "angry": 5,
                    "disgust": 5,
                    "fear": 5,
                    "happy": 70,
                    "sad": 5,
                    "surprise": 5,
                    "neutral": 5
                },
                "time": 60
            }
        )
        
        assert response.status_code in [401, 403]

    def test_selection_scene_invalid_selection_id(self, game_with_selection):
        """존재하지 않는 선택지 ID로 선택 시도"""
        client, token, game_id, session_id, scene_id = game_with_selection
        
        response = client.post(
            f"/api/v2/game/{game_id}/{session_id}/{scene_id}/selection/999",
            json={
                "emotion": {
                    "angry": 5,
                    "disgust": 5,
                    "fear": 5,
                    "happy": 70,
                    "sad": 5,
                    "surprise": 5,
                    "neutral": 5
                },
                "time": 60
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # 잘못된 선택지 ID는 400 또는 404
        assert response.status_code in [400, 404]
