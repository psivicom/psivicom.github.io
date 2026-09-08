
Here’s a smarter tree renderer, with directories first and nicer output:

```go
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
	b.WriteString("# TREE.md\n\n")
	b.WriteString("psivicom.github.io/\n")
	for _, e := range entries {
		prefix := "- "
		if e.dir {
			prefix = "- "
		}
		b.WriteString(prefix)
		b.WriteString(e.path)
		if e.dir {
			b.WriteByte('/')
		}
		b.WriteByte('\n')
	}
	b.WriteByte('\n')

	return b.String(), nil
}

func shouldSkip(path string) bool {
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
