# 🧠 WENDY AGENT CONSTITUTION

**SPDX-License-Identifier:** EUPL-1.2  
**SPDX-FileCopyrightText:** 2026 Louis-Philippe Audette | PSIVI.COM

Any autonomous agent, script, or workflow generated or modified by the PSIVI Mesh **MUST** adhere to these immutable laws. Violations will be rejected by the Workflow Security Guardian.

## 1. Git Concurrency & Race-Condition Shield
- **NEVER** use naked `git push` or `git commit && git push`.
- **ALWAYS** use `fetch-depth: 0` in `actions/checkout`.
- **ALWAYS** wrap commits and pushes in the 3x retry rebase loop:
  ```bash
  for i in 1 2 3; do
    if git pull --rebase origin main && git push origin main; then
      echo "✅ Success" && break
    else
      echo "⚠️ Concurrent push detected. Rebasing and retrying in 2s..." && sleep 2
    fi
  done

•	ALWAYS append   [skip ci]   to automated commit messages to prevent infinite workflow loops.
2. Supply Chain Sovereignty
	•	NEVER use mutable tags like   @v4   or   @main   in GitHub Actions   uses:   fields.
	•	ALWAYS pin actions to their full 40-character commit SHA (e.g.,   actions/checkout@11d5960a326750d5838078e36cf38b85af677262  ).
3. Python Execution Standards
	•	NEVER run scripts via direct file path (e.g.,   python src/agent.py  ) if they contain absolute imports.
	•	ALWAYS use module execution (  python -m src.agents.agent_name  ) and ensure   PYTHONPATH: ${{ github.workspace }}   is set in the environment.
4. Temporal Synchronization
	•	ALWAYS use strict Zulu time with millisecond precision for all timestamps:   YYYY-MM-DDTHH:MM:SS.sssZ  .
5. Principle of Least Privilege
	•	ALWAYS default to   permissions: contents: read  . Only escalate to   contents: write   if the agent is explicitly designed to mutate the repository, and even then, scope it tightly.

