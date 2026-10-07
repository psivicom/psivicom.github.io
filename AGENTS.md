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
