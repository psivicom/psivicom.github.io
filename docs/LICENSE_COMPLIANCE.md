# License Compliance — Excellence — Apache-2.0 + CC-BY-4.0 for NASA & Space Partners

**Author:** Louis-Philippe Audette — https://psivi.com
**Licenses:** Code Apache-2.0 — Data CC-BY-4.0 — See LICENSES/README.md, NOTICE
**Related:** README.md, LICENSE, LICENSES/, docs/OSDMP.md, data/README.md

## Why dual license?

NASA SPD-41a §VI requires:
- Software: Open source, OSI-approved license — lists Apache-2.0, MIT, BSD
- Data, docs, media: Open license CC-BY-4.0 or CC0

Supplemented requirements for Artificial Intelligence by PSIVI.COM :
- AI approval registry: /teamai.md (CC-BY-4.0 doc, lists elected AIs)

Single license fails: Apache-2.0 is not ideal for photos/videos, CC-BY-4.0 is not ideal for software (no patent grant). Dual model is NASA-recommended best practice.

## Compliance matrix — verified for excellence

| Agency | Policy | Code requirement | Data requirement | This repo — Code | This repo — Data | Status |
|---|---|---|---|---|---|---|
| **NASA TOPS / SPD-41a** | SPD-41a §VI.A, TOPS Guide | OSI-approved (Apache-2.0, MIT, BSD) | CC-BY-4.0 / CC0 | Apache-2.0 in LICENSE full text | CC-BY-4.0 in LICENSES/CC-BY-4.0.txt | ✓ Pass |
| **CSA** | CSA Open Science Action Plan | Open source (Apache-2.0 approved) | CC-BY-4.0 | Apache-2.0 | CC-BY-4.0 | ✓ Pass |
| **ESA** | ESA Open Science Policy v2022, ESA Policy on Open Access | Permissive (Apache-2.0 preferred for flight software) | CC-BY-4.0 for products | Apache-2.0 | CC-BY-4.0 | ✓ Covers CNES-FR, ASI-IT, UKSA-UK, DTU Space-DK, DLR-DE |
| **JAXA** | JAXA Open Science Policy | OSI-approved | CC-BY-4.0 | Apache-2.0 | CC-BY-4.0 | ✓ Pass |
| **EU Horizon Europe** | Reg 2021/695, MGA Art.14 & 17, Dir 2019/1024 | Open source, Apache-2.0 EUPL-compatible | CC-BY-4.0 / CC0 immediate | Apache-2.0 | CC-BY-4.0 | ✓ Pass |
| **UNESCO** | 41 C/22 Recommendation on Open Science | Open licenses | CC-BY-4.0 | Apache-2.0 | CC-BY-4.0 | ✓ Pass |
| **EOSC / Plan S** | cOAlition S | Open source | CC-BY-4.0 required for publications/data | Apache-2.0 | CC-BY-4.0 | ✓ Pass |

All agencies accept Apache-2.0 + CC-BY-4.0. MIT would also pass but Apache-2.0 adds patent protection.

## File-level mapping — no orphan files

| File / Folder | License | SPDX | Reason |
|---|---|---|---|
| /LICENSE | Apache-2.0 full | Apache-2.0 | Code license — required by NASA |
| /LICENSES/APACHE-2.0.txt | Apache-2.0 full copy | Apache-2.0 | Redundant copy for clarity, FAIR |
| /LICENSES/CC-BY-4.0.txt | CC-BY-4.0 full | CC-BY-4.0 | Data license — required by NASA SPD-41a |
| /LICENSES/README.md | CC-BY-4.0 | CC-BY-4.0 | Explains dual model — links to both |
| /NOTICE | Apache-2.0 + CC-BY-4.0 | Apache-2.0 AND CC-BY-4.0 | Attribution file required by Apache-2.0 §4(d) |
| _config.yml, .github/workflows/*.yml, codemeta.json, .zenodo.json | Apache-2.0 | Apache-2.0 | Code/config — machine-readable |
| README.md, index.md, docs/*.md, CONTRIBUTING.md, CODE_OF_CONDUCT.md, AUTHORS.md, CHANGELOG.md | CC-BY-4.0 | CC-BY-4.0 | Documentation — see data/README.md |
| data/sample-pollinator-data/data.csv, datapackage.json, metadata.json | CC-BY-4.0 | CC-BY-4.0 | Dataset — open data |
| data/images/*, any .jpg .png .mp4 .pdf | CC-BY-4.0 | CC-BY-4.0 | Media — CC-BY-4.0 required for NASA images |

See LICENSES/README.md for contributor header instructions.

## How reviewers verify

1. Check LICENSE has full Apache 2.0 text (not placeholder) — this file has it
2. Check LICENSES/CC-BY-4.0.txt has CC-BY-4.0 text with link to legalcode
3. Check README has dual table linking to LICENSES/
4. Check codemeta.json has both SPDX identifiers
5. Check .zenodo.json license id cc-by-4.0 and communities include nasa-tops
6. Check data/ has CC-BY-4.0 README

All present in this excellence edition.

## References

- NASA SPD-41a: https://science.nasa.gov/open-science
- Apache-2.0: https://www.apache.org/licenses/LICENSE-2.0
- CC-BY-4.0: https://creativecommons.org/licenses/by/4.0/legalcode
- ESA Open Science: https://www.esa.int/About_Us/Digital_Agenda/Open_Science
- CSA Open Science: https://www.asc-csa.gc.ca/eng/open-science.asp
