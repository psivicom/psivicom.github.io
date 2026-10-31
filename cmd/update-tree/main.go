package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
)

func runTree(args ...string) (string, error) {
	cmd := exec.Command("tree", args...)
	out, err := cmd.Output()
	if err != nil {
		return "", err
	}
	return string(out), nil
}

func main() {
	// 1. Visual Tree (Markdown)
	// -a: all files, -I: ignore, --noreport: no footer, -p: permissions (optional)
	visual, _ := runTree("-a", "-I", ".git|.github|update-tree|TREE|tree.json|tree.md|tree_clean.txt", "--noreport")
	
	f1, _ := os.Create("tree.md")
	defer f1.Close()
	fmt.Fprintln(f1, "```text")
	f1.WriteString(visual)
	fmt.Fprintln(f1, "```")

	// 2. JSON Tree (for programmatic use)
	jsonOut, _ := runTree("-J", "-a", "-I", ".git|.github|update-tree|TREE|tree.json|tree.md|tree_clean.txt", "--noreport")
	os.WriteFile("tree.json", []byte(jsonOut), 0644)

	// 3. Plain Tree (for simple lists)
	plain, _ := runTree("-i", "-a", "-I", ".git|.github|update-tree|TREE|tree.json|tree.md|tree_clean.txt", "--noreport")
	os.WriteFile("TREE", []byte(plain), 0644)
	
	// 4. Clean Text for HTML (no backticks)
	os.WriteFile("tree_clean.txt", []byte(visual), 0644)

	fmt.Println("Tree generated with pipes.")
}
