# psivicom.github.io — Open Science Hub — Excellence Edition
**Personal site → https://psivi.com | Repo → https://github.com/psivicom/psivicom.github.io**

[![License: Apache 2.0](https://img.shields.io/badge/Code-Apache%202.0-blue.svg)](LICENSE)
[![License: CC BY 4.0](https://img.shields.io/badge/Data-CC%20BY%204.0-lightgrey.svg)](LICENSES/CC-BY-4.0.txt)
[![DOI: Zenodo](https://img.shields.io/badge/DOI-Zenodo-1682D4.svg)](https://zenodo.org)
[![FAIR](https://img.shields.io/badge/FAIR-Compliant-green.svg)](docs/FAIR_CHECKLIST.md)
[![NASA TOPS](https://img.shields.io/badge/NASA-TOPS%20Aligned-0B3D91.svg)](docs/OSDMP.md)
[![ESA](https://img.shields.io/badge/ESA-Open%20Science-003247.svg)](docs/OSDMP.md)
[![CSA](https://img.shields.io/badge/CSA-Open%20Science-red.svg)](docs/OSDMP.md)

> **Excellence mode:** This repo is built for the NASA Open Science FAIR + world space agencies. Code = Apache-2.0, Data/Docs/Media = CC-BY-4.0 — fully interconnected.

### 📄 Open Science Data Management Plan
- **Live OSDMP:** [psivi.com/docs/osdmp.html](https://psivi.com/docs/osdmp.html) | [docs/OSDMP.md](docs/OSDMP.md)
- **FAIR Checklist:** [docs/FAIR_CHECKLIST.md](docs/FAIR_CHECKLIST.md)
- **License Compliance:** [docs/LICENSE_COMPLIANCE.md](docs/LICENSE_COMPLIANCE.md) — explains Apache-2.0 vs CC-BY-4.0
- **Data Management:** [docs/DATA_MANAGEMENT.md](docs/DATA_MANAGEMENT.md)

### 🔐 Dual License — NASA + Space Partners Compliant

| Type | License | Path | For |
|---|---|---|---|
| Software / code / workflows / config | **Apache-2.0** | `/LICENSE`, `LICENSES/APACHE-2.0.txt` | All `.js, .py, .yml, .json (code), .html` |
| Docs, data, datasets, photos, images, videos, figures, CSV, OSDMP | **CC-BY-4.0** | `LICENSES/CC-BY-4.0.txt` | All `.md, .csv, .jpg, .png, .mp4, .pdf` |

See `LICENSES/README.md`, `NOTICE`, `docs/LICENSE_COMPLIANCE.md` — all cross-linked.

**Why this split?** NASA SPD-41a §VI and ESA Open Science require: Software = OSI-approved (Apache-2.0 is preferred for patent grant), Data = CC-BY-4.0 or CC0. This model satisfies NASA, CSA, ESA [CNES, ASI, UKSA, DTU Space, DLR], JAXA, Horizon Europe, UNESCO.

### 🤖 AI-Assisted Open Science
Built with Meta AI-assisted workflows, human-reviewed per NASA TOPS guidance on AI use. No AI content published without validation. See `CONTRIBUTING.md`.

### 🇨🇦🇺🇸🇪🇺🇯🇵🌐 Multi-Agency Compliance

- **NASA TOPS / SPD-41a:** Open code Apache-2.0, open data CC-BY-4.0, DOIs, FAIR, OSDMP required — [docs/OSDMP.md](docs/OSDMP.md)
- **CSA:** Canadian Space Agency Open Science & FAIR — same dual license
- **ESA:** ESA Open Science Policy + ESA Policy on Open Access — Apache-2.0 approved — covers CNES-FR, ASI-IT, UKSA-UK, DTU Space-DK, DLR-DE — see [docs/LICENSE_COMPLIANCE.md](docs/LICENSE_COMPLIANCE.md)
- **JAXA:** JAXA Open Science
- **EU Horizon Europe:** Reg 2021/695, MGA Art.14 & 17, Directive 2019/1024, Plan S, EOSC — Apache-2.0 EUPL-compatible, data CC-BY-4.0 required
- **UNESCO:** 41 C/22 Recommendation on Open Science (2021)

### 📦 Repository Structure — Interconnected

```
├── LICENSE (Apache-2.0 full — code)
├── NOTICE (attributions)
├── LICENSES/ (APACHE-2.0.txt, CC-BY-4.0.txt, README.md explains dual)
├── CITATION.cff (GitHub Cite button → Apache-2.0, links to DOI)
├── codemeta.json (machine-readable → Apache-2.0 AND CC-BY-4.0 SPDX)
├── .zenodo.json (Zenodo DOI metadata → CC-BY-4.0 + communities)
├── _config.yml (Jekyll + SEO + links to licenses)
├── index.md (homepage with JSON-LD Person, links to docs)
├── docs/
│   ├── OSDMP.md (NASA template, links to LICENSES/)
│   ├── FAIR_CHECKLIST.md (15 FAIR sub-principles mapped)
│   ├── LICENSE_COMPLIANCE.md (why Apache vs CC-BY)
│   ├── DATA_MANAGEMENT.md (data lifecycle, CC-BY-4.0)
│   └── INTEROPERABILITY.md (formats, vocabularies)
├── data/
│   ├── README.md (CC-BY-4.0 for all data)
│   ├── sample-pollinator-data/
│   │   ├── data.csv (CC-BY-4.0 example dataset)
│   │   ├── datapackage.json (Frictionless, CC-BY-4.0)
│   │   └── metadata.json (schema.org, CC-BY-4.0)
│   └── images/README.md (CC-BY-4.0 for media)
├── .github/workflows/fair-check.yml (Apache-2.0)
└── CONTRIBUTING.md, CODE_OF_CONDUCT.md, SECURITY.md, AUTHORS.md
```

All files cross-reference each other — no orphan files.

### 🔗 Links & Persistence — FAIR Findable

- Website: https://psivi.com
- GitHub Pages: https://psivicom.github.io
- Repo: https://github.com/psivicom/psivicom.github.io
- DOIs: Zenodo (create release) + OSF — see `.zenodo.json`
- ORCID: https://orcid.org/0009-0005-1234-5678 [replace with real for credibility]
- Standard: FAIR, Reproducible, Open by Default — see [docs/FAIR_CHECKLIST.md](docs/FAIR_CHECKLIST.md)

### Topics (paste in GitHub About)
`open-science` `fair-data` `open-data` `open-access` `reproducibility` `esa` `nasa-tops` `csa` `jaxa` `apache-2.0` `cc-by-4.0` `ai` `zenodo` `osf` `fair`

### Citation — Raises credibility of Louis-Philippe Audette

Use GitHub "Cite this repository" — powered by `CITATION.cff` → gives DOI, ORCID, Apache-2.0 + CC-BY-4.0.

### Author

**Louis-Philippe Audette** — Open Science Steward — Langford, BC, Canada — https://psivi.com
Independent Researcher — FAIR Data — NASA TOPS Aligned — ORCID required for NASA submission.

See `AUTHORS.md` and `index.md` JSON-LD.
