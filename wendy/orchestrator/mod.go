package orchestrator

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"os/exec"
	"sync"
)

type SelfModificationOrchestrator struct {
	mu       sync.Mutex
	active   bool
	PythonHE string
}

type FitnessResult struct {
	Score   float64 `json:"score"`
	Valid   bool    `json:"valid"`
	Message string  `json:"message"`
}

func NewOrchestrator(pythonHEPath string) *SelfModificationOrchestrator {
	return &SelfModificationOrchestrator{
		PythonHE: pythonHEPath,
	}
}

func (o *SelfModificationOrchestrator) EvaluateCandidate(ctx context.Context, sourceCode string) (*FitnessResult, error) {
	o.mu.Lock()
	defer o.mu.Unlock()

	cmd := exec.CommandContext(ctx, "python3", o.PythonHE, sourceCode)
	out, err := cmd.CombinedOutput()
	if err != nil {
		return nil, fmt.Errorf("python execution failed: %w, output: %s", err, string(out))
	}

	var res FitnessResult
	if err := json.Unmarshal(out, &res); err != nil {
		return nil, fmt.Errorf("failed to parse fitness result: %w, raw: %s", err, string(out))
	}

	return &res, nil
}

func (o *SelfModificationOrchestrator) ApplyPatch(ctx context.Context, sourceCode string) error {
	res, err := o.EvaluateCandidate(ctx, sourceCode)
	if err != nil {
		return err
	}
	if !res.Valid || res.Score < 0.85 {
		return errors.New("candidate failed fitness evaluation threshold")
	}
	o.active = true
	return nil
}
