# =====================================================================
# FILE: backend/test_nvidia_service.py
# DESCRIPTION: Unit tests for the NVIDIA service layer (generate_text and chat)
#              with mocked requests to local or remote API.
# =====================================================================

import unittest
from unittest.mock import patch, MagicMock
import json
import requests
from app.services.nvidia_service import generate_text, generate_text_stream, chat, chat_stream, is_boilerplate_response

class TestNvidiaService(unittest.TestCase):
    
    def setUp(self):
        # Patch the settings object to bypass configuration validations
        self.patcher = patch("app.services.nvidia_service.settings")
        self.mock_settings = self.patcher.start()
        self.mock_settings.NVIDIA_API_KEY = "mock-api-key"
        self.mock_settings.NVIDIA_MODEL = "nvidia/nemotron-3-nano-30b-a3b"
        self.mock_settings.NVIDIA_API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
        self.mock_settings.NVIDIA_TIMEOUT = 15.0

    def tearDown(self):
        self.patcher.stop()

    @patch("app.services.nvidia_service.requests.post")
    def test_generate_text_success(self, mock_post):
        # Configure mock response for successful non-streaming call
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "A detailed agricultural response about rice cultivation."
                    }
                }
            ]
        }
        mock_post.return_value = mock_response
        
        result = generate_text("How do I cultivate rice?")
        self.assertEqual(result, "A detailed agricultural response about rice cultivation.")
        mock_post.assert_called_once()
        
    @patch("app.services.nvidia_service.requests.post")
    def test_generate_text_retry_and_success(self, mock_post):
        # Configure mock to fail twice, then succeed
        mock_fail = MagicMock()
        mock_fail.raise_for_status.side_effect = requests.exceptions.HTTPError("Service Unavailable")
        
        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "Success after retries"
                    }
                }
            ]
        }
        
        mock_post.side_effect = [mock_fail, mock_fail, mock_success]
        
        # Call generate_text with a patched retry delay to avoid wasting time in tests
        with patch("time.sleep", return_value=None):
            result = generate_text("Retry test prompt")
            
        self.assertEqual(result, "Success after retries")
        self.assertEqual(mock_post.call_count, 3)

    @patch("app.services.nvidia_service.requests.post")
    @patch("app.services.gemini_service.ask_gemini")
    def test_generate_text_failure_raises_runtime_error(self, mock_ask_gemini, mock_post):
        # Configure mock to always fail
        mock_post.side_effect = requests.exceptions.Timeout("Connection timed out")
        mock_ask_gemini.side_effect = Exception("Gemini failed too")
        
        with patch("time.sleep", return_value=None):
            with self.assertRaises(RuntimeError):
                generate_text("Fail prompt")

    def test_is_boilerplate_response(self):
        self.assertTrue(is_boilerplate_response("what's on your mind"))
        self.assertTrue(is_boilerplate_response("hello"))
        self.assertFalse(is_boilerplate_response("To enrich the soil nitrogen content, legumes should be planted."))

    @patch("app.services.nvidia_service.requests.post")
    def test_chat_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "🌿 Premium advice on crop health."
                    }
                }
            ]
        }
        mock_post.return_value = mock_response
        
        result = chat("Tell me about crop health", history=[], location_name="Odisha")
        self.assertEqual(result, "🌿 Premium advice on crop health.")

    @patch("app.services.nvidia_service.requests.post")
    def test_generate_text_stream(self, mock_post):
        # Mock streaming response
        mock_response = MagicMock()
        mock_response.status_code = 200
        
        # Create an iterator over simulated SSE chunk lines
        mock_response.iter_lines.return_value = [
            b'data: {"choices": [{"delta": {"content": "Hello"}}]}',
            b'data: {"choices": [{"delta": {"content": " World"}}]}',
            b'data: [DONE]'
        ]
        mock_post.return_value = mock_response
        
        tokens = list(generate_text_stream("Stream prompt"))
        self.assertEqual(tokens, ["Hello", " World"])

    @patch("app.services.nvidia_service.requests.post")
    @patch("app.services.gemini_service.ask_gemini")
    def test_generate_text_gemini_fallback_success(self, mock_ask_gemini, mock_post):
        # Configure mock post to always fail
        mock_post.side_effect = requests.exceptions.Timeout("Connection timed out")
        mock_ask_gemini.return_value = "Gemini fallback response text"
        
        with patch("time.sleep", return_value=None):
            result = generate_text("Prompt needing fallback")
            
        self.assertEqual(result, "Gemini fallback response text")
        mock_ask_gemini.assert_called_once_with("Prompt needing fallback", temperature=0.7)

    @patch("app.services.nvidia_service.requests.post")
    @patch("app.services.gemini_service.model.generate_content")
    def test_generate_text_stream_gemini_fallback_success(self, mock_gemini_generate, mock_post):
        # Configure mock post to always fail
        mock_post.side_effect = requests.exceptions.Timeout("Connection timed out")
        
        # Configure mock gemini generate_content to yield chunks
        mock_chunk_1 = MagicMock()
        mock_chunk_1.text = "Hello"
        mock_chunk_2 = MagicMock()
        mock_chunk_2.text = " from Gemini"
        mock_gemini_generate.return_value = [mock_chunk_1, mock_chunk_2]
        
        with patch("time.sleep", return_value=None):
            tokens = list(generate_text_stream("Stream prompt"))
            
        self.assertEqual(tokens, ["Hello", " from Gemini"])
        mock_gemini_generate.assert_called_once_with("Stream prompt", stream=True, generation_config={"temperature": 0.7})


if __name__ == "__main__":
    unittest.main()
