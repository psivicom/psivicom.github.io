package main

import (
	"fmt"
	"os"
	"os/exec"
)

func main() {
	// -a: all files, -I: ignore patterns, --noreport: skip footer
	// -N: Turn off colorization and quoting (ensures clean pipes)
	args := []string{"-a", "-N", "--noreport", "-I", ".git|.github|update-tree|TREE|tree.json|tree.md|tree_clean.txt"}
	
	cmd := exec.Command("tree", args...)
	out, err := cmd.Output()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error running tree: %v\n", err)
		os.Exit(1)
	}

	treeContent := string(out)

	// 1. Write Markdown version
	mdContent := "```text\n" + treeContent + "```\n"
	os.WriteFile("tree.md", []byte(mdContent), 0644)

	// 2. Write Clean Text for HTML (no backticks)
	os.WriteFile("tree_clean.txt", []byte(treeContent), 0644)

	// 3. Write JSON version
	jsonCmd := exec.Command("tree", append(args, "-J")...)
	jsonOut, _ := jsonCmd.Output()
	os.WriteFile("tree.json", jsonOut, 0644)

	// 4. Write Plain version
	plainCmd := exec.Command("tree", append(args, "-i")...)
	plainOut, _ := plainCmd.Output()
	os.WriteFile("TREE", plainOut, 0644)

	fmt.Println("Tree with pipes generated.")
}
