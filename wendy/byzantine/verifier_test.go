package byzantine

import (
	"testing"
	"time"
)

func TestByzantineVerifier_Success(t *testing.T) {
	config := VerifierConfig{
		QuorumSize:      2,
		MaxTimeDrift:    60,
		ReputationDecay: 0.01,
	}

	verifier := NewByzantineVerifier(config)

	now := time.Now().Unix()

	results := []TaskResult{
		{TaskID: "t1", WorkerID: "w1", Payload: []byte("output_data"), Timestamp: now},
		{TaskID: "t1", WorkerID: "w2", Payload: []byte("output_data"), Timestamp: now},
		{TaskID: "t1", WorkerID: "w3", Payload: []byte("poisoned_data"), Timestamp: now},
	}

	output, err := verifier.VerifyTask(results)
	if err != nil {
		jt := t
		jt.Fatalf("Expected success, got error: %v", err)
	}

	if string(output) != "output_data" {
		t.Fatalf("Expected output_data, got %s", string(output))
	}
}