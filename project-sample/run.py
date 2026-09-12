#!/usr/bin/env python3
import sqlite3
import subprocess
import requests
import json
import re
import os

MODEL_API_URL = "http://localhost:5001/v1/chat/completions"
DB_PATH = "testtask/execution.db"
PROMPT_DIR = "testtask/prompts"
LOG_DIR = "testtask/logs"

def log_to_file(task_id, role, content):
    """Writes verbose execution details to a dedicated log file."""
    os.makedirs(LOG_DIR, exist_ok=True)
    log_path = os.path.join(LOG_DIR, f"{task_id}.log")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"\n=== [{role}] ===\n{content}\n")

def load_prompt(filename):
    path = os.path.join(PROMPT_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Prompt file missing: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()

def get_workspace_context(target_dir="testtask"):
    """Reads workspace tree structure and full contents of core source files."""
    if not os.path.exists(target_dir):
        return "(Workspace empty)"

    context = []
    for root, dirs, files in os.walk(target_dir):
        # Exclude non-source directories
        dirs[:] = [d for d in dirs if d not in ('logs', '__pycache__', 'tests') and not d.startswith('.')]
        for file in files:
            if file.endswith('.py') and not file.startswith('test_'):
                full_path = os.path.join(root, file)
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    context.append(f"--- FILE: {full_path} ---\n{content}\n")
                except Exception as e:
                    context.append(f"--- FILE: {full_path} (Error reading: {e}) ---")

    return "\n".join(context) if context else "(No source files found in workspace)"

def parse_agent_response(raw_text):
    if not raw_text:
        return None

    # Standard attempt
    try:
        data = json.loads(raw_text.strip())
        if isinstance(data, dict): return data
    except json.JSONDecodeError:
        pass

    # Regex capture for JSON boundaries
    json_match = re.search(r'(\{.*\}|\[.*\])', raw_text, re.DOTALL)
    if json_match:
        extracted = json_match.group(0)
        try:
            data = json.loads(extracted)
            if isinstance(data, dict): return data
            if isinstance(data, list) and len(data) > 0: return data[0]
        except json.JSONDecodeError:
            # Escape raw line breaks inside JSON strings if the LLM output raw multi-line strings
            sanitized = re.sub(r'(?<!\\)\n', r'\\n', extracted)
            try:
                data = json.loads(sanitized)
                if isinstance(data, dict): return data
            except json.JSONDecodeError:
                pass

    return None

def call_local_llm(system_prompt, user_prompt):
    payload = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.1,
        "response_format": {"type": "json_object"}
    }
    try:
        response = requests.post(MODEL_API_URL, json=payload)
        return response.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"[ERROR] LLM Request failed: {e}")
        return ""

