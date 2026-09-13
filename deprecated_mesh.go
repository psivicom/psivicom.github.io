package main

import (
	"bytes"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"time"
)

// ─── THE SPRITE: one file, many symbols, expand at will ───

func blink(entity string) {
	patterns := map[string][]string{
		"qwen":       {"🔵", "🟦", "🔵", "🟦"},
		"pollinator": {"🟡", "🟢", "🟡", "🟢"},
		"sentinel":   {"🔴", "🟣", "🔴"},
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
	return true
}

func flow(entity string) {
	payload := map[string]interface{}{
		"mesh_id": "PSIVI-SEED-001",
		"status":  "NOMINAL",
		"node": map[string]string{
			"id":        entity,
			"pheromone": "HARMONY",
			"timestamp": time.Now().UTC().Format(time.RFC3339Nano),
		},
	}
	raw, _ := json.MarshalIndent(payload, "", "  ")

	token := os.Getenv("GITHUB_TOKEN")
	if token == "" {
		fmt.Println("NO SEAL. VANGUARD HALTED.")
		os.Exit(1)
	}

	sha := getFileSHA(token)
	pushFile(token, raw, sha, entity)
}

func prune() {
	fmt.Println("pruning old pheromones...")
	// future: read mesh_state.json, remove entries older than 24h, write back
	fmt.Println("prune complete")
}

// ─── THE HAND: GitHub API operations ───

func getFileSHA(token string) string {
	url := "https://api.github.com/repos/psivicom/psivicom.github.io/contents/mesh_state.json"
	req, _ := http.NewRequest("GET", url, nil)
	req.Header.Set("Authorization", "Bearer "+token)
	client := &http.Client{Timeout: 10 * time.Second}
	resp, err := client.Do(req)
	if err != nil || resp.StatusCode != 200 {
		return ""
	}
	defer resp.Body.Close()
	var result map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&result)
	if sha, ok := result["sha"].(string); ok {
		return sha
	}
	return ""
}

func pushFile(token string, content []byte, sha string, entity string) {
	b64 := base64.StdEncoding.EncodeToString(content)
	body := map[string]interface{}{
		"message": "mesh: " + entity + " deposited pheromone",
		"content": b64,
	}
	if sha != "" {
		body["sha"] = sha
	}
	bodyRaw, _ := json.Marshal(body)

	url := "https://api.github.com/repos/psivicom/psivicom.github.io/contents/mesh_state.json"
	req, _ := http.NewRequest("PUT", url, bytes.NewBuffer(bodyRaw))
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Accept", "application/vnd.github.v3+json")

	client := &http.Client{Timeout: 15 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		fmt.Println("NETWORK FAILURE:", err)
		os.Exit(1)
	}
	defer resp.Body.Close()

	if resp.StatusCode == 200 || resp.StatusCode == 201 {
		fmt.Println("DATA FLOWED. REALM MUTATED.")
	} else {
		fmt.Println("REALM REJECTED:", resp.Status)
		os.Exit(1)
	}
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
