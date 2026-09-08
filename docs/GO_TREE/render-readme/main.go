// cmd/render-readme/main.go
package main

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"os"
	"strings"
)

const (
	startMarker = "<!-- TREE:START -->"
	endMarker   = "<!-- TREE:END -->"
)

func main() {
	readme, err := os.ReadFile("README.md")
	if err != nil {
		panic(err)
	}
	tree, err := os.ReadFile("TREE.md")
	if err != nil {
		panic(err)
	}
	hashBytes, err := os.ReadFile(".tree.hash")
	if err != nil {
		panic(err)
	}

	treeHash := strings.TrimSpace(string(hashBytes))
	sum := sha256.Sum256(tree)
	actual := hex.EncodeToString(sum[:])
	if treeHash != actual {
		panic("TREE.md hash mismatch")
	}

	content := string(readme)
	start := strings.Index(content, startMarker)
	end := strings.Index(content, endMarker)
	if start == -1 || end == -1 || end < start {
		panic("TREE markers missing or invalid")
	}

	replacement := startMarker + "\n\n```text\n" + string(tree) + "```\n\n" + endMarker
	newContent := content[:start] + replacement + content[end+len(endMarker):]

	if newContent == content {
		fmt.Println("README.md already up to date")
		return
	}

	if err := os.WriteFile("README.md", []byte(newContent), 0644); err != nil {
		panic(err)
	}

	fmt.Println("updated README.md")
}
