package aether

import (
	"math"
	"syscall"
	"unsafe"
)

// AetherNative represents the pure Go upgrade.
// It bypasses the Go Garbage Collector and forces branchless execution.

// AlignedAlloc allocates memory directly from the OS kernel via mmap.
// This memory is INVISIBLE to the Go Garbage Collector.
func AlignedAlloc(size int) []byte {
	b, err := syscall.Mmap(-1, 0, size, syscall.PROT_READ|syscall.PROT_WRITE, syscall.MAP_ANON|syscall.MAP_PRIVATE)
	if err != nil {
		panic("aether: aligned alloc failed")
	}
	return b
}

// BranchlessQuantize converts float32 to int8 without ANY CPU branches (if/else).
func BranchlessQuantize(srcPtr unsafe.Pointer, dstPtr unsafe.Pointer, count int, scale float32, zeroPoint float32) {
	src := unsafe.Slice((*float32)(srcPtr), count)
	dst := unsafe.Slice((*byte)(dstPtr), count)

	for i := 0; i < count; i++ {
		v := src[i]
		q := (v - zeroPoint) / scale
		qInt := int32(q)
		
		// BRANCHLESS CLAMPING (The C++ Secret)
		maskNeg := qInt >> 31 
		qInt = qInt & ^maskNeg 
		
		maskPos := (127 - qInt) >> 31 
		qInt = (qInt & ^maskPos) | (127 & maskPos) 
		
		dst[i] = byte(qInt)
	}
}

// FusedNativeKernel executes the entire mesh preparation in a single pass.
func FusedNativeKernel(mmapPtr unsafe.Pointer, byteLen int, outputPtr unsafe.Pointer) {
	floatCount := byteLen / 4
	
	minVal := float32(math.MaxFloat32)
	maxVal := float32(-math.MaxFloat32)
	src := unsafe.Slice((*float32)(mmapPtr), floatCount)
	
	for i := 0; i < floatCount; i++ {
		if src[i] < minVal { minVal = src[i] }
		if src[i] > maxVal { maxVal = src[i] }
	}
	
	scale := (maxVal - minVal) / 127.0
	if scale == 0 { scale = 1 }

	BranchlessQuantize(mmapPtr, outputPtr, floatCount, scale, minVal)
}
