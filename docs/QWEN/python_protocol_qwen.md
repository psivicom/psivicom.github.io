```markdown
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

**Rationale:** `sys.path.insert` is fragile, environment-specific, and breaks when code is executed via `python -m` or in CI/CD pipelines. The mesh relies on `PYTHONPATH` being set correctly at the execution layer (GitHub Actions, daemon scripts, etc.).

---

### 2. Absolute Imports Only

**PROHIBITED:**
```python
# ❌ Relative imports that break module execution
from ..base.base_agent import BaseAgent
from ...core.psvc_reference import write_file
import base_agent  # Ambiguous
```

**REQUIRED:**
```python
# ✅ Absolute imports from project root
from src.base.base_agent import BaseAgent
from src.core.psvc_reference import write_file
from src.agents.pilot_agent import PilotAgent
```

**Rationale:** Absolute imports are unambiguous, work consistently with `PYTHONPATH`, and are compatible with `python -m` module execution.

---

### 3. Module Execution Standard

**PROHIBITED:**
```bash
# ❌ Direct script execution
python src/tools/auto_reporter.py
python src/agents/instruction_agent.py
```

**REQUIRED:**
```bash
# ✅ Module execution with PYTHONPATH set
PYTHONPATH=/path/to/repo python -m src.tools.auto_reporter
PYTHONPATH=/path/to/repo python -m src.agents.instruction_agent
```

**GitHub Actions Example:**
```yaml
# ✅ CORRECT
env:
  PYTHONPATH: ${{ github.workspace }}
run: |
  python -m src.tools.auto_reporter
```

**Rationale:** `python -m` treats the code as a module, respecting package structure and `__init__.py` files. It is the modern Python standard for running package code.

---

## 📁 File Placement Guide

| File Type | Location | Example |
|-----------|----------|---------|
| **Agents** | `src/agents/` | `src/agents/pilot_agent.py` |
| **Tools / Entry Points** | `src/tools/` | `src/tools/auto_reporter.py` |
| **Core Libraries** | `src/core/` | `src/core/psvc_reference.py` |
| **Orchestrators** | `src/orchestrator/` | `src/orchestrator/chain_orchestrator.py` |
| **Mesh Infrastructure** | `src/mesh/` | `src/mesh/vram_mesh.py` |
| **Automation Scripts** | `src/automation/` | `src/automation/ai_planner.py` |
| **Base Classes** | `src/base/` | `src/base/base_agent.py` |
| **Workflows** | `.github/workflows/` | `.github/workflows/mesh-daemon.yml` |
| **Configuration** | `config/` | `config/agent_templates.json` |
| **Documentation** | `docs/QWEN/` | `docs/QWEN/PYTHON_PROTOCOL.md` |
| **Data (Ground Truth)** | `data/` | `data/osdr_ground_truth.jsonl` |
| **Instruction Queue** | `data/instruction_queue/` | `data/instruction_queue/instruction_*.psvc` |
| **Scientific Reports** | `reports/scientific_reports/` | `reports/scientific_reports/report_*.psvc` |
| **Pico Containers** | `reports/pico_containers/` | `reports/pico_containers/*.psvc` |

---

## 🧪 Testing Your Code

Before committing any Python code to the mesh, verify it adheres to this protocol:

### 1. Import Test
```bash
# From repository root
PYTHONPATH=. python -c "from src.agents.pilot_agent import PilotAgent; print('✅ Imports OK')"
```

### 2. Module Execution Test
```bash
# From repository root
PYTHONPATH=. python -m src.tools.auto_reporter
```

### 3. No `sys.path` Grep
```bash
# Verify no sys.path hacks exist
grep -r "sys.path.insert" src/
# Expected: No results
```

### 4. Workflow Lint
```bash
# Verify workflow sets PYTHONPATH and uses python -m
grep -A 5 "PYTHONPATH" .github/workflows/mesh-daemon.yml
grep "python -m" .github/workflows/mesh-daemon.yml
```

---

## 🤖 AI Agent Checklist

When an external AI (Qwen, Claude, etc.) generates or modifies Python code for the PSIVI Mesh, it **MUST** verify:

- [ ] No `sys.path.insert` or `sys.path.append` lines exist
- [ ] All imports are absolute (e.g., `from src.* import ...`)
- [ ] Entry points are executable via `python -m src.tools.*`
- [ ] Workflow YAML files set `PYTHONPATH: ${{ github.workspace }}`
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
