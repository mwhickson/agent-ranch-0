mkdir -p ./{.agent0/logs,src,tests}

# Initialize SQLite database for state management
sqlite3 .agent0/execution.db << 'EOF'
CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    role TEXT NOT NULL,
    description TEXT NOT NULL,
    status TEXT CHECK(status IN ('PENDING', 'PASS', 'FAIL', 'BLOCKED')) DEFAULT 'PENDING',
    retry_count INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS execution_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT,
    role TEXT,
    command TEXT,
    output TEXT,
    exit_code INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(task_id) REFERENCES tasks(id)
);
EOF
