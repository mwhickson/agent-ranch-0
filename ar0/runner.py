import os
import subprocess
from ar0.config import Config

class TaskRunner:
    def __init__(self, config: Config):
        self.config = config

    def log_to_file(self, task_id: str, role: str, content: str):
        os.makedirs(self.config.log_dir, exist_ok=True)
        log_path = os.path.join(self.config.log_dir, f"{task_id}.log")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"\n=== [{role}] ===\n{content}\n")

    def get_workspace_context(self) -> str:
        project_root = os.path.abspath(self.config.project_dir)
        tree_output = []
        file_contents = []

        for root, dirs, files in os.walk(project_root):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            rel_root = os.path.relpath(root, project_root)
            if rel_root == ".":
                rel_root = ""

            for f in files:
                rel_path = os.path.join(rel_root, f) if rel_root else f
                tree_output.append(rel_path)

                # Read contents of source files so Builder never needs to 'cat' them
                if f.endswith('.py') and ('src' in rel_path or 'tests' in rel_path):
                    full_path = os.path.join(root, f)
                    try:
                        with open(full_path, 'r', encoding='utf-8') as file_ref:
                            file_contents.append(f"--- FILE: {rel_path} ---\n{file_ref.read().strip()}\n")
                    except Exception as e:
                        file_contents.append(f"--- FILE: {rel_path} --- (Error reading file: {e})\n")

        context = f"PROJECT ROOT: {project_root}\n\n"
        context += "WORKSPACE STRUCTURE:\n" + ("\n".join(f"- {p}" for p in tree_output) if tree_output else "- (empty)") + "\n\n"
        context += "EXISTING FILE CONTENTS:\n" + ("\n".join(file_contents) if file_contents else "(No python files written yet)")

        return context

    def validate_python_syntax(self) -> tuple[bool, str]:
        src_dir = os.path.join(self.config.project_dir, "src")
        if not os.path.exists(src_dir):
            return True, ""

        for root, _, files in os.walk(src_dir):
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

    def execute_shell(self, command: str) -> subprocess.CompletedProcess:
        # Build dynamic PYTHONPATH including the project root and its src/ directory
        project_root = os.path.abspath(self.config.project_dir)
        src_dir = os.path.join(project_root, "src")

        current_pythonpath = os.environ.get("PYTHONPATH", "")
        new_pythonpath = f"{project_root}:{src_dir}:{current_pythonpath}".strip(":")

        env = os.environ.copy()
        env["PYTHONPATH"] = new_pythonpath

        return subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=self.config.project_dir,  # Ensures commands execute inside the project directory
            env=env
        )
