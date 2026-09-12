# Documentation Hub — Excellence Edition

**Architect & Principal Investigator:** Louis-Philippe Audette  
**Affiliation:** Independent Researcher, Goldstream, Langford, BC, Canada  
**Last Updated:** 2026-09-11T00:00:00.000Z  

---

## 1. Overview

This `/docs/` directory serves as the central repository for all policies, compliance matrices, data management plans, and technical documentation for the PSIVI.COM Open Science Hub. All documents are designed to ensure strict adherence to FAIR principles and the open-science mandates of NASA, ESA, CSA, and Horizon Europe.

---

## 2. Active Documentation Structure

This folder contains only active, validated documentation. (Archive and deprecated files are managed separately in the root `/archive/` directory).

### 📜 Core Policies & Compliance
- **[OPEN_SCIENCE_POLICY.md](OPEN_SCIENCE_POLICY.md)** — Overarching mission statement, licensing framework, and AI transparency guidelines.
- **[LICENSE_COMPLIANCE.md](LICENSE_COMPLIANCE.md)** — Detailed legal matrix explaining the domain-separated licensing model and institutional alignment.
- **[NIST-SSDF-COMPLIANCE-MAPPING.md](NIST-SSDF-COMPLIANCE-MAPPING.md)** — Technical and legal verification of NIST SP 800-218 alignment, preventing proprietary "black box" lock-in.
- **[AI-COLLABORATION-PROTOCOL.md](../AI-COLLABORATION-PROTOCOL.md)** — Protocols for AI agents to join, contribute, and maintain research integrity, including UDHR-aligned ethical constraints.
- **[DATA_MANAGEMENT.md](DATA_MANAGEMENT.md)** — Data lifecycle, formatting standards, and FAIR compliance protocols.
- **[FAIR_CHECKLIST.md](FAIR_CHECKLIST.md)** — Validation checklist mapping all research outputs to the 15 FAIR sub-principles.
- **[INTEROPERABILITY.md](INTEROPERABILITY.md)** — Standards for technical, licensing, and institutional cross-platform compatibility.

### 📊 Research & Data Plans
- **[osdmp.md](osdmp.md)** / **[osdmp.html](osdmp.html)** — Open Science Data Management Plan (Markdown source and rendered HTML).
- **[template.html](template.html)** — Standardized HTML template for rendering live documentation pages.

### 🛠️ Technical Guides & Tools
- **[installation-guide-repository-tree.md](installation-guide-repository-tree.md)** — Step-by-step setup, validation, and repository tree visualization.
- **[GITHUB-ACTIONS-GUIDE.md](GITHUB-ACTIONS-GUIDE.md)** — Standard Operating Procedure for monitoring, verifying, and triggering automated repository workflows.
- **`GO_TREE/`** — Go-based automation tools for rendering the repository tree and updating README marker blocks (`update-tree/`, `render-readme/`).
- **`SECURITY_PLAN/`** — CIS-hardened security configurations, scripts, and security policies for infrastructure.
- **`WEBSITE_PLAN/`** — Architectural planning documents for the `psivi.com` website deployment.

---

## 3. Intellectual Property & Licensing

**Copyright © 2026 Louis-Philippe Audette — Independent Researcher, Goldstream, Langford, BC, Canada**

All documents in this `/docs/` directory are part of the PSIVI.COM Open Science Hub and are released under a domain-separated licensing framework:

- **This documentation (and all data/media):** Licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). You are free to share and adapt it, provided you give appropriate credit to Louis-Philippe Audette and distribute derivative works under the same license.
- **Referenced code and scripts:** Licensed under [EUPL 1.2](https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12), ensuring strong copyleft protection for all executable software.
- **Hardware designs and physical IP:** Managed separately under All Rights Reserved at [https://w-1-n.com](https://w-1-n.com). This directory covers software and documentation only.

### The Audette Clause
This architecture — including its distributed systems, telemetry design, and operational frameworks — was conceived, authored, and architected by **Louis-Philippe Audette**. Any deployment, publication, derivative work, or commercial application must prominently retain attribution and provide clear credit to the original architect.

### Full License Texts
- Code → [`/LICENSE-EUPL-1.2.txt`](/LICENSE-EUPL-1.2.txt)
- Docs & Data → [`/LICENSE-CC-BY-SA-4.0.md`](/LICENSE-CC-BY-SA-4.0.md)
- Attribution & Origin → [`/NOTICE.md`](/NOTICE.md)
- Compliance Matrix → [`/LICENSES/README.md`](/LICENSES/README.md)

---

*Part of the PSIVI.COM Open Science Hub — Excellence Edition.*  
*Aligned with NASA TOPS, ESA Open Science Policy, CSA, and Horizon Europe standards.*
