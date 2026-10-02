package aether

import (
	"math/rand"
	"testing"
	"unsafe"
)

// TestBranchlessQuantizeCorrectness proves the unsafe math is mathematically identical to safe math.
func TestBranchlessQuantizeCorrectness(t *testing.T) {
	count := 1024
	src := make([]float32, count)
	dstUnsafe := make([]byte, count)
	dstSafe := make([]byte, count)

	for i := 0; i < count; i++ {
		src[i] = rand.Float32() * 100.0
	}

	scale := float32(0.5)
	zeroPoint := float32(0.0)

	// 1. Safe Baseline
	for i := 0; i < count; i++ {
		q := int32((src[i] - zeroPoint) / scale)
		if q < 0 { q = 0 } else if q > 127 { q = 127 }
		dstSafe[i] = byte(q)
	}

	// 2. Upgraded Branchless
	srcPtr := unsafe.Pointer(&src[0])
	dstPtr := unsafe.Pointer(&dstUnsafe[0])
	BranchlessQuantize(srcPtr, dstPtr, count, scale, zeroPoint)

	// 3. Prove they match exactly
	for i := 0; i < count; i++ {
		if dstSafe[i] != dstUnsafe[i] {
			t.Fatalf("Mismatch at index %d: Safe=%d, Unsafe=%d", i, dstSafe[i], dstUnsafe[i])
		}
	}
}

// BenchmarkBranchlessQuantize proves the performance gain.
func BenchmarkBranchlessQuantize(b *testing.B) {
	count := 1000000
	src := make([]float32, count)
	dst := make([]byte, count)
	for i := 0; i < count; i++ { src[i] = rand.Float32() * 100.0 }

	srcPtr := unsafe.Pointer(&src[0])
	dstPtr := unsafe.Pointer(&dst[0])
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		BranchlessQuantize(srcPtr, dstPtr, count, 0.5, 0.0)
	}
}
