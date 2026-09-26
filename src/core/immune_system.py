# src/core/immune_system.py
"""
PSIVI AETHER Mesh - Autonomic Immune System
Protocol: RFC 1001
Time Standard: ISO 8601 Zulu (millisecond precision)

Diagnoses workflow failures and applies deterministic treatments.
The mesh heals itself. No human intervention required.
"""

import os
import sys
import json
import re
import requests
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional, Tuple


def get_zulu_time_ms() -> str:
    now = datetime.now(timezone.utc)
    return f"{now.strftime('%Y-%m-%dT%H:%M:%S.')}{now.microsecond // 1000:03d}Z"


class ImmuneSystem:
    """Autonomic error diagnosis and treatment engine."""

    ERROR_TAXONOMY = {
        "FILE_NOT_FOUND": {
            "patterns": [
                r"FileNotFoundError: \[Errno 2\] No such file or directory: '(.+?)'",
                r"can't open file '(.+?)'",
            ],
            "treatment": "create_missing_file",
        },
        "MODULE_NOT_FOUND": {
            "patterns": [
                r"ModuleNotFoundError: No module named '(.+?)'",
            ],
            "treatment": "add_dependency",
        },
        "JSON_DECODE": {
            "patterns": [
                r"json\.decoder\.JSONDecodeError",
                r"Expecting .+?: line (\d+) column (\d+)",
            ],
            "treatment": "repair_json",
        },
        "KEY_ERROR": {
            "patterns": [
                r"KeyError: '(.+?)'",
            ],
            "treatment": "add_default_key",
        },
        "IMPORT_ERROR": {
            "patterns": [
                r"ImportError: cannot import name '(.+?)' from '(.+?)'",
            ],
            "treatment": "fix_import",
        },
        "SYNTAX_ERROR": {
            "patterns": [
                r"SyntaxError: (.+?) \((.+?), line (\d+)\)",
            ],
            "treatment": "log_for_review",
        },
        "TYPE_ERROR": {
            "patterns": [
                r"TypeError: (.+?)",
            ],
            "treatment": "log_for_review",
        },
    }

    def __init__(self):
        self.token = os.environ.get("GITHUB_TOKEN", "")
        self.repo = "psivicom/psivicom.github.io"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {self.token}",
        }
        self.diagnosis: Dict = {}

    def fetch_failed_run_details(self, run_id: str) -> Dict:
        """Fetch job details and annotations from the failed workflow run."""
        jobs_url = f"https://api.github.com/repos/{self.repo}/actions/runs/{run_id}/jobs"
        resp = requests.get(jobs_url, headers=self.headers, timeout=30)
        if resp.status_code != 200:
            return {"error": f"Failed to fetch jobs: {resp.status_code}"}

        jobs = resp.json().get("jobs", [])
        failed_jobs = [j for j in jobs if j.get("conclusion") == "failure"]

        if not failed_jobs:
            return {"error": "No failed jobs found in run"}

        annotations = []
        for job in failed_jobs:
            job_id = job["id"]
            ann_url = f"https://api.github.com/repos/{self.repo}/check-runs/{job_id}/annotations"
            ann_resp = requests.get(ann_url, headers=self.headers, timeout=30)
            if ann_resp.status_code == 200:
                annotations.extend(ann_resp.json())

        return {
            "run_id": run_id,
            "failed_jobs": failed_jobs,
            "annotations": annotations,
        }

    def classify_error(self, annotations: list) -> Tuple[str, str, str, str]:
        """Classify the error and extract file/line/message."""
        error_class = "UNKNOWN"
        error_file = ""
        error_line = ""
        error_message = ""

        for ann in annotations:
            message = ann.get("message", "")
            path = ann.get("path", "")
            line = str(ann.get("start_line", ""))
            title = ann.get("title", "")

            full_text = f"{message} {title}"

            for class_name, taxonomy in self.ERROR_TAXONOMY.items():
                for pattern in taxonomy["patterns"]:
                    match = re.search(pattern, full_text)
                    if match:
                        error_class = class_name
                        error_file = path
                        error_line = line
                        error_message = message
                        return error_class, error_file, error_line, error_message

        if annotations:
            error_message = annotations[0].get("message", "Unknown error")
            error_file = annotations[0].get("path", "")
            error_line = str(annotations[0].get("start_line", ""))

        return error_class, error_file, error_line, error_message

    def diagnose(self):
        """Main diagnosis entry point. Outputs GitHub Actions step outputs."""
        run_id = os.environ.get("FAILED_RUN_ID", "")
        if not run_id:
            print("::error::No FAILED_RUN_ID provided")
            sys.exit(1)

        details = self.fetch_failed_run_details(run_id)
        if "error" in details:
            print(f"::error::{details['error']}")
            self._set_output("error_class", "UNKNOWN")
            self._set_output("error_file", "")
            self._set_output("error_line", "")
            self._set_output("error_message", details["error"])
            self._set_output("run_id", run_id)
            sys.exit(0)

        annotations = details.get("annotations", [])
        error_class, error_file, error_line, error_message = self.classify_error(annotations)

        timestamp = get_zulu_time_ms()
        print(f"[{timestamp}] 🧬 Immune Diagnosis Complete")
        print(f"  Class: {error_class}")
        print(f"  File: {error_file}:{error_line}")
        print(f"  Message: {error_message[:200]}")

        self._set_output("error_class", error_class)
        self._set_output("error_file", error_file)
        self._set_output("error_line", error_line)
        self._set_output("error_message", error_message[:500])
        self._set_output("run_id", run_id)

    def treat(self):
        """Apply treatment based on diagnosed error class."""
        error_class = os.environ.get("ERROR_CLASS", "UNKNOWN")
        error_file = os.environ.get("ERROR_FILE", "")
        error_line = os.environ.get("ERROR_LINE", "")
        error_message = os.environ.get("ERROR_MESSAGE", "")

        timestamp = get_zulu_time_ms()
        print(f"[{timestamp}] 🧬 Applying Treatment: {error_class}")

        treatment = self.ERROR_TAXONOMY.get(error_class, {}).get("treatment", "log_for_review")

        if treatment == "create_missing_file":
            self._treat_missing_file(error_file, error_message)
        elif treatment == "add_dependency":
            self._treat_missing_dependency(error_message)
        elif treatment == "repair_json":
            self._treat_json_repair(error_file)
        elif treatment == "add_default_key":
            self._treat_key_error(error_file, error_message)
        elif treatment == "fix_import":
            self._treat_import_error(error_file, error_message)
        else:
            self._treat_log_for_review(error_class, error_file, error_message)

    def _treat_missing_file(self, file_path: str, message: str):
        """Create a missing file with a minimal stub."""
        if not file_path:
            match = re.search(r"'(.+?)'", message)
            if match:
                file_path = match.group(1)

        if not file_path:
            print("Cannot determine missing file path")
            return

        path = Path(file_path)
        if path.suffix == ".py":
            path.parent.mkdir(parents=True, exist_ok=True)
            if not path.exists():
                path.write_text(
                    f'"""\nAuto-generated stub by Immune Protocol.\nTimestamp: {get_zulu_time_ms()}\n"""\n\n# TODO: Implement\n'
                )
                print(f"✅ Created missing file: {file_path}")
        elif path.suffix == ".json":
            path.parent.mkdir(parents=True, exist_ok=True)
            if not path.exists():
                path.write_text("{}")
                print(f"✅ Created missing JSON: {file_path}")
        elif path.suffix == ".jsonl":
            path.parent.mkdir(parents=True, exist_ok=True)
            if not path.exists():
                path.write_text("")
                print(f"✅ Created missing JSONL: {file_path}")

    def _treat_missing_dependency(self, message: str):
        """Add missing module to requirements.txt."""
        match = re.search(r"No module named '(.+?)'", message)
        if not match:
            return

        module_name = match.group(1).split(".")[0]
        req_path = Path("requirements.txt")

        existing = req_path.read_text() if req_path.exists() else ""
        if module_name not in existing:
            with open(req_path, "a") as f:
                f.write(f"\n{module_name}\n")
            print(f"✅ Added dependency: {module_name}")

    def _treat_json_repair(self, file_path: str):
        """Attempt to repair malformed JSON by wrapping in valid structure."""
        if not file_path or not Path(file_path).exists():
            return

        try:
            content = Path(file_path).read_text()
            json.loads(content)
        except json.JSONDecodeError:
            try:
                stripped = content.strip()
                if stripped.startswith("{") or stripped.startswith("["):
                    fixed = stripped.rstrip(",") + ("}" if stripped.startswith("{") else "]")
                    json.loads(fixed)
                    Path(file_path).write_text(fixed)
                    print(f"✅ Repaired JSON: {file_path}")
                else:
                    Path(file_path).write_text("{}")
                    print(f"🛑 Reset corrupt JSON: {file_path}")
            except Exception:
                Path(file_path).write_text("{}")
                print(f"🛑 Reset corrupt JSON: {file_path}")

    def _treat_key_error(self, file_path: str, message: str):
        """Add missing key with default value to JSON files."""
        match = re.search(r"KeyError: '(.+?)'", message)
        if not match:
            return

        missing_key = match.group(1)

        json_files = list(Path("reports").glob("*.json"))
        for jf in json_files:
            try:
                data = json.loads(jf.read_text())
                if isinstance(data, dict) and missing_key not in data:
                    data[missing_key] = 0 if "count" in missing_key.lower() else ""
                    jf.write_text(json.dumps(data, indent=2))
                    print(f"✅ Added missing key '{missing_key}' to {jf}")
            except Exception:
                continue

    def _treat_import_error(self, file_path: str, message: str):
        """Log import errors for structural review."""
        timestamp = get_zulu_time_ms()
        log_path = Path("reports/immune_log.jsonl")
        log_path.parent.mkdir(parents=True, exist_ok=True)

        entry = {
            "timestamp": timestamp,
            "error_class": "IMPORT_ERROR",
            "file": file_path,
            "message": message,
            "action": "flagged_for_structural_review",
        }
        with open(log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")
        print(f"📋 Logged import error for review: {message[:100]}")

    def _treat_log_for_review(self, error_class: str, file_path: str, message: str):
        """Log unresolvable errors for human architectural review."""
        timestamp = get_zulu_time_ms()
        log_path = Path("reports/immune_log.jsonl")
        log_path.parent.mkdir(parents=True, exist_ok=True)

        entry = {
            "timestamp": timestamp,
            "error_class": error_class,
            "file": file_path,
            "message": message,
            "action": "escalated_to_architect",
        }
        with open(log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")
        print(f"📋 Escalated to architect: {error_class}")

    def _set_output(self, name: str, value: str):
        """Set GitHub Actions step output."""
        github_output = os.environ.get("GITHUB_OUTPUT", "")
        if github_output:
            with open(github_output, "a") as f:
                f.write(f"{name}={value}\n")
        else:
            print(f"::set-output name={name}::{value}")


if __name__ == "__main__":
    immune = ImmuneSystem()

    if len(sys.argv) < 2:
        print("Usage: python immune_system.py [diagnose|treat]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "diagnose":
        immune.diagnose()
    elif command == "treat":
        immune.treat()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
