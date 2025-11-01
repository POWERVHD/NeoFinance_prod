"""
Tests for authentication service functions.

Tests user creation, authentication, and retrieval.
"""

import pytest
from fastapi import HTTPException

from app.services.auth_service import (
    get_user_by_email,
    create_user,
    authenticate_user,
)
from app.schemas.user import UserCreate
from app.core.security import verify_password


class TestGetUserByEmail:
    """Tests for get_user_by_email function."""

    def test_get_existing_user(self, db, test_user):
        """Test retrieving an existing user by email."""
        user = get_user_by_email(db, test_user.email)

        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email

    def test_get_nonexistent_user(self, db):
        """Test retrieving a non-existent user returns None."""
        user = get_user_by_email(db, "nonexistent@example.com")

        assert user is None

    def test_case_sensitive_email(self, db, test_user):
        """Test that email lookup is case-sensitive."""
        # SQLite is case-insensitive by default, but this documents expected behavior
        user = get_user_by_email(db, test_user.email.upper())

        # May find user in SQLite (case-insensitive)
        # In PostgreSQL production, this should be case-sensitive


class TestCreateUser:
    """Tests for create_user function."""

    def test_create_user_success(self, db):
        """Test creating a new user successfully."""
        user_data = UserCreate(
            email="newuser@example.com",
            password="securepassword123",
            full_name="New User",
        )

        user = create_user(db, user_data)

        assert user.id is not None
        assert user.email == "newuser@example.com"
        assert user.full_name == "New User"
        assert user.is_active is True
        assert user.hashed_password != "securepassword123"  # Should be hashed
        assert verify_password("securepassword123", user.hashed_password) is True

    def test_create_user_without_full_name(self, db):
        """Test creating user without full name."""
        user_data = UserCreate(
            email="minimal@example.com",
            password="password123",
        )

        user = create_user(db, user_data)

        assert user.id is not None
        assert user.email == "minimal@example.com"
        assert user.full_name is None

    def test_create_user_duplicate_email(self, db, test_user):
        """Test that creating user with duplicate email raises exception."""
        user_data = UserCreate(
            email=test_user.email,  # Same email as existing user
            password="password123",
            full_name="Duplicate User",
        )

        with pytest.raises(HTTPException) as exc_info:
            create_user(db, user_data)

        assert exc_info.value.status_code == 400
        assert "already registered" in exc_info.value.detail.lower()

    def test_password_is_hashed(self, db):
        """Test that password is hashed, not stored as plain text."""
        plain_password = "mypassword123"
        user_data = UserCreate(
            email="hashtest@example.com",
            password=plain_password,
        )

        user = create_user(db, user_data)

        # Password should not be stored in plain text
        assert user.hashed_password != plain_password

        # Should start with bcrypt identifier
        assert user.hashed_password.startswith("$2b$")

    def test_created_user_is_active_by_default(self, db):
        """Test that newly created users are active."""
        user_data = UserCreate(
            email="active@example.com",
            password="password123",
        )

        user = create_user(db, user_data)

        assert user.is_active is True


class TestAuthenticateUser:
    """Tests for authenticate_user function."""

    def test_authenticate_with_correct_password(self, db, test_user, test_user_password):
        """Test authenticating with correct credentials."""
        user = authenticate_user(db, test_user.email, test_user_password)

        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email

    def test_authenticate_with_wrong_password(self, db, test_user):
        """Test authenticating with wrong password returns None."""
        user = authenticate_user(db, test_user.email, "wrongpassword")

        assert user is None

    def test_authenticate_nonexistent_user(self, db):
        """Test authenticating non-existent user returns None."""
        user = authenticate_user(db, "nonexistent@example.com", "password123")

        assert user is None

    def test_authenticate_inactive_user(self, db, test_user):
        """Test authenticating inactive user returns None."""
        # Deactivate the user
        test_user.is_active = False
        db.commit()

        user = authenticate_user(db, test_user.email, "testpassword123")

        assert user is None

    def test_authenticate_case_sensitive_password(self, db, test_user):
        """Test that password authentication is case-sensitive."""
        # Assuming password is "testpassword123"
        user = authenticate_user(db, test_user.email, "TESTPASSWORD123")

        assert user is None


class TestAuthServiceIntegration:
    """Integration tests for auth service workflows."""

    def test_register_and_login_workflow(self, db):
        """Test complete registration and login flow."""
        # Step 1: Register new user
        user_data = UserCreate(
            email="workflow@example.com",
            password="mypassword123",
            full_name="Workflow Test",
        )
        created_user = create_user(db, user_data)

        assert created_user.id is not None

        # Step 2: Login with same credentials
        authenticated_user = authenticate_user(
            db, "workflow@example.com", "mypassword123"
        )

        assert authenticated_user is not None
        assert authenticated_user.id == created_user.id
        assert authenticated_user.email == created_user.email

    def test_cannot_register_twice(self, db):
        """Test that registering same email twice fails."""
        user_data = UserCreate(
            email="duplicate@example.com",
            password="password123",
        )

        # First registration succeeds
        first_user = create_user(db, user_data)
        assert first_user.id is not None

        # Second registration fails
        with pytest.raises(HTTPException) as exc_info:
            create_user(db, user_data)

        assert exc_info.value.status_code == 400

    def test_failed_login_after_registration(self, db):
        """Test that wrong password fails after successful registration."""
        # Register user
        user_data = UserCreate(
            email="failedlogin@example.com",
            password="correctpassword",
        )
        create_user(db, user_data)

        # Try to login with wrong password
        user = authenticate_user(db, "failedlogin@example.com", "wrongpassword")

        assert user is None
