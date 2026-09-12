# SECURITY_PLAN.md
## Operational Security, Provenance, and Archiving Plan

**Architect & Principal Investigator:** Louis-Philippe Audette  
**Last Updated:** 2026-09-11T00:00:00.000Z  
**Project:** psivicom.github.io  
**Applies to:** main branch, linked notebooks, reference files, archives, and release artifacts  

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
- **Domain Separation:** Software is EUPL 1.2, Data/Docs are CC BY-SA 4.0, and Hardware/Physical IP is All Rights Reserved (managed at w-1-n.com).

## 3. Recommended File Map
**Top-level files:**
- SECURITY.md — Policy and reporting
- SECURITY_PLAN.md — Operational steps (this file)
- README.md — Project entry point
- AUTHORS.md — Authorship and attribution
- NOTICE.md — "The Audette Clause" and copyright notices
- CHANGELOG.md — Material changes over time

**Supporting folders:**
- docs/ — Policies, compliance matrices, and OSDMP
- NOTEBOOKS/ — Jupyter notebooks and analysis drafts
- REFERENCES/ — Source files, citations, notes, and traceability records
- DATA/ — Raw and processed data (CC BY-SA 4.0)
- ARCHIVE/ — Release notes, DOI metadata, preserved snapshots
- REPORTS/ — Security findings, summaries, and remediation records (if needed)

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
- Creation date (Strict Zulu time: YYYY-MM-DDTHH:MM:SS.sssZ)
- Author or maintainer
- Source inputs
- Method or notebook used
- Output generated
- Version or release tag
- Related references
- Archived DOI or external identifier, if any

### Good practice: Provenance Header
Use a simple provenance note at the top of major files:
> # SPDX-FileCopyrightText: 2026 Louis-Philippe Audette
> # SPDX-License-Identifier: [EUPL-1.2 or CC-BY-SA-4.0]
> # Created: YYYY-MM-DDTHH:MM:SS.sssZ
> # Author: Louis-Philippe Audette
> # Purpose: Short description
> # Inputs: linked files or source references

## 5. Zenodo DOI Archiving
Zenodo is used for stable archival copies of finished or release-worthy artifacts.

### When to archive
- A release is stable and citable.
- A notebook supports a published result.
- A dataset or analysis needs a persistent citation.
- A version must remain accessible for audit or reproducibility.

### What to archive
- Final notebooks and reports
- Release snapshots
- Important reference bundles
- Release metadata (.zenodo.json, codemeta.json, CITATION.cff)

### Archiving steps
1. Prepare a clean release folder.
2. Confirm all linked files and SPDX headers are present and correct.
3. Remove temporary scratch files.
4. Freeze the version with a Git release tag.
5. Upload the release package to Zenodo.
6. Record the DOI in ARCHIVE/zenodo_metadata.md.
7. Link the DOI from README.md, SECURITY.md, or the relevant release note.
8. Keep the archived package unchanged after publication.

### Metadata to record
- Release version
- Zenodo DOI
- Upload date (Zulu time)
- Included files
- Checksum or hash (SHA-256), if used
- Short description of what was archived

## 6. Supply-Chain Integrity
Supply-chain integrity means verifying that the tools, dependencies, and artifacts you use are the ones you intended to use.

### Required checks
- Pin dependencies where possible (e.g., requirements.txt, go.mod).
- Review dependency updates before merging.
- Prefer signed or trusted releases when available.
- Keep a record of exact versions used for important work.
- Verify notebook kernels, libraries, and build tools before release.
- Avoid pulling unknown code into active analysis without review.
- Record any manual override or exception.

### Operational checks (per release or major analysis)
- List dependency versions.
- Confirm source repository or package origin.
- Note integrity checks if available.
- Record any critical tool changes.
- Rerun important analysis after dependency changes when results matter.

### Example integrity record
> Tool: Python
> Version: 3.11.x
> Notebook kernel: linked
> Dependency lockfile: present
> Notable changes: none
> Verification date: 2026-09-11T00:00:00.000Z

## 7. No-Orphan File Rule
No file should exist without a path back to the project’s main structure.

### Rule
If a file is important enough to keep, it must be:
- Linked from README.md, SECURITY.md, SECURITY_PLAN.md, or an index file.
- Placed in a relevant folder.
- Named clearly.
- Referenced by at least one other project file.

### How to avoid orphans
- Maintain an index.md file for each major folder (docs/, NOTEBOOKS/, ARCHIVE/).
- Add cross-links in the README.md.
- Keep reference files at the bottom of the project or in a dedicated reference folder.
- Ensure every notebook points to its source files and outputs.
- Ensure every archive record points back to the release it preserves.

## 8. File Linking and Traceability
Every important file should state where it belongs.

### Required links
- README.md should point to policy, plan, references, and archives.
- SECURITY.md should point to this plan.
- SECURITY_PLAN.md should point to the notebook, reference, and archive locations.
- Each notebook should reference its input files and output reports.
- Each archive record should reference the exact release it preserves.

### Traceability chain
A complete chain should look like:
source file → notebook/analysis draft → report/result → release snapshot → Zenodo DOI → changelog entry

## 9. Release Checklist
Before any release, verify:
- [ ] All important files are linked
- [ ] No orphan files remain
- [ ] Provenance notes and SPDX headers are present and correct
- [ ] Source references are complete
- [ ] Dependencies are recorded and pinned
- [ ] Release version is tagged
- [ ] Archive package is clean
- [ ] Zenodo/OSF metadata is prepared and aligned (codemeta.json, .zenodo.json)
- [ ] Checksums or hashes are recorded if used
- [ ] Changelog is updated
- [ ] AI-generated content has been human-reviewed and validated

## 10. Incident or Security Finding Workflow
If a security issue or integrity issue is found:
1. Record it privately.
2. Identify affected files and notebooks.
3. Preserve evidence (do not delete history).
4. Document the fix and the Zulu timestamp of resolution.
5. Update this plan if the process failed.
6. Archive the corrected release when appropriate.

## 11. Maintenance
- Review this plan when the project structure changes.
- Update file indexes when new folders are added.
- Keep archived records aligned with releases.
- Refresh dependency records when tooling changes.
- Preserve old versions rather than deleting history.

## 12. Bottom-Line Rule
If a file, notebook, or archive matters, it must be **traceable, linked, dated (Zulu), licensed (SPDX), and preserved**.

---

## Related Policy
This plan implements the requirements in:
- [Trust and Provenance](TRUST_AND_PROVENANCE.md)
- [Security Policy](SECURITY.md)
- [Repository Policy](POLICY.md)
- [License Compliance](docs/LICENSE_COMPLIANCE.md)
- [Notice & Attribution](NOTICE.md)
