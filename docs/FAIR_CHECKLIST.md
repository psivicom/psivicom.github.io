# FAIR Compliance Checklist — Excellence Edition

**Architect & Principal Investigator:** Louis-Philippe Audette  
**Affiliation:** Independent Researcher, Goldstream, Langford, BC, Canada  
**Last Updated:** 2026-09-11T00:00:00.000Z  

---

## Overview

This checklist validates that all research data, software, and documentation within the PSIVI.COM Open Science Hub adhere to the **FAIR Principles** (Findable, Accessible, Interoperable, Reusable) as mandated by NASA TOPS, ESA Open Science Policy, CSA, and Horizon Europe.

All 15 FAIR sub-principles are mapped below with explicit implementation details.

---

## 🔍 FINDABLE (F)

### F1: (Meta)data are assigned a globally unique and persistent identifier
- ✅ **Implementation:** All major datasets and software releases are archived via **Zenodo** and/or **OSF**, minting permanent DOIs (e.g., `10.5281/zenodo.xxxxxxx`).
- ✅ **Verification:** Check `.zenodo.json` and `CITATION.cff` for DOI placeholders.

### F2: Data are described with rich metadata
- ✅ **Implementation:** All datasets include `metadata.json` or `datapackage.json` with comprehensive descriptions, temporal/spatial coverage, and methodology.
- ✅ **Verification:** Review `data/sample-pollinator-data/metadata.json`.

### F3: Metadata clearly and explicitly include the identifier of the data they describe
- ✅ **Implementation:** Metadata files explicitly reference the DOI, GitHub repo URL, and Zenodo record URL.
- ✅ **Verification:** Check that `metadata.json` contains `doi`, `url`, and `repository` fields.

### F4: (Meta)data are registered or indexed in a searchable resource
- ✅ **Implementation:** Research is indexed via GitHub (searchable), Zenodo (searchable), and OSF (searchable). Website `psivi.com` includes structured JSON-LD for search engine indexing.
- ✅ **Verification:** Test search queries on Zenodo, GitHub, and Google for "Louis-Philippe Audette" or "PSIVI.COM".

---

## 🔓 ACCESSIBLE (A)

### A1: (Meta)data are retrievable by their identifier using a standardized communications protocol
- ✅ **Implementation:** DOIs resolve via HTTPS to Zenodo/OSF records. GitHub repo is publicly accessible.
- ✅ **Verification:** Test DOI resolution (e.g., `https://doi.org/10.5281/zenodo.xxxxxxx`).

### A2: Metadata are accessible, even when the data are no longer available
- ✅ **Implementation:** Zenodo and OSF provide permanent archival. Metadata is stored in version-controlled Git, ensuring long-term accessibility.
- ✅ **Verification:** Confirm that Zenodo records remain accessible even if GitHub repo is deleted.

---

## 🔗 INTEROPERABLE (I)

### I1: (Meta)data use a formal, accessible, shared, and broadly applicable language for knowledge representation
- ✅ **Implementation:** Metadata uses JSON (RFC 8259) and YAML (YAML 1.2), both widely supported and machine-readable.
- ✅ **Verification:** Validate JSON files with `jsonlint` or similar tools.

### I2: (Meta)data use vocabularies that follow FAIR principles
- ✅ **Implementation:** Controlled vocabularies are used where applicable (e.g., standard ecological terms, NASA Earthdata product names).
- ✅ **Verification:** Review metadata for consistent terminology.

### I3: (Meta)data include qualified references to other (meta)data
- ✅ **Implementation:** Metadata includes cross-references to related datasets, publications, and software versions.
- ✅ **Verification:** Check for `related_identifiers` in `.zenodo.json` and `relatedLink` in `codemeta.json`.

### I4: (Meta)data include qualified references to other (meta)data (persistent)
- ✅ **Implementation:** All references use persistent identifiers (DOIs, ORCIDs, URLs) rather than ephemeral links.
- ✅ **Verification:** Ensure no broken links; all URLs are stable.

---

## ♻️ REUSABLE (R)

### R1: (Meta)data are richly described with a plurality of accurate and relevant attributes
- ✅ **Implementation:** Metadata includes temporal coverage, spatial extent, methodology, instrumentation, and quality flags.
- ✅ **Verification:** Review `metadata.json` for completeness.

### R2: (Meta)data are released with a clear and accessible data usage license
- ✅ **Implementation:** All data and documentation are licensed under **CC BY-SA 4.0**. All code is licensed under **EUPL 1.2**. Hardware is **All Rights Reserved** (see [w-1-n.com](https://w-1-n.com)).
- ✅ **Verification:** Check `LICENSE-CC-BY-SA-4.0.md`, `LICENSE-EUPL-1.2.txt`, and `LICENSES/README.md`.

### R3: (Meta)data are associated with their provenance
- ✅ **Implementation:** All data is version-controlled via Git. Processing scripts are included in the repository. The "Audette Clause" ensures clear attribution and provenance tracking.
- ✅ **Verification:** Check Git history and `NOTICE.md` for provenance information.

---

## Additional Excellence Criteria

### ✅ Reproducibility
- All processing scripts are version-controlled and include pinned dependencies.
- Synthetic datasets and test fixtures are provided for validation.

### ✅ AI Transparency
- AI-assisted workflows are documented.
- No AI-generated content is published without human review.

### ✅ Timestamps & Provenance
- All timestamps use strict Zulu time (UTC) with millisecond precision: `YYYY-MM-DDTHH:MM:SS.sssZ`.

### ✅ Domain Separation
- Software (EUPL 1.2), Data/Docs (CC BY-SA 4.0), and Hardware (All Rights Reserved) are cleanly separated.

---

## Compliance Cross-Reference

- For overarching research policies, see: [OPEN_SCIENCE_POLICY.md](OPEN_SCIENCE_POLICY.md)
- For licensing legalities, see: [LICENSE_COMPLIANCE.md](LICENSE_COMPLIANCE.md)
- For data management details, see: [DATA_MANAGEMENT.md](DATA_MANAGEMENT.md)
- For the OSDMP, see: [osdmp.md](osdmp.md)

---

*This checklist is a living document. It is updated as new research is published and new FAIR best practices emerge.*
