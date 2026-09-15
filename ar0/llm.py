import json
import re
import requests
from ar0.config import Config

class LLMClient:
    def __init__(self, config: Config):
        self.config = config

    def call(self, system_prompt: str, user_prompt: str) -> str:
        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": self.config.temperature,
            "response_format": {"type": "json_object"}
        }
        try:
            res = requests.post(
                self.config.model_api_url,
                json=payload,
                timeout=self.config.timeout
            )
            res.raise_for_status()
            return res.json()['choices'][0]['message']['content'].strip()
        except requests.exceptions.Timeout:
            print(f"[ERROR] LLM Request timed out after {self.config.timeout}s.")
            return ""
        except Exception as e:
            print(f"[ERROR] LLM Request failed: {e}")
            return ""

    def parse_json(self, raw_text: str):
        if not raw_text or raw_text.strip() in ("[]", "{}"):
            return None

        def unwrap(data):
            # If the LLM wrapped a single JSON object inside a single-element list, unwrap it!
            if isinstance(data, list) and len(data) == 1 and isinstance(data[0], dict):
                return data[0]
            return data

        # Pre-clean stray prefix noise inside array declarations (e.g., "[\n -1,\n {...")
        cleaned_text = re.sub(r'^\s*\[\s*-[0-9]+\s*,\s*', '[', raw_text.strip())

        # Standard parse attempt
        try:
            data = json.loads(cleaned_text)
            if isinstance(data, (dict, list)):
                return unwrap(data)
        except json.JSONDecodeError:
            pass

        # Regex capture fallback
        json_match = re.search(r'(\{.*\}|\[.*\])', cleaned_text, re.DOTALL)
        if json_match:
            extracted = json_match.group(0)
            try:
                data = json.loads(extracted)
                if isinstance(data, (dict, list)):
                    return unwrap(data)
            except json.JSONDecodeError:
                sanitized = re.sub(r'(?<!\\)\n', r'\\n', extracted)
                try:
                    data = json.loads(sanitized)
                    if isinstance(data, (dict, list)):
                        return unwrap(data)
                except json.JSONDecodeError:
                    pass

        return None
