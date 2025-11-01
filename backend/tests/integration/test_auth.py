"""
Integration tests for authentication API endpoints.

Tests the full authentication flow including:
- User registration
- User login
- Get current user
"""

import pytest
from fastapi import status


class TestRegisterEndpoint:
    """Tests for POST /api/v1/auth/register endpoint."""

    def test_register_success(self, client):
        """Test successful user registration."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "securepassword123",
                "full_name": "New User"
            }
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0

    def test_register_duplicate_email(self, client, test_user):
        """Test registration with duplicate email fails."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": test_user.email,  # Duplicate email
                "password": "password123",
                "full_name": "Duplicate User"
            }
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response.json()["detail"].lower()

    def test_register_invalid_email(self, client):
        """Test registration with invalid email format."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "not-an-email",  # Invalid email
                "password": "password123",
                "full_name": "Test User"
            }
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_missing_password(self, client):
        """Test registration without password fails."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                # Missing password
                "full_name": "Test User"
            }
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_without_full_name(self, client):
        """Test registration without full_name (optional field)."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "minimal@example.com",
                "password": "password123",
                # full_name is optional
            }
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "access_token" in data


class TestLoginEndpoint:
    """Tests for POST /api/v1/auth/login endpoint."""

    def test_login_success(self, client, test_user, test_user_password):
        """Test successful login with correct credentials."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,  # OAuth2 uses 'username' field
                "password": test_user_password
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0

    def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password fails."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                "password": "wrongpassword"
            }
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "incorrect" in response.json()["detail"].lower()

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent email fails."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "password123"
            }
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_inactive_user(self, client, test_user, test_user_password, db):
        """Test login with inactive user fails."""
        # Deactivate user
        test_user.is_active = False
        db.commit()

        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                "password": test_user_password
            }
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_missing_username(self, client):
        """Test login without username fails."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                # Missing username
                "password": "password123"
            }
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_login_missing_password(self, client, test_user):
        """Test login without password fails."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                # Missing password
            }
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestGetMeEndpoint:
    """Tests for GET /api/v1/auth/me endpoint."""

    def test_get_me_success(self, client, auth_headers, test_user):
        """Test getting current user information."""
        response = client.get(
            "/api/v1/auth/me",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email
        assert data["full_name"] == test_user.full_name
        assert data["is_active"] == test_user.is_active
        assert "created_at" in data
        assert "updated_at" in data
        # Should NOT include hashed_password
        assert "hashed_password" not in data
        assert "password" not in data

    def test_get_me_without_token(self, client):
        """Test getting current user without token fails."""
        response = client.get("/api/v1/auth/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_me_invalid_token(self, client):
        """Test getting current user with invalid token fails."""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_me_malformed_token(self, client):
        """Test getting current user with malformed Authorization header."""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "NotBearer token"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestAuthenticationFlow:
    """Integration tests for complete authentication flows."""

    def test_register_and_use_token(self, client):
        """Test registering and immediately using the returned token."""
        # Register
        register_response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "flow@example.com",
                "password": "password123",
                "full_name": "Flow Test"
            }
        )

        assert register_response.status_code == status.HTTP_201_CREATED
        token = register_response.json()["access_token"]

        # Use token to get user info
        me_response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert me_response.status_code == status.HTTP_200_OK
        user_data = me_response.json()
        assert user_data["email"] == "flow@example.com"
        assert user_data["full_name"] == "Flow Test"

    def test_login_after_registration(self, client):
        """Test logging in after registration."""
        # Register
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "loginafter@example.com",
                "password": "mypassword",
                "full_name": "Login Test"
            }
        )

        # Login with same credentials
        login_response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "loginafter@example.com",
                "password": "mypassword"
            }
        )

        assert login_response.status_code == status.HTTP_200_OK
        token = login_response.json()["access_token"]

        # Verify token works
        me_response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert me_response.status_code == status.HTTP_200_OK
        assert me_response.json()["email"] == "loginafter@example.com"

    def test_tokens_from_register_and_login_both_work(self, client):
        """Test that both register and login return working tokens."""
        email = "dualtoken@example.com"
        password = "password123"

        # Register and get first token
        register_response = client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": password, "full_name": "Dual Token"}
        )
        token1 = register_response.json()["access_token"]

        # Login and get second token
        login_response = client.post(
            "/api/v1/auth/login",
            data={"username": email, "password": password}
        )
        token2 = login_response.json()["access_token"]

        # Both tokens should work
        response1 = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token1}"}
        )
        response2 = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token2}"}
        )

        assert response1.status_code == status.HTTP_200_OK
        assert response2.status_code == status.HTTP_200_OK
        assert response1.json()["email"] == email
        assert response2.json()["email"] == email
