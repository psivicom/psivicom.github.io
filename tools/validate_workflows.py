#!/usr/bin/env python3
"""
Read-only workflow path validator.
Exits with non-zero status if any workflow references a non-existent Python target.
NO AUTO-FIX. CI must fail fast to prevent silent corruption.
"""
import sys
import re
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required. Run: pip install pyyaml")
    sys.exit(1)

def main():
    workflows_dir = Path(".github/workflows")
    if not workflows_dir.exists():
        print("ERROR: .github/workflows directory not found.")
        sys.exit(1)

    errors = []

    for yml_file in workflows_dir.glob("*.yml"):
        with open(yml_file, 'r', encoding='utf-8') as f:
            try:
                content = yaml.safe_load(f)
            except yaml.YAMLError as e:
                errors.append(f"{yml_file.name}: Invalid YAML syntax - {e}")
                continue
        
        if not content or 'jobs' not in content:
            continue
            
        for job_name, job_data in content.get('jobs', {}).items():
            for step in job_data.get('steps', []):
                run_cmd = step.get('run', '')
                if not isinstance(run_cmd, str):
                    continue
                
                # Match 'python script.py', 'python3 script.py', or 'python -m module'
                # Note: We explicitly ignore 'python -' which means read from stdin (heredoc)
                matches = re.findall(r'python3?\s+(-m\s+)?([^\s;&|>]+)', run_cmd)
                for is_module, target in matches:
                    # Ignore stdin execution
                    if target == '-':
                        continue
                        
                    if is_module:
                        # Convert module path to file path: src.agents.foo -> src/agents/foo.py
                        file_path = Path(target.replace('.', '/') + '.py')
                    else:
                        file_path = Path(target)
                    
                    if not file_path.exists():
                        errors.append(f"{yml_file.name}: Target does not exist -> '{target}' (resolved to {file_path})")

    if errors:
        print("❌ WORKFLOW INTEGRITY CHECK FAILED:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    
    print("✅ All workflow Python targets are valid and resolvable.")
    sys.exit(0)

if __name__ == "__main__":
    main()
