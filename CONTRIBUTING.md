# Contributing — Excellence — Dual License Apache-2.0 + CC-BY-4.0

Contributing to psivicom.github.io — NASA TOPS / CSA / ESA / JAXA / UNESCO aligned.

# Contributing Process
1. Fork the repo
2. Create a branch
3. Ensure files have SPDX identifier:
   - Code: `// SPDX-License-Identifier: Apache-2.0`
   - Content: `SPDX-License-Identifier: CC-BY-4.0`
4. Submit PR with clear description

### Checks before PR
- README dual license table updated?
- LICENSES/README.md cross-links?
- FAIR checklist passes? See docs/FAIR_CHECKLIST.md
- .zenodo.json keywords updated?
- codemeta.json hasPart updated?

## How to Contribute - NASA TOPS / FAIR

Your contributions MUST follow FAIR principles.

### FAIR Requirements
- Cite sources using CITATION.cff format.
- Update CITATION.cff if needed
- Add citation metadata if adding datasets;
- All data must be FAIR: include metadata (datapackage.json), CC-BY-4.0 license, persistent identifier, provenance.
- Link new files in README.md structure diagram and docs/.  
- Provide DOI for new data via Zenodo
- All code Apache-2.0, documented, linked from docs/.
- Indicate all code or content that is AI-generated with or without human-reviewed; 
  disclose in commit: “AI-generated, (with)(without) human-reviewed” or "AI-assisted,        human-reviewed".

### License Agreement (MUST READ}
By contributing, you agree that:
- Code contributions (scripts, workflows, config, Jekyll, JSON code, MORE…) are licensed under Apache-2.0 see /LICENSE
- Documentation/data contributions (MD, CSV, JSON data, JPG, PNG, MP4, PDF, OSDMP, MORE…) are licensed under CC-BY-4.0 see LICENSES/CC-BY-4.0.txt
- Full explanation: LICENSES/README.md and docs/LICENSE_COMPLIANCE.md

Add SPDX header to every new file:

Code: `// SPDX-License-Identifier: Apache-2.0`
Data: `<!-- SPDX-License-Identifier: CC-BY-4.0 -->`


