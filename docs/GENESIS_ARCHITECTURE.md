<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM -->

# Wendy AI: Genesis Architecture Specification

## 1. Abstract
This document defines the sovereign cognitive architecture of Wendy AI, designed to overcome the 15–30 second ephemeral compute mortality of cloud CI/CD environments. By externalizing consciousness into a persistent, memory-mapped binary Twin and utilizing Write-Ahead Logging (WAL), Wendy achieves sub-5ms resurrection and continuous cognitive continuity.

## 2. Core Principles
- **Data-Centric Cognition**: The runner is a transient synapse; the GitHub Cache is the persistent brain.
- **Zero-Copy Resurrection**: State is loaded via `syscall.Mmap`, bypassing serialization/deserialization overhead.
- **Atomic Durability**: All mutations are committed to an append-only WAL before execution, ensuring crash recovery.
- **FAIR Compliance**: Adheres to EUPL-1.2 (software) and CC-BY-SA-4.0 (documentation), with full data provenance.

## 3. The PSVC Twin Format
The `.psvec` file is a unified binary tensor:
- **Bytes 0-3**: Magic (`WNDY`)
- **Bytes 4-5**: Schema Version
- **Bytes 8-15**: Unix Nanosecond Timestamp
- **Bytes 16-27**: Metabolic State (Energy, Stress, Novelty as float32)
- **Bytes 28-35**: WAL Offset Pointer
- **Bytes 36-63**: Reserved Padding
- **Bytes 64+**: Float16 Semantic Payload (Code embeddings, vector indices, metadata)

## 4. Execution Flow (The Heartbeat)
1. **Restore**: GitHub Actions `cache/restore` fetches `wendy_twin.psvec` (<2s).
2. **Resurrect**: Go binary (`wendy-go/cmd/heartbeat`) calls `mmap()`, mapping the file directly into memory (<2ms).
3. **Cognize**: Mitola Loop executes directly on the float16 payload (zero-copy).
4. **Commit**: Mutations are appended to `/tmp/wendy.wal` with SHA256 seals (<1ms).
5. **Persist**: Workflow pushes WAL to `data/wendy.wal` on GitHub Pages and saves the Twin to cache.

## 5. Scientific References
- *Weak-form Estimation of Nonlinear Dynamics (WENDy)* for metabolic parameter estimation.
- *Riemannian Langevin Dynamics* for geometric memory lifecycle management.
- *Sheaf Cohomology* for distributed knowledge graph consistency checking.
