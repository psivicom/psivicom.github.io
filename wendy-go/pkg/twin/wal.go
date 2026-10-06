// SPDX-License-Identifier: EUPL-1.2
// SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

package twin

import (
	"crypto/sha256"
	"encoding/binary"
	"io"
	"os"
)

// WAL manages atomic, append-only state mutations.
type WAL struct {
	path string
	file *os.File
}

// NewWAL opens or creates the append-only log.
func NewWAL(path string) (*WAL, error) {
	f, err := os.OpenFile(path, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		return nil, err
	}
	return &WAL{path: path, file: f}, nil
}

// Commit writes a mutation with a SHA256 integrity seal.
func (w *WAL) Commit(twin *Twin, mutation []byte) error {
	hash := sha256.Sum256(mutation)
	record := make([]byte, 4+len(mutation)+32)
	
	binary.BigEndian.PutUint32(record[0:4], uint32(len(mutation)))
	copy(record[4:4+len(mutation)], mutation)
	copy(record[4+len(mutation):], hash[:])

	if _, err := w.file.Write(record); err != nil {
		return err
	}

	// Atomic flush to disk (prevents corruption on abrupt runner death)
	if err := w.file.Sync(); err != nil {
		return err
	}

	// Update Twin header with new offset
	offset, _ := w.file.Seek(0, io.SeekCurrent)
	twin.Header.WALOffset = uint64(offset)
	return twin.Seal()
}

func (w *WAL) Close() error {
	return w.file.Close()
}
