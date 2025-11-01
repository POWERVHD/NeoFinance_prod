"""
Test configuration and fixtures for the Finance Dashboard API.

This module provides pytest fixtures for:
- Test database setup and teardown
- Test client for API requests
- Test user creation
- Authentication token generation
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import get_password_hash
from app.db.session import Base, get_db
from app.main import app
from app.models import User, Transaction  # Import both models to resolve relationships
from app.schemas.user import UserCreate

# Use in-memory SQLite database for testing (faster than PostgreSQL)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# Create test engine with special SQLite settings
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # Keep same connection for in-memory DB
)

# Create test session factory
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """
    Create a fresh database for each test function.

    This fixture:
    1. Creates all tables
    2. Yields a database session
    3. Drops all tables after test completes

    Yields:
        Session: SQLAlchemy database session
    """
    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create a new session for the test
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """
    Create a test client with overridden database dependency.

    This fixture overrides the get_db dependency to use our test database
    and disables the startup event to prevent PostgreSQL connection attempts.

    Args:
        db: Database session from db fixture

    Yields:
        TestClient: FastAPI test client
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    # Clear startup/shutdown events to prevent PostgreSQL connection during tests
    # Tables are already created by the db fixture above
    app.router.on_startup = []
    app.router.on_shutdown = []

    with TestClient(app) as test_client:
        yield test_client

    # Clear overrides after test
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(db):
    """
    Create a test user in the database.

    Creates a user with:
    - email: test@example.com
    - password: testpassword123
    - full_name: Test User

    Args:
        db: Database session from db fixture

    Returns:
        User: Created test user model
    """
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123"),
        full_name="Test User",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_user_2(db):
    """
    Create a second test user for testing ownership boundaries.

    Creates a user with:
    - email: test2@example.com
    - password: testpassword123
    - full_name: Test User 2

    Args:
        db: Database session from db fixture

    Returns:
        User: Created second test user model
    """
    user = User(
        email="test2@example.com",
        hashed_password=get_password_hash("testpassword123"),
        full_name="Test User 2",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def auth_token(client, test_user):
    """
    Get authentication token for test user.

    This fixture:
    1. Logs in the test user
    2. Extracts the access token
    3. Returns token for use in authenticated requests

    Args:
        client: Test client from client fixture
        test_user: Test user from test_user fixture

    Returns:
        str: JWT access token
    """
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": "testpassword123",
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def auth_headers(auth_token):
    """
    Get authentication headers for API requests.

    Args:
        auth_token: JWT token from auth_token fixture

    Returns:
        dict: Headers dictionary with Authorization bearer token
    """
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture(scope="function")
def test_user_password():
    """
    Return the plain text password for test user.

    Useful for login tests.

    Returns:
        str: Plain text password
    """
    return "testpassword123"
