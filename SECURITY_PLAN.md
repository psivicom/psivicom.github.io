# SECURITY_PLAN.md
## Operational Security, Provenance, and Archiving Plan

**Architect & Principal Investigator:** Louis-Philippe Audette  
**Last Updated:** 2026-09-11T00:00:00.000Z  
**Project:** psivicom.github.io  
**Applies to:** `main` branch, linked notebooks, reference files, archives, and release artifacts  

---

## 1. Purpose
This plan translates the repository's security and trust policies into concrete operational steps. It exists to preserve authorship, provenance, reproducibility, integrity, and persistence of the project’s research and code artifacts, in strict alignment with NASA SPD-41a, FAIR/TRUST principles, and the domain-separated licensing model.

## 2. Core Principles
- Every important file must have a clear purpose and correct SPDX license header.
- Every important file must be linked from a main index or policy file.
- **No orphan files:** If a file matters, it must be discoverable from the project structure.
- Source, drafts, notebooks, references, and archives must remain strictly traceable.
- Stable releases must be archived with persistent identifiers (DOIs) when appropriate.
- Research claims must be backed by dated notes, source files, and reproducible steps.
- **Domain Separation:** Software is EUPL 1.2, Data/Docs are CC BY-SA 4.0, and Hardware/Physical IP is All Rights Reserved (managed at [w-1-n.com](https://w-1-n.com)).

## 3. Recommended File Map
**Top-level files:**
- `SECURITY.md` — Policy and reporting
- `SECURITY_PLAN.md` — Operational steps (this file)
- `README.md` — Project entry point
- `AUTHORS.md` — Authorship and attribution
- `NOTICE.md` — "The Audette Clause" and copyright notices
- `CHANGELOG.md` — Material changes over time

**Supporting folders:**
- `docs/` — Policies, compliance matrices, and OSDMP
- `NOTEBOOKS/` — Jupyter notebooks and analysis drafts
- `REFERENCES/` — Source files, citations, notes, and traceability records
- `DATA/` — Raw and processed data (CC BY-SA 4.0)
- `ARCHIVE/` — Release notes, DOI metadata, preserved snapshots
- `REPORTS/` — Security findings, summaries, and remediation records (if needed)

## 4. Provenance Recording
Provenance means being able to show where a file came from, who created it, when it was created, and how it changed.

### Required practices
- Start important work in a dated notebook or draft file.
- Record author, date, and purpose at the top of each major file.
- Keep source material grouped with its related analysis.
- Preserve the original input files used to create results.
- Do not overwrite a file without keeping prior versions via Git history or a changelog entry.
- When a claim is made, include the source file or reference that supports it.
- **AI Transparency:** Any AI-assisted code or data generation must be explicitly noted and human-reviewed before commitment.

### Provenance metadata to record
For each important artifact, track:
- File name
- Creation date (Strict Zulu time: `YYYY-MM-DDTHH:MM:SS.sssZ`)
- Author or maintainer
- Source inputs
- Method or notebook used
- Output generated

- 
- Version or release tag
- Related references
- Archived DOI or external identifier, if any

### Good practice: Provenance Header
Use a simple provenance note at the top of major files:
```text
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette
# SPDX-License-Identifier: [EUPL-1.2 or CC-BY-SA-4.0]
# Created: YYYY-MM-DDTHH:MM:SS.sssZ
# Author: Louis-Philippe Audette
# Purpose: Short description
# Inputs: linked files or source references

5. Zenodo DOI ArchivingZenodo is used for stable archival copies of finished or release-worthy artifacts.When to archiveA release is stable and citable.A notebook supports a published result.A dataset or analysis needs a persistent citation.A version must remain accessible for audit or reproducibility.What to archiveFinal notebooks and reportsRelease snapshotsImportant reference bundlesRelease metadata (.zenodo.json, codemeta.json, CITATION.cff)Archiving stepsPrepare a clean release folder.Confirm all linked files and SPDX headers are present and correct.Remove temporary scratch files.Freeze the version with a Git release tag.Upload the release package to Zenodo.Record the DOI in ARCHIVE/zenodo_metadata.md.Link the DOI from README.md, SECURITY.md, or the relevant release note.Keep the archived package unchanged after publication.Metadata to recordRelease versionZenodo DOIUpload date (Zulu time)Included filesChecksum or hash (SHA-256), if usedShort description of what was archived6. Supply-Chain IntegritySupply-chain integrity means verifying that the tools, dependencies, and artifacts you use are the ones you intended to use.Required checksPin dependencies where possible (e.g., requirements.txt, go.mod).Review dependency updates before merging.Prefer signed or trusted releases when available.Keep a record of exact versions used for important work.Verify notebook kernels, libraries, and build tools before release.Avoid pulling unknown code into active analysis without review.Record any manual override or exception.Operational checks (per release or major analysis)List dependency versions.Confirm source repository or package origin.Note integrity checks if available.Record any critical tool changes.Rerun important analysis after dependency changes when results matter.Example integrity record


