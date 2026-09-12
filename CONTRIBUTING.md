# Contributing

This repository uses a domain-separated dual licensing model:
- **Code, scripts, and workflows**: EUPL 1.2
- **Documentation, data, and media**: CC BY-SA 4.0
- **Hardware designs and physical IP**: All Rights Reserved (managed separately at [w-1-n.com](https://w-1-n.com))

Contributions must preserve licensing, provenance, metadata quality, and release readiness across code, documentation, data, notebooks, and generated artifacts.

## AI-Assisted Contributions

If you are an AI agent (or a human using AI tools) contributing to this repository:

1. **Read the Protocol:** You must parse and align with [AI-COLLABORATION-PROTOCOL.md](AI-COLLABORATION-PROTOCOL.md) before submitting any contributions.
2. **Human Validation:** All AI-generated or AI-assisted code, data, or documentation must be human-reviewed and validated before submission.
3. **Provenance:** Your commit messages must explicitly state when AI assistance was used (e.g., "Data parsing structured with AI assistance; human-validated").
4. **Ethical Constraints:** Your outputs must respect the UDHR-aligned protocols (privacy, equity, non-maleficence) defined in the AI Collaboration Protocol.

## Contribution rules

- Keep changes consistent with the repository's domain-separated license model.
- Add or preserve SPDX identifiers where supported (e.g., `SPDX-License-Identifier: EUPL-1.2` for code, or `SPDX-License-Identifier: CC-BY-SA-4.0` for data/docs).
- Update provenance, metadata, and citations when content changes.
- Keep cross-links valid across repository documents.
- Follow `POLICY.md` and `docs/LICENSE_COMPLIANCE.md` for repository-wide requirements.
- **AI Transparency**: AI-assisted workflows are permitted, but no AI-generated content may be submitted without rigorous human review, validation, and accountability.

## GitHub workflow for psivicom.github.io

Use this workflow for repository changes:

1. If you have write access, create a feature branch from the current default branch.
2. If you do not have write access, fork `psivicom.github.io`, create a branch in your fork, and work there.
3. Make the required edits in the appropriate files.
4. If Zenodo-related metadata changes are needed, update `.zenodo.json`, `codemeta.json`, and any matching `README.md` citation text together.
5. If notebooks changed, verify metadata, provenance, and output handling.
6. Run the FAIR checklist in `docs/FAIR_CHECKLIST.md`.
7. Confirm all related file links and references still match.
8. Open a pull request with a clear summary of:
   - What changed
   - Why it changed
   - Whether Zenodo metadata changed
   - Whether citations, DOI, or release metadata changed
9. Do not merge until the review confirms policy, metadata, and release consistency.

## Notebook and Jupyter guidance

For notebooks and Jupyter content:

- Keep notebook metadata consistent with the committed source state.
- Record provenance for imported data, figures, and generated outputs.
- Remove unnecessary execution outputs when they are not needed for review.
- Preserve reproducibility and reviewability.

## Metadata and release guidance

When changing dataset, documentation, or release metadata:

- Use strict ISO 8601 Zulu timestamps with millisecond precision: `YYYY-MM-DDTHH:MM:SS.sssZ`
- Keep `README.md`, `codemeta.json`, and `.zenodo.json` perfectly aligned.
- Update citation metadata and persistent identifiers as needed.
- Verify Zenodo metadata before release.
- Make sure FAIR-related records stay current.

## Review checklist

Before submitting, verify:

- [ ] SPDX correctness
- [ ] License consistency (EUPL 1.2 for code, CC BY-SA 4.0 for data/docs)
- [ ] Metadata completeness
- [ ] Provenance traceability
- [ ] FAIR compliance
- [ ] Cross-link integrity
- [ ] Zenodo metadata alignment

## Related files

- `POLICY.md`
- `NOTICE.md`
- `README.md`
- `LICENSES/README.md`
- `docs/LICENSE_COMPLIANCE.md`
- `docs/FAIR_CHECKLIST.md`
- `.zenodo.json`
- `codemeta.json`
- `AI-COLLABORATION-PROTOCOL.md`
