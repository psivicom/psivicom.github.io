package main

import (
	"fmt"
	"log"
	"os/exec"
	"sync"
)

type WENDYMesh struct {
	mu sync.Mutex
	state string
}

func (w *WENDYMesh) ProcessVector(csvData string) error {
	w.mu.Lock()
	defer w.mu.Unlock()
	
	fmt.Println("🕸️ Mesh: Routing sensory input to Vector Engine...")
	cmd := exec.Command("./src/core/vector_engine", csvData)
	output, err := cmd.CombinedOutput()
	if err != nil {
		return err
	}
	fmt.Printf("Vector Output: %s\n", output)
	return nil
}

func (w *WENDYMesh) EvolveState(inputPath, outputPath string) error {
	w.mu.Lock()
	defer w.mu.Unlock()

	fmt.Println("🧠 Mesh: Initiating Cognitive Evolution...")
	cmd := exec.Command("./src/core/wendy_engine", inputPath, outputPath)
	output, err := cmd.CombinedOutput()
	if err != nil {
		return err
	}
	fmt.Printf("Evolution Output: %s\n", output)
	return nil
}

func main() {
	mesh := &WENDYMesh{state: "IDLE"}
	fmt.Println("⚡ WENDY Mesh Orchestrator Online")
	
	// Example: Process a dummy vector and evolve
	_ = mesh.ProcessVector("0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,0.1,0.2,0.3,0.4,0.5,0.6")
	log.Println("Mesh cycle complete.")
}
