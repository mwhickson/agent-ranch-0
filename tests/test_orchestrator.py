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

        # Create dummy prompt files needed by Orchestrator
        for p in ["planner_system.txt", "builder_system.txt", "tester_system.txt"]:
            with open(os.path.join(self.config.prompt_dir, p), "w", encoding="utf-8") as f:
                f.write("System prompt context")

        self.db = Database(self.config)
        self.db.init_schema()

        # Patch LLM Client to prevent actual network calls during tests
        self.llm_patcher = patch("ar0.orchestrator.LLMClient.call", return_value='{}')
        self.mock_llm_call = self.llm_patcher.start()

        self.orchestrator = Orchestrator(self.config, self.db)

    def tearDown(self):
        self.llm_patcher.stop()
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
             patch.object(self.orchestrator.runner, "validate_syntax", return_value=(True, "")), \
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

        with patch.object(self.orchestrator, "run_builder_phase", return_value=builder_payload), \
             patch.object(self.orchestrator.runner, "execute_shell") as mock_shell, \
             patch.object(self.orchestrator.runner, "validate_syntax", return_value=(True, "")), \
             patch.object(self.orchestrator, "run_tester_phase", return_value=(False, "Assertion error")):

            mock_shell.return_value.returncode = 0
            mock_shell.return_value.stdout = "OK"
            mock_shell.return_value.stderr = ""

            status = self.orchestrator.execute_workflow("T1")
            self.assertEqual(status, "PASS")

        task = self.db.get_task("T1")
        self.assertEqual(task[2], "PASS")

    @patch("builtins.input", return_value="y")
    @patch("ar0.orchestrator.Orchestrator.run_builder_phase")
    @patch("ar0.orchestrator.Orchestrator.run_tester_phase")
    def test_execute_workflow_builder_syntax_failure_autoretries_before_human_approval(self, mock_tester, mock_builder, mock_input):
        with self.db.get_connection() as conn:
            conn.execute("INSERT INTO tasks (id, role, description, status, retry_count) VALUES ('T1', 'BUILDER', 'Test Task', 'PENDING', 0)")
            conn.commit()

        mock_builder.return_value = {
            "thought": "Writing broken code",
            "action": "execute_shell",
            "command": "cat << 'EOF' > src/main.go\npackage main\nEOF"
        }

        self.orchestrator.runner.execute_shell = MagicMock(return_value=MagicMock(returncode=0, stdout="", stderr=""))
        self.orchestrator.runner.validate_syntax = MagicMock(return_value=(False, "Go compilation error"))

        status = self.orchestrator.execute_workflow("T1")

        self.assertEqual(status, "BLOCKED")
        mock_tester.assert_not_called()
        mock_input.assert_not_called()

    @patch("ar0.orchestrator.Orchestrator.run_builder_phase")
    @patch("ar0.orchestrator.Orchestrator.run_tester_phase")
    def test_execute_workflow_noop_bypasses_tester_and_passes(self, mock_tester, mock_builder):
        with self.db.get_connection() as conn:
            conn.execute("INSERT INTO tasks (id, role, description, status, retry_count) VALUES ('T2', 'BUILDER', 'Noop Task', 'PENDING', 0)")
            conn.commit()

        mock_builder.return_value = {
            "thought": "Already done",
            "action": "no_op",
            "command": "NO_OP"
        }

        status = self.orchestrator.execute_workflow("T2")

        self.assertEqual(status, "PASS")
        mock_tester.assert_not_called()


if __name__ == "__main__":
    unittest.main()