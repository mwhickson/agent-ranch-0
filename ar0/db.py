import sqlite3
from typing import List, Tuple, Optional
from ar0.config import Config

class Database:
    def __init__(self, config: Config):
        self.db_path = config.db_path

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_schema(self):
        """Ensures state tables exist inside the project database."""
        with self.get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    role TEXT NOT NULL,
                    description TEXT NOT NULL,
                    status TEXT CHECK(status IN ('PENDING', 'REVIEW_PENDING', 'PASS', 'FAIL', 'BLOCKED')) DEFAULT 'PENDING',
                    retry_count INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS verifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL,
                    verifier_role TEXT NOT NULL CHECK(verifier_role IN ('REVIEWER', 'SYSTEM', 'TESTER')),
                    result TEXT NOT NULL CHECK(result IN ('PASS', 'FAIL')),
                    feedback TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS execution_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT, role TEXT, command TEXT, output TEXT, exit_code INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            """)

    def get_task(self, task_id: str) -> Optional[Tuple]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT role, description, status, retry_count FROM tasks WHERE id = ?", (task_id,))
            return cursor.fetchone()

    def update_task_status(self, task_id: str, status: str, increment_retry: bool = False):
        with self.get_connection() as conn:
            if increment_retry:
                conn.execute("UPDATE tasks SET status = ?, retry_count = retry_count + 1 WHERE id = ?", (status, task_id))
            else:
                conn.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))

    def log_verification(self, task_id: str, role: str, result: str, feedback: str):
        with self.get_connection() as conn:
            conn.execute(
                "INSERT INTO verifications (task_id, verifier_role, result, feedback) VALUES (?, ?, ?, ?)",
                (task_id, role, result, feedback)
            )

    def get_last_failure_feedback(self, task_id: str) -> str:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT feedback FROM verifications WHERE task_id = ? AND result = 'FAIL' ORDER BY id DESC LIMIT 1",
                (task_id,)
            )
            row = cursor.fetchone()
            return row[0] if row else ""

    def get_pending_tasks(self) -> List[str]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM tasks WHERE status IN ('PENDING', 'FAIL') ORDER BY id ASC")
            return [row[0] for row in cursor.fetchall()]
