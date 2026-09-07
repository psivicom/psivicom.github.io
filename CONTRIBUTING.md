# Contributing

This repository uses a dual license:
- Code: Apache-2.0
- Documentation and data: CC-BY-4.0

Contributions must preserve licensing, provenance, metadata quality, and release readiness across code, documentation, data, notebooks, and generated artifacts.

## Contribution rules

- Keep changes consistent with the repository license model.
- Add or preserve SPDX identifiers where supported.
- Update provenance, metadata, and citations when content changes.
- Keep cross-links valid across repository documents.
- Follow `POLICY.md` for repository-wide requirements.

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
   - what changed
   - why it changed
   - whether Zenodo metadata changed
   - whether citations, DOI, or release metadata changed
9. Do not merge until the review confirms policy, metadata, and release consistency.

## Notebook and Jupyter guidance

For notebooks and Jupyter content:

- Keep notebook metadata consistent with the committed source state.
- Record provenance for imported data, figures, and generated outputs.
- Remove unnecessary execution outputs when they are not needed for review.
- Preserve reproducibility and reviewability.

## Metadata and release guidance

When changing dataset, documentation, or release metadata:

- Use ISO 8601 Zulu timestamps with millisecond precision: `YYYY-MM-DDTHH:MM:SS.sssZ`
- Keep `README.md`, `codemeta.json`, and `.zenodo.json` aligned
- Update citation metadata and persistent identifiers as needed
- Verify Zenodo metadata before release
- Make sure FAIR-related records stay current

## Review checklist

Before submitting, verify:

- SPDX correctness
- License consistency
- Metadata completeness
- Provenance traceability
- FAIR compliance
- Cross-link integrity
- Zenodo metadata alignment

## Related files

- `POLICY.md`
- `README.md`
- `LICENSES/README.md`
- `docs/FAIR_CHECKLIST.md`
- `.zenodo.json`
- `codemeta.json`
