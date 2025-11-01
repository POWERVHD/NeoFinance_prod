"""
Google Gemini API integration service.
Handles all communication with Gemini AI model.
"""

import os
import google.generativeai as genai
from typing import Optional
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)


class GeminiService:
    """Service for interacting with Google Gemini API."""

    def __init__(self):
        """Initialize Gemini service with API key."""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        logger.info("Gemini service initialized successfully")

    async def generate_response(
        self,
        prompt: str,
        system_instruction: Optional[str] = None
    ) -> str:
        """
        Generate AI response from prompt.

        Args:
            prompt: User question with context
            system_instruction: System-level instructions for AI behavior

        Returns:
            AI-generated response string

        Raises:
            Exception: If API call fails
        """
        try:
            # Combine system instruction with prompt if provided
            full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt

            # Generate response
            response = self.model.generate_content(full_prompt)

            logger.info(f"Generated response: {len(response.text)} characters")
            return response.text

        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            raise Exception(f"Failed to generate AI response: {str(e)}")

    async def generate_streaming_response(
        self,
        prompt: str,
        system_instruction: Optional[str] = None
    ):
        """
        Generate streaming AI response (for future enhancement).

        Args:
            prompt: User question with context
            system_instruction: System-level instructions

        Yields:
            Chunks of AI response text
        """
        try:
            full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt

            response = self.model.generate_content(full_prompt, stream=True)

            for chunk in response:
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            logger.error(f"Streaming error: {str(e)}")
            raise Exception(f"Streaming failed: {str(e)}")

    def test_connection(self) -> bool:
        """
        Test Gemini API connection.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = self.model.generate_content("Say 'Hello' if you can read this.")
            return "hello" in response.text.lower()
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False


# Singleton instance
_gemini_service: Optional[GeminiService] = None


def get_gemini_service() -> GeminiService:
    """Get or create Gemini service instance (singleton pattern)."""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service
