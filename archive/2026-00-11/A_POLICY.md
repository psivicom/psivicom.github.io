# Repository Policy

This policy governs all repository content, including code, documentation, data, notebooks, metadata files, and generated artifacts.

## License policy

- Code is licensed under Apache-2.0.
- Documentation and data are licensed under CC-BY-4.0.
- Every new file where supported must include the correct SPDX identifier.
- Mixed-content files must use the repository’s declared license.

## Provenance and metadata policy

When adding or changing data, documentation, or repository metadata:

- Use ISO 8601 Zulu timestamps with millisecond precision: `YYYY-MM-DDTHH:MM:SS.sssZ`
- Provenance, licensing, and persistent identifiers must be included where required
- Citation metadata for datasets must be included where required
- Metadata must remain aligned across repository files where required

## Zenodo policy

Zenodo metadata changes must be explicit, complete, and audit-ready.

For any release, citation update, or metadata change that affects repository identity:

- `.zenodo.json` must be updated.
- `codemeta.json` must remain consistent with `.zenodo.json`.
- `README.md` must remain consistent with release and citation metadata.
- Title, authors, affiliations, ORCID identifiers where available, descriptions, version, publication date, and keywords must be included where required.
- The correct Zenodo DOI or DOI placeholder workflow must be used for the release state.
- Persistent identifiers and citation metadata for audited releases must be preserved.
- Zenodo-related fields must be internally consistent before merge or release.
- Any metadata source or derivation used for the update must be recorded.

## Notebook and Jupyter policy

For notebooks and Jupyter content:

- Notebook metadata must remain consistent with the committed source state.
- Provenance for imported data, figures, and generated outputs must be recorded.
- Unnecessary execution outputs must be removed when not needed for review.
- Reproducibility expectations must be preserved during review and release.
- `CONTRIBUTING.md` must be followed for workflow and submission steps.

## Review policy

Changes affecting licensing, metadata, FAIR records, datasets, notebooks, or documentation structure must be reviewed for:

- SPDX correctness
- License consistency
- Metadata completeness
- Provenance traceability
- FAIR compliance
- Cross-link integrity
- Zenodo metadata consistency

## Related files

- `README.md`
- `CONTRIBUTING.md`
- `LICENSES/README.md`
- `docs/FAIR_CHECKLIST.md`
- `.zenodo.json`
- `codemeta.json`

## Policy precedence

If this policy conflicts with a higher-priority policy, the higher-priority policy controls.
