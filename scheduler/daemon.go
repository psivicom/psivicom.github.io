package scheduler

import (
	"context"
	"sync"
	"sync/atomic"
)

type Task struct {
	ID       string
	Payload  []byte
	Priority int32
}

type MeshDaemon struct {
	mu          sync.Mutex
	workQueue   chan Task
	activeNodes int64
}

func NewMeshDaemon(bufferSize int) *MeshDaemon {
	return &MeshDaemon{
		workQueue: make(chan Task, bufferSize),
	}
}

func (d *MeshDaemon) Steal(ctx context.Context) (Task, bool) {
	select {
	case task := <-d.workQueue:
		return task, true
	case <-ctx.Done():
		return Task{}, false
	default:
		return Task{}, false
	}
}

func (d *MeshDaemon) Submit(t Task) {
	d.workQueue <- t
}