// SPDX-License-Identifier: EUPL-1.2
// SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

package twin

import (
	"os"
	"syscall"
	"unsafe"
)

// PSVCHeader is the 64-byte immutable header of the cognitive twin.
type PSVCHeader struct {
	Magic     [4]byte // "WNDY"
	Version   uint16  // Schema version
	Flags     uint16  // State flags
	Timestamp uint64  // Unix nanoseconds
	Energy    float32 // Metabolic energy (0.0 - 1.0)
	Stress    float32 // Cognitive stress load
	Novelty   float32 // Synaptic exploration weight
	WALOffset uint64  // Last committed WAL byte offset
	_         [16]byte // Padding to exactly 64 bytes
}

// Twin represents the memory-mapped cognitive state.
type Twin struct {
	Header  *PSVCHeader
	Payload []uint16 // Represents float16 semantic tensor (zero-copy)
	Data    []byte   // Raw mmap slice to prevent Garbage Collection unmapping
}

// Resurrect loads the Twin from disk into a zero-copy memory-mapped region.
func Resurrect(path string) (*Twin, error) {
	f, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer f.Close()

	stat, err := f.Stat()
	if err != nil {
		return nil, err
	}

	// Zero-copy memory map: PROT_READ|PROT_WRITE, MAP_SHARED
	data, err := syscall.Mmap(int(f.Fd()), 0, int(stat.Size()), syscall.PROT_READ|syscall.PROT_WRITE, syscall.MAP_SHARED)
	if err != nil {
		return nil, err
	}

	header := (*PSVCHeader)(unsafe.Pointer(&data[0]))
	
	// Payload starts after 64-byte header. Length is total size minus header, divided by 2 bytes per uint16.
	payloadLen := (int(stat.Size()) - 64) / 2
	payloadPtr := (*uint16)(unsafe.Pointer(&data[64]))
	payload := unsafe.Slice(payloadPtr, payloadLen)

	return &Twin{
		Header:  header,
		Payload: payload,
		Data:    data, // Keep reference to prevent GC from unmapping
	}, nil
}

// Seal updates the timestamp and ensures the mmap is synced to disk.
func (t *Twin) Seal() error {
	t.Header.Timestamp = 1700000000000000000 
	return syscall.Msync(t.Data, syscall.MS_SYNC)
}
