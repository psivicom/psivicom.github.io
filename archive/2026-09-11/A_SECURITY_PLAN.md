# SECURITY_PLAN.md
## Operational Security, Provenance, and Archiving Plan
**Project:** psivicom.github.io  
**Applies to:** main branch, linked notebooks, reference files, archives, and release artifacts

## 1. Purpose
This plan turns the security policy into operational steps. It exists to preserve authorship, provenance, reproducibility, integrity, and persistence of the project’s research and code artifacts.

## 2. Core Principles
- Every important file must have a clear purpose.
- Every important file must be linked from a main index or policy file.
- No orphan files: if a file matters, it must be discoverable from the project structure.
- Source, drafts, notebooks, references, and archives must remain traceable.
- Stable releases should be archived with persistent identifiers when appropriate.
- Research claims must be backed by dated notes, source files, and reproducible steps.

## 3. Recommended File Map
Top-level files:
- `SECURITY.md` — policy and reporting
- `SECURITY_PLAN.md` — operational steps
- `README.md` — project entry point
- `AUTHORS.md` — authorship and attribution
- `CHANGELOG.md` — material changes over time

Supporting folders:
- `NOTEBOOKS/` — Jupyter notebooks and analysis drafts
- `REFERENCES/` — source files, citations, notes, and traceability records
- `DATA/` — raw and processed data
- `ARCHIVE/` — release notes, DOI metadata, preserved snapshots
- `REPORTS/` — security findings, summaries, and remediation records if needed

## 4. Provenance Recording
Provenance means being able to show where a file came from, who created it, when it was created, and how it changed.

### Required practices
- Start important work in a dated notebook or draft file.
- Record author, date, and purpose at the top of each major file.
- Keep source material with its related analysis.
- Preserve the original input files used to create results.
- Do not overwrite a file without keeping prior versions or a changelog entry.
- When a claim is made, include the source file or reference that supports it.

### Provenance metadata to record
For each important artifact, track:
- file name
- creation date
- author or maintainer
- source inputs
- method or notebook used
- output generated
- version or release tag
- related references
- archived DOI or external identifier, if any

### Good practice
Use a simple provenance note at the top of major files:
```text
Created: YYYY-MM-DD
Author: Name or handle
Purpose: Short description
Inputs: linked files or source references

5. Zenodo DOI Archiving

Zenodo is used for stable archival copies of finished or release-worthy artifacts.

When to archive

Archive when:

a release is stable
a notebook supports a published result
a dataset or analysis needs a persistent citation
a version must remain accessible for audit or reproducibility
What to archive

final notebooks
final reports
release snapshots
important reference bundles
release metadata
Archiving steps

Prepare a clean release folder.
Confirm all linked files are present.
Remove temporary scratch files.
Freeze the version with a release tag.
Upload the release package to Zenodo.
Record the DOI in ARCHIVE/zenodo_metadata.md.
Link the DOI from README.md, SECURITY.md, or the relevant release note.
Keep the archived package unchanged after publication.
Metadata to record

release version
Zenodo DOI
upload date
included files
checksum or hash, if used
short description of what was archived
6. Supply-Chain Integrity

Supply-chain integrity means verifying that the tools, dependencies, and artifacts you use are the ones you intended to use.

Required checks

Pin dependencies where possible.
Review dependency updates before merging.
Prefer signed or trusted releases when available.
Keep a record of exact versions used for important work.
Verify notebook kernels, libraries, and build tools before release.
Avoid pulling unknown code into active analysis without review.
Record any manual override or exception.
Operational checks

For each release or major analysis:

list dependency versions
confirm source repository or package origin
note integrity checks if available
record any critical tool changes
rerun important analysis after dependency changes when results matter

Example integrity record

Tool: Python
Version: 3.x.x
Notebook kernel: linked
Dependency lockfile: present or not present
Notable changes: none / listed here
Verification date: YYYY-MM-DD

7. No-Orphan File Rule

No file should exist without a path back to the project’s main structure.

Rule

If a file is important enough to keep, it must be:

linked from README.md, SECURITY.md, SECURITY_PLAN.md, or an index file
placed in a relevant folder
named clearly
referenced by at least one other project file
How to avoid orphans

Maintain an index file for each major folder.
Add cross-links in the README.
Keep reference files at the bottom of the project or in a dedicated reference folder.
Ensure every notebook points to its source files and outputs.
Ensure every archive record points back to the release it preserves.
Folder index suggestion

REFERENCES/index.md
NOTEBOOKS/index.md
ARCHIVE/index.md
8. File Linking and Traceability

Every important file should say where it belongs.

Required links

README.md should point to policy, plan, references, and archives.
SECURITY.md should point to this plan.
SECURITY_PLAN.md should point to the notebook, reference, and archive locations.
Each notebook should reference its input files and output reports.
Each archive record should reference the exact release it preserves.
Traceability chain

A complete chain should look like:

source file
notebook or analysis draft
report or result
release snapshot
Zenodo DOI
changelog entry
9. Release Checklist

Before any release:

 All important files are linked
 No orphan files remain
 Provenance notes are present
 Source references are complete
 Dependencies are recorded
 Release version is tagged
 Archive package is clean
 Zenodo metadata is prepared
 Checksums or hashes are recorded if used
 Changelog is updated
10. Incident or Security Finding Workflow

If a security issue or integrity issue is found:

record it privately
identify affected files and notebooks
preserve evidence
document the fix
update the plan if the process failed
archive the corrected release when appropriate
11. Maintenance

Review this plan when the project structure changes.
Update file indexes when new folders are added.
Keep archived records aligned with releases.
Refresh dependency records when tooling changes.
Preserve old versions rather than deleting history.
12. Bottom-Line Rule

If a file, notebook, or archive matters, it must be traceable, linked, dated, and preserved.

## Related Policy
This plan implements the requirements in [Trust and Provenance](TRUST_AND_PROVENANCE.md) and [Security Policy](SECURITY.md).

