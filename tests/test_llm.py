import unittest
from unittest.mock import patch, MagicMock
import requests
from ar0.config import Config
from ar0.llm import LLMClient


class TestLLMClient(unittest.TestCase):

    def setUp(self):
        self.config = Config(project_dir="/tmp")
        self.client = LLMClient(self.config)

    @patch("requests.post")
    def test_call_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": '{"thought": "ok"}'}}]
        }
        mock_post.return_value = mock_response

        res = self.client.call("sys", "user")
        self.assertEqual(res, '{"thought": "ok"}')

    @patch("requests.post")
    def test_call_timeout_handles_gracefully(self, mock_post):
        mock_post.side_effect = requests.exceptions.Timeout("Timeout hit")
        res = self.client.call("sys", "user")
        self.assertEqual(res, "")

    def test_parse_json_variations(self):
        # 1. Standard dict
        parsed = self.client.parse_json('{"action": "test"}')
        self.assertEqual(parsed, {"action": "test"})

        # 2. Wrapped single item list unwrap
        parsed_list = self.client.parse_json('[{"action": "test"}]')
        self.assertEqual(parsed_list, {"action": "test"})

        # 3. Regex extractions from surrounding prose
        raw_text = "Here is the response:\n```json\n{\"command\": \"ls\"}\n```"
        parsed_regex = self.client.parse_json(raw_text)
        self.assertEqual(parsed_regex, {"command": "ls"})

        # 4. Invalid JSON
        self.assertIsNone(self.client.parse_json("Not JSON at all"))


if __name__ == "__main__":
    unittest.main()