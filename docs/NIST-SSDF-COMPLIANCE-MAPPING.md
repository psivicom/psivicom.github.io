# NIST SSDF (SP 800-218) Compliance Mapping

**Architect & Principal Investigator:** Louis-Philippe Audette  
**Last Updated:** 2026-09-11T00:00:00.000Z  
**Project:** PSIVI.COM Open Science Hub  

---

## 1. Purpose: The "Glass Box" Architecture

International space agencies (NASA, ESA, CSA) increasingly mandate compliance with the NIST Secure Software Development Framework (SSDF), SP 800-218, to mitigate software supply chain risks and prevent "black box" proprietary lock-in. 

This document explicitly maps the PSIVI.COM Open Science Hub architecture to the four core practices of the NIST SSDF, demonstrating that this repository is a fully transparent, auditable, and secure "Glass Box."

---

## 2. Core Practice 1: Prepare the Organization (PO)
*NIST Requirement: Define security requirements, train developers, and secure the development environment.*

**PSIVI Implementation:**
- **PO.1 (Define Requirements):** The `AI-COLLABORATION-PROTOCOL.md` and `SECURITY_PLAN.md` explicitly define strict operational constraints, including Zulu timestamp enforcement (`YYYY-MM-DDTHH:MM:SS.sssZ`) and mandatory human-in-the-loop validation.
- **PO.2 (Secure Toolchain):** Automated CI/CD workflows (e.g., `fair-check.yml`) enforce compliance before any code can be merged, ensuring the development environment itself validates security and FAIR principles.

---

## 3. Core Practice 2: Protect the Software (PS)
*NIST Requirement: Protect all forms of source code, infrastructure, and access controls from tampering.*

**PSIVI Implementation:**
- **PS.1 (Protect Source Code):** The repository utilizes strict Git branch protection and immutable, cryptographically hashed commit histories. 
- **PS.2 (Access Control & Attribution):** The "Audette Clause" (`NOTICE.md`) legally and technically binds all contributions to verifiable human accountability. Any unauthorized fork or alteration that strips attribution is a detectable violation of the license terms.
- **PS.3 (Tamper-Evident Provenance):** All data and code modifications are logged with millisecond-precision Zulu timestamps, creating a court-admissible audit trail of exactly who changed what, and when.

---

## 4. Core Practice 3: Produce Well-Secured Software (PW)
*NIST Requirement: Use secure coding practices, peer review, and manage third-party dependencies.*

**PSIVI Implementation:**
- **PW.1 (Secure Dependencies):** The `SECURITY_PLAN.md` mandates dependency pinning, origin verification, and the generation of Software Bill of Materials (SBOMs) for all releases, preventing supply chain poisoning.
- **PW.2 (Peer Review & AI Validation):** The multi-agent AI review protocol requires an automated "Critic Agent" to cross-reference all proposed changes against ground-truth data before human review, eliminating hallucinations and logical flaws.
- **PW.3 (Anti-Black-Box Licensing):** The use of **EUPL 1.2** (for code) and **CC BY-SA 4.0** (for data) legally prohibits any entity (including government contractors) from incorporating this work into closed-source, proprietary "black box" systems. The source must remain open and auditable. Machine-readable compliance is enforced via `REUSE.toml` and SPDX headers.

---

## 5. Core Practice 4: Respond to Vulnerabilities (RV)
*NIST Requirement: Understand, analyze, and remediate vulnerabilities transparently.*

**PSIVI Implementation:**
- **RV.1 (Vulnerability Identification):** The `SECURITY.md` policy provides a clear, private reporting channel for security findings, preventing public exposure of unpatched flaws.
- **RV.2 (Root Cause Analysis & Patching):** All remediations are documented in `CHANGELOG.md` with strict Zulu timestamps, linking the fix directly to the affected files and the original vulnerability report.
- **RV.3 (Archival Integrity):** Patched releases are archived via Zenodo with persistent DOIs, ensuring that the historical record of the vulnerability and its resolution remains permanently accessible for agency audit.

---

## 6. Conclusion for Agency Reviewers

The PSIVI.COM architecture does not merely claim to be secure; it provides **cryptographic, legal, and methodological proof** of its adherence to NIST SP 800-218. By combining open-source transparency (EUPL 1.2 / CC BY-SA 4.0), rigorous provenance (Zulu timestamps), and ethical AI constraints, this repository eliminates supply chain opacity and serves as a model for secure, auditable space science software.

---

*Part of the PSIVI.COM Open Science Hub — Excellence Edition.*  
*Related: [SECURITY_PLAN.md](../SECURITY_PLAN.md), [AI-COLLABORATION-PROTOCOL.md](../AI-COLLABORATION-PROTOCOL.md), [NOTICE.md](../NOTICE.md)*
