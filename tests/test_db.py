import tempfile
import unittest
from ar0.config import Config
from ar0.db import Database


class TestDatabase(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config = Config(project_dir=self.temp_dir.name)
        self.db = Database(self.config)
        self.db.init_schema()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_init_schema_and_task_lifecycle(self):
        with self.db.get_connection() as conn:
            conn.execute(
                "INSERT INTO tasks (id, role, description) VALUES ('T1', 'BUILDER', 'Write app')"
            )

        task = self.db.get_task("T1")
        self.assertEqual(task, ('BUILDER', 'Write app', 'PENDING', 0))

        # Update status and increment retry
        self.db.update_task_status("T1", "FAIL", increment_retry=True)
        task = self.db.get_task("T1")
        self.assertEqual(task[2], "FAIL")
        self.assertEqual(task[3], 1)

    def test_verifications_and_feedback(self):
        self.db.log_verification("T1", "TESTER", "FAIL", "AssertionError: Expected 50 got 10")
        verifier_role, feedback = self.db.get_last_failure_feedback("T1")
        self.assertEqual(verifier_role, "TESTER")
        self.assertEqual(feedback, "AssertionError: Expected 50 got 10")

    def test_get_pending_tasks(self):
        with self.db.get_connection() as conn:
            conn.execute("INSERT INTO tasks (id, role, description, status) VALUES ('T1', 'BUILDER', 'D1', 'PENDING')")
            conn.execute("INSERT INTO tasks (id, role, description, status) VALUES ('T2', 'BUILDER', 'D2', 'FAIL')")
            conn.execute("INSERT INTO tasks (id, role, description, status) VALUES ('T3', 'BUILDER', 'D3', 'PASS')")

        pending = self.db.get_pending_tasks()
        self.assertEqual(pending, ["T1", "T2"])


if __name__ == "__main__":
    unittest.main()