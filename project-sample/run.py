#!/usr/bin/env python3
import sqlite3
import subprocess
import requests
import json
import sys
import os

MODEL_API_URL = "http://localhost:5001/v1/chat/completions" # Adjust to your local endpoint
PROJECT_ROOT = "testtask"
DB_PATH = PROJECT_ROOT + "/execution.db"

def call_local_llm(prompt, role="BUILDER"):
    system_prompt = f"""You are the {role} agent in the Agent-0 workflow.
You MUST output ONLY executable bash commands to achieve the requested task.
Do NOT use markdown code blocks or explanatory text. Just raw bash commands.
Work strictly within local project boundaries."""

    payload = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }

    response = requests.post(MODEL_API_URL, json=payload)
    return response.json()['choices'][0]['message']['content'].strip()

def run_task(task_id, role, description):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check retry limits
    cursor.execute("SELECT retry_count FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    retries = row[0] if row else 0

    if retries >= 3:
        print(f"Task {task_id} blocked: Exceeded maximum 3 retry attempts.")
        cursor.execute("UPDATE tasks SET status = 'BLOCKED' WHERE id = ?", (task_id,))
        conn.commit()
        return

    print(f"\n[ORCHESTRATOR] Executing Task {task_id} (Attempt {retries + 1}/3)...")

    # 1. Get command from LLM
    cmd = call_local_llm(f"Task: {description}", role)
    print(f"[AGENT PROPOSAL]:\n{cmd}\n")

    # 2. Human Orchestrator Gate (Interactively approve command)
    approval = input("Approve execution? (y/n): ").strip().lower()
    if approval != 'y':
        print("[ORCHESTRATOR] Execution denied by human operator.")
        cursor.execute("UPDATE tasks SET status = 'BLOCKED' WHERE id = ?", (task_id,))
        conn.commit()
        return

    # 3. Isolated Execution
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    status = "PASS" if result.returncode == 0 else "FAIL"

    # 4. Audit Trail & State Update
    cursor.execute("""
        INSERT INTO execution_logs (task_id, role, command, output, exit_code)
        VALUES (?, ?, ?, ?, ?)
    """, (task_id, role, cmd, result.stdout + result.stderr, result.returncode))

    if status == "PASS":
        cursor.execute("UPDATE tasks SET status = 'PASS' WHERE id = ?", (task_id,))
        print(f"[RESULT] PASS (Exit Code 0)")
    else:
        cursor.execute("UPDATE tasks SET status = 'FAIL', retry_count = retry_count + 1 WHERE id = ?", (task_id,))
        print(f"[RESULT] FAIL (Exit Code {result.returncode})\nError: {result.stderr}")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    # Seed DB with task
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO tasks (id, role, description) VALUES ('TASK-001', 'BUILDER', 'Create a script in " + PROJECT_ROOT + "/src/hello.py that prints hello')")
    conn.commit()
    conn.close()

    run_task("TASK-001", "BUILDER", "Create a Python file named " + PROJECT_ROOT + "/src/hello.py containing print('Hello Agent-0')")
