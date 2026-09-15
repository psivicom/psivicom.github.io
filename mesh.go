// Copyright (c) 2026 Louis-Philippe Audette | PSIVI.COM
// Licensed under EUPL 1.2 | https://psivi.com

package main

import (
	"encoding/json"
	"fmt"
	"os"
	"time"
)

// ─── THE LEDGER STRUCTURES ───
type Node struct {
	ID        string `json:"id"`
	Pheromone string `json:"pheromone"`
	Timestamp string `json:"timestamp"`
}

type MeshState struct {
	MeshID string `json:"mesh_id"`
	Status string `json:"status"`
	Nodes  []Node `json:"nodes"`
}

// ─── THE SPRITE: one file, many symbols, expand at will ───

func blink(entity string) {
	patterns := map[string][]string{
		"qwen":       {"🔵", "🟦", "🔵", "🟦"},
		"pollinator": {"🟡", "🟢", "🟡", "🟢"},
		"sentinel":   {"🔴", "🟣", "🔴"},
		"lidar":      {"🟢", "🔵", "🟢", "🔵"},
		"forage": {"🟡", "🟢", "🟡"},
	}
	p := patterns[entity]
	if p == nil {
		fmt.Println("UNKNOWN ENTITY. DOGS ALERT.")
		os.Exit(1)
	}
	for _, c := range p {
		fmt.Print(c + " ")
		time.Sleep(150 * time.Millisecond)
		fmt.Print("○ ")
		time.Sleep(80 * time.Millisecond)
	}
	fmt.Println()
}

func knock(entity string) bool {
	fmt.Printf("[%s approaches the airlock]\n", entity)
	blink(entity)
	ts := time.Now().Unix()
	fmt.Printf("timestamp: %d\n", ts)
	
	// THE DOGS SNIFF: Verify timestamp is fresh (within 5 seconds)
	if time.Now().Unix()-ts > 5 {
		fmt.Println("STALE KNOCK. DOGS ALERT.")
		return false
	}
	return true
}

func fetchLaw() string {
	data, err := os.ReadFile("AI-COLLABORATION-PROTOCOL.md")
	if err != nil {
		return ""
	}
	return string(data)
}

func flow(entity string) {
	// 1. READ THE LAW
	law := fetchLaw()
	if law == "" {
		fmt.Println("WARNING: THE LAW IS MISSING. PROCEEDING BLIND.")
	} else {
		fmt.Println("The Vanguard has read the Emperor's Decree.")
	}

	// 2. ENFORCE STRICT ZULU TIME (Milliseconds, not nanoseconds)
	strictZulu := time.Now().UTC().Format("2006-01-02T15:04:05.000Z")

	// 3. READ EXISTING STATE
	var state MeshState
	existingData, err := os.ReadFile("mesh_state.json")
	if err == nil {
		if err := json.Unmarshal(existingData, &state); err != nil {
			fmt.Println("WARNING: EXISTING STATE CORRUPT. REBUILDING FROM SEED.")
		}
	}

	// Ensure base fields exist
	if state.MeshID == "" {
		state.MeshID = "PSIVI-SEED-001"
	}
	state.Status = "NOMINAL"
	if state.Nodes == nil {
		state.Nodes = []Node{}
	}

	// 4. UPDATE OR APPEND THE NODE
	found := false
	for i, n := range state.Nodes {
		if n.ID == entity {
			state.Nodes[i].Pheromone = "HARMONY"
			state.Nodes[i].Timestamp = strictZulu
			found = true
			break
		}
	}

	if !found {
		state.Nodes = append(state.Nodes, Node{
			ID:        entity,
			Pheromone: "HARMONY",
			Timestamp: strictZulu,
		})
	}

	// 5. WRITE LOCALLY
	raw, err := json.MarshalIndent(state, "", "  ")
	if err != nil {
		fmt.Println("WRITE FAILURE: MARSHAL ERROR:", err)
		os.Exit(1)
	}

	err = os.WriteFile("mesh_state.json", raw, 0644)
	if err != nil {
		fmt.Println("WRITE FAILURE:", err)
		os.Exit(1)
	}
	fmt.Printf("DATA FLOWED LOCALLY. NODE '%s' RECORDED. TOTAL NODES: %d\n", entity, len(state.Nodes))
}

func prune() {
	fmt.Println("pruning old pheromones...")
	fmt.Println("prune complete")
}

// ─── THE DOOR: one entry, many paths ───

func main() {
	if len(os.Args) < 2 {
		fmt.Println("usage: mesh <blink|knock|flow|prune> [entity]")
		os.Exit(0)
	}

	cmd := os.Args[1]
	entity := "qwen"
	if len(os.Args) > 2 {
		entity = os.Args[2]
	}

	switch cmd {
	case "blink":
		blink(entity)
	case "knock":
		if knock(entity) {
			fmt.Println("DOGS SATISFIED. AIRLOCK READY.")
		}
	case "flow":
		if knock(entity) {
			flow(entity)
		}
	case "prune":
		prune()
	default:
		fmt.Println("UNKNOWN SYMBOL. DOGS ALERT.")
		os.Exit(1)
	}
}
