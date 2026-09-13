import os
import re
from dataclasses import dataclass

@dataclass
class Config:
    project_dir: str
    model_api_url: str = "http://localhost:5001/v1/chat/completions"
    temperature: float = 0.1
    max_retries: int = 3
    timeout: int = 600  # Bump default to 10 minutes for local inference

    @property
    def db_path(self) -> str:
        return os.path.join(self.project_dir, "execution.db")

    @property
    def prompt_dir(self) -> str:
        return os.path.join(self.project_dir, "prompts")

    @property
    def log_dir(self) -> str:
        return os.path.join(self.project_dir, "logs")

    @property
    def spec_path(self) -> str:
        return os.path.join(self.project_dir, "PROJECT_SPEC.md")

    @classmethod
    def from_project_dir(cls, project_dir: str) -> "Config":
        spec_file = os.path.join(project_dir, "PROJECT_SPEC.md")
        config = cls(project_dir=project_dir)

        if os.path.exists(spec_file):
            with open(spec_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse optional inline config blocks from PROJECT_SPEC.md:
            # e.g. <!-- AR0_CONFIG: API_URL=http://localhost:5001/v1/chat/completions -->
            url_match = re.search(r"API_URL=(http[^\s\n]+)", content)
            if url_match:
                config.model_api_url = url_match.group(1)

            temp_match = re.search(r"TEMPERATURE=([0-9.]+)", content)
            if temp_match:
                config.temperature = float(temp_match.group(1))

        return config
