# Contributing — Dual License Apache-2.0 + CC-BY-4.0

Contributions to this repository must follow project licensing, documentation, and review requirements.

## Contributing Process
1. Fork the repository.
2. Create a branch.
3. Ensure files use the correct SPDX identifier:
   - Code: `// SPDX-License-Identifier: Apache-2.0`
   - Content: `SPDX-License-Identifier: CC-BY-4.0`
4. Submit a pull request with a clear description of the changes.

## Pre-Submission Checks
- Update the README dual-license table if needed.
- Verify `LICENSES/README.md` cross-links.
- Check `docs/FAIR_CHECKLIST.md`.
- Update `.zenodo.json` keywords if needed.
- Update `codemeta.json` if needed.
- Link new files in the README structure diagram and relevant docs.

## FAIR and Documentation Requirements
- Use Zulu timestamps in ISO 8601 format to millisecond precision:
  `YYYY-MM-DDTHH:MM:SS.sssZ`
- Add citation metadata when adding datasets.
- Include metadata, provenance, licensing, and persistent identifiers for new data where applicable.
- Provide a DOI for new data via Zenodo when applicable.
- Code and documentation must be accurate, maintainable, and consistently licensed.

## Licensing
By contributing, you agree that:
- Code contributions are licensed under Apache-2.0.
- Documentation and data contributions are licensed under CC-BY-4.0.

See `LICENSES/README.md` and `docs/LICENSE_COMPLIANCE.md` for details.

## File Headers
Add the correct SPDX header to every new file.
