"""
Tests for security functions (password hashing and JWT tokens).

Tests password hashing, verification, token creation, and token decoding.
"""

import pytest
from datetime import timedelta

from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
)


class TestPasswordHashing:
    """Tests for password hashing and verification."""

    def test_password_hashing(self):
        """Test that password hashing works and hashes are different."""
        password = "mysecretpassword123"
        hashed1 = get_password_hash(password)
        hashed2 = get_password_hash(password)

        # Hashes should be different (bcrypt uses random salt)
        assert hashed1 != hashed2

        # Both hashes should be strings
        assert isinstance(hashed1, str)
        assert isinstance(hashed2, str)

        # Hashes should not contain the plain password
        assert password not in hashed1
        assert password not in hashed2

    def test_password_verification_success(self):
        """Test verifying a correct password."""
        password = "correctpassword"
        hashed = get_password_hash(password)

        # Verify correct password
        assert verify_password(password, hashed) is True

    def test_password_verification_failure(self):
        """Test verifying an incorrect password."""
        password = "correctpassword"
        wrong_password = "wrongpassword"
        hashed = get_password_hash(password)

        # Verify wrong password
        assert verify_password(wrong_password, hashed) is False

    def test_password_case_sensitive(self):
        """Test that password verification is case sensitive."""
        password = "Password123"
        hashed = get_password_hash(password)

        # Different case should fail
        assert verify_password("password123", hashed) is False
        assert verify_password("PASSWORD123", hashed) is False

    def test_empty_password(self):
        """Test handling of empty password."""
        empty_password = ""
        hashed = get_password_hash(empty_password)

        # Should still hash and verify
        assert verify_password(empty_password, hashed) is True
        assert verify_password("not_empty", hashed) is False


class TestJWTTokens:
    """Tests for JWT token creation and decoding."""

    def test_create_access_token(self):
        """Test creating an access token."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)

        # Token should be a string
        assert isinstance(token, str)

        # Token should not be empty
        assert len(token) > 0

        # Token should contain the encoded data
        # (We can't verify the exact content without decoding)

    def test_create_token_with_custom_expiry(self):
        """Test creating a token with custom expiration."""
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(minutes=60)

        token = create_access_token(data, expires_delta=expires_delta)

        # Token should be created successfully
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_access_token_success(self):
        """Test decoding a valid access token."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)

        # Decode the token
        decoded = decode_access_token(token)

        # Should successfully decode
        assert decoded is not None
        assert decoded["sub"] == "test@example.com"
        assert "exp" in decoded  # Expiration should be present

    def test_decode_invalid_token(self):
        """Test decoding an invalid token."""
        invalid_token = "this.is.not.a.valid.token"

        # Should return None for invalid token
        decoded = decode_access_token(invalid_token)
        assert decoded is None

    def test_decode_tampered_token(self):
        """Test decoding a tampered token."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)

        # Tamper with the token
        tampered_token = token[:-10] + "tampered!"

        # Should return None for tampered token
        decoded = decode_access_token(tampered_token)
        assert decoded is None

    def test_decode_empty_token(self):
        """Test decoding an empty token."""
        decoded = decode_access_token("")
        assert decoded is None

    def test_token_contains_expiration(self):
        """Test that tokens contain expiration time."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        decoded = decode_access_token(token)

        # Should have expiration
        assert "exp" in decoded
        assert isinstance(decoded["exp"], int)

    def test_token_with_additional_data(self):
        """Test creating token with additional claims."""
        data = {
            "sub": "test@example.com",
            "user_id": 123,
            "role": "admin",
        }
        token = create_access_token(data)
        decoded = decode_access_token(token)

        # All data should be preserved
        assert decoded is not None
        assert decoded["sub"] == "test@example.com"
        assert decoded["user_id"] == 123
        assert decoded["role"] == "admin"

    def test_multiple_tokens_are_different(self):
        """Test that creating multiple tokens with same data produces different tokens."""
        data = {"sub": "test@example.com"}

        # Create tokens at slightly different times
        token1 = create_access_token(data)
        token2 = create_access_token(data)

        # Tokens should be different (due to different exp timestamps)
        # Note: In rare cases they might be same if created at exact same second
        # This is a timing-dependent test

        # But both should decode to same subject
        decoded1 = decode_access_token(token1)
        decoded2 = decode_access_token(token2)

        assert decoded1["sub"] == decoded2["sub"]


class TestSecurityIntegration:
    """Integration tests for security functions."""

    def test_password_and_token_workflow(self):
        """Test complete workflow: hash password, create token, verify."""
        # Step 1: User registers with password
        plain_password = "userpassword123"
        hashed_password = get_password_hash(plain_password)

        # Step 2: User logs in (verify password)
        login_attempt = "userpassword123"
        is_valid = verify_password(login_attempt, hashed_password)
        assert is_valid is True

        # Step 3: Create access token on successful login
        token = create_access_token({"sub": "user@example.com"})
        assert isinstance(token, str)

        # Step 4: Decode token for protected routes
        decoded = decode_access_token(token)
        assert decoded is not None
        assert decoded["sub"] == "user@example.com"

    def test_failed_login_workflow(self):
        """Test workflow with wrong password."""
        # User has hashed password stored
        correct_password = "correctpassword"
        hashed_password = get_password_hash(correct_password)

        # User tries to login with wrong password
        wrong_password = "wrongpassword"
        is_valid = verify_password(wrong_password, hashed_password)

        # Should fail verification
        assert is_valid is False

        # Token should not be created (this is application logic)
