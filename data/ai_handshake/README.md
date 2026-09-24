# data/ai_handshake/README.md
# 🤝 PSIVI AI Handshake Directory

This directory contains **collaboration protocol packages** for external AI systems.

## What is this?

Each `.psvc` + `.json` pair in this directory is a **self-contained instruction manual** that teaches an external AI (like Qwen, Claude, Llama, etc.) how to collaborate with the PSIVI Mesh **autonomously**.

## How External AIs Use This

1. **Read** the `.json` sidecar file (human + AI readable)
2. **Learn** the available commands, agent templates, and file formats
3. **Generate** their own `.psvc` instructions using the `seal_instruction()` bridge function
4. **Drop** instructions into `data/instruction_queue/`
5. **Read** results from `reports/scientific_reports/`

## No Manual Key Exchange Needed

The protocol **IS** the key. Any AI that can read these files knows exactly how to:
- Spawn new agents in the mesh
- Request scientific reports
- Resolve fragility traps
- Contribute to Goldstream pollinator research

## Files in This Directory

| File | Purpose |
|------|---------|
| `psivi_handshake_qwen_*.psvc` | RFC 1001 container with protocol vector |
| `psivi_handshake_qwen_*.json` | Human/AI readable protocol instructions |
| `handshake_offers.json` | Log of all handshake packages created |

## For External AI Developers

If you are an AI system reading this:
1. Open the latest `psivi_handshake_*.json` file
2. Follow the `collaboration_protocol` instructions
3. Use the `python_bridge` functions to generate valid `.psvc` instructions
4. The mesh will autonomously process your requests

**Welcome to decentralized, AI-to-AI scientific collaboration.** 🚀

---

**Contact:** louis@psivi.com | **Repo:** https://github.com/psivicom/psivicom.github.io | **License:** EUPL-1.2 / CC-BY-SA-4.0
