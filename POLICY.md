```md
# Repository Policy

This policy applies to all repository content, including code, documentation, data, notebooks, metadata files, and generated artifacts.

## License policy

- Code is licensed under Apache-2.0.
- Documentation and data are licensed under CC-BY-4.0.
- Add the correct SPDX identifier to every new file where supported.
- Use the repository’s declared license for mixed-content files.

## Provenance and metadata policy

When adding or changing data, documentation, or repository metadata:

- Use ISO 8601 Zulu timestamps with millisecond precision: `YYYY-MM-DDTHH:MM:SS.sssZ`
- Include provenance, licensing, and persistent identifiers where applicable
- Include citation metadata for datasets where applicable
- Provide a DOI through Zenodo when applicable

## Notebook and Jupyter policy

For notebooks and Jupyter content:

- Keep notebook metadata consistent with the committed source state.
- Record provenance for imported data, figures, and generated outputs.
- Remove unnecessary execution outputs when they are not needed for review.
- Preserve notebook reproducibility expectations during review and release.
- Follow `CONTRIBUTING.md` for Jupyter-specific workflow and submission guidance.

## Zenodo policy

When a release includes new or updated data, metadata, or other citable research outputs:

- Update `.zenodo.json` as needed
- Keep release metadata consistent with `codemeta.json` and `README.md`
- Include citation metadata and persistent identifiers where applicable
- Create or update a Zenodo DOI when applicable

## Review policy

Changes affecting licensing, metadata, FAIR records, datasets, notebooks, or documentation structure should be reviewed for:

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
```
