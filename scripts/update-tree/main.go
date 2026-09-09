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
