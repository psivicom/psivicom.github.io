func main() {
    // ... (your existing tree generation logic) ...
    treeContent := renderTree(rootDir)
    timestamp := time.Now().UTC().Format("2006-01-02T15:04:05.000Z")
    hash := sha256.Sum256([]byte(treeContent))
    hashStr := hex.EncodeToString(hash[:])

    // 1. Update README.md
    if err := updateFileWithMarkers("README.md", treeContent, timestamp, hashStr); err != nil {
        log.Printf("Warning: Failed to update README.md: %v", err)
    }
    
    // 2. Update index.html
    if err := updateFileWithMarkers("index.html", treeContent, timestamp, hashStr); err != nil {
        log.Printf("Warning: Failed to update index.html (it may lack markers): %v", err)
    }

    // 3. Write TREE.md
    if err := os.WriteFile("TREE.md", []byte(treeContent), 0644); err != nil {
        log.Fatalf("Failed to write TREE.md: %v", err)
    }
    
    // 4. Write .tree.hash
    if err := os.WriteFile(".tree.hash", []byte(hashStr), 0644); err != nil {
        log.Fatalf("Failed to write .tree.hash: %v", err)
    }
    
    fmt.Println("✅ Successfully updated TREE.md, README.md, and index.html")
}
