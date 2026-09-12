#!/usr/bin/env python3
import sqlite3
import subprocess
import requests
import json
import os

MODEL_API_URL = "http://localhost:5001/v1/chat/completions"
DB_PATH = "testtask/execution.db"

def call_local_llm(system_prompt, user_prompt):
    payload = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.2
    }
    response = requests.post(MODEL_API_URL, json=payload)
    return response.json()['choices'][0]['message']['content'].strip()

def run_builder_phase(task_id, description, last_feedback=""):
    system_prompt = """You are the BUILDER agent in Agent-0.
Your task is to write code or execute shell actions.
You MUST output ONLY executable bash commands to perform the work.
Do NOT use markdown formatting or explanations. Just raw bash commands."""

    user_prompt = f"Task: {description}"
    if last_feedback:
        user_prompt += f"\n\nPREVIOUS ATTEMPT FAILED WITH FEEDBACK:\n{last_feedback}\nPlease fix the issues."

    return call_local_llm(system_prompt, user_prompt)

def run_tester_phase(task_id, description, builder_output):
    system_prompt = """You are the TESTER agent in Agent-0.
Your task is to generate shell commands that run test suites, linters, or verification checks against the Builder's output.
You MUST output ONLY executable bash commands (e.g., pytest, python3 -m unittest, go test, etc.).
Do NOT use markdown or conversational text."""

    user_prompt = f"Target Task: {description}\nBuilder Output/Changes: {builder_output}\nProvide the test/validation command."

    test_cmd = call_local_llm(system_prompt, user_prompt)
    print(f"\n[TESTER PROPOSAL]:\n{test_cmd}\n")

    approval = input("Approve TESTER execution? (y/n): ").strip().lower()
    if approval != 'y':
        return False, "Tester execution rejected by human operator."

    result = subprocess.run(test_cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        return True, result.stdout
    else:
        return False, f"Test failed with exit code {result.returncode}.\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"

def execute_workflow(task_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Fetch task and verify retry constraints
    cursor.execute("SELECT role, description, status, retry_count FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    if not row:
        print(f"Task {task_id} not found.")
        return

    role, description, status, retries = row

    if retries >= 3:
        print(f"[ORCHESTRATOR] Task {task_id} BLOCKED: Retry limit (3) reached.")
        cursor.execute("UPDATE tasks SET status = 'BLOCKED' WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()
        return

    # Fetch last failure feedback if available
    cursor.execute("SELECT feedback FROM verifications WHERE task_id = ? AND result = 'FAIL' ORDER BY id DESC LIMIT 1", (task_id,))
    feedback_row = cursor.fetchone()
    last_feedback = feedback_row[0] if feedback_row else ""

    print(f"\n==========================================")
    print(f"[ORCHESTRATOR] Starting Task {task_id} | Attempt {retries + 1}/3")
    print(f"Description: {description}")
    print(f"==========================================")

    # 2. BUILDER PHASE
    cmd = run_builder_phase(task_id, description, last_feedback)
    print(f"\n[BUILDER PROPOSAL]:\n{cmd}\n")

    if input("Approve BUILDER execution? (y/n): ").strip().lower() != 'y':
        print("[ORCHESTRATOR] Builder denied by human operator.")
        return

    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    # Log execution
    cursor.execute("INSERT INTO execution_logs (task_id, role, command, output, exit_code) VALUES (?, 'BUILDER', ?, ?, ?)",
                   (task_id, cmd, res.stdout + res.stderr, res.returncode))

    if res.returncode != 0:
        print(f"[BUILDER RESULT] FAIL (Exit Code {res.returncode})")
        cursor.execute("UPDATE tasks SET status = 'FAIL', retry_count = retry_count + 1 WHERE id = ?", (task_id,))
        cursor.execute("INSERT INTO verifications (task_id, verifier_role, result, feedback) VALUES (?, 'BUILDER', 'FAIL', ?)",
                       (task_id, res.stderr))
        conn.commit()
        conn.close()
        return

    # Builder succeeded, move to REVIEW_PENDING
    cursor.execute("UPDATE tasks SET status = 'REVIEW_PENDING' WHERE id = ?", (task_id,))
    conn.commit()

    # 3. VERIFICATION / TESTER PHASE
    print("\n[ORCHESTRATOR] Builder succeeded. Handing off to TESTER agent...")
    passed, test_feedback = run_tester_phase(task_id, description, res.stdout)

    if passed:
        print("\n[VERIFICATION RESULT] PASS! Task marked as fully complete.")
        cursor.execute("UPDATE tasks SET status = 'PASS' WHERE id = ?", (task_id,))
        cursor.execute("INSERT INTO verifications (task_id, verifier_role, result, feedback) VALUES (?, 'TESTER', 'PASS', ?)",
                       (task_id, test_feedback))
    else:
        print(f"\n[VERIFICATION RESULT] FAIL! Feedback captured for Builder retry.\nFeedback: {test_feedback}")
        cursor.execute("UPDATE tasks SET status = 'FAIL', retry_count = retry_count + 1 WHERE id = ?", (task_id,))
        cursor.execute("INSERT INTO verifications (task_id, verifier_role, result, feedback) VALUES (?, 'TESTER', 'FAIL', ?)",
                       (task_id, test_feedback))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    # Seed a task that requires a simple test suite
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO tasks (id, role, description, status, retry_count)
        VALUES ('TASK-002', 'BUILDER', 'Write a Python function in testtask/src/math_utils.py called add(a, b) that returns the sum of two numbers. Also write a unit test in testtask/tests/test_math.py using unittest.', 'PENDING', 0)
    """)
    conn.commit()
    conn.close()

    execute_workflow("TASK-002")
