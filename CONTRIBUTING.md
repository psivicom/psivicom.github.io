## Contributing

This repository uses dual licensing:

- **Code:** Apache-2.0
- **Documentation and data:** CC-BY-4.0

By contributing, you agree that your contributions will be licensed under the applicable repository license.

## Scope

These rules apply to:

- Code
- Documentation
- Data
- Notebooks
- Metadata files
- Generated artifacts

## Requirements

### File licensing
- Add the correct SPDX identifier to every new file where supported.
- Update the SPDX identifier when a file’s primary content changes.
- Use the repository’s declared license for mixed-content files.

### File header formats
- Code files: `SPDX-License-Identifier: Apache-2.0`
- Documentation and content files: `SPDX-License-Identifier: CC-BY-4.0`
- Data files: `SPDX-License-Identifier: CC-BY-4.0`

### Jupyter notebooks
- Keep notebook metadata consistent with the committed source state.
- Record provenance for imported data, figures, and generated outputs.
- Remove unnecessary execution outputs when they are not needed for review.

### FAIR and metadata
When adding or changing data, documentation, or repository metadata:

- Use ISO 8601 Zulu timestamps with millisecond precision: `YYYY-MM-DDTHH:MM:SS.sssZ`
- Include citation metadata for datasets where applicable
- Include provenance, licensing, and persistent identifiers where applicable
- Provide a DOI through Zenodo when applicable

### Zenodo
When a release includes new or updated data, metadata, or other citable research outputs:

- Update `.zenodo.json` as needed
- Keep release metadata consistent with `codemeta.json` and `README.md`
- Include citation metadata and persistent identifiers where applicable
- Create or update a Zenodo DOI when applicable

## Contributing process

1. Fork the repository.
2. Create a branch.
3. Make your changes.
4. Verify licensing, metadata, and documentation updates.
5. Open a pull request with a clear description of the changes.

## Pre-submission checks

Verify that:

- `README.md` dual-license references are current
- `LICENSES/README.md` cross-links are valid
- `docs/FAIR_CHECKLIST.md` is up to date
- `.zenodo.json` keywords are current when repository metadata changes
- `codemeta.json` is current when project metadata changes
- New files are linked in the README structure diagram and relevant documentation

## Review requirements

Changes affecting licensing, metadata, FAIR records, datasets, notebooks, or documentation structure should be reviewed for:

- SPDX correctness
- License consistency
- Metadata completeness
- Provenance traceability
- FAIR compliance
- Cross-link integrity

## Conflict handling

If this file conflicts with `POLICY.md` or any higher-priority repository policy, the higher-priority policy controls.