def run_planner_phase(spec_text):
    system_prompt = load_prompt("planner_system.txt")
    user_prompt = f"Decompose the following specification into 3-4 coarse tasks:\n\n{spec_text}"

    raw_response = call_local_llm(system_prompt, user_prompt)

    try:
        tasks = json.loads(raw_response)
        if isinstance(tasks, list):
            return tasks
    except json.JSONDecodeError:
        match = re.search(r'\[.*\]', raw_response, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
    return []

def run_builder_phase(task_id, description, last_feedback=""):
    system_prompt = load_prompt("builder_system.txt")
    context = get_workspace_context()

    user_prompt = (
        f"CURRENT WORKSPACE CONTEXT:\n{context}\n\n"
        f"Task: {description}"
    )
    if last_feedback:
        user_prompt += f"\n\nPREVIOUS ATTEMPT FAILED WITH FEEDBACK:\n{last_feedback}\nPlease fix the issues."

    raw_response = call_local_llm(system_prompt, user_prompt)
    parsed = parse_agent_response(raw_response)

    if not parsed:
        print("[ORCHESTRATOR ERROR] Builder returned completely invalid JSON.")
        return None
    if "command" not in parsed:
        print("[ORCHESTRATOR ERROR] Builder JSON missing required 'command' field.")
        log_to_file(task_id, "BUILDER_RAW_RESPONSE", raw_response)
        return None

    return parsed

def run_tester_phase(task_id, description, builder_output):
    system_prompt = load_prompt("tester_system.txt")
    context = get_workspace_context()

    user_prompt = (
        f"CURRENT WORKSPACE CONTEXT:\n{context}\n\n"
        f"Target Task: {description}\n"
        f"Builder Changes: {builder_output}\n"
        f"Author unit tests in testtask/tests/ and execute them."
    )

    raw_response = call_local_llm(system_prompt, user_prompt)
    parsed = parse_agent_response(raw_response)

    if not parsed or "command" not in parsed:
        return False, "Tester failed to return a valid JSON command schema."

    log_to_file(task_id, "TESTER_THOUGHT", parsed.get("thought", "N/A"))
    log_to_file(task_id, "TESTER_COMMAND", parsed["command"])

    print(f"\n[TESTER THOUGHT]: {parsed.get('thought', 'N/A')}")
    print(f"[TESTER COMMAND]:\n{parsed['command']}\n")

    approval = input("Approve TESTER execution? (y/n): ").strip().lower()
    if approval != 'y':
        return False, "Tester execution rejected by human operator."

    result = subprocess.run(parsed['command'], shell=True, capture_output=True, text=True)
    log_output = f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    log_to_file(task_id, "TESTER_OUTPUT", log_output)

    if result.returncode == 0:
        return True, result.stdout
    else:
        return False, f"Test execution failed (Exit Code {result.returncode}).\n{result.stderr if result.stderr else result.stdout}"

def validate_python_syntax(target_dir="testtask/src"):
    """
    Scans modified Python files and ensures they compile without SyntaxError.
    """
    for root, _, files in os.walk(target_dir):
        for file in files:
            if file.endswith('.py'):
                full_path = os.path.join(root, file)
                res = subprocess.run(
                    f"python3 -m py_compile {full_path}",
                    shell=True, capture_output=True, text=True
                )
                if res.returncode != 0:
                    return False, f"Syntax error in {full_path}:\n{res.stderr}"
    return True, ""

def execute_workflow(task_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT role, description, status, retry_count FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    if not row:
        print(f"Task {task_id} not found.")
        conn.close()
        return "FAIL"

    role, description, status, retries = row

    if retries >= 3:
        print(f"[ORCHESTRATOR] Task {task_id} BLOCKED: Retry limit (3) reached.")
        cursor.execute("UPDATE tasks SET status = 'BLOCKED' WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()
        return "BLOCKED"

    cursor.execute("SELECT feedback FROM verifications WHERE task_id = ? AND result = 'FAIL' ORDER BY id DESC LIMIT 1", (task_id,))
    feedback_row = cursor.fetchone()
    last_feedback = feedback_row[0] if feedback_row else ""

    print(f"\n==========================================")
    print(f"[ORCHESTRATOR] Task {task_id} | Attempt {retries + 1}/3")
    print(f"Description: {description}")
    print(f"==========================================")

    # 1. BUILDER PHASE
    builder_payload = run_builder_phase(task_id, description, last_feedback)
    if not builder_payload or "command" not in builder_payload:
        print("[ORCHESTRATOR] Failed to parse JSON from Builder. Retrying...")
        cursor.execute("UPDATE tasks SET status = 'FAIL', retry_count = retry_count + 1 WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()
        return "FAIL"

    log_to_file(task_id, "BUILDER_THOUGHT", builder_payload.get("thought", "N/A"))
    log_to_file(task_id, "BUILDER_COMMAND", builder_payload["command"])

    print(f"\n[BUILDER THOUGHT]: {builder_payload.get('thought', 'N/A')}")
    print(f"[BUILDER COMMAND]:\n{builder_payload['command']}\n")

    if input("Approve BUILDER execution? (y/n): ").strip().lower() != 'y':
        print("[ORCHESTRATOR] Builder denied by human operator.")
        conn.close()
        return "BLOCKED"

    # 1. BUILDER EXECUTION
    res = subprocess.run(builder_payload['command'], shell=True, capture_output=True, text=True)

    # 2. IMMEDIATE SYNTAX SANITY CHECK
    valid_syntax, syntax_error = validate_python_syntax()
    if not valid_syntax:
        print(f"\n[BUILDER RESULT] FAIL - Code broke Python syntax checks!")
        print(syntax_error)
        cursor.execute("UPDATE tasks SET status = 'FAIL', retry_count = retry_count + 1 WHERE id = ?", (task_id,))
        cursor.execute("INSERT INTO verifications (task_id, verifier_role, result, feedback) VALUES (?, 'TESTER', 'FAIL', ?)",
                       (task_id, syntax_error))
        conn.commit()
        conn.close()
        return "FAIL"

    log_to_file(task_id, "BUILDER_OUTPUT", f"STDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}")

    cursor.execute("INSERT INTO execution_logs (task_id, role, command, output, exit_code) VALUES (?, 'BUILDER', ?, ?, ?)",
                   (task_id, builder_payload['command'], res.stdout + res.stderr, res.returncode))

    if res.returncode != 0:
        print(f"[BUILDER RESULT] FAIL (Exit Code {res.returncode})")
        cursor.execute("UPDATE tasks SET status = 'FAIL', retry_count = retry_count + 1 WHERE id = ?", (task_id,))
        cursor.execute("INSERT INTO verifications (task_id, verifier_role, result, feedback) VALUES (?, 'TESTER', 'FAIL', ?)",
                       (task_id, res.stderr if res.stderr else res.stdout))
        conn.commit()
        conn.close()
        return "FAIL"

    cursor.execute("UPDATE tasks SET status = 'REVIEW_PENDING' WHERE id = ?", (task_id,))
    conn.commit()

    # 2. VERIFICATION / TESTER PHASE
    print("\n[ORCHESTRATOR] Builder succeeded. Handing off to TESTER agent...")
    passed, test_feedback = run_tester_phase(task_id, description, res.stdout)

    final_status = "FAIL"
    if passed:
        print("\n[VERIFICATION RESULT] PASS! Task complete.")
        cursor.execute("UPDATE tasks SET status = 'PASS' WHERE id = ?", (task_id,))
        cursor.execute("INSERT INTO verifications (task_id, verifier_role, result, feedback) VALUES (?, 'TESTER', 'PASS', ?)",
                       (task_id, test_feedback))
        final_status = "PASS"
    else:
        print(f"\n[VERIFICATION RESULT] FAIL! Feedback captured for Builder retry.\nFeedback:\n{test_feedback}")
        cursor.execute("UPDATE tasks SET status = 'FAIL', retry_count = retry_count + 1 WHERE id = ?", (task_id,))
        cursor.execute("INSERT INTO verifications (task_id, verifier_role, result, feedback) VALUES (?, 'TESTER', 'FAIL', ?)",
                       (task_id, test_feedback))
        final_status = "FAIL"

    conn.commit()
    conn.close()
    return final_status

def seed_tasks_from_planner(spec_file_path):
    if not os.path.exists(spec_file_path):
        print(f"[ERROR] Specification file {spec_file_path} not found.")
        return False

    with open(spec_file_path, 'r', encoding='utf-8') as f:
        spec_content = f.read()

    print("\n[ORCHESTRATOR] Invoking PLANNER agent...")
    tasks = run_planner_phase(spec_content)

    if not tasks:
        print("[ERROR] Planner failed to generate structured tasks.")
        return False

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    print(f"\n[PLANNER PROPOSAL] Generated {len(tasks)} tasks:")
    for t in tasks:
        print(f"  - [{t['id']}] ({t['role']}): {t['description']}")
        c.execute("""
            INSERT OR REPLACE INTO tasks (id, role, description, status, retry_count)
            VALUES (?, ?, ?, 'PENDING', 0)
        """, (t['id'], t['role'], t['description']))

    conn.commit()
    conn.close()

    return input("\nApprove PLANNER task list to start execution loop? (y/n): ").strip().lower() == 'y'

def run_project_queue():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Fetch tasks that are PENDING or FAIL, skipping PASS
    c.execute("SELECT id FROM tasks WHERE status IN ('PENDING', 'FAIL') ORDER BY id ASC")
    pending_tasks = [row[0] for row in c.fetchall()]
    conn.close()

    if not pending_tasks:
        print("\n[ORCHESTRATOR] All tasks are marked PASS! Project build complete.")
        return

    print(f"\n[ORCHESTRATOR] Resuming build queue. {len(pending_tasks)} task(s) remaining...")
    for task_id in pending_tasks:
        status = execute_workflow(task_id)
        if status != "PASS":
            print(f"\n[ORCHESTRATOR] Workflow halted on {task_id}. Fix issues before resuming.")
            break

if __name__ == "__main__":
    spec_path = "testtask/PROJECT_SPEC.md"

    # Check if we have an active state in SQLite
    has_existing_tasks = False
    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM tasks")
        count = c.fetchone()[0]
        has_existing_tasks = count > 0
        conn.close()

    if has_existing_tasks:
        print("[ORCHESTRATOR] Existing project database detected.")
        resume = input("Resume current project from last checkpoint? (y/n): ").strip().lower()
        if resume == 'y':
            run_project_queue()
        else:
            if seed_tasks_from_planner(spec_path):
                run_project_queue()
    else:
        if seed_tasks_from_planner(spec_path):
            run_project_queue()
