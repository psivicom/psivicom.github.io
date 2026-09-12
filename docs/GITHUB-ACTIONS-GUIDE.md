# GitHub Actions Operations Guide

**Architect & Principal Investigator:** Louis-Philippe Audette  
**Last Updated:** 2026-09-11T00:00:00.000Z  
**Project:** PSIVI.COM Open Science Hub  

---

## 1. Overview

This repository utilizes GitHub Actions to automate critical maintenance, compliance, and build tasks. These workflows ensure that documentation remains synchronized, timestamps adhere to NASA SPD-41a Zulu standards, and the repository structure remains accurately mapped without manual intervention.

---

## 2. Accessing GitHub Actions

To view, monitor, or manually trigger automated workflows:

1. Navigate to the repository: https://github.com/psivicom/psivicom.github.io
2. Click the **Actions** tab located in the top navigation bar (between "Pull requests" and "Security").
3. The left sidebar will display a list of all configured workflows.

---

## 3. Available Workflows

| Workflow File | Purpose | Trigger |
| :--- | :--- | :--- |
| `docs.yml` | Converts Markdown documentation (e.g., `docs/osdmp.md`) into static HTML (e.g., `docs/osdmp.html`) for the live website. | Push to `main` or manual dispatch. |
| `update-tree.yml` | Automatically scans the repository and updates the interconnected file tree diagram in `README.md`. | Push to `main` affecting file structure. |
| `fix-all-timestamps.yml` | Scans repository files and corrects timestamp formatting to strict RFC3339 Zulu time with millisecond precision. | Manual dispatch or scheduled maintenance. |
| `timestamp-check.yml` | Validates that all new commits and modified files adhere to the canonical `YYYY-MM-DDTHH:MM:SS.sssZ` format. | Pull requests and pushes to `main`. |

---

## 4. Manual Execution (Workflow Dispatch)

If a workflow needs to be run immediately (e.g., after updating `osdmp.md` to force the HTML regeneration):

1. Go to the **Actions** tab.
2. Select the desired workflow from the left sidebar (e.g., **docs**).
3. On the right side of the screen, click the **Run workflow** dropdown button.
4. Ensure the **Branch** is set to `main`.
5. Click the green **Run workflow** button.

---

## 5. Monitoring and Verification

After triggering a workflow (or after a standard push):

1. Click on the specific workflow run name in the list (e.g., "docs: Convert OSDMP to HTML").
2. Click on the job name (e.g., `build` or `update`) to expand the execution logs.
3. **Success:** A green checkmark indicates the job completed all steps without errors. Changes will be automatically committed back to the repository if configured to do so.
4. **Failure:** A red "X" indicates a failure. Click the failed step to view the specific error output in the console logs.

---

## 6. Troubleshooting Common Issues

If a workflow fails, check the logs for the following common causes:

- **Case Sensitivity Errors:** Linux-based GitHub runners are strictly case-sensitive. Ensure file paths in scripts match the exact casing of the repository (e.g., `osdmp.md`, not `OSDMP.md`).
- **Missing Dependencies:** Workflows requiring external tools (e.g., Pandoc for HTML conversion, Go for tree rendering) must have the installation step successfully completed.
- **License/Formatting Violations:** The `timestamp-check.yml` workflow will intentionally fail a Pull Request if a file is committed with a local timezone offset or missing millisecond precision, preventing non-compliant code from merging.
- **Permission Denied:** Ensure the `GITHUB_TOKEN` has the necessary `contents: write` permissions in the workflow YAML file to commit automated changes.

---

## 7. Best Practices for Contributors

- **Do not manually edit auto-generated files** (e.g., `docs/osdmp.html` or the `AUTO_TREE` block in `README.md`). Always edit the source Markdown files and let the workflows handle the generation.
- **Review Action logs** after making significant structural changes to ensure the `update-tree.yml` workflow executed successfully.
- **Use the provided templates** for commit messages to ensure automated parsers and changelog generators function correctly.

---

## 8. Workflow Identification and Verification Protocol

The execution names displayed in the GitHub Actions user interface correspond directly to the `name:` parameter defined in the header of each `.yml` configuration file. 

### Mapping Execution Names to Source YAML Files
- **Update Repository Tree** maps to `.github/workflows/update-tree.yml`.
- **build-docs-styled** (or similar) maps to `.github/workflows/docs.yml` (responsible for Markdown to HTML conversion, e.g., `osdmp.md` to `osdmp.html`).
- **Fix ALL timestamps to mil...** maps to `.github/workflows/fix-all-timestamps.yml`.
- **NASA Auto-Correct to .ss...** maps to `.github/workflows/timestamp-check.yml`.
- *Platform Native:* **pages-build-deployment** is an automated, platform-native GitHub Pages workflow managed by GitHub. It does not correspond to a repository-specific YAML file.

### Standard Operating Procedure for Verification
To verify that the correct automation pipeline executed successfully and produced the expected artifact:
1. **Identify the Execution Run:** Navigate to the Actions tab and select the specific workflow run by clicking its execution name.
2. **Confirm Source Configuration:** Verify the workflow file path displayed at the top of the execution summary (e.g., `Workflow file: .github/workflows/docs.yml`).
3. **Evaluate Execution Status:**
   - **Success (Green Checkmark):** The pipeline completed all steps without syntax or runtime errors.
   - **Failure (Red X):** The pipeline encountered an error. Review the console logs of the specific failed job step to identify the root cause (e.g., case-sensitivity mismatches, missing dependencies).
4. **Validate Artifact Generation:** Do not rely solely on UI status indicators. Navigate to the repository file tree and inspect the target output file (e.g., `docs/osdmp.html`) to confirm that the content reflects the latest source updates, correct licensing (EUPL 1.2 / CC BY-SA 4.0), and strict Zulu timestamps.

---

## 9. Manual Dispatch Procedures

If an automated trigger fails to initiate or an immediate regeneration is required, the workflow can be dispatched manually via the Actions interface:
1. Select the target workflow from the left navigation pane.
2. Click the **Run workflow** dropdown menu on the right.
3. Ensure the target branch is set to `main`.
4. Initiate the run and monitor the execution queue for the newly generated job.

---

<br>
<br>

---
**© 2026 Louis-Philippe Audette**  
**Contact:** louis@psivi.com | **Web:** https://psivi.com  

**Licensing:**  
This documentation is licensed under **Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)**.  
Associated software and workflows in this repository are licensed under the **European Union Public Licence v. 1.2 (EUPL 1.2)**.  
Hardware designs, schematics, and physical IP are **All Rights Reserved** (https://w-1-n.com).  

*Part of the PSIVI.COM Open Science Hub — Excellence Edition.*
