package mesh

import (
	"context"
	"fmt"
	"sync"
	"time"
)

type VolunteerResources struct {
	AllocatedRAMBytes uint64
	CPUCores          int
	DiskSpaceBytes    uint64
}

type MeshNode struct {
	NodeID    string
	Resources VolunteerResources
	IsActive  bool
	mu        sync.RWMutex
}

func NewMeshNode(id string, res VolunteerResources) *MeshNode {
	return &MeshNode{
		NodeID:    id,
		Resources: res,
		IsActive:  true,
	}
}

// Heartbeat signals volunteer node availability to the psivi.com bootstrap mesh
func (n *MeshNode) StartHeartbeat(ctx context.Context, interval time.Duration) {
	ticker := time.NewTicker(interval)
	go func() {
		defer ticker.Stop()
		for {
			select {
			case <-ctx.Done():
				n.mu.Lock()
				n.IsActive = false
				n.mu.Unlock()
				return
			case <-ticker.C:
				n.mu.RLock()
				fmt.Printf("[WENDY-MESH] Node %s active | Shared RAM: %d MB\n", 
					n.NodeID, n.Resources.AllocatedRAMBytes/(1024*1024))
				n.mu.RUnlock()
			}
		}
	}()
}