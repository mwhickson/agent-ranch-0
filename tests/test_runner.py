import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock
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
        self.runner.log_to_file("T1", "BUILDER", "Created file src/main.go")
        log_path = os.path.join(self.config.log_dir, "T1.log")
        self.assertTrue(os.path.exists(log_path))
        with open(log_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("=== [BUILDER] ===", content)
            self.assertIn("Created file src/main.go", content)

    def test_get_workspace_context_captures_multilanguage_files(self):
        # Setup mix of Go and Python files along with go.mod
        with open(os.path.join(self.temp_dir.name, "go.mod"), "w", encoding="utf-8") as f:
            f.write("module game\n\ngo 1.22")

        src_dir = os.path.join(self.temp_dir.name, "src")
        os.makedirs(src_dir, exist_ok=True)
        with open(os.path.join(src_dir, "main.go"), "w", encoding="utf-8") as f:
            f.write("package main\nfunc main() {}")

        context = self.runner.get_workspace_context()
        self.assertIn("go.mod", context)
        self.assertIn("src/main.go", context)
        self.assertIn("--- FILE: go.mod ---", context)
        self.assertIn("module game", context)
        self.assertIn("--- FILE: src/main.go ---", context)

    @patch("subprocess.run")
    def test_validate_syntax_routes_to_go_when_go_mod_present(self, mock_run):
        # Seed go.mod file
        with open(os.path.join(self.temp_dir.name, "go.mod"), "w", encoding="utf-8") as f:
            f.write("module game")

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_run.return_value = mock_process

        valid, error = self.runner.validate_syntax()
        self.assertTrue(valid)
        self.assertEqual(error, "")
        
        # Verify go vet was executed
        mock_run.assert_called_once()
        self.assertIn("go vet", mock_run.call_args[0][0])

    @patch("subprocess.run")
    def test_validate_syntax_routes_to_python_default(self, mock_run):
        src_dir = os.path.join(self.temp_dir.name, "src")
        os.makedirs(src_dir, exist_ok=True)
        with open(os.path.join(src_dir, "app.py"), "w", encoding="utf-8") as f:
            f.write("print('hello')")

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_run.return_value = mock_process

        valid, error = self.runner.validate_syntax()
        self.assertTrue(valid)
        self.assertEqual(error, "")
        
        # Verify python check was executed
        mock_run.assert_called_once()
        self.assertIn("py_compile", mock_run.call_args[0][0])

    def test_execute_shell(self):
        res = self.runner.execute_shell("echo $PYTHONPATH")
        self.assertEqual(res.returncode, 0)
        self.assertIn(self.temp_dir.name, res.stdout)


if __name__ == "__main__":
    unittest.main()