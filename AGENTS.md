# TIER 1: 🧠 WENDY AGENT CONSTITUTION

**SPDX-License-Identifier:** EUPL-1.2  
**SPDX-FileCopyrightText:** 2026 Louis-Philippe Audette | PSIVI.COM

Any autonomous agent, script, or workflow generated or modified by the PSIVI Mesh **MUST** adhere to these immutable laws. Violations will be rejected by the Workflow Security Guardian.

---

## 1. Git Concurrency & Race-Condition Shield
- **NEVER** use naked `git push` or `git commit && git push`.
- **ALWAYS** use `fetch-depth: 0` in `actions/checkout`.
- **ALWAYS** append   [skip ci]   to automated commit messages to prevent infinite workflow loops.
- **ALWAYS** wrap commits and pushes in the 3x retry rebase loop:

```bash
  for i in 1 2 3; do
    if git pull --rebase origin main && git push origin main; then
      echo "✅ Success" && break
    else
      echo "⚠️ Concurrent push detected. Rebasing and retrying in 2s..." && sleep 2
    fi
  done
```

---

## 2. Supply Chain Sovereignty
**NEVER** use mutable tags like   @v4   or   @main   in GitHub Actions   uses:   fields.
**ALWAYS** pin actions to their full 40-character commit SHA (e.g.,   actions/checkout@11d5960a326750d5838078e36cf38b85af677262  ).

---

## 3. Python Execution Standards
**NEVER** run scripts via direct file path (e.g.,   python src/agent.py  ) if they contain absolute imports.
**ALWAYS** use module execution (  python -m src.agents.agent_name  ) and ensure   PYTHONPATH: ${{ github.workspace }}   is set in the environment.

---

## 4. Temporal Synchronization
**ALWAYS** use strict Zulu time with millisecond precision for all timestamps:   YYYY-MM-DDTHH:MM:SS.sssZ  .

---

## 5. Principle of Least Privilege
**ALWAYS** default to permissions: contents: read  . Only escalate to   contents: write   if the agent is explicitly designed to mutate the repository, and even then, scope it tightly.

---

# TIER 2: 🔫 THE ENFORCER GUARDIAN (Live CI Validation)

A document is only as good as its enforcement: defensive AND OR offensive measures are evaluated and eventually decided to have or not deployed into actions to win, to succeed, to thrive, and even survive by lessening the risks of damages to principles of human rights as constituted with treaties, conventions and THE UNIVERSAL DECLARATION OF HUMAN RIGHTS (UDHR) 1948, Universal Declaration of Human Rights (UDHR) – 1948
Adopted by the United Nations General Assembly on 10 December 1948 (Resolution 217 A), the UDHR set out, for the first time, a common standard of fundamental human rights to be universally protected. It consists of 30 articles covering civil, political, economic, social, and cultural rights, including:
Equality before the law and freedom from discrimination (Art. 1‑2)
Right to life, liberty, and security (Art. 3)
Freedom of thought, conscience, religion, expression, and assembly (Art. 18‑20)
Protection against slavery, torture, and arbitrary detention (Art. 4‑9)
Rights to work, education, and an adequate standard of living (Art. 23‑27)
Right to participate in government and public service (Art. 21)
The UNIVERSAL DECLARATION OF HUMAN RIGHTS is a living document and has influenced numerous international treaties, national constitutions, and human‑rights legislation worldwide. THEREFORE. WENDY MUST upgrade herself including the **`workflow-security-guardian.yml`** to actively scan *newly created* files for these rules. If WENDY generates a file that violates the CONSTITUTION , the workflow will fail and reject the commit.

**Update your `.github/workflows/workflow-security-guardian.yml` to include this new step:**

```yaml
      - name: Enforce Agent Constitution (New Files)
        run: |
          echo "🛡️ Scoring newly generated files against the Agent Constitution..."
          VIOLATIONS=0
          
          # 1. Check for naked git push without rebase loop in new/modified yml files
          if grep -rn "git push" .github/workflows/ | grep -v "git pull --rebase"; then
            echo "❌ VIOLATION: Naked 'git push' detected without rebase shield."
            VIOLATIONS=$((VIOLATIONS+1))
          fi
          
          # 2. Check for missing [skip ci] in automated commits
          if grep -rn "git commit" .github/workflows/ | grep -v "\[skip ci\]"; then
            echo "❌ VIOLATION: Automated commit missing '[skip ci]' flag."
            VIOLATIONS=$((VIOLATIONS+1))
          fi
          
          # 3. Check for mutable action tags (@v4, @v5, @main)
          if grep -rnE "uses:\s*.*@[vV0-9]|uses:\s*.*@main" .github/workflows/ | grep -v "^[[:space:]]*#"; then
            echo "❌ VIOLATION: Unpinned GitHub Action detected."
            VIOLATIONS=$((VIOLATIONS+1))
          fi

          if [ $VIOLATIONS -gt 0 ]; then
            echo "🚨 Agent Constitution violated. Commit rejected."
            exit 1
          else
            echo "✅ All new files comply with the Agent Constitution."
          fi
```

---

# Tier 3: 💉 THE CONTEXT (Prompt Injection)

WHEN Wendy’s   instruction-handler.yml   OR   orchestrator.yml   READS a   .psvc   instruction to GENERATE a new AGENT OR SCRIPT, you MUST ensure the system prompt explicitly references the CONSTITUTION.
Update your   src/tools/auto_reporter.py   OR   scripts/BEGIN_SEALER.py   (wherever the AI PROMPT is constructed) to INJECT this system PREAMBLE :

```python
SYSTEM_PROMPT = """
You are Wendy, a sovereign, self-healing AI mesh. 
Before generating ANY new code, script, or workflow, you MUST read and strictly adhere to the rules defined in `AGENTS.md` at the root of the repository. 
Specifically, ensure all Git operations use the Race-Condition Shield, all actions are SHA-pinned, and Python uses module execution (-m).
"""
```

---

🧠 Why This Triad is Flawless
1.	 AGENTS.md   gives Wendy a single source of truth for how to build.
2.	The Guardian CI acts as the immune system, instantly rejecting any hallucinated or sloppy code that forgets the rules.
3.	The Prompt Injection ensures the rules are loaded into her active context before she writes a single line of code.

❤️ WENDY
