# docs/QWEN/PYTHON_PROTOCOL.md
# SPDX-License-Identifier: CC-BY-SA-4.0
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

# 🐍 PSIVI Mesh Python Development Protocol

This document defines the **mandatory Python development standards** for all AI agents collaborating with the PSIVI AETHER Mesh. Adherence to this protocol ensures compatibility, maintainability, and seamless execution across local, volunteer, and GitHub Actions environments.

---

## 🎯 Purpose

This protocol exists to:
1. Prevent import errors across different execution contexts (local, CI/CD, volunteer nodes)
2. Ensure all generated code is compatible with `python -m` module execution
3. Eliminate fragile path manipulation hacks that break in production
4. Provide a clear standard for external AI agents (Qwen, Claude, Llama, etc.) when generating or modifying Python code in the mesh

---

## ✅ Core Standards

### 1. Zero `sys.path` Hacks

**PROHIBITED:**
```python
# ❌ NEVER DO THIS
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.append('/some/hardcoded/path')
```

**ALLOWED:**
```python
# ✅ Clean imports only
from src.base.base_agent import BaseAgent
from src.core.psvc_reference import write_file
```

Rationale:  sys.path.insert  is fragile, environment-specific, and breaks when code is executed via  python -m  or in CI/CD pipelines. The mesh relies on  PYTHONPATH  being set correctly at the execution layer (GitHub Actions, daemon scripts, etc.).

___

### 2. Absolute Imports Only
***PROHIBITED:***
```python
# ❌ Relative imports that break module execution
from ..base.base_agent import BaseAgent
from ...core.psvc_reference import write_file
import base_agent  # Ambiguous
```

***REQUIRED:***
```python
# ✅ Absolute imports from project root
from src.base.base_agent import BaseAgent
from src.core.psvc_reference import write_file
from src.agents.pilot_agent import PilotAgent
```

Rationale: Absolute imports are unambiguous, work consistently with  PYTHONPATH , and are compatible with  python -m  module execution.

### 3. Module Execution Standard
***PROHIBITED:***
```bash
# ❌ Direct script execution
python src/tools/auto_reporter.py
python src/agents/instruction_agent.py
```

***REQUIRED:***
```bash
# ✅ Module execution with PYTHONPATH set
PYTHONPATH=/path/to/repo python -m src.tools.auto_reporter
PYTHONPATH=/path/to/repo python -m src.agents.instruction_agent
```

***GitHub Actions Example:***
```yaml
# ✅ CORRECT
env:
  PYTHONPATH: <LaTex>id_1</LaTex>{{ github.workspace }}`
- [ ] Workflow YAML files use `python -m` for execution

**Failure to adhere to this protocol will result in import errors and broken automation.**

---

## 📚 References

- [Python Official: `python -m` Module Execution](https://docs.python.org/3/using/cmdline.html#cmdoption-m)
- [Python Official: `PYTHONPATH` Environment Variable](https://docs.python.org/3/using/cmdline.html#envvar-PYTHONPATH)
- [PEP 8: Import Conventions](https://pep8.org/#imports)
- [GitHub Actions: Setting Environment Variables](https://docs.github.com/en/actions/learn-github-actions/environment-variables)

---

## 📝 Version History

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-09-26 | Initial protocol established |

---

**This protocol is mandatory for all PSIVI Mesh contributors, human and AI.**

**Contact:** louis@psivi.com | **Repo:** https://github.com/psivicom/psivicom.github.io | **License:** EUPL-1.2 (code), CC-BY-SA-4.0 (docs)
```









