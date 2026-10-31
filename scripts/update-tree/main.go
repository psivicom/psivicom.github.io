package main

import (
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"sort"
	"strings"
	"time"
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

// 1. Generates CLEAN Markdown (No ANSI color codes, just bold for folders)
func translateToMarkdown(node *Node, prefix string, isLast bool, sb *strings.Builder) {
	connector := "├── "
	if isLast {
		connector = "└── "
	}

	if node.IsDir {
		fmt.Fprintf(sb, "%s%s**%s**\n", prefix, connector, node.Name)
	} else {
		fmt.Fprintf(sb, "%s%s%s\n", prefix, connector, node.Name)
	}

	ext := "│   "
	if isLast {
		ext = "    "
	}
	for i, child := range node.Children {
		translateToMarkdown(child, prefix+ext, i == len(node.Children)-1, sb)
	}
}

// 2. Generates Colored HTML (Klein Blue Background)
func translateToWebList(node *Node, prefix string, isLast bool, sb *strings.Builder) {
	connector := "├── "
	if isLast {
		connector = "└── "
	}
	
	color := "#ffffff" // White text for contrast against Klein Blue
	if node.IsDir {
		color = "#80BFFF" // Lighter blue for folders on dark background
	} else if strings.HasSuffix(node.Name, ".sh") || strings.HasSuffix(node.Name, ".go") || strings.HasSuffix(node.Name, ".py") {
		color = "#80FF80" // Light green for scripts on dark background
	}
	
	// Escape HTML to prevent breaking the page
	escapedName := strings.ReplaceAll(node.Name, "&", "&amp;")
	escapedName = strings.ReplaceAll(escapedName, "<", "&lt;")
	escapedName = strings.ReplaceAll(escapedName, ">", "&gt;")
	
	fmt.Fprintf(sb, "<span style=\"color:%s\">%s%s%s</span><br>\n", color, prefix, connector, escapedName)
	
	ext := "│   "
	if isLast {
		ext = "    "
	}
	for i, child := range node.Children {
		translateToWebList(child, prefix+ext, i == len(node.Children)-1, sb)
	}
}

// 3. Injects the generated content into the target file
func injectIntoFile(filePath, newContent string) error {
	content, err := os.ReadFile(filePath)
	if err != nil {
		return fmt.Errorf("failed to read %s: %w", filePath, err)
	}

	// Find the AUTO_TREE markers
	re := regexp.MustCompile(`(?s)<!-- AUTO_TREE_START -->.*?<!-- AUTO_TREE_END -->`)
	if !re.Match(content) {
		return fmt.Errorf("markers not found in %s", filePath)
	}

	timestamp := time.Now().UTC().Format("2006-01-02T15:04:05.000Z")
	replacement := fmt.Sprintf("<!-- AUTO_TREE_START -->\n<!-- Auto-updated by .github/workflows/update-tree.yml -->\n<!-- Last updated: %s -->\n%s\n<!-- AUTO_TREE_END -->", timestamp, newContent)

	updatedContent := re.ReplaceAll(content, []byte(replacement))
	return os.WriteFile(filePath, updatedContent, 0644)
}

func main() {
	exclude := map[string]bool{
		".git": true, ".github": true, "TREE": true,
		"tree.json": true, "tree.md": true, "tree_clean.txt": true,
		"tree_snippet.html": true, "tree-gen": true,
	}
	
	root, _ := os.Getwd()
	tree, err := buildTree(root, exclude)
	if err != nil {
		fmt.Printf("❌ Error building tree: %v\n", err)
		os.Exit(1)
	}

	var mdBuilder, htmlBuilder strings.Builder

	// Build Markdown
	mdBuilder.WriteString("```\n")
	for i, child := range tree.Children {
		translateToMarkdown(child, "", i == len(tree.Children)-1, &mdBuilder)
	}
	mdBuilder.WriteString("```")

	// Build HTML (KLEIN BLUE BACKGROUND)
	htmlBuilder.WriteString("<div style=\"font-family:monospace; line-height:1.5; background:#002FA7; color:#ffffff; padding:24px; border-radius:12px;\">\n")
	for i, child := range tree.Children {
		translateToWebList(child, "", i == len(tree.Children)-1, &htmlBuilder)
	}
	htmlBuilder.WriteString("</div>")

	// Inject into ROOT README.md
	if err := injectIntoFile("README.md", mdBuilder.String()); err != nil {
		fmt.Printf("⚠️ Warning: %v\n", err)
	} else {
		fmt.Println("✅ Successfully updated README.md (Clean Markdown)")
	}

	// Inject into ROOT index.html
	if err := injectIntoFile("index.html", htmlBuilder.String()); err != nil {
		fmt.Printf("⚠️ Warning: %v\n", err)
	} else {
		fmt.Println("✅ Successfully updated index.html (Klein Blue HTML)")
	}

	fmt.Println("🎉 Tree generation and injection complete.")
}
