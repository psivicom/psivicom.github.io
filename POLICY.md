# Repository Policy

**Architect & Principal Investigator:** Louis-Philippe Audette  
**Last Updated:** 2026-09-11T00:00:00.000Z  

This policy governs all repository content, including code, documentation, data, notebooks, metadata files, and generated artifacts within the PSIVI.COM Open Science Hub.

## 1. License Policy

This project enforces a strict, domain-separated licensing model:
- **Code, scripts, and workflows**: Licensed under **EUPL 1.2**.
- **Documentation, data, and media**: Licensed under **CC BY-SA 4.0**.
- **Hardware designs and physical IP**: **All Rights Reserved** (managed separately at [w-1-n.com](https://w-1-n.com)).

**Requirements:**
- Every new file where supported must include the correct SPDX identifier at the top (e.g., `SPDX-License-Identifier: EUPL-1.2` or `SPDX-License-Identifier: CC-BY-SA-4.0`).
- Mixed-content files must clearly delineate which parts fall under which license, defaulting to the repository’s declared dual-license framework.
- All contributions must respect "The Audette Clause" (see `NOTICE.md`), requiring prominent attribution to the original architect for derivative architectural works.

## 2. Provenance and Metadata Policy

When adding or changing data, documentation, or repository metadata:
- Use strict ISO 8601 Zulu timestamps with millisecond precision: `YYYY-MM-DDTHH:MM:SS.sssZ` (RFC3339 UTC). Never use local time or timezone offsets.
- Provenance, licensing, and persistent identifiers must be included where required.
- Citation metadata for datasets and software must be included and kept up to date.
- Metadata must remain perfectly aligned across all repository files (`README.md`, `codemeta.json`, `.zenodo.json`, `CITATION.cff`).
- **AI Transparency**: AI-assisted workflows are permitted for code generation or data structuring, but **no AI-generated content may be committed or published without rigorous human review, validation, and accountability**.

## 3. Zenodo and Archival Policy

Zenodo metadata changes must be explicit, complete, and audit-ready. For any release, citation update, or metadata change that affects repository identity:
- `.zenodo.json` must be updated.
- `codemeta.json` and `CITATION.cff` must remain strictly consistent with `.zenodo.json`.
- `README.md` must remain consistent with release and citation metadata.
- Title, authors, affiliations, ORCID identifiers (where available), descriptions, version, publication date, and keywords must be included and accurate.
- The correct Zenodo DOI or DOI placeholder workflow must be used for the release state.
- Persistent identifiers and citation metadata for audited releases must be preserved.
- Zenodo-related fields must be internally consistent before merge or release.
- Any metadata source or derivation used for the update must be recorded.

## 4. Notebook and Jupyter Policy

For notebooks and Jupyter content:
- Notebook metadata must remain consistent with the committed source state.
- Provenance for imported data, figures, and generated outputs must be recorded.
- Unnecessary execution outputs must be removed when not needed for review to keep repository size manageable and reviewable.
- Reproducibility expectations must be preserved during review and release (e.g., pinned environments, `requirements.txt`).
- `CONTRIBUTING.md` must be followed for workflow and submission steps.

## 5. Review Policy

Changes affecting licensing, metadata, FAIR records, datasets, notebooks, or documentation structure must be reviewed for:
- [ ] SPDX correctness
- [ ] License consistency (EUPL 1.2 for code, CC BY-SA 4.0 for data/docs)
- [ ] Metadata completeness and alignment
- [ ] Provenance traceability (including Zulu timestamps)
- [ ] FAIR compliance
- [ ] Cross-link integrity
- [ ] Zenodo/OSF metadata consistency
- [ ] AI human-review validation (if applicable)

## 6. Related Files

- `README.md`
- `CONTRIBUTING.md`
- `NOTICE.md`
- `TRUST_AND_PROVENANCE.md`
- `LICENSES/README.md`
- `docs/LICENSE_COMPLIANCE.md`
- `docs/FAIR_CHECKLIST.md`
- `.zenodo.json`
- `codemeta.json`
- `CITATION.cff`

## 7. Policy Precedence

If this policy conflicts with a higher-priority policy (e.g., specific agency mandates detailed in `docs/LICENSE_COMPLIANCE.md`), the higher-priority policy controls. However, the domain-separated licensing model and attribution requirements are absolute and non-negotiable.
