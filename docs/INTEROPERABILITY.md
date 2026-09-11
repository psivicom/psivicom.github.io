# Interoperability Policy — Excellence Edition

**Architect & Principal Investigator:** Louis-Philippe Audette  
**Affiliation:** Independent Researcher, Goldstream, Langford, BC, Canada  
**Last Updated:** 2026-09-11T00:00:00.000Z  

---

## 1. Overview

This document defines the interoperability standards for the PSIVI.COM Open Science Hub. Interoperability ensures that research data, software, and documentation can be seamlessly integrated, reused, and validated across different platforms, institutions, and scientific communities, in strict alignment with NASA, ESA, CSA, and Horizon Europe requirements.

Interoperability is addressed across four dimensions:
1. **Technical Interoperability** — File formats, APIs, and data structures
2. **Licensing Interoperability** — How EUPL 1.2 and CC BY-SA 4.0 coexist and complement each other
3. **Institutional Interoperability** — Compliance with global space agency and research mandates
4. **Domain Separation** — Clear boundaries between open science and proprietary hardware IP

---

## 2. Technical Interoperability

### 2.1 File Formats

All data and documentation use open, non-proprietary, machine-readable formats:

| Data Type | Format | Standard | Rationale |
| :--- | :--- | :--- | :--- |
| **Tabular Data** | `.csv` | RFC 4180 | Universal compatibility, human-readable, version-control friendly |
| **Metadata** | `.json` | RFC 8259 | Machine-readable, schema-validatable, Zenodo/OSF compatible |
| **Configuration** | `.yml` | YAML 1.2 | Human-readable, widely supported in scientific toolchains |
| **Documentation** | `.md` | CommonMark/GFM | GitHub-native, renders cleanly, version-control friendly |
| **Geospatial** | GeoTIFF, NetCDF | OGC/CF conventions | Compatible with GDAL, xarray, NASA Earthdata workflows |
| **Code** | `.go`, `.py`, `.sh`, `.js` | Language-specific | Open-source, cross-platform, no vendor lock-in |

### 2.2 Metadata Standards

All datasets include rich, structured metadata using standardized schemas:
- **Data Packages:** `datapackage.json` (Frictionless Data standard)
- **Schema.org:** JSON-LD for web indexing and semantic search
- **Codemeta:** `codemeta.json` for software citation and discovery
- **Zenodo:** `.zenodo.json` for DOI minting and archival

### 2.3 APIs & Interfaces

- **RESTful APIs:** Where applicable, APIs follow OpenAPI 3.0 specifications
- **CLI Tools:** Command-line interfaces provide clear `--help` documentation and exit codes
- **RPC Protocols:** Distributed inference uses standard gRPC or HTTP/JSON-RPC for cross-platform compatibility

### 2.4 Version Control & Provenance

- **Git:** All code, data, and documentation are version-controlled
- **Semantic Versioning:** Software releases follow `MAJOR.MINOR.PATCH` (e.g., `1.2.3`)
- **Timestamps:** All timestamps use strict Zulu time (UTC) with millisecond precision: `YYYY-MM-DDTHH:MM:SS.sssZ`
- **Commit Messages:** Follow conventional commits format for automated changelog generation

---

## 3. Licensing Interoperability

### 3.1 Domain-Separated Licensing Model

The PSIVI.COM repository employs a strict, domain-separated licensing framework to maximize open-science impact while protecting specific commercial interests:

