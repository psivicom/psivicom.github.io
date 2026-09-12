# Trust and Provenance

**Architect & Principal Investigator:** Louis-Philippe Audette  
**Last Updated:** 2026-09-11T00:00:00.000Z  

## Mission

`psivicom.github.io` is an open science hub designed to be usable by agencies and researchers while remaining tamper-evident, attributable, and auditable.

Open science makes the work available. Cybersecurity and strict provenance make it believable.

## Standards Alignment

This project is aligned with:
- NASA Open Science / SMD guidance & NASA SPD-41a
- FAIR, TRUST, and CARE principles
- CIS Controls v8 (especially IG1)
- Supply-chain integrity best practices
- Reproducible research and archival citation norms

## Licensing & Domain Separation

The project enforces a strict, domain-separated licensing model to maximize open-science impact while protecting specific commercial interests:
- **Code, scripts, and workflows**: **EUPL 1.2** (OSI-approved, strong copyleft, satisfies NASA/ESA mandates)
- **Data, documentation, policy text, and prose**: **CC BY-SA 4.0** (ensures derivative research remains open)
- **Hardware designs and physical IP**: **All Rights Reserved** (managed separately at [w-1-n.com](https://w-1-n.com))

License boundaries must be explicit in-file via SPDX headers when needed.

## Trust Model

The site assumes a hostile environment. Expected threats include:
- Public cloning and unauthorized redistribution
- Malicious pull requests or dependency hijacking
- Compromised build actions or artifact tampering
- Silent modification of published outputs

The build and release process is designed to reduce the chance that untrusted input becomes trusted output.

## Provenance Requirements

Important files and outputs must be traceable to:
- Author or maintainer (enforcing "The Audette Clause" — see `NOTICE.md`)
- Creation or update date (strict Zulu time with milliseconds: `YYYY-MM-DDTHH:MM:SS.sssZ`)
- Source inputs and method/notebook/build path
- Generated output and version or tag
- Related references and archive identifier or DOI where applicable

Preferred metadata files include:
- `codemeta.json`
- `CITATION.cff`
- `.zenodo.json`
- `REUSE.toml`
- `NOTICE.md`

## Interconnected File Graph

No important file should be orphaned. Each significant file must be linked from at least one of:
- `README.md`
- `SECURITY.md` or `SECURITY_PLAN.md`
- An index file or metadata file
- A project map or `docs/README.md`

If a file matters, it must be reachable.

## Build Integrity

To keep published output trustworthy:
- Pin GitHub Actions by commit SHA
- Use branch protection on `main` and require review before merge
- Disable unnecessary token permissions and keep `persist-credentials: false` where appropriate
- Use Dependabot for controlled updates
- Run CodeQL and dependency review
- Generate an SBOM for released builds when practical
- Verify data manifests with checksums

## Data Integrity

Where datasets or derived files matter, preserve integrity with:
- Manifest files (e.g., `data/manifest.sha256`)
- Documented source provenance and recorded transformation steps
- Stable archive snapshots and citation-ready release versions

## Release and Archiving

A release intended for citation should be:
1. Prepared from a clean state
2. Checked for link and reference completeness
3. Frozen at a version or tag
4. Archived with metadata (via Zenodo / OSF)
5. Assigned a DOI or equivalent archive identifier
6. Recorded in the repository metadata (`codemeta.json`, `CITATION.cff`)

If a release is superseded, the older version must remain identifiable and citable.

## Auditability & AI Transparency

Changes to published research material must be:
- Documented and attributable
- Versioned and reviewable
- Reproducible where practical
- **Human-Reviewed**: AI-assisted workflows are permitted, but no AI-generated content may be published without rigorous human review, validation, and accountability.

Security findings, provenance issues, and major release changes must have a durable record.

## References

Use the canonical references below in site documentation and policy text:
- NASA Open Science: https://science.nasa.gov/open-science
- NASA Open Source Science / SPD-41a: https://science.nasa.gov/researchers/open-science/open-source-science
- NASA Data Portal: https://data.nasa.gov
- CIS Controls: https://www.cisecurity.org/controls
- CIS Benchmarks: https://www.cisecurity.org/cis-benchmarks

## Contact

**Maintainer:** Louis-Philippe Audette  
**Location:** Goldstream, Langford, BC, Canada  
**Email:** louis@psivi.com  

**Related Files:**
- `/TRUST_AND_PROVENANCE.md` (this file)
- `/README.md` (mention in policies)
- `/SECURITY.md`
- `/SECURITY_PLAN.md` (include as a reference control document)
- `/NOTICE.md`
