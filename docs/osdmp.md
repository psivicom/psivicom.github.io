<!—-  ⭐ Test from mobile - automation works! —>
# Open Science Data Management Plan (OSDMP) — Excellence — NASA SPD-41a — Dual License Apache-2.0 + CC-BY-4.0

**Author:** Louis-Philippe Audette — https://psivi.com — https://psivicom.github.io
**Version:** 1.1 — 2026-08-29
**Licenses:** Code Apache-2.0 (/LICENSE) — Data/Docs/Media CC-BY-4.0 (LICENSES/CC-BY-4.0.txt) — See LICENSES/README.md
**Standard:** NASA TOPS / SPD-41a / CSA / ESA / JAXA / Horizon Europe MGA Art.14 & 17 / UNESCO 41 C/22
**Related:** README.md, LICENSES/README.md, docs/LICENSE_COMPLIANCE.md, docs/DATA_MANAGEMENT.md, codemeta.json, .zenodo.json

---

## 1. Data Description — CC-BY-4.0

- Types: OSDMP docs, FAIR metadata, open science guidance, example datasets (pollinator monitoring), photos, images, videos — all CC-BY-4.0 — see data/README.md
- Code: Scripts, Jekyll config, validation workflows — Apache-2.0 — see LICENSE
- Formats: Markdown, JSON, CSV (open, machine-readable), HTML, JPG/PNG/MP4 (with CC-BY-4.0 attribution) — see docs/INTEROPERABILITY.md

Sample dataset: data/sample-pollinator-data/data.csv (CC-BY-4.0) with datapackage.json (Frictionless) and metadata.json (schema.org).

## 2. FAIR Compliance — Interconnected Files

**F1 — Persistent Identifier:** DOI via Zenodo (.zenodo.json → creates 10.5281/zenodo.XXXXXXX) + ORCID in CITATION.cff, codemeta.json, AUTHORS.md — see .zenodo.json
**F2 — Rich Metadata:** CITATION.cff (GitHub Cite button), codemeta.json (machine-readable with dual licenses), _config.yml (SEO), index.md (schema.org JSON-LD Person), data/sample-pollinator-data/metadata.json
**F3 — Metadata includes PID:** DOI in CITATION.cff identifiers, codemeta.json citation
**F4 — Indexed:** GitHub search (topics: open-science, apache-2.0, cc-by-4.0), Zenodo communities nasa-tops, esa, psivi.com mirror

**A1 — Retrievable via HTTPS:** https://psivicom.github.io and https://psivi.com — open protocol, no auth
**A1.1 — Open license:** Code Apache-2.0 (full text LICENSE) + Data CC-BY-4.0 (LICENSES/CC-BY-4.0.txt) — explicit in README dual table, LICENSES/README.md, NOTICE
**A2 — Long-term preservation:** GitHub + Zenodo archive + OSF + psivi.com — retention 10+ years per NASA SPD-41a — see docs/DATA_MANAGEMENT.md

**I1 — Knowledge representation:** JSON-LD, Dublin Core, codemeta, Frictionless datapackage, SPDX license identifiers (Apache-2.0 AND CC-BY-4.0)
**I2 — FAIR vocabularies:** schema.org, codemeta, DataCite via .zenodo.json, ORCID
**I3 — Qualified references:** Related identifiers in .zenodo.json, relatedLink in codemeta.json, links to docs/LICENSE_COMPLIANCE.md

**R1 — Rich attributes:** Provenance in AUTHORS.md, CHANGELOG.md, docs/
**R1.1 — License:** Dual — Code Apache-2.0, Data CC-BY-4.0 — see LICENSES/README.md, docs/LICENSE_COMPLIANCE.md, NOTICE
**R1.2 — Provenance:** AUTHORS.md, CHANGELOG.md, Git history, CITATION.cff
**R1.3 — Community standards:** NASA OSDMP template, Horizon Europe DMP template, Frictionless data

## 3. Licensing Rationale — Why Apache-2.0 + CC-BY-4.0

See docs/LICENSE_COMPLIANCE.md for full matrix.

- **Apache-2.0 for software:** NASA SPD-41a explicitly lists Apache-2.0 as compliant permissive license. Adds patent grant Clause 3, protects contributors — preferred by ESA for space software over MIT. Compatible with CC-BY-4.0 data.
- **CC-BY-4.0 for data/docs/media:** NASA SPD-41a requires data as CC-BY-4.0 or CC0. ESA Open Science Policy, CSA, JAXA, Horizon Europe MGA Art.14, UNESCO all require CC-BY-4.0 for non-code. Photos, images, videos, datasets, figures must be CC-BY-4.0 for reuse.

This dual model satisfies all agencies simultaneously.

## 4. Open Science Practices

- Open by default, as closed as necessary — see README
- Code Apache-2.0, Data CC-BY-4.0 — see LICENSES/README.md
- Pre-registration, reproducibility, transparency
- AI use disclosed: Meta AI-assisted drafting with human review — see CONTRIBUTING.md
- Versioning via CHANGELOG.md and GitHub releases (creates Zenodo DOI)

## 5. Preservation & Storage

- GitHub repo + Zenodo archive (DOI) + OSF + psivi.com mirror — see .zenodo.json communities
- Backup: _site excluded via .gitignore, data preserved
- Retention: 10+ years per NASA SPD-41a, Horizon Europe requires duration of project + 10 years

## 6. Ethics, Security, Privacy

- No personal data, no sensitive data — see SECURITY.md
- Compliance: Tri-Council Canada, NASA, EU GDPR for metadata only
- Photos/images/videos: All CC-BY-4.0, consent documented, attribution required — see data/images/README.md

## 7. Roles

- Louis-Philippe Audette — Data Steward — ORCID — see AUTHORS.md

## 8. Costs

- Zero cost via GitHub Pages + Zenodo free archiving — dual license does not add cost, Apache-2.0 and CC-BY-4.0 are free.

---

See also: README.md structure diagram, LICENSES/README.md, docs/FAIR_CHECKLIST.md, docs/DATA_MANAGEMENT.md
