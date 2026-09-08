Where does that go;

# Trust and Provenance

## Mission

psivicom.github.io is an open science hub designed to be usable by agencies and researchers while remaining tamper-evident, attributable, and auditable.

Open science makes the work available. Cybersecurity makes it believable.

## Standards Alignment

This project is aligned with:

- NASA Open Science / SMD guidance
- NASA SPD-41a
- FAIR, TRUST, and CARE principles
- CIS Controls v8, especially IG1
- supply-chain integrity best practices
- reproducible research and archival citation norms

## Licensing

The project keeps a dual-license model:

- code fixes and technical patches: **Apache-2.0**
- data, documentation, policy text, and prose: **CC-BY-4.0**

License boundaries should be explicit in-file when needed.

## Trust Model

The site assumes a hostile environment.

Expected threats include:

- public cloning
- malicious pull requests
- dependency hijacking
- compromised build actions
- artifact tampering
- silent modification of published outputs

The build and release process should reduce the chance that untrusted input becomes trusted output.

## Provenance Requirements

Important files and outputs should be traceable to:

- author or maintainer
- creation or update date
- source inputs
- method, notebook, or build path
- generated output
- version or tag
- related references
- archive identifier or DOI where applicable

Preferred metadata files include:

- `codemeta.json`
- `CITATION.cff`
- `CHANGELOG.md`
- archive metadata under `ARCHIVE/`

## Interconnected File Graph

No important file should be orphaned.

Each significant file should be linked from at least one of:

- `README.md`
- `SECURITY.md`
- `SECURITY_PLAN.md`
- an index file
- a metadata file
- a project map

If a file matters, it must be reachable.

## Build Integrity

To keep published output trustworthy:

- pin GitHub Actions by commit SHA
- use branch protection on `main`
- require review before merge
- disable unnecessary token permissions
- keep `persist-credentials: false` where appropriate
- use Dependabot for controlled updates
- run CodeQL and dependency review
- generate an SBOM for released builds when practical
- verify data manifests with checksums

## Data Integrity

Where datasets or derived files matter, preserve integrity with:

- manifest files such as `data/manifest.sha256`
- documented source provenance
- recorded transformation steps
- stable archive snapshots
- citation-ready release versions

## Release and Archiving

A release intended for citation should be:

1. prepared from a clean state
2. checked for link and reference completeness
3. frozen at a version or tag
4. archived with metadata
5. assigned a DOI or equivalent archive identifier
6. recorded in the repository metadata

If a release is superseded, the older version must remain identifiable and citable.

## Auditability

Changes to published research material should be:

- documented
- attributable
- versioned
- reviewable
- reproducible where practical

Security findings, provenance issues, and major release changes should have a durable record.

## References

Use the canonical references below in site documentation and policy text:

- NASA Open Science: https://science.nasa.gov/open-science
- NASA Open Source Science / SPD-41a: https://science.nasa.gov/researchers/open-science/open-source-science
- NASA data portal: https://data.nasa.gov
- NASA open science funding: https://science.nasa.gov/open-science/nasa-open-science-funding-opportunities/
- CIS Controls: https://www.cisecurity.org/controls
- CIS Benchmarks: https://www.cisecurity.org/cis-benchmarks

## Contact

Maintainer: Louis-Philippe Audette  
Location: Goldstream, Langford, BC  
Email: louis@psivi.com

**Related file:
/TRUST_AND_PROVENANCE.md (this file)
/README.md (mention in policies)
/SECURITY.md 
/SECURITY_PLAN.md (include as a reference control document)
