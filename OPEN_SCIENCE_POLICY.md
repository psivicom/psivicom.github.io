# Open Science Policy

## Purpose

This repository follows an **Open Data, Hardened Build** model:

- research outputs, data, and documentation are open and reusable
- code and build processes are hardened to support integrity, traceability, and auditability
- all major project artifacts must be attributable, versioned, and traceable

This policy exists to support reproducible research, prevent misrepresentation, and make provenance clear.

## Scope

This policy applies to:

- source code
- notebooks
- datasets
- documentation
- release artifacts
- metadata files
- archived snapshots
- any derived or published research outputs

## Licensing

Unless otherwise noted:

- code fixes and technical patches are licensed under **Apache-2.0**
- data, policy text, and documentation are licensed under **CC-BY-4.0**

If a file needs a different license, it must be stated clearly in that file or its header.

## Authorship and Attribution

Every important file should have clear provenance.

Required metadata, where practical:

- file name
- creation date
- author or maintainer
- source inputs
- method or notebook used
- output produced
- version or tag
- related references
- DOI or archive link when applicable

Authorship must not be obscured. Contributions should be credited in a way that remains durable across releases and archives.

## Provenance Rules

To preserve auditability:

- keep analysis in dated notebooks or equivalent traceable documents
- record source inputs and transformations
- retain references for claims, figures, and derived conclusions
- avoid untracked manual edits to published research outputs
- link release artifacts to their source materials
- archive release snapshots when a result is intended to be citable

## Archiving

When releasing a stable research output:

1. prepare a clean release folder
2. verify links and references
3. freeze the version
4. archive the release, including metadata
5. record the DOI or archive identifier in the project records

If a release is superseded, the earlier version must remain identifiable.

## No-Orphan File Rule

Important files must not be isolated.

Every significant file should be reachable from at least one of:

- `README.md`
- `SECURITY.md`
- `SECURITY_PLAN.md`
- an index file
- a project map or metadata file

If a file matters to the project, it must be linked, referenced, or indexed.

## Supply Chain Integrity

Build and release processes should favor integrity and reproducibility.

Recommended controls include:

- pinned dependencies where practical
- versioned build environments
- recorded tool versions
- review before merge for release-impacting changes
- protected branches for published work
- signed or verified release artifacts where feasible

## Change Control

Changes to published research outputs should be:

- documented
- traceable
- attributable
- versioned

Material changes should include a note describing what changed and why.

## Exceptions

Any exception to this policy should be:

- documented
- time-bounded
- approved by the maintainer
- linked to the affected file, release, or record

## Contact

Maintainer: Louis-Philippe Audette  
Location: Goldstream, Langford, BC  
Email: louis@psivi.com

## Related Files

- `SECURITY.md`
- `SECURITY_PLAN.md`
- `AUTHORS.md`
- `CHANGELOG.md`
- `README.md`
