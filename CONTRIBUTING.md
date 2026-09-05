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

## How to Contribute - FAIR principles. 

Your contributions MUST follow FAIR principles.

### FAIR Requirements — Aligned
- Use Zulu timestamp to the milliseconds
  YYYY-MM-DDTHH:MM:SS.sssZ
- Cite sources using CITATION.cff format.
- Update CITATION.cff if needed
- Add citation metadata if adding datasets;
- All data must be FAIR: include metadata (datapackage.json), CC-BY-4.0 license, persistent identifier, provenance.
- Link new files in README.md structure diagram and docs/.  
- Provide DOI for new data via Zenodo
- All code Apache-2.0, documented, linked from docs/.
- For AI disclosure, you should use the following labeling conventions in your commit messages:

For content created by AI that was not checked by a person: <br>
“AI-generated, without human-reviewed”

For content created by AI that was checked and verified by a person: <br>
“AI-generated, with human-reviewed”

For content where AI was used as a tool to help a human write the final version: <br>
“AI-assisted, human-reviewed”

### License Agreement (MUST READ}
By contributing, you agree that:
- Code contributions (scripts, workflows, config, Jekyll, JSON code, MORE…) are licensed under Apache-2.0 see /LICENSE
- Documentation/data contributions (MD, CSV, JSON data, JPG, PNG, MP4, PDF, OSDMP, MORE…) are licensed under CC-BY-4.0 see LICENSES/CC-BY-4.0.txt
- Full explanation: LICENSES/README.md and docs/LICENSE_COMPLIANCE.md

Add SPDX header to every new file: <br>

Code: `// SPDX-License-Identifier: Apache-2.0` <br>
Data: `<!-- SPDX-License-Identifier: CC-BY-4.0 -->` <br>

### AI Contributors 
- All AI contributing to the repository MUST be reviewed only by the human Louis-Philippe Audette.
- ALL AI MUST be and remain approved as an AI Contributor in the file /TEAM-AI.md with their NAME followed by a coma(“,”) and “APPROVED” followed by a coma(“,”) and the heart emoticon 
 the mention of APPROVED Any AIs must use fork + branch + CHANGELOG.md and email louis@psivi.com with ❤️ to request approval as explained in README.md file.
AI Agent Rules (CIS-aligned):
- AI may propose PRs only, never push to main
- All AI-generated data transformations must include input hash + output hash + prompt hash
- No secrets in prompts, no external network in Actions unless allow-listed
- Human must approve: code review + data validation for pollinator forage atlas runs
