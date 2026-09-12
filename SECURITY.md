# Security Policy — psivicom.github.io

**Architect & Principal Investigator:** Louis-Philippe Audette  
**Last Updated:** 2026-09-11T00:00:00.000Z  

## Purpose
This policy describes how security issues, authorship, traceability, and project integrity are handled for the PSIVI.COM Open Science Hub (`psivicom.github.io`).

## Scope
This policy applies to the `main` branch and to all linked project files, notebooks, drafts, references, and archived artifacts within this repository.

## Licensing & Domain Separation
This repository follows a strict, domain-separated dual-license model:
- **Code fixes, scripts, and technical patches**: Licensed under **EUPL 1.2**.
- **Policy text, documentation, and data**: Licensed under **CC BY-SA 4.0**.
- **Hardware designs and physical IP**: **All Rights Reserved** (managed separately at [w-1-n.com](https://w-1-n.com)). File-level licensing is explicit via SPDX headers.

## Reporting Security Issues
Report security concerns through the [psivi.com contact form](https://psivi.com). 

**Do not** submit sensitive details, vulnerabilities, or proprietary information in public GitHub issues or public comments. Security reports are kept strictly private until a fix is prepared, validated, and released.

## Handling of Reports
- Triage all reports privately and securely.
- Preserve a dated log of findings and actions using strict Zulu time with millisecond precision (`YYYY-MM-DDTHH:MM:SS.sssZ`).
- Link each report to relevant source files, notebooks, and metadata.
- Keep reference files at the bottom of the project for traceability.
- Avoid orphan files; every security-related file must be linked from this policy, `TRUST_AND_PROVENANCE.md`, or a central index file.

## Authorship and Attribution
- Use dated notebooks and drafts (Zulu time).
- Keep source files grouped with their related analysis.
- Preserve provenance for major changes, enforcing "The Audette Clause" (see `NOTICE.md`) to ensure the original architect receives prominent credit for derivative architectural works.
- Use Zenodo or OSF for archival copies and stable identifiers when appropriate.
- Clearly separate working drafts from final, citable releases.

## Secure Project Practices
- Maintain backups of original files and metadata.
- Keep detailed changelogs for material changes.
- Review linked files for completeness and license consistency before release.
- Do not overwrite source material without preserving prior versions via Git history.
- Store supporting references in dedicated folders (e.g., `docs/`, `archive/`) rather than scattered files.

## Release Process
- Prepare fixes in a separate branch or draft area.
- Verify linked files, SPDX headers, and references before publishing.
- Publish only after reviewing traceability, attribution, and FAIR compliance.
- Include clear release notes for significant changes, updating `codemeta.json` and `.zenodo.json` as needed.

## Related Documents
- [Trust and Provenance](TRUST_AND_PROVENANCE.md)
- [Security Plan](SECURITY_PLAN.md)
- [Repository Policy](POLICY.md)
- [License Compliance](docs/LICENSE_COMPLIANCE.md)
- [Notice & Attribution](NOTICE.md)

## Contact
Use the [psivi.com contact form](https://psivi.com) for all security-related reports. For hardware-specific security or IP inquiries, contact via [w-1-n.com](https://w-1-n.com).

---
*License: CC BY-SA 4.0 for this documentation file. EUPL 1.2 for any associated code fixes or scripts.*
