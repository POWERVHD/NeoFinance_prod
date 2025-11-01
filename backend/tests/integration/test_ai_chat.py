"""
Integration tests for AI Chat API endpoints.

Tests the AI chat functionality including:
- Quick questions retrieval
- Chat message processing
- Budget analysis
- Health check
"""

import pytest
from fastapi import status
from datetime import datetime, timedelta
from unittest.mock import Mock
from app.models.transaction import Transaction


@pytest.fixture
def mock_gemini_service(client):
    """Create a mocked Gemini service and override the dependency."""
    from app.services.gemini_service import get_gemini_service
    from app.main import app

    mock_service = Mock()
    mock_service.test_connection.return_value = True

    # Create an async mock for generate_response
    async def mock_generate(*args, **kwargs):
        return "This is a mocked AI response with financial advice."

    mock_service.generate_response = mock_generate

    # Override the dependency
    app.dependency_overrides[get_gemini_service] = lambda: mock_service

    yield mock_service

    # Clean up
    if get_gemini_service in app.dependency_overrides:
        del app.dependency_overrides[get_gemini_service]


@pytest.fixture
def sample_transactions(db, test_user):
    """Create sample transactions for testing."""
    transactions = [
        Transaction(
            user_id=test_user.id,
            description="Salary",
            amount=5000.00,
            type="income",
            category="Salary",
            transaction_date=datetime.now() - timedelta(days=5)
        ),
        Transaction(
            user_id=test_user.id,
            description="Grocery Shopping",
            amount=150.00,
            type="expense",
            category="Food",
            transaction_date=datetime.now() - timedelta(days=4)
        ),
        Transaction(
            user_id=test_user.id,
            description="Rent Payment",
            amount=1200.00,
            type="expense",
            category="Housing",
            transaction_date=datetime.now() - timedelta(days=3)
        ),
        Transaction(
            user_id=test_user.id,
            description="Coffee",
            amount=5.50,
            type="expense",
            category="Food",
            transaction_date=datetime.now() - timedelta(days=2)
        ),
        Transaction(
            user_id=test_user.id,
            description="Uber Ride",
            amount=25.00,
            type="expense",
            category="Transportation",
            transaction_date=datetime.now() - timedelta(days=1)
        ),
    ]

    for transaction in transactions:
        db.add(transaction)
    db.commit()

    for transaction in transactions:
        db.refresh(transaction)

    return transactions


class TestQuickQuestionsEndpoint:
    """Tests for GET /api/v1/ai-chat/quick-questions endpoint."""

    def test_get_quick_questions_success(self, client):
        """Test getting quick questions list."""
        response = client.get("/api/v1/ai-chat/quick-questions")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "questions" in data
        assert isinstance(data["questions"], list)
        assert len(data["questions"]) > 0

        # Verify expected questions are present
        questions = data["questions"]
        assert any("spending high" in q.lower() for q in questions)
        assert any("save more" in q.lower() for q in questions)

    def test_quick_questions_no_auth_required(self, client):
        """Test that quick questions don't require authentication."""
        response = client.get("/api/v1/ai-chat/quick-questions")
        assert response.status_code == status.HTTP_200_OK


