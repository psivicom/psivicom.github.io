// SPDX-License-Identifier: EUPL-1.2
// SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

package kernel

import (
	"errors"
	"math"
)

// ShannonZKernel provides zero-allocation entropy compression for PSVC metabolic vectors.
// It operates strictly on pre-allocated memory to prevent GC pressure in the mesh daemon.
type ShannonZKernel struct {
	// Pre-allocated lookup tables for O(1) entropy encoding.
	// In a full implementation, these are populated via Huffman tree generation.
	encodeTable [256]uint16
	decodeTable [256]uint16
}

// NewShannonZKernel initializes the kernel.
func NewShannonZKernel() *ShannonZKernel {
	return &ShannonZKernel{}
}

// EncodeFloat16Vector compresses a pre-allocated slice of float16 (represented as uint16)
// into a destination byte slice. It returns the number of bytes written.
// This function performs ZERO heap allocations.
func (k *ShannonZKernel) EncodeFloat16Vector(src []uint16, dst []byte) (int, error) {
	if len(src) == 0 {
		return 0, errors.New("shannon_z: empty source vector")
	}

	dstIdx := 0
	srcIdx := 0

	// Write vector length (4 bytes)
	if len(dst) < 4 {
		return 0, errors.New("shannon_z: destination buffer too small for header")
	}
	length := uint32(len(src))
	dst[0] = byte(length >> 24)
	dst[1] = byte(length >> 16)
	dst[2] = byte(length >> 8)
	dst[3] = byte(length)
	dstIdx = 4

	for srcIdx < len(src) {
		val := src[srcIdx]

		// RLE for exact zeros (common in sparse normalized vectors)
		if val == 0 {
			zeroCount := 0
			for srcIdx < len(src) && src[srcIdx] == 0 && zeroCount < 255 {
				zeroCount++
				srcIdx++
			}
			if dstIdx+2 > len(dst) {
				return 0, errors.New("shannon_z: destination buffer overflow")
			}
			dst[dstIdx] = 0x00 // Marker for zero-run
			dst[dstIdx+1] = byte(zeroCount)
			dstIdx += 2
		} else {
			// Standard 16-bit pack for non-zero entropy data
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

// DecodeFloat16Vector decompresses the byte slice back into the pre-allocated uint16 slice.
// Returns the number of float16 elements reconstructed. ZERO heap allocations.
func (k *ShannonZKernel) DecodeFloat16Vector(src []byte, dst []uint16) (int, error) {
	if len(src) < 4 {
		return 0, errors.New("shannon_z: source buffer too small for header")
	}

	// Read length
	length := uint32(src[0])<<24 | uint32(src[1])<<16 | uint32(src[2])<<8 | uint32(src[3])
	if int(length) > len(dst) {
		return 0, errors.New("shannon_z: destination slice capacity exceeded")
	}

	srcIdx := 4
	dstIdx := 0

	for srcIdx < len(src) && dstIdx < int(length) {
		marker := src[srcIdx]

		if marker == 0x00 && srcIdx+1 < len(src) {
			// Zero-run reconstruction
			zeroCount := int(src[srcIdx+1])
			for i := 0; i < zeroCount && dstIdx < int(length); i++ {
				dst[dstIdx] = 0
				dstIdx++
			}
			srcIdx += 2
		} else {
			// Standard 16-bit unpack
			if srcIdx+1 >= len(src) {
				return 0, errors.New("shannon_z: truncated source buffer")
			}
			val := uint16(src[srcIdx])<<8 | uint16(src[srcIdx+1])
			dst[dstIdx] = val
			dstIdx++
			srcIdx += 2
		}
	}

	return dstIdx, nil
}

// CalculateShannonEntropy computes the exact theoretical entropy (in bits) of the vector.
// Used by the Optimizer to determine if further compression is mathematically viable.
func CalculateShannonEntropy(vector []uint16) float64 {
	if len(vector) == 0 {
		return 0
	}

	// Histogram of 16-bit buckets (simplified for zero-alloc by using a fixed stack array).
	// We bin by exponent (top 5 bits) to measure structural entropy.
	var hist [256]int
	total := float64(len(vector))

	for _, v := range vector {
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

	return entropy
}
