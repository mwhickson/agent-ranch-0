import os
import json
import re
from ar0.config import Config
from ar0.db import Database
from ar0.llm import LLMClient
from ar0.runner import TaskRunner

class Orchestrator:
    def __init__(self, config: Config, db: Database):
        self.config = config
        self.db = db
        self.llm = LLMClient(config)
        self.runner = TaskRunner(config)

    def load_prompt(self, filename: str) -> str:
        path = os.path.join(self.config.prompt_dir, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Prompt file missing: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()

    def run_planner_phase(self, spec_text: str) -> list:
        system_prompt = self.load_prompt("planner_system.txt")
        user_prompt = f"Decompose the following specification into human-auditable engineering tasks:\n\n{spec_text}"

        raw_response = self.llm.call(system_prompt, user_prompt)
        parsed = self.llm.parse_json(raw_response)

        if isinstance(parsed, list):
            return parsed
        elif isinstance(parsed, dict):
            for key in ("tasks", "plan", "items"):
                if key in parsed and isinstance(parsed[key], list):
                    return parsed[key]

        print(f"[ORCHESTRATOR DEBUG] Raw Planner Output:\n{raw_response}")
        return []

    def run_builder_phase(self, task_id: str, description: str, last_feedback: str = "") -> dict:
        system_prompt = self.load_prompt("builder_system.txt")
        context = self.runner.get_workspace_context()

        user_prompt = (
            f"CURRENT WORKSPACE CONTEXT:\n{context}\n\n"
            f"Task: {description}"
        )
        if last_feedback:
            user_prompt += f"\n\nPREVIOUS ATTEMPT FAILED WITH FEEDBACK:\n{last_feedback}\nPlease fix the issues."

        raw_response = self.llm.call(system_prompt, user_prompt)
        parsed = self.llm.parse_json(raw_response)

        if not parsed:
            print("[ORCHESTRATOR ERROR] Builder returned completely invalid JSON.")
            return None

        if "command" not in parsed:
            print("[ORCHESTRATOR ERROR] Builder JSON missing required 'command' field.")
            self.runner.log_to_file(task_id, "BUILDER_RAW_RESPONSE", raw_response)
            return None

        builder_command = parsed.get("command", "").strip()
        action = parsed.get("action", "")

        is_noop = action == "no_op" or builder_command == "NO_OP"

        if not is_noop:
            # Reject commands that don't attempt to write files or modify state
            if not any(writer in builder_command for writer in [">", "cat <<", "touch", "cp", "mv"]):
                print("[ORCHESTRATOR ERROR] Builder command issued a passive/read-only shell operation!")
                return None

        return parsed

    def run_tester_phase(self, task_id: str, description: str, builder_output: str, is_noop: bool = False, test_error_context: str = None) -> tuple[bool, str]:
        system_prompt = self.load_prompt("tester_system.txt")
        context = self.runner.get_workspace_context()

        if test_error_context:
            user_prompt = (
                f"CURRENT WORKSPACE CONTEXT:\n{context}\n\n"
                f"Target Task: {description}\n\n"
                f"ATTENTION: Your previous test execution failed with the following output:\n"
                f"{test_error_context}\n\n"
                f"INSTRUCTION: Inspect the source code in workspace context versus your test code. "
                f"If the failure was caused by a bug in your test logic, mock side_effects, or missing/incorrect assertions, "
                f"REWRITE AND FIX YOUR TEST FILE in `tests/`. Do NOT change the source code in `src/`."
            )
        else:
            user_prompt = (
                f"CURRENT WORKSPACE CONTEXT:\n{context}\n\n"
                f"Target Task: {description}\n"
                f"Builder Output / Command:\n{builder_output}\n\n"
                f"INSTRUCTION: Read the existing code carefully. Write unit tests ONLY for functions that actually exist. "
                f"If testing interactive loops, mock input/print carefully so side_effects match expected game loop flow."
            )

        raw_response = self.llm.call(system_prompt, user_prompt)
        payload = self.llm.parse_json(raw_response)

        if not payload or "command" not in payload:
            return False, "Tester failed to generate a valid test payload."

        self.runner.log_to_file(task_id, "TESTER_THOUGHT", payload.get("thought", "N/A"))
        self.runner.log_to_file(task_id, "TESTER_COMMAND", payload["command"])

        print(f"\n[TESTER THOUGHT]: {payload.get('thought', 'N/A')}")
        print(f"[TESTER COMMAND]:\n{payload['command']}\n")

        res = self.runner.execute_shell(payload['command'])
        self.runner.log_to_file(task_id, "TESTER_OUTPUT", f"STDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}")

        if res.returncode == 0:
            return True, res.stdout
        else:
            return False, res.stderr if res.stderr else res.stdout

    def execute_workflow(self, task_id: str) -> str:
        row = self.db.get_task(task_id)
        if not row:
            print(f"Task {task_id} not found.")
            return "FAIL"

        role, description, status, retries = row

        while retries < self.config.max_retries:
            last_feedback = self.db.get_last_failure_feedback(task_id)

            print(f"\n==========================================")
            print(f"[ORCHESTRATOR] Task {task_id} | Attempt {retries + 1}/{self.config.max_retries}")
            print(f"Description: {description}")
            print(f"==========================================")

            # 1. BUILDER PHASE
            builder_payload = self.run_builder_phase(task_id, description, last_feedback)
            if not builder_payload:
                print("[ORCHESTRATOR] Builder phase failed (read-only command or invalid JSON). Retrying attempt...")
                self.db.update_task_status(task_id, 'FAIL', increment_retry=True)
                retries += 1
                last_feedback = "CRITICAL ERROR: Read-only bash commands (e.g. 'cat', 'ls') are strictly forbidden! You MUST write code using 'cat << EOF > src/file.py' or return a 'no_op'."
                self.db.log_verification(task_id, 'SYSTEM', 'FAIL', last_feedback)
                continue  # Loop back for immediate retry

            self.runner.log_to_file(task_id, "BUILDER_THOUGHT", builder_payload.get("thought", "N/A"))
            self.runner.log_to_file(task_id, "BUILDER_COMMAND", builder_payload["command"])

            print(f"\n[BUILDER THOUGHT]: {builder_payload.get('thought', 'N/A')}")
            print(f"[BUILDER COMMAND]:\n{builder_payload['command']}\n")

            if input("Approve BUILDER execution? (y/n): ").strip().lower() != 'y':
                print("[ORCHESTRATOR] Builder denied by human operator.")
                return "BLOCKED"

            is_builder_noop = builder_payload.get("action") == "no_op" or builder_payload["command"].strip() == "NO_OP"

            if is_builder_noop:
                print("\n[BUILDER RESULT] Task already satisfied. Skipping code execution...")
                builder_output = "NO_CHANGES: Code was already implemented."
            else:
                res = self.runner.execute_shell(builder_payload['command'])
                self.runner.log_to_file(task_id, "BUILDER_OUTPUT", f"STDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}")

                if res.returncode != 0:
                    print(f"[BUILDER RESULT] FAIL (Exit Code {res.returncode})")
                    self.db.update_task_status(task_id, 'FAIL', increment_retry=True)
                    self.db.log_verification(task_id, 'TESTER', 'FAIL', res.stderr if res.stderr else res.stdout)
                    retries += 1
                    continue

                valid_syntax, syntax_error = self.runner.validate_python_syntax()
                if not valid_syntax:
                    print(f"\n[BUILDER RESULT] FAIL - Code broke Python syntax checks!")
                    print(syntax_error)
                    self.db.update_task_status(task_id, 'FAIL', increment_retry=True)
                    self.db.log_verification(task_id, 'TESTER', 'FAIL', syntax_error)
                    retries += 1
                    continue

                builder_output = builder_payload.get("command", "")

            self.db.update_task_status(task_id, 'REVIEW_PENDING')

            # 2. VERIFICATION / TESTER PHASE
            print("\n[ORCHESTRATOR] Builder phase complete. Handing off to TESTER agent...")

            tester_loop_active = True
            test_error_context = None

            while tester_loop_active:
                max_tester_retries = 2
                passed = False
                test_feedback = ""

                for test_attempt in range(max_tester_retries):
                    if test_attempt > 0:
                        print(f"\n[ORCHESTRATOR] Asking TESTER to review/fix its own test suite (Attempt {test_attempt + 1}/{max_tester_retries})...")

                    passed, test_feedback = self.run_tester_phase(
                        task_id, description, builder_output, is_noop=is_builder_noop, test_error_context=test_error_context
                    )

                    if passed:
                        break
                    else:
                        test_error_context = test_feedback

                if passed:
                    print("\n[VERIFICATION RESULT] PASS! Task complete.")
                    self.db.update_task_status(task_id, 'PASS')
                    self.db.log_verification(task_id, 'TESTER', 'PASS', test_feedback)
                    return "PASS"

                print(f"\n[VERIFICATION RESULT] FAIL! Unit tests failed.\n--- Failure Context ---\n{test_feedback}\n-----------------------")

                # Interactive Operator Choice
                choice = input("\nAction needed: [b] Reject & Send to Builder | [t] Force Retry Tester | [p] Manual PASS override? (b/t/p): ").strip().lower()

                if choice == 'p':
                    print("[ORCHESTRATOR] Manual PASS override accepted by operator.")
                    self.db.update_task_status(task_id, 'PASS')
                    self.db.log_verification(task_id, 'TESTER', 'PASS', "Manual operator override.")
                    return "PASS"
                elif choice == 't':
                    print("[ORCHESTRATOR] Forcing another Tester retry...")
                    # Re-run tester loop with error context without leaving to Builder
                    test_error_context = test_feedback
                    continue
                else:
                    # Choice 'b' or default: Reject and send feedback to Builder
                    print("[ORCHESTRATOR] Rejecting build and sending feedback to Builder...")
                    self.db.update_task_status(task_id, 'FAIL', increment_retry=True)
                    self.db.log_verification(task_id, 'TESTER', 'FAIL', test_feedback)
                    retries += 1
                    tester_loop_active = False  # Break out to Builder loop

        print(f"[ORCHESTRATOR] Task {task_id} BLOCKED: Retry limit reached.")
        self.db.update_task_status(task_id, 'BLOCKED')
        return "BLOCKED"

    def seed_tasks_from_planner(self) -> bool:
        spec_path = self.config.spec_path
        if not os.path.exists(spec_path):
            print(f"[ERROR] Specification file {spec_path} not found.")
            return False

        with open(spec_path, 'r', encoding='utf-8') as f:
            spec_content = f.read()

        print("\n[ORCHESTRATOR] Invoking PLANNER agent...")
        tasks = self.run_planner_phase(spec_content)

        if not tasks:
            print("[ERROR] Planner failed to generate structured tasks.")
            return False

        print(f"\n[PLANNER PROPOSAL] Generated {len(tasks)} tasks:")
        with self.db.get_connection() as conn:
            for t in tasks:
                print(f"  - [{t['id']}] ({t['role']}): {t['description']}")
                conn.execute("""
                    INSERT OR REPLACE INTO tasks (id, role, description, status, retry_count)
                    VALUES (?, ?, ?, 'PENDING', 0)
                """, (t['id'], t['role'], t['description']))
            conn.commit()

        return input("\nApprove PLANNER task list to start execution loop? (y/n): ").strip().lower() == 'y'

    def run(self):
        pending_tasks = self.db.get_pending_tasks()

        if pending_tasks:
            print(f"[ORCHESTRATOR] Existing project database detected with uncompleted tasks.")
            resume = input("Resume current project from last checkpoint? (y/n): ").strip().lower()
            if resume != 'y':
                if not self.seed_tasks_from_planner():
                    return
        else:
            if not self.seed_tasks_from_planner():
                return

        pending_tasks = self.db.get_pending_tasks()
        print(f"\n[ORCHESTRATOR] Starting build queue. {len(pending_tasks)} task(s) to execute...")

        for task_id in pending_tasks:
            status = self.execute_workflow(task_id)
            if status != "PASS":
                print(f"\n[ORCHESTRATOR] Workflow halted on {task_id}. Fix issues before resuming.")
                break
