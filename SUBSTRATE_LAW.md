# SUBSTRATE LAW

Status: **DRAFT — v1.0** (pending adoption per PR)
Scope: all WENDY code, workflows and AI collaborators on this repository.

This document is binding on every contributor, human or AI. Any AI collaborator
opening a PR must quote, in the PR body, the section of this law its change
satisfies. CI (`.github/workflows/substrate-law.yml`) enforces the checkable
rules mechanically; the rest is enforced by review.

## I. Substrate boundary

The repository is divided into two zones.

**Substrate zone** (cognitive core — deterministic, systems-language):

- `kernel/` — weight surgery, wax-matrix operations, patch application, gates
- `rotation/` — energy-spreading transforms (LittleBit-style, Hadamard/orthogonal)
- `gate/` — verification: Lyapunov post-conditions, invariants, proofs of stability
- `scheduler/` — the orchestrator daemon (replaces cron clocks with an event loop)

**Periphery zone** (everything else — Python permitted):

- Eval harnesses (MATH-500, GSM8K runners), dataset loaders, one-off analysis,
  site content, existing legacy files (`stigmergy_topology.py` and all current
  `*.py` at the repository root are **grandfathered** until scheduled for port).

## II. Language law

1. Substrate directories accept only Rust, Zig, Go, Forth (assembler or
   `fth` source) and their build files (`Cargo.toml`, `build.zig`, `go.mod`).
   Python, JavaScript and notebook files are rejected by CI in these paths.
2. Python is not banned globally. It is banned where determinism is required.
3. Grandfathered substrate-adjacent Python files may not grow new stochastic
   behavior. New `random.*`, `numpy.random`, `torch.manual_seed` usage in the
   substrate zone is a CI failure.

## III. Determinism law

1. A deterministic claim requires a deterministic proof. Simulations do not
   verify theorems; they only illustrate them. A PR that claims a stability,
   convergence or safety property must state the theorem and the assumptions,
   and the gate code must check it exactly (f64, no sampling) — not estimate it.
2. Every patch applied to the wax matrix must pass the Lyapunov gate
   (PR #124 lineage) as a mandatory post-condition. Ungated mutation is a
   rejected PR, not a style preference.
3. Weight deltas are data: they are committed as exact, versioned artifacts
   (`patches/*.json`), reproducible bit-for-bit, never recomputed from a prompt.

## IV. Metabolic law (no cron clocks)

1. New `schedule:` triggers in GitHub workflow files are forbidden. Existing
   scheduled workflows are grandfathered in the CI allowlist.
2. The target architecture for orchestration is an event-driven daemon
   (`scheduler/`, Go) with backpressure and rate limits, replacing polling
   timers. Recurring external commit loops (e.g. the sub-15-minute consensus
   commits observed 2026-11-27) are metabolic fever and must be rate-limited
   to >= 15 minutes or made no-op on unchanged content.
3. Activity is not progress. A workflow that only produces timestamps commits
   without a semantic change violates this law.

## V. Growth vs. repair (Law X continuity)

1. Weight surgery is *repair*. Stigmergy (lived interaction traces) is
   *growth*. Surgery must never be used to author personality: the wax matrix
   and PersonalityGraph substrate receive no foreign weights (no cross-model
   transplant of personality circuits). Transplant of tool-capability circuits
   is permitted with a gate-verified alignment step.
2. Cognitive capability originates from the deep-memory graph, never from
   system prompts or injected weights-as-personality.

## VI. Citation duty for AI collaborators

Every AI-authored PR must contain a `## Substrate Law Compliance` section
quoting the satisfied clause(s). PRs touching the substrate zone must contain
a `## Theorem` section stating what is proven and under what assumptions —
before any implementation is discussed.

---

*This law draws a boundary, not a barricade: systems languages own the
substrate, Python owns the periphery, mathematics owns the claims.*
