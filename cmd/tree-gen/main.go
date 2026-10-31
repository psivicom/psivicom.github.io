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

func translateToHTMLTable(node *Node, prefix string, isLast bool, sb *strings.Builder) {
	connector := "├── "
	if isLast {
		connector = "└── "
	}

	color := "#d4d4d4" // Default file color
	if node.IsDir {
		color = "#569cd6" // Blue for folders
	} else if strings.HasSuffix(node.Name, ".sh") || strings.HasSuffix(node.Name, ".go") {
		color = "#6a9955" // Green for code
	}

	// Translate to an HTML Table Row with inline colors
	fmt.Fprintf(sb, "<tr><td style=\"font-family:monospace; white-space:pre; color:#888;\">%s%s</td><td style=\"font-family:monospace; color:%s;\">%s</td></tr>\n",
		prefix, connector, color, node.Name)

	ext := "│   "
	if isLast {
		ext = "    "
	}
	for i, child := range node.Children {
		translateToHTMLTable(child, prefix+ext, i == len(node.Children)-1, sb)
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

	// Start Markdown Table
	mdBuilder.WriteString("<table style=\"border:none; background:#1e1e1e; border-radius:8px; padding:10px;\">\n")
	for i, child := range tree.Children {
		translateToHTMLTable(child, "", i == len(tree.Children)-1, &mdBuilder)
	}
	mdBuilder.WriteString("</table>")

	// Start Web List
	htmlBuilder.WriteString("<div style=\"font-family:monospace; line-height:1.5;\">")
	for i, child := range tree.Children {
		translateToWebList(child, "", i == len(tree.Children)-1, &htmlBuilder)
	}
	htmlBuilder.WriteString("</div>")

	os.WriteFile("tree.md", []byte(mdBuilder.String()), 0644)
	os.WriteFile("tree_snippet.html", []byte(htmlBuilder.String()), 0644)
	fmt.Println("Translation complete.")
}
