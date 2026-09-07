# Repository Policy

This policy governs all repository content, including code, documentation, data, notebooks, metadata files, and generated artifacts.

## License policy

- Code is licensed under Apache-2.0.
- Documentation and data are licensed under CC-BY-4.0.
- Add the correct SPDX identifier to every new file where supported.
- Use the repository’s declared license for mixed-content files.

## Provenance and metadata policy

When adding or changing data, documentation, or repository metadata:

- Use ISO 8601 Zulu timestamps with millisecond precision: `YYYY-MM-DDTHH:MM:SS.sssZ`
- Include provenance, licensing, and persistent identifiers where required
- Include citation metadata for datasets where required
- Provide a DOI through Zenodo where required

## Notebook and Jupyter policy

For notebooks and Jupyter content:

- Keep notebook metadata consistent with the committed source state.
- Record provenance for imported data, figures, and generated outputs.
- Remove unnecessary execution outputs when they are not needed for review.
- Preserve reproducibility expectations during review and release.
- Follow `CONTRIBUTING.md` for Jupyter-specific workflow and submission guidance.

## Zenodo policy

For releases that include new or updated citable research outputs:

- Update `.zenodo.json` as needed.
- Keep release metadata consistent with `codemeta.json` and `README.md`.
- Include citation metadata and persistent identifiers where required.
- Create or update a Zenodo DOI where required.
- Verify Zenodo-related entries before release.

## Review policy

Changes affecting licensing, metadata, FAIR records, datasets, notebooks, or documentation structure must be reviewed for:

- SPDX correctness
- License consistency
- Metadata completeness
- Provenance traceability
- FAIR compliance
- Cross-link integrity

## Related files

- `README.md`
- `CONTRIBUTING.md`
- `LICENSES/README.md`
- `docs/FAIR_CHECKLIST.md`
- `.zenodo.json`
- `codemeta.json`

## Policy precedence

If this policy conflicts with a higher-priority policy, the higher-priority policy controls.
