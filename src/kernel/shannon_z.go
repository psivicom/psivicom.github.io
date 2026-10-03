// SPDX-License-Identifier: EUPL-1.2
// SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

package main

/*
#include <stdint.h>
*/
import "C"
import (
	"errors"
	"math"
	"unsafe"
)

// ShannonZKernel provides zero-allocation entropy compression.
type ShannonZKernel struct{}

func NewShannonZKernel() *ShannonZKernel {
	return &ShannonZKernel{}
}

// CompressFloat16 is the C-exported entry point for Python.
// It accepts raw C pointers, converts them to Go slices with ZERO allocation,
// performs the compression, and returns the number of bytes written.
//
//export CompressFloat16
func CompressFloat16(src *C.uint16_t, srcLen C.int, dst *C.uchar, dstCap C.int) C.int {
	// Convert C pointers to Go slices (Zero heap allocation!)
	goSrc := unsafe.Slice((*uint16)(unsafe.Pointer(src)), int(srcLen))
	goDst := unsafe.Slice((*byte)(unsafe.Pointer(dst)), int(dstCap))

	kernel := NewShannonZKernel()
	n, err := kernel.EncodeFloat16Vector(goSrc, goDst)
	if err != nil {
		return -1
	}
	return C.int(n)
}

// EncodeFloat16Vector compresses the vector using Run-Length Encoding for sparse zeros.
func (k *ShannonZKernel) EncodeFloat16Vector(src []uint16, dst []byte) (int, error) {
	if len(src) == 0 {
		return 0, errors.New("shannon_z: empty source vector")
	}

	dstIdx := 0
	srcIdx := 0

	if len(dst) < 4 {
		return 0, errors.New("shannon_z: destination buffer too small")
	}
	
	length := uint32(len(src))
	dst[0] = byte(length >> 24)
	dst[1] = byte(length >> 16)
	dst[2] = byte(length >> 8)
	dst[3] = byte(length)
	dstIdx = 4

	for srcIdx < len(src) {
		val := src[srcIdx]

		if val == 0 {
			zeroCount := 0
			for srcIdx < len(src) && src[srcIdx] == 0 && zeroCount < 255 {
				zeroCount++
				srcIdx++
			}
			if dstIdx+2 > len(dst) {
				return 0, errors.New("shannon_z: destination buffer overflow")
			}
			dst[dstIdx] = 0x00
			dst[dstIdx+1] = byte(zeroCount)
			dstIdx += 2
		} else {
			if dstIdx+2 > len(dst) {
				return 0, errors.New("shannon_z: destination buffer overflow")
			}
			dst[dstIdx] = byte(val >> 8)
			dst[dstIdx+1] = byte(val)
			dstIdx += 2
			srcIdx++
		}
	}

	return dstIdx, nil
}

// CalculateShannonEntropy computes the theoretical entropy of the vector.
//export CalculateShannonEntropy
func CalculateShannonEntropy(vector *C.uint16_t, length C.int) C.double {
	goVec := unsafe.Slice((*uint16)(unsafe.Pointer(vector)), int(length))
	if len(goVec) == 0 {
		return 0
	}

	var hist [256]int
	total := float64(len(goVec))

	for _, v := range goVec {
		bin := (v >> 11) & 0x1F
		hist[bin]++
	}

	entropy := 0.0
	for _, count := range hist {
		if count > 0 {
			p := float64(count) / total
			entropy -= p * math.Log2(p)
		}
	}

	return C.double(entropy)
}

func main() {}
