import os
from typing import Optional
import google.generativeai as genai
from abc import ABC, abstractmethod

API_KEY = os.getenv("GEMINI_API_KEY")  # TODO: Consider moving to a secure config
DEFAULT_GEMINI_MODEL = "gemini-2.0-flash"  # Updated to a more current model


class BaseClient(ABC):
    """
    Abstract base class for LLM clients.
    """

    @abstractmethod
    def generate_content(self, prompt: str) -> str:
        """
        Generate text content based on the given prompt.

        Args:
            prompt: The prompt to send to the LLM.

        Returns:
            The generated content as a string.
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """Close any resources used by the client."""
        pass

    def __enter__(self):
        """Enter the runtime context related to this object."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the runtime context and close the client."""
        self.close()


class BaseClientImpl(BaseClient):
    """
    A base client for interacting with the Gemini API.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or API_KEY
        self.model = model or DEFAULT_GEMINI_MODEL
        self.client = genai.GenerativeModel(
            self.model
        )  # Changed to use GenerativeModel
        genai.configure(api_key=self.api_key)

    def generate_content(self, prompt: str) -> Optional[str]:
        """
        Generates content using the Gemini API.

        Args:
            prompt: The prompt to send to the API.

        Returns:
            The text response from the API, or None if an error occurs or the response is empty.
        """
        try:
            # Handle potential API errors or empty responses
            # According to documentation, response.text might not exist if the prompt is blocked
            # or if the response is empty.
            # gemini-1.5-flash uses generate_content, not client.models.generate_content
            response = self.client.generate_content(contents=prompt)

            # Check for empty parts or finish reason
            if not response.parts:
                print(
                    f"Warning: Received no parts in response for prompt: {prompt[:100]}..."
                )
                return None
            if response.prompt_feedback and response.prompt_feedback.block_reason:
                print(
                    f"Warning: Prompt was blocked. Reason: {response.prompt_feedback.block_reason_message}"
                )
                return None

            return response.text
        except Exception as e:
            print(f"Error generating content with Gemini: {e}")
            return None

    def close(self) -> None:
        """Close any resources used by the client."""
        # No specific resource release needed for this client
        pass


if __name__ == "__main__":
    # Example usage (optional, for testing)
    with BaseClientImpl() as test_client:
        test_prompt = "Translate 'hello world' into French."
        response_text = test_client.generate_content(test_prompt)
        if response_text:
            print(f"Prompt: {test_prompt}")
            print(f"Response: {response_text}")
        else:
            print(f"Failed to get a response for prompt: {test_prompt}")
