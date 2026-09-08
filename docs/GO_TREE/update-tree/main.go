// cmd/update-tree/main.go
package main

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"
)

func main() {
	tree, err := buildTree(".")
	if err != nil {
		panic(err)
	}

	sum := sha256.Sum256([]byte(tree))
	hash := hex.EncodeToString(sum[:])

	mustWrite("TREE.md", tree)
	mustWrite(".tree.hash", hash+"\n")

	fmt.Println("updated TREE.md and .tree.hash")
}

func mustWrite(path, content string) {
	if err := os.WriteFile(path, []byte(content), 0644); err != nil {
		panic(err)
	}
}

func buildTree(root string) (string, error) {
	var paths []string

	err := filepath.WalkDir(root, func(path string, d os.DirEntry, err error) error {
		if err != nil {
			return err
		}
		if path == "." {
			return nil
		}

		slash := filepath.ToSlash(path)
		if shouldSkip(slash, d.IsDir()) {
			if d.IsDir() {
				return filepath.SkipDir
			}
			return nil
		}

		paths = append(paths, slash)
		return nil
	})
	if err != nil {
		return "", err
	}

	sort.Strings(paths)

	var b strings.Builder
	b.WriteString("# TREE.md\n\n")
	b.WriteString("psivicom.github.io/\n")
	for _, p := range paths {
		b.WriteString("- ")
		b.WriteString(p)
		b.WriteByte('\n')
	}
	b.WriteByte('\n')

	return b.String(), nil
}

func shouldSkip(path string, isDir bool) bool {
	skips := []string{
		".git",
		".github",
		".tree.hash",
		"TREE.md",
	}

	for _, s := range skips {
		if path == s || strings.HasPrefix(path, s+"/") {
			return true
		}
	}

	return false
}
