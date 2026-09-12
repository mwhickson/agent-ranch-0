#!/usr/bin/env python3
import sqlite3
import subprocess
import requests
import json
import re

MODEL_API_URL = "http://localhost:5001/v1/chat/completions"
DB_PATH = "testtask/execution.db"

def parse_agent_response(raw_text):
    """
    Extracts and normalizes JSON payloads from local LLMs,
    handling single dicts, arrays of dicts, or markdown wrappers.
    """
    try:
        data = json.loads(raw_text.strip())
    except json.JSONDecodeError:
        # Regex extraction to handle extra text or markdown code blocks around JSON
        json_match = re.search(r'(\[.*\]|\{.*\})', raw_text, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group(0))
            except json.JSONDecodeError:
                return None
        else:
            return None

    # Normalization Step: Merge list of dicts into a single dict if necessary
    if isinstance(data, list):
        merged = {}
        for item in data:
            if isinstance(item, dict):
                merged.update(item)
        return merged
    elif isinstance(data, dict):
        return data

    return None

def call_local_llm(system_prompt, user_prompt):
    payload = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.1,  # Lower temperature for strict JSON adherence
        "response_format": {"type": "json_object"}  # Native JSON mode for supported endpoints
    }
    try:
        response = requests.post(MODEL_API_URL, json=payload)
        return response.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"[ERROR] LLM Request failed: {e}")
        return ""

def run_builder_phase(task_id, description, last_feedback=""):
    system_prompt = """You are the BUILDER agent in Agent-0.
Provide an executable bash command to complete the task.

Respond ONLY with a single JSON object following this EXACT format:

{
  "thought": "Your step-by-step plan",
  "action": "execute_shell",
  "command": "mkdir -p testtask/src testtask/tests && cat << 'EOF' > testtask/src/string_utils.py\ndef reverse_string(s):\n    return s[::-1]\nEOF\ncat << 'EOF' > testtask/tests/test_strings.py\nimport unittest\nfrom testtask.src.string_utils import reverse_string\n\nclass TestStrings(unittest.TestCase):\n    def test_reverse(self):\n        self.assertEqual(reverse_string('hello'), 'olleh')\n\nif __name__ == '__main__':\n    unittest.main()\nEOF"
}

Do NOT output arrays or text outside the JSON object."""

    user_prompt = f"Task: {description}"
    if last_feedback:
        user_prompt += f"\n\nPREVIOUS ATTEMPT FAILED WITH FEEDBACK:\n{last_feedback}\nPlease fix the issues."

    raw_response = call_local_llm(system_prompt, user_prompt)
    return parse_agent_response(raw_response)

def run_tester_phase(task_id, description, builder_output):
    system_prompt = """You are the TESTER agent in Agent-0.
Your task is to generate shell commands that run test suites, linters, or verification checks against the Builder's output.
You MUST reply strictly in JSON format matching this schema:
{
  "thought": "Brief explanation of test strategy",
  "action": "run_test",
  "command": "exact test command (e.g. python3 -m unittest discover testtask/tests)"
}
Do NOT include markdown formatting or extra text outside the JSON object."""

    user_prompt = f"Target Task: {description}\nBuilder Output/Changes: {builder_output}\nProvide the test/validation command."

    raw_response = call_local_llm(system_prompt, user_prompt)
    parsed = parse_agent_response(raw_response)

    if not parsed or "command" not in parsed:
        return False, "Tester failed to return a valid JSON command schema."

    print(f"\n[TESTER THOUGHT]: {parsed.get('thought', 'N/A')}")
    print(f"[TESTER COMMAND]: {parsed['command']}\n")

    approval = input("Approve TESTER execution? (y/n): ").strip().lower()
    if approval != 'y':
        return False, "Tester execution rejected by human operator."

    result = subprocess.run(parsed['command'], shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        return True, result.stdout
    else:
        return False, f"Test failed with exit code {result.returncode}.\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"

def execute_workflow(task_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

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

    cursor.execute("SELECT feedback FROM verifications WHERE task_id = ? AND result = 'FAIL' ORDER BY id DESC LIMIT 1", (task_id,))
    feedback_row = cursor.fetchone()
    last_feedback = feedback_row[0] if feedback_row else ""

    print(f"\n==========================================")
    print(f"[ORCHESTRATOR] Starting Task {task_id} | Attempt {retries + 1}/3")
    print(f"Description: {description}")
    print(f"==========================================")

    # 1. BUILDER PHASE
    builder_payload = run_builder_phase(task_id, description, last_feedback)
    if not builder_payload or "command" not in builder_payload:
        print("[ORCHESTRATOR] Failed to parse a valid JSON payload from Builder. Retrying task...")
        cursor.execute("UPDATE tasks SET status = 'FAIL', retry_count = retry_count + 1 WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()
        return

    print(f"\n[BUILDER THOUGHT]: {builder_payload.get('thought', 'N/A')}")
    print(f"[BUILDER COMMAND]:\n{builder_payload['command']}\n")

    if input("Approve BUILDER execution? (y/n): ").strip().lower() != 'y':
        print("[ORCHESTRATOR] Builder denied by human operator.")
        conn.close()
        return

    res = subprocess.run(builder_payload['command'], shell=True, capture_output=True, text=True)

    cursor.execute("INSERT INTO execution_logs (task_id, role, command, output, exit_code) VALUES (?, 'BUILDER', ?, ?, ?)",
                   (task_id, builder_payload['command'], res.stdout + res.stderr, res.returncode))

    if res.returncode != 0:
        print(f"[BUILDER RESULT] FAIL (Exit Code {res.returncode})")
        cursor.execute("UPDATE tasks SET status = 'FAIL', retry_count = retry_count + 1 WHERE id = ?", (task_id,))
        cursor.execute("INSERT INTO verifications (task_id, verifier_role, result, feedback) VALUES (?, 'BUILDER', 'FAIL', ?)",
                       (task_id, res.stderr))
        conn.commit()
        conn.close()
        return

    cursor.execute("UPDATE tasks SET status = 'REVIEW_PENDING' WHERE id = ?", (task_id,))
    conn.commit()

    # 2. VERIFICATION / TESTER PHASE
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
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO tasks (id, role, description, status, retry_count)
        VALUES ('TASK-003', 'BUILDER', 'Write a Python function in testtask/src/string_utils.py called reverse_string(s) that reverses a string. Create a test case in testtask/tests/test_strings.py using unittest.', 'PENDING', 0)
    """)
    conn.commit()
    conn.close()

    execute_workflow("TASK-003")
