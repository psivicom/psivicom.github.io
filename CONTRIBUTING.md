# Contributing — Excellence — Dual License Apache-2.0 + CC-BY-4.0

Thank you for contributing to psivicom.github.io — NASA TOPS / CSA / ESA / JAXA / UNESCO aligned.

### License Agreement (must read)

By contributing you agree:

- **Code contributions** (scripts, workflows, config, Jekyll, JSON code): **Apache-2.0** — see /LICENSE
- **Data/docs/media contributions** (MD, CSV, JSON data, JPG, PNG, MP4, PDF, OSDMP): **CC-BY-4.0** — see LICENSES/CC-BY-4.0.txt
- Full explanation: LICENSES/README.md and docs/LICENSE_COMPLIANCE.md

Add SPDX header to every new file:

Code: `// SPDX-License-Identifier: Apache-2.0`
Data: `<!-- SPDX-License-Identifier: CC-BY-4.0 -->`

### FAIR Requirements

1. All data must be FAIR: include metadata (datapackage.json), CC-BY-4.0 license, persistent identifier, provenance.
2. All code Apache-2.0, documented, linked from docs/.
3. No AI-generated content without human review — disclose in commit: "AI-assisted, human-reviewed".
4. Cite sources using CITATION.cff format.
5. Link new files in README.md structure diagram and docs/.

### Checks before PR

- README dual license table updated?
- LICENSES/README.md cross-links?
- FAIR checklist passes? See docs/FAIR_CHECKLIST.md
- .zenodo.json keywords updated?
- codemeta.json hasPart updated?

See CODE_OF_CONDUCT.md, SECURITY.md, AUTHORS.md
