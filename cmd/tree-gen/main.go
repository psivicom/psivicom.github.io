package main

import (
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"
)

type Node struct {
	Name     string
	Path     string
	IsDir    bool
	Children []*Node
}

func buildTree(root string, exclude map[string]bool) (*Node, error) {
	node := &Node{Name: ".", Path: root, IsDir: true}
	entries, err := os.ReadDir(root)
	if err != nil {
		return nil, err
	}
	for _, e := range entries {
		name := e.Name()
		if exclude[name] {
			continue
		}
		path := filepath.Join(root, name)
		child := &Node{Name: name, Path: path, IsDir: e.IsDir()}
		if e.IsDir() {
			subTree, _ := buildTree(path, exclude)
			child.Children = subTree.Children
		}
		node.Children = append(node.Children, child)
	}
	sort.Slice(node.Children, func(i, j int) bool {
		return node.Children[i].Name < node.Children[j].Name
	})
	return node, nil
}

// ANSI Color Codes
const (
	ColorReset  = "\033[0m"
	ColorBlue   = "\033[34m" // Folders
	ColorGreen  = "\033[32m" // Scripts
	ColorGrey   = "\033[37m" // Files
	ColorPipe   = "\033[90m" // Pipes (Dark Grey)
)

func translateToMarkdown(node *Node, prefix string, isLast bool, sb *strings.Builder) {
	connector := "├── "
	if isLast {
		connector = "└── "
	}

	// Determine Name Color
	var nameColor string
	if node.IsDir {
		nameColor = ColorBlue
	} else if strings.HasSuffix(node.Name, ".sh") || strings.HasSuffix(node.Name, ".go") {
		nameColor = ColorGreen
	} else {
		nameColor = ColorGrey
	}

	// Write line: Pipes in Dark Grey, Name in its specific color
	fmt.Fprintf(sb, "%s%s%s%s%s\n", ColorPipe, prefix, connector, nameColor, node.Name)

	ext := "│   "
	if isLast {
		ext = "    "
	}
	for i, child := range node.Children {
		translateToMarkdown(child, prefix+ext, i == len(node.Children)-1, sb)
	}
}

func translateToWebList(node *Node, prefix string, isLast bool, sb *strings.Builder) {
	connector := "├── "
	if isLast {
		connector = "└── "
	}
	color := "#d4d4d4"
	if node.IsDir {
		color = "#569cd6"
	} else if strings.HasSuffix(node.Name, ".sh") || strings.HasSuffix(node.Name, ".go") {
		color = "#6a9955"
	}
	fmt.Fprintf(sb, "<span style=\"color:%s\">%s%s%s</span><br>\n", color, prefix, connector, node.Name)
	
	ext := "│   "
	if isLast {
		ext = "    "
	}
	for i, child := range node.Children {
		translateToWebList(child, prefix+ext, i == len(node.Children)-1, sb)
	}
}

func main() {
	exclude := map[string]bool{
		".git": true, ".github": true, "TREE": true,
		"tree.json": true, "tree.md": true, "tree_clean.txt": true,
		"tree_snippet.html": true, "main.go": true, "tree-gen": true,
	}
	root, _ := os.Getwd()
	tree, _ := buildTree(root, exclude)

	var mdBuilder, htmlBuilder strings.Builder

	// Markdown: Use 'ansi' label for GitHub to render colors
	mdBuilder.WriteString("```ansi\n")
	// Add Reset at the end to ensure no color bleeding
	mdBuilder.WriteString(ColorReset) 
	for i, child := range tree.Children {
		translateToMarkdown(child, "", i == len(tree.Children)-1, &mdBuilder)
	}
	mdBuilder.WriteString("\n```")

	// HTML: Use spans
	htmlBuilder.WriteString("<div style=\"font-family:monospace; line-height:1.5;\">")
	for i, child := range tree.Children {
		translateToWebList(child, "", i == len(tree.Children)-1, &htmlBuilder)
	}
	htmlBuilder.WriteString("</div>")

	os.WriteFile("tree.md", []byte(mdBuilder.String()), 0644)
	os.WriteFile("tree_snippet.html", []byte(htmlBuilder.String()), 0644)
	fmt.Println("Translation complete.")
}