| Domain | License | SPDX Identifier | Scope |
| :--- | :--- | :--- | :--- |
| **Software, Code, Scripts** | European Union Public Licence v. 1.2 | `EUPL-1.2` | All `.go`, `.py`, `.sh`, `.js`, `.yml`, `.json` (code), `.html` |
| **Documentation, Data, Media** | Creative Commons Attribution-ShareAlike 4.0 International | `CC-BY-SA-4.0` | All `.md`, `.csv`, `.jpg`, `.png`, `.mp4`, `.pdf`, OSDMP |
| **Hardware, Physical IP** | **All Rights Reserved** | N/A | Physical designs, CAD, PCB layouts (Managed at [w-1-n.com](https://w-1-n.com)) |

### 3.2 How EUPL 1.2 and CC BY-SA 4.0 Coexist

The EUPL 1.2 (for code) and CC BY-SA 4.0 (for data/docs) are **compatible and complementary**:
- **EUPL 1.2** is a strong copyleft license for software, ensuring that derivative code remains open-source
- **CC BY-SA 4.0** is a strong copyleft license for data and documentation, ensuring that derivative research remains open
- **Both licenses mandate attribution** (The Audette Clause), ensuring clear provenance
- **Both licenses are OSI-approved** (EUPL 1.2) or Open Definition-compliant (CC BY-SA 4.0), ensuring institutional acceptance

### 3.3 The Hardware Separation Wall

Hardware designs, schematics, and physical implementations are **strictly excluded** from the open-source licenses. They are:
- **All Rights Reserved** under the commercial entity at [w-1-n.com](https://w-1-n.com)
- **Not included** in this repository (only architectural theory and software are present)
- **Available for commercial licensing** through separate agreements

This separation ensures that:
1. Open science remains uncontaminated by commercial restrictions
2. Physical IP is protected for future commercialization
3. Institutional partners (NASA, ESA, CSA) can freely use the software/data without hardware encumbrances

---

## 4. Institutional Interoperability

### 4.1 NASA (TOPS / SPD-41a)

- ✅ **Software:** EUPL 1.2 is OSI-approved, meeting NASA's open-source mandate
- ✅ **Data:** CC BY-SA 4.0 meets and exceeds FAIR data requirements
- ✅ **Archival:** Zenodo/OSF DOIs ensure persistent, citable identifiers
- ✅ **Reproducibility:** All code and data are version-controlled and reproducible

### 4.2 ESA (European Space Agency)

- ✅ **Software:** EUPL 1.2 is the **official and preferred** license of the European Commission and ESA
- ✅ **Data:** CC BY-SA 4.0 aligns with ESA Open Science Policy
- ✅ **Compatibility:** EUPL 1.2 is explicitly compatible with other major licenses (GPL, Apache 2.0, etc.)

### 4.3 CSA (Canadian Space Agency)

- ✅ **Software:** EUPL 1.2 is fully accepted under Canadian Open Science Policy
- ✅ **Data:** CC BY-SA 4.0 meets FAIR data mandates
- ✅ **Collaboration:** Clear licensing enables seamless collaboration with Canadian universities and research institutions

### 4.4 EU Horizon Europe

- ✅ **Regulation 2021/695:** Compliant with EU open science mandates
- ✅ **MGA Art. 14 & 17:** EUPL 1.2 is native to EU frameworks; CC BY-SA 4.0 meets data requirements
- ✅ **Plan S:** Open access to publications and data is ensured

### 4.5 UNESCO

- ✅ **41 C/22 Recommendation:** Aligns with global open science principles for transparent, reproducible knowledge sharing

---

## 5. Cross-Platform Compatibility

### 5.1 Operating Systems

All software is designed to run on:
- **Linux:** Primary target (Ubuntu 22.04+, Debian 12+, OpenBSD)
- **macOS:** Full compatibility (Apple Silicon and Intel)
- **Windows:** Supported via WSL2 or native builds where applicable

### 5.2 Cloud & HPC Environments

- **GitHub Actions:** CI/CD workflows for automated testing and deployment
- **Google Colab:** Jupyter notebooks for interactive, zero-setup demos
- **HPC Clusters:** MPI and Slurm-compatible scripts for high-performance computing

### 5.3 Scientific Toolchains

- **Python Ecosystem:** Compatible with NumPy, SciPy, pandas, xarray, GDAL
- **Go Ecosystem:** Standard library + popular packages (no vendor lock-in)
- **Earth Observation:** Compatible with NASA Earthdata, RADARSAT, Sentinel, Landsat workflows

---

## 6. Compliance Cross-Reference

- For licensing legalities, see: [LICENSE_COMPLIANCE.md](LICENSE_COMPLIANCE.md)
- For overarching research policies, see: [OPEN_SCIENCE_POLICY.md](OPEN_SCIENCE_POLICY.md)
- For data management details, see: [DATA_MANAGEMENT.md](DATA_MANAGEMENT.md)
- For FAIR validation, see: [FAIR_CHECKLIST.md](FAIR_CHECKLIST.md)
- For the OSDMP, see: [osdmp.md](osdmp.md)

---

*This document is a living policy. It is updated as new interoperability standards emerge and as the research evolves.*
