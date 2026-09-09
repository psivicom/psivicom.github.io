This document answers the how to replicate this exact automation in this repository (or any future fork/clone of it), ensuring the setup is reproducible—a core pillar of FAIR principles.


***

###  REPOSITORY TREE `docs/Installation-Guide-Repository-Tree.md`

```markdown
# Installation & Setup Guide: Auto-Updating Repository Tree

This guide provides step-by-step instructions for setting up the automated repository tree generator. This system ensures that `TREE.md` and the repository structure section in `README.md` are always perfectly synchronized, complete with millisecond-accurate timestamps and SHA-256 provenance hashes.

## Prerequisites
- A GitHub repository.
- Go (Golang) installed locally (v1.21 or higher) for local testing (optional, but recommended).
- GitHub Actions enabled for the repository.

---

## Step 1: Prepare the `README.md`
The automation needs to know exactly where to inject the tree without overwriting your manual content. 

1. Open your `README.md`.
2. Navigate to the section where you want the repository tree to appear (e.g., "06 — Repository Structure").
3. Insert the following HTML comment markers exactly as shown:

```markdown
## 06 — Repository Structure

<!-- AUTO_TREE_START -->
<!-- This section is automatically updated by .github/workflows/update-tree.yml -->
<!-- Last updated: [Will be populated automatically] | Hash: [Will be populated automatically] -->

[The generated tree will be injected here]

<!-- AUTO_TREE_END -->
```
*Note: The script will replace everything between `<!-- AUTO_TREE_START -->` and `<!-- AUTO_TREE_END -->`.*

---

## Step 2: Add the Go Script
The core logic is written in Go for speed and reliability.

1. In the root of your repository, create the directory structure: `scripts/update-tree/`
2. Create a new file named `main.go` inside that directory: `scripts/update-tree/main.go`
3. Paste the complete Go source code into this file. *(Ensure the code includes the `buildTree`, `renderTree`, and `updateREADME` functions with the `2006-01-02T15:04:05.000Z` millisecond timestamp formatting).*

---

## Step 3: Add the GitHub Actions Workflow
This workflow triggers the Go script automatically on every push to the `main` branch, or manually via the GitHub UI.

1. In the root of your repository, create the directory structure: `.github/workflows/`
2. Create a new file named `update-tree.yml` inside that directory.
3. Paste the following YAML configuration:

```yaml
name: Update Repository Tree

on:
  push:
    branches: [ main ]
  workflow_dispatch: # Allows manual triggering from the Actions tab

permissions:
  contents: write

jobs:
  update-tree:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Go
        uses: actions/setup-go@v5
        with:
          go-version: "1.23"
          cache: false

      - name: Generate TREE.md and update README.md
        run: go run ./scripts/update-tree/main.go

      - name: Commit and push changes
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add TREE.md README.md .tree.hash
          git diff --cached --quiet || git commit -m "chore: auto-update tree and README [skip ci]"
          git push
```

---

## Step 4: Initial Execution & Verification

### Option A: Local Testing (Recommended)
Before pushing to GitHub, test the script locally to ensure it finds your `README.md` and markers correctly.
1. Open your terminal in the root of the repository.
2. Run: `go run ./scripts/update-tree/main.go`
3. Check your local `README.md` and `TREE.md`. You should see the beautifully formatted ASCII tree injected between the markers, along with a live timestamp and hash.

### Option B: GitHub Actions
1. Commit the new `scripts/update-tree/main.go` and `.github/workflows/update-tree.yml` files.
2. Push to the `main` branch.
3. Navigate to the **Actions** tab in your GitHub repository.
4. You should see the "Update Repository Tree" workflow running. 
5. Within ~30 seconds, it will complete successfully and create a new commit from `github-actions[bot]` containing the updated `TREE.md`, `README.md`, and `.tree.hash`.

---

## Troubleshooting
- **"no such file or directory"**: Ensure the `README.md` is in the root directory and the markers `<!-- AUTO_TREE_START -->` and `<!-- AUTO_TREE_END -->` are spelled exactly as shown, with no extra spaces.
- **Infinite Loop**: The workflow includes `[skip ci]` in the commit message. Do not remove this, as it prevents the bot's commit from triggering the workflow again.
- **Missing `.github` in tree**: Ensure `.github` is *not* in the `shouldSkip` list in `main.go` if you want workflows to be visible in the generated tree.
```

***
---

## ⚖️ Licensing & Compliance

This repository and its automation tools adhere to a strict dual-licensing model to ensure compliance with Open Science policies (including NASA SPD-41a, CSA, and ESA guidelines) and the REUSE Software Specification.

When implementing or adapting this setup, please note the following license assignments:

| File / Asset Type | Examples in this Guide | License |
| :--- | :--- | :--- |
| **Software & Configuration** | `scripts/update-tree/main.go`, `.github/workflows/update-tree.yml` | **Apache-2.0** |
| **Documentation & Generated Output** | `README.md`, `TREE.md`, `docs/INSTALLATION_GUIDE.md` | **CC-BY-4.0** |

- **Apache-2.0** is used for all code and workflows because it is an OSI-approved license that includes an explicit patent grant, making it the gold standard for space agency and open-source software compliance.
- **CC-BY-4.0** is used for all documentation, datasets, and generated outputs (like the tree structure) to maximize scientific reuse, ensure proper attribution, and align with FAIR data principles.

*For full license texts and machine-readable SPDX compliance, please refer to the `/LICENSES` directory and the `REUSE.toml` file in the root of this repository.*

---

## 👤 Author & Contact

**Louis-Philippe Audette**
Independent Researcher — Goldstream, Langford, BC, Canada

- **Web**: [psivi.com](https://psivi.com) | [psivicom.github.io](https://psivicom.github.io)
- **Email**: [louis@psivi.com](mailto:louis@psivi.com)

*For questions about this setup, the pollinator forage atlas, or collaboration on Earth observation and beekeeping research, please don't hesitate to reach out.*