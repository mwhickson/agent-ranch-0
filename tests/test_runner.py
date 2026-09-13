import os
import tempfile
import unittest
from ar0.config import Config
from ar0.runner import TaskRunner


class TestTaskRunner(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config = Config(project_dir=self.temp_dir.name)
        self.runner = TaskRunner(self.config)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_log_to_file(self):
        self.runner.log_to_file("T1", "BUILDER", "Created file src/main.py")
        log_path = os.path.join(self.config.log_dir, "T1.log")
        self.assertTrue(os.path.exists(log_path))
        with open(log_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("=== [BUILDER] ===", content)
            self.assertIn("Created file src/main.py", content)

    def test_get_workspace_context(self):
        src_dir = os.path.join(self.temp_dir.name, "src")
        os.makedirs(src_dir, exist_ok=True)
        with open(os.path.join(src_dir, "app.py"), "w", encoding="utf-8") as f:
            f.write("print('hello')")

        context = self.runner.get_workspace_context()
        self.assertIn("src/app.py", context)
        self.assertIn("--- FILE: src/app.py ---", context)
        self.assertIn("print('hello')", context)

    def test_execute_shell(self):
        res = self.runner.execute_shell("echo $PYTHONPATH")
        self.assertEqual(res.returncode, 0)
        self.assertIn(self.temp_dir.name, res.stdout)


if __name__ == "__main__":
    unittest.main()