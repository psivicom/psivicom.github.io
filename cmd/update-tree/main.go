package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"strings"
)

func runTreeCommand(args ...string) (string, error) {
	cmd := exec.Command("tree", args...)
	out, err := cmd.Output()
	if err != nil {
		return "", err
	}
	return string(out), nil
}

func writeVisualTree() error {
	// -a: all files, -I: ignore patterns, --noreport: skip footer
	output, err := runTreeCommand("-a", "-I", ".git|.github|update-tree|TREE|tree.json|tree.md", "--noreport")
	if err != nil {
		return err
	}

	f, err := os.Create("tree.md")
	if err != nil {
		return err
	}
	defer f.Close()
	
	w := bufio.NewWriter(f)
	fmt.Fprintln(w, "```text")
	w.WriteString(output)
	fmt.Fprintln(w, "```")
	return w.Flush()
}

func writeJSON() error {
	// Keep JSON for programmatic use (fastest to parse)
	output, err := runTreeCommand("-J", "-a", "-I", ".git|.github|update-tree|TREE|tree.json|tree.md", "--noreport")
	if err != nil {
		return err
	}
	return os.WriteFile("tree.json", []byte(output), 0644)
}

func writePlain() error {
	// Keep plain text for simple lists
	output, err := runTreeCommand("-i", "-a", "-I", ".git|.github|update-tree|TREE|tree.json|tree.md", "--noreport")
	if err != nil {
		return err
	}
	return os.WriteFile("TREE", []byte(output), 0644)
}

func main() {
	if err := writeVisualTree(); err != nil {
		fmt.Fprintf(os.Stderr, "visual tree failed: %v\n", err)
		os.Exit(1)
	}
	if err := writeJSON(); err != nil {
		fmt.Fprintf(os.Stderr, "json tree failed: %v\n", err)
		os.Exit(1)
	}
	if err := writePlain(); err != nil {
		fmt.Fprintf(os.Stderr, "plain tree failed: %v\n", err)
		os.Exit(1)
	}
	fmt.Println("Tree generated successfully.")
}
