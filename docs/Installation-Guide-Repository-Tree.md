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

// /scripts/update-tree/main.go
```GO
package main

import (
	"bytes"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"time"
)

const (
	readmePath  = "README.md"
	treePath    = "TREE.md"
	hashPath    = ".tree.hash"
	markerStart = "<!-- AUTO_TREE_START -->"
	markerEnd   = "<!-- AUTO_TREE_END -->"
)

func main() {
	fmt.Println("🚀 Starting tree update script...")
	
	cwd, err := os.Getwd()
	if err != nil {
		panic(fmt.Errorf("getting working directory: %w", err))
	}
	fmt.Printf("📁 Current working directory: %s\n", cwd)

	fmt.Println("🌳 Building repository tree...")
	tree, err := buildTree(".")
	if err != nil {
		panic(fmt.Errorf("building tree: %w", err))
	}

	sum := sha256.Sum256([]byte(tree))
	hash := hex.EncodeToString(sum[:])
	timestamp := time.Now().UTC().Format("2006-01-02T15:04:05.000Z")

	fmt.Printf("💾 Writing %s and %s...\n", treePath, hashPath)
	mustWrite(treePath, tree)
	mustWrite(hashPath, hash+"\n")

	fmt.Printf("📝 Attempting to read and update %s...\n", readmePath)
	err = updateREADME(tree, hash, timestamp)
	if err != nil {
		panic(fmt.Errorf("updating README: %w", err))
	}

	fmt.Println("✅ Successfully updated TREE.md, .tree.hash, and README.md")
}

func mustWrite(path, content string) {
	if err := os.WriteFile(path, []byte(content), 0644); err != nil {
		panic(fmt.Errorf("writing %s: %w", path, err))
	}
}

func updateREADME(tree, hash, timestamp string) error {
	content, err := os.ReadFile(readmePath)
	if err != nil {
		return fmt.Errorf("reading %s: %w", readmePath, err)
	}

	newBlock := fmt.Sprintf("%s\n<!-- Last updated: %s | Hash: %s -->\n\n%s\n%s",
		markerStart, timestamp, hash, strings.TrimSpace(tree), markerEnd)

	startIdx := bytes.Index(content, []byte(markerStart))
	endIdx := bytes.Index(content, []byte(markerEnd))

	if startIdx == -1 || endIdx == -1 {
		return fmt.Errorf("could not find %s and %s markers in %s", markerStart, markerEnd, readmePath)
	}

	if startIdx >= endIdx {
		return fmt.Errorf("markers are in the wrong order in %s", readmePath)
	}

	var newContent bytes.Buffer
	newContent.Write(content[:startIdx])
	newContent.WriteString(newBlock)
	newContent.Write(content[endIdx+len(markerEnd):])

	return os.WriteFile(readmePath, newContent.Bytes(), 0644)
}

// --- NEW TREE BUILDING AND RENDERING LOGIC ---

type TreeNode struct {
	Name     string
	IsDir    bool
	Children []*TreeNode
}

func buildTree(root string) (string, error) {
	var entries []string
	var isDir []bool

	err := filepath.WalkDir(root, func(path string, d os.DirEntry, err error) error {
		if err != nil {
			return err
		}
		if path == "." {
			return nil
		}

		slash := filepath.ToSlash(path)
		if shouldSkip(slash) {
			if d.IsDir() {
				return filepath.SkipDir
			}
			return nil
		}

		entries = append(entries, slash)
		isDir = append(isDir, d.IsDir())
		return nil
	})
	if err != nil {
		return "", err
	}

	// Build the tree structure
	rootNode := &TreeNode{Name: "psivicom.github.io", IsDir: true}
	
	for i, path := range entries {
		parts := strings.Split(path, "/")
		current := rootNode
		for j, part := range parts {
			isLastPart := (j == len(parts)-1)
			
			var child *TreeNode
			for _, c := range current.Children {
				if c.Name == part {
					child = c
					break
				}
			}
			
			if child == nil {
				child = &TreeNode{
					Name:  part,
					IsDir: !isLastPart || isDir[i],
				}
				current.Children = append(current.Children, child)
			}
			current = child
		}
	}

	// Sort children recursively (directories first, then alphabetically)
	sortTree(rootNode)

	// Render the tree
	var b strings.Builder
	b.WriteString("```\n")
	b.WriteString(renderTree(rootNode, "", true))
	b.WriteString("```\n")

	return b.String(), nil
}

