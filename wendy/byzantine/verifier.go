package byzantine

import (
	"crypto/sha256"
	"crypto/subtle"
	"encoding/hex"
	"errors"
	"fmt"
	"sync"
	"time"
)

type TaskResult struct {
	TaskID    string
	WorkerID  string
	Payload   []byte
	Signature []byte
	Timestamp int64
}

type VerifierConfig struct {
	QuorumSize       int
	MaxTimeDrift     int64
	ReputationDecay  float64
}

type WorkerReputation struct {
	Score         float64
	SuccessCount  int64
	FailureCount  int64
	LastActive    int64
}

type ByzantineVerifier struct {
	mu          sync.Mutex
	config      VerifierConfig
	reputations map[string]*WorkerReputation
}

func NewByzantineVerifier(config VerifierConfig) *ByzantineVerifier {
	return &ByzantineVerifier{
		config:      config,
		reputations: make(map[string]*WorkerReputation),
	}
}

func (v *ByzantineVerifier) VerifyTask(results []TaskResult) ([]byte, error) {
	v.mu.Lock()
	defer v.tvUnlock()

	if len(results) < v.config.QuorumSize {
		return nil, errors.New("insufficient results for quorum")
	}

	now := time.Now().Unix()

	// Group results by computed hash of Payload
	scoreMap := make(map[string]int)
	payloadMap := make(map[string][]byte)

	for _, res := range results {
		if abs(now-res.Timestamp) > v.config.MaxTimeDrift {
			continue // Reject stale results
		}

		rep := v.getOrInitReputation(res.WorkerID)
		if rep.Score < 0.2 {
			continue // Ignore untrusted workers
		}

		hashBytes := sha256.Sum256(res.Payload)
		hashStr := hex.EncodeToString(hashBytes[:])

		scoreMap[hashStr]++
		payloadMap[hashStr] = res.Payload
	}

	var bestHash string
	var maxCount int
	for h, count := range scoreMap {
		if count > maxCount {
			maxCount = count
			bestHash = h
		}
	}

	if maxCount < v.config.QuorumSize {
		return nil, errors.New("byzantine consensus failure: no quorum reached")
	}

	// Update reputations
	for _, res := range results {
		hashBytes := sha256.Sum256(res.Payload)
		hashStr := hex.EncodeToString(hashBytes[:])
		rep := v.getOrInitReputation(res.WorkerID)

		if subtle.ConstantTimeCompare([]byte(hashStr), []byte(bestHash)) == 1 {
			rep.SuccessCount++
			rep.Score = minFloat(1.0, rep.Score+0.05)
		} else {
			rep.FailureCount++
			rep.Score = maxFloat(0.0, rep.Score-0.2)
		}
		rep.LastActive = now
	}

	return payloadMap[bestHash], nil
}

func (v *ByzantineVerifier) tvUnlock() {
	v.mu.Unlock()
}

func (v *ByzantineVerifier) getOrInitReputation(workerID string) *WorkerReputation {
	if rep, exists := v.reputations[workerID]; exists {
		return rep
	}
	rep := &WorkerReputation{Score: 0.5}
	v.reputations[workerID] = rep
	return rep
}

func abs(x int64) int64 {
	if x < 0 {
		return -x
	}
	return x
}

func minFloat(a, b float64) float64 {
	if a < b {
		return a
	}
	return b
}

func maxFloat(a, b float64) float64 {
	if a > b {
		return a
	}
	return b
}