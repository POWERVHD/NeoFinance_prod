"""
Unit tests for Gemini AI service.

Tests the GeminiService class including:
- Service initialization
- Response generation
- Connection testing
- Error handling
"""

import pytest
from unittest.mock import Mock, patch
from app.services.gemini_service import GeminiService, get_gemini_service


class TestGeminiServiceInitialization:
    """Tests for GeminiService initialization."""

    @patch('app.services.gemini_service.genai')
    @patch('app.services.gemini_service.os.getenv')
    def test_init_success(self, mock_getenv, mock_genai):
        """Test successful service initialization with valid API key."""
        mock_getenv.return_value = "test_api_key"
        mock_model = Mock()
        mock_genai.GenerativeModel.return_value = mock_model

        service = GeminiService()

        mock_getenv.assert_called_once_with("GEMINI_API_KEY")
        mock_genai.configure.assert_called_once_with(api_key="test_api_key")
        mock_genai.GenerativeModel.assert_called_once_with('gemini-pro')
        assert service.model == mock_model

    @patch('app.services.gemini_service.os.getenv')
    def test_init_missing_api_key(self, mock_getenv):
        """Test initialization fails without API key."""
        mock_getenv.return_value = None

        with pytest.raises(ValueError) as exc_info:
            GeminiService()

        assert "GEMINI_API_KEY not found" in str(exc_info.value)


class TestGenerateResponse:
    """Tests for generate_response method."""

    @pytest.fixture
    def mock_service(self):
        """Create a mocked GeminiService."""
        with patch('app.services.gemini_service.genai'), \
             patch('app.services.gemini_service.os.getenv', return_value="test_key"):
            service = GeminiService()
            service.model = Mock()
            return service

    @pytest.mark.asyncio
    async def test_generate_response_without_system_instruction(self, mock_service):
        """Test generating response without system instruction."""
        mock_response = Mock()
        mock_response.text = "This is a test response"
        mock_service.model.generate_content.return_value = mock_response

        result = await mock_service.generate_response("What is 2+2?")

        assert result == "This is a test response"
        mock_service.model.generate_content.assert_called_once_with("What is 2+2?")

    @pytest.mark.asyncio
    async def test_generate_response_with_system_instruction(self, mock_service):
        """Test generating response with system instruction."""
        mock_response = Mock()
        mock_response.text = "Professional response"
        mock_service.model.generate_content.return_value = mock_response

        system_prompt = "You are a helpful assistant"
        user_prompt = "Hello"

        result = await mock_service.generate_response(
            prompt=user_prompt,
            system_instruction=system_prompt
        )

        assert result == "Professional response"
        expected_full_prompt = f"{system_prompt}\n\n{user_prompt}"
        mock_service.model.generate_content.assert_called_once_with(expected_full_prompt)

    @pytest.mark.asyncio
    async def test_generate_response_api_error(self, mock_service):
        """Test error handling when API call fails."""
        mock_service.model.generate_content.side_effect = Exception("API rate limit exceeded")

        with pytest.raises(Exception) as exc_info:
            await mock_service.generate_response("Test prompt")

        assert "Failed to generate AI response" in str(exc_info.value)
        assert "API rate limit exceeded" in str(exc_info.value)


class TestConnectionTest:
    """Tests for test_connection method."""

    @pytest.fixture
    def mock_service(self):
        """Create a mocked GeminiService."""
        with patch('app.services.gemini_service.genai'), \
             patch('app.services.gemini_service.os.getenv', return_value="test_key"):
            service = GeminiService()
            service.model = Mock()
            return service

    def test_connection_success(self, mock_service):
        """Test successful connection test."""
        mock_response = Mock()
        mock_response.text = "Hello, I can read this!"
        mock_service.model.generate_content.return_value = mock_response

        result = mock_service.test_connection()

        assert result is True
        mock_service.model.generate_content.assert_called_once()

    def test_connection_success_case_insensitive(self, mock_service):
        """Test connection test with uppercase response."""
        mock_response = Mock()
        mock_response.text = "HELLO there!"
        mock_service.model.generate_content.return_value = mock_response

        result = mock_service.test_connection()

        assert result is True

    def test_connection_failure(self, mock_service):
        """Test connection test when API call fails."""
        mock_service.model.generate_content.side_effect = Exception("Network error")

        result = mock_service.test_connection()

        assert result is False

    def test_connection_unexpected_response(self, mock_service):
        """Test connection test with unexpected response."""
        mock_response = Mock()
        mock_response.text = "I don't understand"
        mock_service.model.generate_content.return_value = mock_response

        result = mock_service.test_connection()

        assert result is False


class TestGetGeminiService:
    """Tests for get_gemini_service singleton function."""

    def test_singleton_returns_same_instance(self):
        """Test that get_gemini_service returns the same instance."""
        with patch('app.services.gemini_service.genai'), \
             patch('app.services.gemini_service.os.getenv', return_value="test_key"):
            # Reset the singleton
            import app.services.gemini_service as service_module
            service_module._gemini_service = None

            service1 = get_gemini_service()
            service2 = get_gemini_service()

            assert service1 is service2

    def test_singleton_creates_service_once(self):
        """Test that GeminiService is only created once."""
        with patch('app.services.gemini_service.genai'), \
             patch('app.services.gemini_service.os.getenv', return_value="test_key"), \
             patch('app.services.gemini_service.GeminiService') as mock_service_class:

            # Reset the singleton
            import app.services.gemini_service as service_module
            service_module._gemini_service = None

            mock_instance = Mock()
            mock_service_class.return_value = mock_instance

            service1 = get_gemini_service()
            service2 = get_gemini_service()
            service3 = get_gemini_service()

            # GeminiService should only be instantiated once
            assert mock_service_class.call_count == 1
            assert service1 == mock_instance
            assert service2 == mock_instance
            assert service3 == mock_instance
