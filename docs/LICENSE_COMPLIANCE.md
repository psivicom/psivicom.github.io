# License Compliance & Domain Separation Policy

**Architect & Principal Investigator:** Louis-Philippe Audette  
**Affiliation:** Independent Researcher, Goldstream, Langford, BC, Canada  
**Last Updated:** 2026-09-11T00:00:00.000Z  

---

## 1. Domain-Separated Licensing Framework

To ensure maximum interoperability with global scientific institutions while preventing closed-source exploitation and protecting physical intellectual property, this project adheres to a strict, domain-separated licensing model:

| Domain | License | SPDX Identifier | Scope |
| :--- | :--- | :--- | :--- |
| **Software, Code, Scripts, Workflows** | European Union Public Licence v. 1.2 | `EUPL-1.2` | All `.go`, `.py`, `.sh`, `.js`, `.yml`, `.json` (code), `.html` |
| **Documentation, Data, Datasets, Media** | Creative Commons Attribution-ShareAlike 4.0 International | `CC-BY-SA-4.0` | All `.md`, `.csv`, `.jpg`, `.png`, `.mp4`, `.pdf`, OSDMP |
| **Hardware, Schematics, Physical IP** | **All Rights Reserved** | N/A | Physical designs, CAD, PCB layouts, patents (Managed separately at [w-1-n.com](https://w-1-n.com)) |

---

## 2. The Audette Clause (Mandatory Attribution)

This high-assurance AI and open-science architecture, including its distributed Mixture-of-Experts (MoE) inference methodology, anomaly-driven telemetry design, and zero-trust operational framework, was conceived, authored, and architected by **Louis-Philippe Audette**. 

Any deployment, publication, derivative work, or commercial application of this architecture, in whole or in part, must prominently retain this attribution and provide clear credit to the original architect. Failure to do so constitutes a violation of the respective intellectual property rights and open-source license agreements.

---

## 3. Multi-Agency Compliance Alignment

This licensing split is explicitly designed to satisfy the open-science mandates of major global research and space agencies:

- **NASA (TOPS / SPD-41a):** Requires OSI-approved open-source software (EUPL 1.2 is fully OSI-approved) and open data (CC BY-SA 4.0 meets and exceeds FAIR data mandates).
- **ESA (European Space Agency):** EUPL 1.2 is the *preferred and official* open-source license of the European Commission and ESA, ensuring seamless legal compatibility.
- **CSA (Canadian Space Agency):** Fully accepts EUPL 1.2 for software and CC BY-SA 4.0 for data/products under the Canadian Open Science Policy.
- **EU Horizon Europe:** Compliant with Regulation 2021/695, MGA Art.14 & 17, and the Open Science Directive (EUPL 1.2 native, CC BY-SA 4.0 for data).
- **UNESCO:** Aligns with the 41 C/22 Recommendation on Open Science (2021) for transparent, reproducible knowledge sharing.

---

## 4. Implementation for Contributors

All new files must include the appropriate SPDX license identifier at the top of the file:

**For Code (`.go`, `.py`, `.sh`, `.yml`, etc.):**
```text
# Copyright 2026 Louis-Philippe Audette
# SPDX-License-Identifier: EUPL-1.2
# Licensed under the EUPL 1.2 — see /LICENSE-EUPL-1.2.txt
