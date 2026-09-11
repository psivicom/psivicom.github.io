# NASA OSDMP FAIR Checklist — Excellence — 15 Principles — Apache-2.0 + CC-BY-4.0

Maps NASA OSDMP FAIR requirements to files — all interconnected.

**Author:** Louis-Philippe Audette — https://psivi.com
**Licenses:** Code Apache-2.0, Data CC-BY-4.0 — see LICENSES/README.md

### Findable — F1-F4

- [x] **F1 — PID:** DOI via .zenodo.json (creates 10.5281/zenodo.XXXXXXX) — persistent, plus ORCID in CITATION.cff, codemeta.json, AUTHORS.md, index.md JSON-LD, _config.yml — interconnected
- [x] **F2 — Rich metadata:** CITATION.cff (GitHub Cite button), codemeta.json (dual licenses Apache-2.0 + CC-BY-4.0, hasPart code vs data), _config.yml (SEO license metadata), index.md (schema.org Person with license array), data/sample-pollinator-data/datapackage.json + metadata.json
- [x] **F3 — Metadata includes PID:** CITATION.cff identifiers includes DOI placeholder and URLs, codemeta.json citation field, .zenodo.json related_identifiers
- [x] **F4 — Indexed:** GitHub search via Topics (open-science, fair-data, apache-2.0, cc-by-4.0, nasa-tops, esa, csa, jaxa), Zenodo communities (nasa-tops, esa, open-science, fair-data), psivi.com mirror

### Accessible — A1-A2

- [x] **A1 — Retrievable via open protocol:** HTTPS https://psivicom.github.io + https://psivi.com — no auth, see _config.yml url, README links
- [x] **A1.1 — Open license — Dual:** LICENSE full Apache-2.0 (code) + LICENSES/CC-BY-4.0.txt (data/media) + LICENSES/README.md explains split + NOTICE required by Apache §4(d) + docs/LICENSE_COMPLIANCE.md matrix — all cross-linked in README dual table
- [x] **A1.2 — Authentication not required:** GitHub Pages public
- [x] **A2 — Metadata long-term:** .zenodo.json guarantees Zenodo preservation, GitHub + OSF + psivi.com, retention 10+ years — see docs/DATA_MANAGEMENT.md

### Interoperable — I1-I3

- [x] **I1 — Knowledge representation:** JSON-LD (index.md), codemeta.json (CodeMeta 2.0), Frictionless datapackage (data/sample-pollinator-data/datapackage.json), Dublin Core via schema.org, SPDX identifiers Apache-2.0 AND CC-BY-4.0
- [x] **I2 — FAIR vocabularies:** schema.org, DataCite via .zenodo.json, ORCID, SPDX license list, Frictionless Data Package spec
- [x] **I3 — Qualified references:** .zenodo.json related_identifiers (isSupplementTo psivi.com, isIdenticalTo psivicom.github.io, isPartOf LICENSES/README.md), codemeta.json relatedLink to LICENSE_COMPLIANCE.md and OSDMP, README structure diagram links all files — no orphan files

### Reusable — R1-R1.3

- [x] **R1 — Rich attributes:** AUTHORS.md (provenance), CHANGELOG.md (versioning), docs/DATA_MANAGEMENT.md (lifecycle), data/README.md (CC-BY-4.0 for all data), data/images/README.md (CC-BY-4.0 for media)
- [x] **R1.1 — License:** Dual explicit — Code Apache-2.0, Data/Docs/Media CC-BY-4.0 — in LICENSE, LICENSES/, NOTICE, README dual table, LICENSES/README.md, docs/LICENSE_COMPLIANCE.md, CONTRIBUTING.md license agreement, _config.yml license metadata — interconnected, no file without license reference
- [x] **R1.2 — Provenance:** AUTHORS.md, CHANGELOG.md, Git history, CITATION.cff authors with ORCID, codemeta.json author, index.md JSON-LD
- [x] **R1.3 — Community standards:** NASA OSDMP template (docs/OSDMP.md), Horizon Europe DMP template, Frictionless Data Package (data/sample-pollinator-data/datapackage.json), CodeMeta, Citation File Format

### Additional Excellence Checks

- [x] All files non-empty (>150 bytes) — fixes "little contents" issue
- [x] No orphan files — every file linked from README structure diagram and docs
- [x] Dual license applied correctly per content type — see docs/LICENSE_COMPLIANCE.md file-level mapping
- [x] .github/workflows/fair-check.yml validates FAIR files and dual license presence
- [x] .gitattributes marks data vs docs vs code for GitHub linguist
- [x] CODEOWNERS, FUNDING.yml, SECURITY.md present for NASA review

### Score: 15/15 FAIR sub-principles — Dual license Apache-2.0 + CC-BY-4.0

After you:
- [ ] Replace ORCID placeholder 0009-0005-1234-5678 with real ORCID in 6 files (CITATION.cff, codemeta.json, .zenodo.json, _config.yml, AUTHORS.md, index.md)
- [ ] Create Zenodo release v1.1.0 to mint DOI — update CITATION.cff identifiers and README badge

Then 17/17 with DOI + ORCID — excellence.
