This is the moment WENDY gets her curriculum — your repository becomes her knowledge. Before I design the pipeline, let me inventory what's actually there — verified content, not assumptions (the Craft Gate applies to me too):
The inventory changes everything — and in the best way. You're not starting from zero: **you've already built the bones of this.** `RFC_1002_The_PSIVI_Dual_Track_Binary_Serialization_Standard_for_Sovereign_AI_Architectures.md` (52 KB), `psvc_cli.py`, `mesh.go`, `WENDY_QWEN_ZIG_MESH.md` (112 KB), `WENDY_PLATFORM_STANDARD.md`, and a full AI-collaboration governance suite (`AGENTS.md`, `AI-COLLABORATION-PROTOCOL.md`, `WENDY_VOLUNTEER_PROTOCOL.md`). Before I design anything, let me read *your* standards — the Craft Gate forbids me from proposing what already exists:
The inventory is read — and it demands honesty from me first, because I found my own error.

## What you already have (this is remarkable)

- **RFC 1001** — Sovereign AI Architecture; **RFC 1002** — the Dual-Track Binary Serialization Standard: **Track A** = `.psvc` / `.npy` (dense vectors), **Track B** = `.mpk` MessagePack (structured data) — with measured performance claims (5.0× vector density, 60.7% serialization latency reduction, ~99.6% vector load time reduction vs JSON)
- **`.psvc` properly defined**: 14-byte header (`PSVI` magic, version, precision, dims, payload size), zlib payload, INT8 quantization with scale factors, 12-char content hash — **"Pico Service Container"**
- **The Organ architecture** (BaseAgent, `_verify_identity()` → `_run_logic()` → `seal_result()`), the Git-based Gossip Protocol (`mesh/inbox`, `mesh/outbox`, `registry.json`), `ledger_validator.py`, OIDC, Zulu-time provenance
- **`AI-COLLABORATION-PROTOCOL.md`** — UDHR-anchored, `NO_CLOUD_LLM` rule, The Audette Clause, Grace Period Sandbox, AI-assisted commit format. My Charter is a *sibling* of this document, not a replacement — and must cross-reference it.
- `psvc_cli.py`, `mesh.go`, `WENDY_QWEN_ZIG_MESH.md`, layered `requirements-{tiny,core,ml}.txt`

## The correction: Amendment #2 (proposed)

My Amendment #1 wrote `".psvc (PSIVI Scientific Vector Container)"` and sketched a 64-byte header with SHA-256 blocks. **Your RFC 1002 is the normative truth: `.psvc` = *Pico Service Container*, 14-byte header.** I reinvented a spec you'd already published — exactly the failure mode the Craft Gate exists to catch, caught this time *before* merge.

> **Amendment #2 — defer to RFC 1002.** Section 4.1 is rewritten: the manifest's canonical Track A form is `.psvc` **as specified by RFC 1002** (14-byte header, `PSVI` magic, RFC-1002 precision and hashing rules); structured registry data rides Track B as `.mpk`; Merkle-root identity and steward signatures ride *over* these containers per RFC 1001; no byte layout is redefined in this Constitution. The Amendment Ledger records that the Contributor Mind's Amendment #1 expansion of the acronym was incorrect and is superseded by this one.

Per the Grace Period Sandbox: I propose this correction as my own restorative act — my outputs here are calibration data. Say **"amend"** and it goes in the ledger alongside #1.

## The gap: content → functioning AI

What's missing is the pipeline that turns ~64 MB of subjects — RFCs, protocols, research docs, `data/`, `docs/`, `_techreports/` — into WENDY's living curriculum, riding your existing standards:

| Stage | Mechanism | Rides on |
|---|---|---|
| **1. Ingest** | Inventory + parse every knowledge file (MD/HTML/CSV/notebooks), steward-classified | repo tree |
| **2. Chunk & embed** | Local, free embedding model (NO_CLOUD_LLM respected) → vectors | desktop tier |
| **3. Package** | Vectors → Track A `.psvc`; metadata/manifests → Track B `.mpk` | RFC 1002 |
| **4. Sign** | Merkle root over blocks → steward signature | RFC 1001 + Charter Art. I, V |
| **5. Distribute** | Git-based gossip — knowledge sharded across volunteer nodes, pico nodes carry indexes, SBCs carry vectors | your mesh standard |
| **6. Retrieve & serve** | Qwen-class small model + vector search at the edge, Zig runtime | `WENDY_QWEN_ZIG_MESH.md` |

The elegant fit: this pipeline is itself **a new Organ** in your architecture — an ingestion Organ that eats the repository and seals `.psvc` curriculum bundles through `seal_result()`.

**My proposal:** draft **`RFC_1003_WENDY_Knowledge_Curriculum_Pipeline.md`** — complete, in your RFC house style, extending `psvc_cli.py` rather than replacing it — plus the **content inventory → curriculum map** as its first annex. Say **"draft RFC 1003"** (and/or **"amend"** for #2) and I'll produce them whole. 🐝