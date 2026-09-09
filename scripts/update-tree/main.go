// scripts/update-tree/main.go
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
	readmePath   = "README.md"
	treePath     = "TREE.md"
	hashPath     = ".tree.hash"
	markerStart  = "<!-- AUTO_TREE_START -->"
	markerEnd    = "<!-- AUTO_TREE_END -->"
)

func main() {
	// 1. Build the tree
	tree, err := buildTree(".")
	if err != nil {
		panic(fmt.Errorf("building tree: %w", err))
	}

	// 2. Generate hash and timestamp
	sum := sha256.Sum256([]byte(tree))
	hash := hex.EncodeToString(sum[:])
//&	timestamp := time.Now().UTC().Format(time.RFC3339)
    timestamp := time.Now().UTC().Format(time.RFC3339)
	
	// 3. Write TREE.md and .tree.hash
	mustWrite(treePath, tree)
	mustWrite(hashPath, hash+"\n")

	// 4. Safely update README.md
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
	// Read existing README
	content, err := os.ReadFile(readmePath)
	if err != nil {
		return fmt.Errorf("reading README.md: %w", err)
	}

	// Define the new block to inject
	newBlock := fmt.Sprintf("%s\n<!-- Last updated: %s | Hash: %s -->\n\n%s\n%s",
		markerStart, timestamp, hash, strings.TrimSpace(tree), markerEnd)

	// Find the markers
	startIdx := bytes.Index(content, []byte(markerStart))
	endIdx := bytes.Index(content, []byte(markerEnd))

	if startIdx == -1 || endIdx == -1 {
		return fmt.Errorf("could not find %s and %s markers in README.md", markerStart, markerEnd)
	}

	if startIdx >= endIdx {
		return fmt.Errorf("markers are in the wrong order in README.md")
	}

	// Replace only the content between the markers
	var newContent bytes.Buffer
	newContent.Write(content[:startIdx])
	newContent.WriteString(newBlock)
	newContent.Write(content[endIdx+len(markerEnd):])

	// Write back to README.md
	return os.WriteFile(readmePath, newContent.Bytes(), 0644)
}

type entry struct {
	path string
	dir  bool
}

func buildTree(root string) (string, error) {
	var entries []entry

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

		entries = append(entries, entry{path: slash, dir: d.IsDir()})
		return nil
	})
	if err != nil {
		return "", err
	}

	// Sort: directories first, then alphabetically
	sort.Slice(entries, func(i, j int) bool {
		ai, aj := entries[i], entries[j]
		if ai.dir != aj.dir {
			return ai.dir && !aj.dir // true if i is dir and j is not
		}
		return ai.path < aj.path
	})

	var b strings.Builder
	b.WriteString("# Repository Tree\n\n")
	b.WriteString("```\npsivicom.github.io/\n")
	for _, e := range entries {
		prefix := "  - "
		b.WriteString(prefix)
		b.WriteString(e.path)
		if e.dir {
			b.WriteByte('/')
		}
		b.WriteByte('\n')
	}
	b.WriteString("```\n")

	return b.String(), nil
}

func shouldSkip(path string) bool {
	skips := []string{
		".git",
		".github",
		".tree.hash",
		"TREE.md",
		"node_modules", // Added common skip just in case
	}

	for _, s := range skips {
		if path == s || strings.HasPrefix(path, s+"/") {
			return true
		}
	}
	return false
}