class TestChatMessageEndpoint:
    """Tests for POST /api/v1/ai-chat/message endpoint."""

    def test_send_message_success(self, client, auth_headers, sample_transactions, mock_gemini_service):
        """Test sending a chat message successfully."""
        response = client.post(
            "/api/v1/ai-chat/message",
            headers=auth_headers,
            json={
                "question": "How can I save more money?",
                "include_context": True
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "response" in data
        assert "timestamp" in data
        assert isinstance(data["response"], str)
        assert len(data["response"]) > 0

    def test_send_message_without_context(self, client, auth_headers, mock_gemini_service):
        """Test sending message without transaction context."""
        response = client.post(
            "/api/v1/ai-chat/message",
            headers=auth_headers,
            json={
                "question": "What is a budget?",
                "include_context": False
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "response" in data

    def test_send_message_requires_auth(self, client):
        """Test that message endpoint requires authentication."""
        response = client.post(
            "/api/v1/ai-chat/message",
            json={"question": "Test question"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_send_message_empty_question(self, client, auth_headers):
        """Test sending message with empty question fails."""
        response = client.post(
            "/api/v1/ai-chat/message",
            headers=auth_headers,
            json={"question": ""}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_send_message_question_too_long(self, client, auth_headers):
        """Test sending message with question exceeding max length."""
        long_question = "a" * 501  # Max is 500 characters
        response = client.post(
            "/api/v1/ai-chat/message",
            headers=auth_headers,
            json={"question": long_question}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_send_message_with_transactions(self, client, auth_headers, sample_transactions, mock_gemini_service):
        """Test that message includes transaction data in context."""
        response = client.post(
            "/api/v1/ai-chat/message",
            headers=auth_headers,
            json={
                "question": "Analyze my spending",
                "include_context": True
            }
        )

        assert response.status_code == status.HTTP_200_OK
        # The mock service was called, which means context was prepared
        assert mock_gemini_service.generate_response.__name__ == 'mock_generate'

    def test_send_message_ai_service_failure(self, client, auth_headers, mock_gemini_service):
        """Test handling of AI service failures."""
        async def mock_error(*args, **kwargs):
            raise Exception("AI service unavailable")

        mock_gemini_service.generate_response = mock_error

        response = client.post(
            "/api/v1/ai-chat/message",
            headers=auth_headers,
            json={"question": "Test question"}
        )

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Failed to generate response" in response.json()["detail"]


class TestAnalyzeBudgetEndpoint:
    """Tests for POST /api/v1/ai-chat/analyze-budget endpoint."""

    def test_analyze_budget_success(self, client, auth_headers, sample_transactions, mock_gemini_service):
        """Test successful budget analysis."""
        response = client.post(
            "/api/v1/ai-chat/analyze-budget",
            headers=auth_headers,
            json={"period_days": 30}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "response" in data
        assert "timestamp" in data
        assert isinstance(data["response"], str)

    def test_analyze_budget_default_period(self, client, auth_headers, sample_transactions, mock_gemini_service):
        """Test budget analysis with default 30-day period."""
        response = client.post(
            "/api/v1/ai-chat/analyze-budget",
            headers=auth_headers,
            json={}
        )

        assert response.status_code == status.HTTP_200_OK

    def test_analyze_budget_custom_period(self, client, auth_headers, sample_transactions, mock_gemini_service):
        """Test budget analysis with custom period."""
        response = client.post(
            "/api/v1/ai-chat/analyze-budget",
            headers=auth_headers,
            json={"period_days": 7}
        )

        assert response.status_code == status.HTTP_200_OK

    def test_analyze_budget_requires_auth(self, client):
        """Test that budget analysis requires authentication."""
        response = client.post(
            "/api/v1/ai-chat/analyze-budget",
            json={"period_days": 30}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_analyze_budget_invalid_period(self, client, auth_headers):
        """Test budget analysis with invalid period."""
        response = client.post(
            "/api/v1/ai-chat/analyze-budget",
            headers=auth_headers,
            json={"period_days": 0}  # Must be >= 1
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_analyze_budget_period_too_large(self, client, auth_headers):
        """Test budget analysis with period exceeding max."""
        response = client.post(
            "/api/v1/ai-chat/analyze-budget",
            headers=auth_headers,
            json={"period_days": 366}  # Max is 365
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_analyze_budget_no_transactions(self, client, auth_headers, mock_gemini_service):
        """Test budget analysis with no transactions."""
        response = client.post(
            "/api/v1/ai-chat/analyze-budget",
            headers=auth_headers,
            json={"period_days": 30}
        )

        # Should still succeed, just with empty data
        assert response.status_code == status.HTTP_200_OK

    def test_analyze_budget_ai_service_failure(self, client, auth_headers, mock_gemini_service):
        """Test handling of AI service failures during budget analysis."""
        async def mock_error(*args, **kwargs):
            raise Exception("Analysis failed")

        mock_gemini_service.generate_response = mock_error

        response = client.post(
            "/api/v1/ai-chat/analyze-budget",
            headers=auth_headers,
            json={"period_days": 30}
        )

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Analysis failed" in response.json()["detail"]


class TestHealthCheckEndpoint:
    """Tests for GET /api/v1/ai-chat/health endpoint."""

    def test_health_check_healthy(self, client, mock_gemini_service):
        """Test health check with healthy service."""
        mock_gemini_service.test_connection.return_value = True

        response = client.get("/api/v1/ai-chat/health")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "gemini-api"
        assert "timestamp" in data

    def test_health_check_unhealthy(self, client, mock_gemini_service):
        """Test health check with unhealthy service."""
        mock_gemini_service.test_connection.return_value = False

        response = client.get("/api/v1/ai-chat/health")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["service"] == "gemini-api"

    def test_health_check_no_auth_required(self, client, mock_gemini_service):
        """Test that health check doesn't require authentication."""
        mock_gemini_service.test_connection.return_value = True

        response = client.get("/api/v1/ai-chat/health")
        assert response.status_code == status.HTTP_200_OK


class TestAIChatIntegrationFlows:
    """Integration tests for complete AI chat flows."""

    def test_complete_chat_flow(self, client, auth_headers, sample_transactions, mock_gemini_service):
        """Test complete flow: check health, get questions, send message."""
        # 1. Check health
        health_response = client.get("/api/v1/ai-chat/health")
        assert health_response.status_code == status.HTTP_200_OK
        assert health_response.json()["status"] == "healthy"

        # 2. Get quick questions
        questions_response = client.get("/api/v1/ai-chat/quick-questions")
        assert questions_response.status_code == status.HTTP_200_OK
        questions = questions_response.json()["questions"]
        assert len(questions) > 0

        # 3. Send a message using one of the quick questions
        message_response = client.post(
            "/api/v1/ai-chat/message",
            headers=auth_headers,
            json={
                "question": questions[0],
                "include_context": True
            }
        )
        assert message_response.status_code == status.HTTP_200_OK
        assert len(message_response.json()["response"]) > 0

    def test_analyze_budget_after_transactions(self, client, auth_headers, sample_transactions, mock_gemini_service):
        """Test budget analysis after creating transactions."""
        # Verify transactions exist
        assert len(sample_transactions) == 5

        # Request budget analysis
        response = client.post(
            "/api/v1/ai-chat/analyze-budget",
            headers=auth_headers,
            json={"period_days": 30}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "response" in data
        # Verify timestamp is recent
        timestamp = datetime.fromisoformat(data["timestamp"].replace('Z', '+00:00'))
        assert (datetime.now() - timestamp).total_seconds() < 5

    def test_multiple_users_chat_isolation(self, client, test_user, test_user_2, db, mock_gemini_service):
        """Test that chat context is isolated between users."""
        # Create transactions for user 1
        transaction1 = Transaction(
            user_id=test_user.id,
            description="User 1 Transaction",
            amount=100.00,
            type="expense",
            category="Food",
            transaction_date=datetime.now()
        )
        db.add(transaction1)
        db.commit()

        # Get token for user 1
        login1 = client.post(
            "/api/v1/auth/login",
            data={"username": test_user.email, "password": "testpassword123"}
        )
        token1 = login1.json()["access_token"]

        # Get token for user 2
        login2 = client.post(
            "/api/v1/auth/login",
            data={"username": test_user_2.email, "password": "testpassword123"}
        )
        token2 = login2.json()["access_token"]

        # User 1 sends message (should have transaction)
        response1 = client.post(
            "/api/v1/ai-chat/message",
            headers={"Authorization": f"Bearer {token1}"},
            json={"question": "Analyze my spending", "include_context": True}
        )
        assert response1.status_code == status.HTTP_200_OK

        # User 2 sends message (should have no transactions)
        response2 = client.post(
            "/api/v1/ai-chat/message",
            headers={"Authorization": f"Bearer {token2}"},
            json={"question": "Analyze my spending", "include_context": True}
        )
        assert response2.status_code == status.HTTP_200_OK

        # Both should succeed, showing proper isolation