func sortTree(node *TreeNode) {
	sort.Slice(node.Children, func(i, j int) bool {
		if node.Children[i].IsDir != node.Children[j].IsDir {
			return node.Children[i].IsDir && !node.Children[j].IsDir
		}
		return node.Children[i].Name < node.Children[j].Name
	})
	for _, child := range node.Children {
		if child.IsDir {
			sortTree(child)
		}
	}
}

func renderTree(node *TreeNode, prefix string, isLast bool) string {
	var b strings.Builder
	
	if node.Name != "psivicom.github.io" {
		connector := "├── "
		if isLast {
			connector = "└── "
		}
		b.WriteString(prefix + connector + node.Name)
		if node.IsDir {
			b.WriteString("/")
		}
		b.WriteString("\n")
		
		if isLast {
			prefix += "    "
		} else {
			prefix += "│   "
		}
	} else {
		b.WriteString(node.Name + "/\n")
	}

	for i, child := range node.Children {
		b.WriteString(renderTree(child, prefix, i == len(node.Children)-1))
	}
	
	return b.String()
}

func shouldSkip(path string) bool {
	// Note: .github is REMOVED from this list so it shows up in your tree!
	skips := []string{
		".git",
		".tree.hash",
		"TREE.md",
		"node_modules",
	}

	for _, s := range skips {
		if path == s || strings.HasPrefix(path, s+"/") {
			return true
		}
	}
	return false
}
```
---

## Step 3: Add the GitHub Actions Workflow
This workflow triggers the Go script automatically on every push to the `main` branch, or manually via the GitHub UI.

1. In the root of your repository, create the directory structure: `.github/workflows/`
2. Create a new file named `update-tree.yml` inside that directory.
3. Paste the following YAML configuration:

// /.github/workflows/update-tree.yml
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

## 🔄 How `TREE.md` is Created and Used (Script Interaction)

Understanding the lifecycle of `TREE.md` is crucial for maintaining the repository's provenance and FAIR compliance. 

### 1. Creation (The Go Script)
`TREE.md` is automatically generated by the Go script located at `scripts/update-tree/main.go`. 
- **What it does**: It walks the repository directory, builds a nested ASCII tree, calculates a SHA-256 hash of the tree content, and generates a millisecond-accurate UTC timestamp.
- **Output**: It writes the formatted tree to `TREE.md`, saves the hash to `.tree.hash`, and safely injects both into `README.md` between the `<!-- AUTO_TREE_START -->` and `<!-- AUTO_TREE_END -->` markers.

### 2. Interaction with Python Scripts (`/scripts` & `/tools`)
If you are using Python scripts in this repository (such as timestamp fixers or metadata validators located in `/scripts` or `/tools`), here is how they interact with the tree automation:
- **Reading the Hash**: Python scripts can read `.tree.hash` or the `<!-- Last updated: ... | Hash: ... -->` comment in `README.md` to verify the exact state of the repository at a given millisecond.
- **Timestamp Alignment**: If a Python script (e.g., `fix_timestamps.py`) updates metadata or file headers, it should be run *before* the Go tree generator. The GitHub Actions workflow ensures the Go script runs last, capturing the final state of the repository after any Python modifications.
- **Validation**: Python scripts can be used in CI/CD to read `TREE.md` and verify that no untracked or unauthorized files have been added to the repository structure.

*Note: The automation pipeline is strictly ordered: Python scripts handle data/metadata processing first, and the Go script acts as the final "snapshotter" to lock in the repository structure and provenance.*


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
