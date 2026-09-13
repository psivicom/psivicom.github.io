# Domain-Separated Licensing Framework — Open Science & Commercial Compliance

This repository implements a strict, domain-separated licensing model designed for global open-science compliance (NASA, CSA, ESA, Horizon Europe, UNESCO) while explicitly protecting proprietary hardware intellectual property.

| Content Type | License | File Location | SPDX Identifier | Rationale & Compliance |
| :--- | :--- | :--- | :--- | :--- |
| **All software, code, scripts, Jekyll config, workflows, codemeta** | **EUPL 1.2** | `/LICENSE-EUPL-1.2.txt` | `EUPL-1.2` | The official open-source license of the European Commission and ESA. Provides strong copyleft protection against closed-source hijacking, while maintaining explicit compatibility with other major licenses, ensuring smooth legal approval by NASA and CSA. |
| **All documentation, papers, text, datasets, CSV, JSON, photos, images, videos, figures** | **CC BY-SA 4.0** | `/LICENSE-CC-BY-SA-4.0.md` | `CC-BY-SA-4.0` | Mandates explicit attribution and ensures derivative works remain open (ShareAlike). Aligns with NASA SPD-41a, ESA Open Science Policy, CSA Open Science, and Horizon Europe MGA Art.14, while preventing proprietary enclosure of open research data. |
| **Hardware designs, patents, schematics, and physical implementations** | **All Rights Reserved** | N/A (See https://w-1-n.com) | N/A | Strictly proprietary. This repository contains architectural theory only. Future open-hardware releases, if any, will be governed separately. |

---

## How to Apply — For Contributors

Add the following header to the top of each file you create or modify to ensure automated SPDX compliance scanners (like FSFE REUSE) can correctly identify the license.

### 1. For Code Files (.sh, .yml, .json, .js, .py, .go, .html)

    # Copyright 2026 Louis-Philippe Audette
    # SPDX-License-Identifier: EUPL-1.2
    # Licensed under the EUPL 1.2 — see /LICENSE-EUPL-1.2.txt

### 2. For Data and Documentation Files (.md, .csv, .txt, data .json)

    # Copyright 2026 Louis-Philippe Audette
    # SPDX-License-Identifier: CC-BY-SA-4.0
    # Licensed under CC BY-SA 4.0 — see /LICENSE-CC-BY-SA-4.0.md

---

## The Audette Clause

All contributions and derivative works must respect "The Audette Clause". This architecture was conceived, authored, and architected by Louis-Philippe Audette. Any deployment, publication, or commercial application must prominently retain attribution and provide clear credit to the original architect. 

See `/NOTICE.md` for the full legal text.

---

## Related Documents

- [NOTICE.md](/NOTICE.md) — Copyright and mandatory attribution.
- [docs/LICENSE_COMPLIANCE.md](/docs/LICENSE_COMPLIANCE.md) — Detailed multi-agency compliance matrix.
- [CONTRIBUTING.md](/CONTRIBUTING.md) — Rules for submitting pull requests under this framework.
