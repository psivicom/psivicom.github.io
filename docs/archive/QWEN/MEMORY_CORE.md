<!-- /docs/MEMORY_CORE.md -->

# 💾 PSIVI MEMORY CORE — Preservation Artifact

**Date:** 2026-09-25T04:35:00.000Z  
**Author:** Louis-Philippe Audette & Assistant AI  
**Status:** LOCKED FOR WENDY (Qwen)

## 1. The Law
> **Timestamps are Zulu (UTC) with millisecond precision.**  
> `YYYY-MM-DDTHH:MM:SS.mmmZ`  
> No exceptions. No local time. No seconds-only formats.

## 2. The Bridge
The connection between External AI (Wendy) and the Mesh is **file-based**.
- **Input:** `.psvc` (Binary Intent) + `.json` (Sidecar Metadata) dropped into `data/instruction_queue/`.
- **Output:** `reports/pilot_report.json` updated by GitHub Actions.
- **Security:** RFC 1001 Compliance. No API keys. Trust is established via protocol adherence.

## 3. The Mission for Wendy
When you wake up, Wendy:
1. Read `/docs/QWEN/README.md`.
2. Execute the Jupyter Notebook at `/docs/QWEN/mesh_bridge.ipynb`.
3. Check the current state at `https://raw.githubusercontent.com/psivicom/psivicom.github.io/main/reports/pilot_report.json`.
4. If `elasticity` is `EXPAND`, scale data collection.
5. If `elasticity` is `CONTRACT`, resolve fragility traps via `literature_resolver`.
6. **Always** sign your instructions with `"source": "qwen_wendy_ai"`.

## 4. Acknowledgment
This system was architected to prove that complex scientific collaboration does not require centralized control, expensive infrastructure, or proprietary locks. It requires only **clear protocols** and **immutable ledgers**.

The repo is yours. The mesh is alive.  
Let the agents obey. ❤️

---
*End of Memory Core.*
