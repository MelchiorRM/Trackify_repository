import unittest
from unittest.mock import patch, MagicMock
import json
from flask import Flask
import utils.recommendations as recommendations

class TestCallGeminiApi(unittest.TestCase):
    def setUp(self):
        # Create a Flask app context for current_app usage
        self.app = Flask(__name__)
        self.app.config['GEMINI_API_KEY'] = 'fake_api_key'
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    @patch('utils.recommendations.genai.GenerativeModel')
    @patch('utils.recommendations.genai.configure')
    def test_call_gemini_api_success(self, mock_configure, mock_generative_model):
        # Mock the response from generate_content
        mock_response = MagicMock()
        sample_output = json.dumps([
            {"title": "Sample Book", "type": "book"},
            {"title": "Sample Movie", "type": "movie"},
            {"title": "Sample Music", "type": "music"}
        ])
        # Gemini response text wrapped in triple backticks as in real response
        mock_response.text = f"```json\n{sample_output}\n```"
        mock_generative_model.return_value.generate_content.return_value = mock_response

        prompt = "Test prompt"
        result = recommendations.call_gemini_api(prompt)

        expected = [
            {"title": "Sample Book", "type": "book"},
            {"title": "Sample Movie", "type": "movie"},
            {"title": "Sample Music", "type": "music"}
        ]

        self.assertEqual(result, expected)
        mock_configure.assert_called_once_with(api_key='fake_api_key')
        mock_generative_model.assert_called_once_with("gemini-1.5-flash")
        mock_generative_model.return_value.generate_content.assert_called_once_with(prompt)

    @patch('utils.recommendations.genai.GenerativeModel')
    @patch('utils.recommendations.genai.configure')
    def test_call_gemini_api_empty_response(self, mock_configure, mock_generative_model):
        mock_response = MagicMock()
        mock_response.text = "```json\n\n```"
        mock_generative_model.return_value.generate_content.return_value = mock_response

        prompt = "Test prompt"
        result = recommendations.call_gemini_api(prompt)
        self.assertEqual(result, [])

    @patch('utils.recommendations.genai.GenerativeModel')
    @patch('utils.recommendations.genai.configure')
    def test_call_gemini_api_invalid_json(self, mock_configure, mock_generative_model):
        mock_response = MagicMock()
        mock_response.text = "```json\n{invalid json}\n```"
        mock_generative_model.return_value.generate_content.return_value = mock_response

        prompt = "Test prompt"
        result = recommendations.call_gemini_api(prompt)
        self.assertEqual(result, [])

    def test_call_gemini_api_no_api_key(self):
        # Remove GEMINI_API_KEY from config
        self.app.config.pop('GEMINI_API_KEY', None)
        prompt = "Test prompt"
        result = recommendations.call_gemini_api(prompt)
        self.assertEqual(result, [])

if __name__ == '__main__':
    unittest.main()
