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
	
	// Debug: print current directory to ensure we are in the right place
	cwd, err := os.Getwd()
	if err != nil {
		panic(fmt.Errorf("getting working directory: %w", err))
	}
	fmt.Printf("📁 Current working directory: %s\n", cwd)
	
	// Debug: list files in the directory to verify README.md is actually there
	files, _ := os.ReadDir(".")
	fmt.Println("📂 Files in current directory:")
	for _, f := range files {
		fmt.Printf("   - %s\n", f.Name())
	}

	// 1. Build the tree
	fmt.Println("🌳 Building repository tree...")
	tree, err := buildTree(".")
	if err != nil {
		panic(fmt.Errorf("building tree: %w", err))
	}

	// 2. Generate hash and timestamp (exact milliseconds)
	sum := sha256.Sum256([]byte(tree))
	hash := hex.EncodeToString(sum[:])
	timestamp := time.Now().UTC().Format("2006-01-02T15:04:05.000Z")

	// 3. Write TREE.md and .tree.hash
	fmt.Printf("💾 Writing %s and %s...\n", treePath, hashPath)
	mustWrite(treePath, tree)
	mustWrite(hashPath, hash+"\n")

	// 4. Safely update README.md
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

	sort.Slice(entries, func(i, j int) bool {
		ai, aj := entries[i], entries[j]
		if ai.dir != aj.dir {
			return ai.dir && !aj.dir
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
		"node_modules",
	}

	for _, s := range skips {
		if path == s || strings.HasPrefix(path, s+"/") {
			return true
		}
	}
	return false
}
