import pytest
from fastapi.testclient import TestClient


class TestSignup:
    def test_signup_success(self, client: TestClient):
        """회원가입 성공 테스트"""
        response = client.post(
            "/api/v2/signup",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "testpassword123"
            }
        )
        assert response.status_code == 200
        assert response.json() == {"message": "회원가입에 성공했습니다."}

    def test_signup_duplicate_username(self, client: TestClient):
        """중복 username으로 회원가입 시도"""
        # 첫 번째 회원가입
        client.post(
            "/api/v2/signup",
            json={
                "username": "testuser",
                "email": "test1@example.com",
                "password": "testpassword123"
            }
        )

        # 동일한 username으로 두 번째 회원가입 시도
        response = client.post(
            "/api/v2/signup",
            json={
                "username": "testuser",
                "email": "test2@example.com",
                "password": "testpassword123"
            }
        )
        assert response.status_code == 400
        assert "Username already registered" in response.json()["detail"]

    def test_signup_duplicate_email(self, client: TestClient):
        """중복 email로 회원가입 시도"""
        # 첫 번째 회원가입
        client.post(
            "/api/v2/signup",
            json={
                "username": "testuser1",
                "email": "test@example.com",
                "password": "testpassword123"
            }
        )

        # 동일한 email로 두 번째 회원가입 시도
        response = client.post(
            "/api/v2/signup",
            json={
                "username": "testuser2",
                "email": "test@example.com",
                "password": "testpassword123"
            }
        )
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]

    def test_signup_invalid_email(self, client: TestClient):
        """잘못된 이메일 형식으로 회원가입 시도"""
        response = client.post(
            "/api/v2/signup",
            json={
                "username": "testuser",
                "email": "invalid-email",
                "password": "testpassword123"
            }
        )
        assert response.status_code == 422


class TestLogin:
    def test_login_success(self, client: TestClient):
        """로그인 성공 테스트"""
        # 먼저 회원가입
        client.post(
            "/api/v2/signup",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "testpassword123"
            }
        )

        # 로그인
        response = client.post(
            "/api/v2/login",
            json={
                "username": "testuser",
                "password": "testpassword123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_login_wrong_password(self, client: TestClient):
        """잘못된 비밀번호로 로그인 시도"""
        # 먼저 회원가입
        client.post(
            "/api/v2/signup",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "testpassword123"
            }
        )

        # 잘못된 비밀번호로 로그인
        response = client.post(
            "/api/v2/login",
            json={
                "username": "testuser",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_nonexistent_user(self, client: TestClient):
        """존재하지 않는 사용자로 로그인 시도"""
        response = client.post(
            "/api/v2/login",
            json={
                "username": "nonexistent",
                "password": "testpassword123"
            }
        )
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]


class TestReissue:
    def test_reissue_success(self, client: TestClient):
        """리프레시 토큰 재발급 성공 테스트"""
        # 회원가입
        client.post(
            "/api/v2/signup",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "testpassword123"
            }
        )

        # 로그인
        login_response = client.post(
            "/api/v2/login",
            json={
                "username": "testuser",
                "password": "testpassword123"
            }
        )
        refresh_token = login_response.json()["refresh_token"]

        # 토큰 재발급
        response = client.post(
            "/api/v2/reissue",
            json={
                "refresh_token": refresh_token
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_reissue_invalid_token(self, client: TestClient):
        """잘못된 리프레시 토큰으로 재발급 시도"""
        response = client.post(
            "/api/v2/reissue",
            json={
                "refresh_token": "invalid_token"
            }
        )
        assert response.status_code == 401

    def test_reissue_with_access_token(self, client: TestClient):
        """액세스 토큰으로 재발급 시도 (리프레시 토큰 타입이 아님)"""
        # 회원가입
        client.post(
            "/api/v2/signup",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "testpassword123"
            }
        )

        # 로그인
        login_response = client.post(
            "/api/v2/login",
            json={
                "username": "testuser",
                "password": "testpassword123"
            }
        )
        access_token = login_response.json()["access_token"]

        # 액세스 토큰으로 재발급 시도
        response = client.post(
            "/api/v2/reissue",
            json={
                "refresh_token": access_token
            }
        )
        assert response.status_code == 401
        assert "Invalid token type" in response.json()["detail"]

