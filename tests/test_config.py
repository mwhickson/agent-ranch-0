import os
import tempfile
import unittest
from ar0.config import Config


class TestConfig(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_default_paths(self):
        cfg = Config(project_dir=self.temp_dir.name)
        self.assertEqual(cfg.db_path, os.path.join(self.temp_dir.name, "execution.db"))
        self.assertEqual(cfg.prompt_dir, os.path.join(self.temp_dir.name, "prompts"))
        self.assertEqual(cfg.log_dir, os.path.join(self.temp_dir.name, "logs"))
        self.assertEqual(cfg.spec_path, os.path.join(self.temp_dir.name, "PROJECT_SPEC.md"))
        self.assertEqual(cfg.timeout, 600)
        self.assertEqual(cfg.max_tester_retries, 3)

    def test_from_project_dir_parses_spec(self):
        spec_file = os.path.join(self.temp_dir.name, "PROJECT_SPEC.md")
        spec_content = (
            "# Project Spec\n"
            "<!-- AR0_CONFIG: API_URL=http://localhost:8080/v1/chat/completions -->\n"
            "TEMPERATURE=0.75\n"
            "MAX_TESTER_RETRIES=4\n"
        )
        with open(spec_file, "w", encoding="utf-8") as f:
            f.write(spec_content)

        cfg = Config.from_project_dir(self.temp_dir.name)
        self.assertEqual(cfg.model_api_url, "http://localhost:8080/v1/chat/completions")
        self.assertEqual(cfg.temperature, 0.75)
        self.assertEqual(cfg.max_tester_retries, 4)

if __name__ == "__main__":
    unittest.main()
