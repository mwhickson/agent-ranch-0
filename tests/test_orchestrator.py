import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from ar0.config import Config
from ar0.db import Database
from ar0.orchestrator import Orchestrator


class TestOrchestrator(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config = Config(project_dir=self.temp_dir.name)
        os.makedirs(self.config.prompt_dir, exist_ok=True)
        
        # Create dummy prompt files
        for p in ["planner_system.txt", "builder_system.txt", "tester_system.txt"]:
            with open(os.path.join(self.config.prompt_dir, p), "w", encoding="utf-8") as f:
                f.write("System prompt context")

        self.db = Database(self.config)
        self.db.init_schema()
        self.orchestrator = Orchestrator(self.config, self.db)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_run_builder_phase_rejects_read_only_commands(self):
        with patch.object(self.orchestrator.llm, "call", return_value='{"thought": "checking", "action": "run", "command": "ls -la"}'):
            result = self.orchestrator.run_builder_phase("T1", "Create file")
            self.assertIsNone(result)

    def test_run_builder_phase_accepts_write_commands(self):
        valid_json = '{"thought": "writing", "action": "write", "command": "cat << \'EOF\' > src/game.py\\npass\\nEOF"}'
        with patch.object(self.orchestrator.llm, "call", return_value=valid_json):
            result = self.orchestrator.run_builder_phase("T1", "Create file")
            self.assertIsNotNone(result)
            self.assertEqual(result["action"], "write")

    @patch("builtins.input", side_effect=["y"])  # Approve Builder execution
    def test_execute_workflow_pass_flow(self, mock_input):
        with self.db.get_connection() as conn:
            conn.execute("INSERT INTO tasks (id, role, description) VALUES ('T1', 'BUILDER', 'Build feature')")

        builder_payload = {"thought": "done", "action": "write", "command": "echo hello > src/file.txt"}

        with patch.object(self.orchestrator, "run_builder_phase", return_value=builder_payload), \
             patch.object(self.orchestrator.runner, "execute_shell") as mock_shell, \
             patch.object(self.orchestrator, "run_tester_phase", return_value=(True, "Tests Passed")):
            
            mock_shell.return_value.returncode = 0
            mock_shell.return_value.stdout = "OK"
            mock_shell.return_value.stderr = ""

            status = self.orchestrator.execute_workflow("T1")
            self.assertEqual(status, "PASS")

        task = self.db.get_task("T1")
        self.assertEqual(task[2], "PASS")

    @patch("builtins.input", side_effect=["y", "p"])  # Approve Builder (y), then select Manual PASS (p)
    def test_execute_workflow_manual_pass_override(self, mock_input):
        with self.db.get_connection() as conn:
            conn.execute("INSERT INTO tasks (id, role, description) VALUES ('T1', 'BUILDER', 'Build feature')")

        builder_payload = {"thought": "done", "action": "write", "command": "echo hello > src/file.txt"}

        # Return False repeatedly to feed inner tester retries without raising StopIteration
        with patch.object(self.orchestrator, "run_builder_phase", return_value=builder_payload), \
             patch.object(self.orchestrator.runner, "execute_shell") as mock_shell, \
             patch.object(self.orchestrator, "run_tester_phase", return_value=(False, "Assertion error")):
            
            mock_shell.return_value.returncode = 0
            mock_shell.return_value.stdout = "OK"
            mock_shell.return_value.stderr = ""

            status = self.orchestrator.execute_workflow("T1")
            self.assertEqual(status, "PASS")

        task = self.db.get_task("T1")
        self.assertEqual(task[2], "PASS")


if __name__ == "__main__":
    unittest.main()