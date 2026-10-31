package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"sort"
	"strings"
)

func getTree() ([]string, error) {
	cmd := exec.Command("git", "ls-tree", "-r", "--name-only", "HEAD")
	out, err := cmd.Output()
	if err != nil {
		return nil, err
	}
	var paths []string
	scanner := bufio.NewScanner(strings.NewReader(string(out)))
	for scanner.Scan() {
		p := scanner.Text()
		if !strings.HasPrefix(p, ".git") && p != "TREE" && p != "tree.json" && p != "tree.md" {
			paths = append(paths, p)
		}
	}
	sort.Strings(paths)
	return paths, nil
}

func writePlain(paths []string) error {
	f, err := os.Create("TREE")
	if err != nil {
		return err
	}
	defer f.Close()
	w := bufio.NewWriter(f)
	for _, p := range paths {
		fmt.Fprintln(w, p)
	}
	return w.Flush()
}

func writeJSON(paths []string) error {
	f, err := os.Create("tree.json")
	if err != nil {
		return err
	}
	defer f.Close()
	enc := json.NewEncoder(f)
	enc.SetIndent("", "  ")
	return enc.Encode(paths)
}

func writeMarkdown(paths []string) error {
	f, err := os.Create("tree.md")
	if err != nil {
		return err
	}
	defer f.Close()
	w := bufio.NewWriter(f)
	fmt.Fprintln(w, "```")
	for _, p := range paths {
		fmt.Fprintln(w, p)
	}
	fmt.Fprintln(w, "```")
	return w.Flush()
}

func main() {
	paths, err := getTree()
	if err != nil {
		fmt.Fprintf(os.Stderr, "failed: %v\n", err)
		os.Exit(1)
	}
	if err := writePlain(paths); err != nil {
		fmt.Fprintf(os.Stderr, "TREE: %v\n", err)
		os.Exit(1)
	}
	if err := writeJSON(paths); err != nil {
		fmt.Fprintf(os.Stderr, "tree.json: %v\n", err)
		os.Exit(1)
	}
	if err := writeMarkdown(paths); err != nil {
		fmt.Fprintf(os.Stderr, "tree.md: %v\n", err)
		os.Exit(1)
	}
	fmt.Printf("wrote %d paths to TREE, tree.json, tree.md\n", len(paths))
}
