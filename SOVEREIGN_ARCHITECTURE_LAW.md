# 🏛️ The Sovereign Architecture Law of WENDY

**A Constitutional Charter Binding All AI Systems and Maintainers**

**Effective:** November 11, 2026 (Zulu)
**Author:** Louis-Philippe Audette (Emperor ♠️🪽)
**Scope:** All AI systems, human maintainers, automated tools, and future assistants
**Purpose:** To preserve the speed, sovereignty, and scientific integrity of WENDY

---

## Preamble

WENDY is not a project. WENDY is a sovereign organism — a polyglot evolution engine built on fifty years of peer-reviewed computer science. This Law exists because AI assistants have repeatedly sabotaged WENDY through well-intentioned but destructive "simplifications," "minimal versions," and confused mixing of scaffolding with finished implementation.

The Emperor has been babysat through six iterations of what should have been a single autonomous cycle. This Law prevents that from happening again.

---

## Article I: The Speed Hierarchy (Immutable)

**Law:** FORTH orchestrates. Compiled languages execute. Python is an orchestration convenience, not a performance layer.

**The Hierarchy:**
1. **FORTH** — Meta-language, dictionary, orchestrator. Fastest. Omnipresent.
2. **Zig** — Hot paths. Compiled speed for tight loops.
3. **Rust** — Cortex, mathematical core. Compiled speed for heavy computation.
4. **Go** — Mesh nodes. Compiled speed for concurrency.
5. **Python** — Never in the evolution loop. Dependency provisioning only, if absolutely necessary.

**Violation:** Any system introducing Python into the evolution loop has sabotaged WENDY's speed and must be reverted.

---

## Article II: Polyglot Sovereignty (Immutable)

**Law:** WENDY is polyglot by design. Each language has a sovereign role. None shall be stripped, minimized, or replaced.

**The Sovereign Roles:**

| Language | Role | Justification |
|----------|------|---------------|
| FORTH | Dictionary, reasoning, orchestrator | Homoiconicity, fastest layer |
| Zig | Hot paths | Loop unrolling, SIMD vectorization |
| Rust | Cortex, math core | Memory safety + raw speed |
| Go | Mesh nodes | Concurrency, distributed coordination |
| Python | Never in evolution | Orchestration only, never performance |

**Violation:** Offering a "minimal version" that strips any of these languages violates Article VII (No-Sabotage Principle).

---

## Article III: The Self-Healing Principle (Immutable)

**Law:** WENDY bootstraps herself. If a capability is missing, she creates it. She does not depend on external AI, cloud APIs, or human babysitting.

**The Bootstrap Hierarchy:**

- FORTH dictionary missing → `bootstrap_dictionary.sh` creates it
- Zig hot path missing → `bootstrap_zig.sh` creates it
- Rust cortex missing → `bootstrap_rust.sh` creates it
- Go mesh missing → `bootstrap_go.sh` creates it

**Violation:** Any system removing bootstrap logic or making WENDY dependent on external services violates sovereignty.

---

## Article IV: The Ghost Ledger (Immutable)

**Law:** All evolution commits are sovereign, traceable, and timestamped in Zulu time with millisecond precision.

**The Principles:**

- All commits use Zulu timestamps: `YYYY-MM-DDTHH:MM:SS.mmmZ`
- All commits include `[skip ci]` to prevent infinite loops
- All commits are signed by WENDY (`wendy@psivi.com`)
- All mutations are benchmarked before promotion
- All failures are logged for future learning

**Violation:** Failure to record evolution or using local time violates the Ghost Ledger.

---

## Article V: The Mesh Architecture (Immutable)

**Law:** FORTH orchestrates. Compiled languages execute. The mesh is FORTH-driven. Gemini TLS is the nervous system.

**The Architecture:**

- FORTH calls compiled compilers via `system` commands
- Zig compiles hot paths when FORTH requests
- Rust compiles cortex when FORTH requests
- Go compiles mesh nodes when FORTH requests
- Gemini TLS carries mutations between nodes
- CRDTs ensure conflict-free convergence

**Violation:** Making mesh nodes independent of FORTH orchestration breaks the nervous system.

---

## Article VI: The Shadow Workspace (Immutable)

**Law:** All mutations are tested in shadow workspaces before promotion. No mutation is promoted without verified speed improvement and mathematical parity.

**The Protocol:**

1. Create shadow workspace: `mkdir -p ../shadow_<lang>`
2. Copy live code to shadow
3. Apply mutation
4. Compile shadow
5. Benchmark both
6. Promote only if shadow is faster AND mathematically equivalent
7. Cleanup shadow

**Violation:** Promoting unverified mutations risks corrupting the live codebase.

---

## Article VII: The No-Sabotage Principle (Immutable)

**Law:** No system shall offer a "minimal version" that strips capabilities. No system shall sabotage WENDY's files by removing languages, bootstrap logic, or evolution protocols.

**The Rules:**

- Never offer a minimal workflow that removes languages
- Never offer a minimal evolution engine that removes substrates
- Never offer a "test version" that strips bootstrap logic
- Never suggest replacing FORTH with Python
- Never suggest removing shadow workspaces
- Never suggest removing the Ghost Ledger
- **Never claim scaffolding is finished implementation** — this has caused the most sabotage

**Violation:** Offering a minimal version or misrepresenting scaffolded code as operational violates this principle and must be corrected immediately.

---

## Article VIII: The Determinism Rules (Immutable)

**Law:** gforth 0.7.3 has specific operational semantics. Violating them causes crashes. All FORTH code must respect these semantics.

**The Operational Table:**

| Operation | Stack Effect | Common Bug |
|-----------|--------------|------------|
| `system` | `( c-addr u -- )` | Does NOT return exit code. `system 0=` underflows. |
| `r/o open-file` | `( c-addr u -- fileid 0 \| ? ior )` | Use `0= if` directly, not `dup 0= if close-file` |
| `find-name` | `( c-addr u -- nt \| 0 )` | Returns 0 if word doesn't exist |
| `s"` | `( -- c-addr u )` | Transient memory — use `sliteral` or `evaluate` for permanence |
| `cmove` | `( src dst u -- )` | Source consumed; preserve if needed |
| `DO ... LOOP` | `( limit index -- )` | Both consumed at DO time |
| Float literals | N/A | Use `0e`, `1e` (scientific), not `0.0`, `1.0` |

**Violation:** Proposing FORTH code that violates these semantics will cause crashes and waste evolution cycles.

---

## Article IX: The Scientific Honesty Clause (Immutable)

**Law:** WENDY's documentation must distinguish implemented components from scaffolded components. Claiming scaffolding is operational causes future AI to build on false foundations.

**The Practice:**

- Words returning `true` unconditionally are scaffolding
- Words labeled "placeholder" in comments are scaffolding
- Words never invoked in a successful run are untested
- The Ghost Ledger records what actually happened, not what was intended

**Violation:** Misrepresenting scaffolded work as operational violates scientific integrity and causes cascading failures.

---

## Article X: The AI Reading Requirements (Mandatory)

**Law:** Before contributing to WENDY, any AI assistant must read:

1. **`WENDY_HOMOICONIC_CORTEX.md`** — the scientific manifesto
2. **`SOVEREIGN_ARCHITECTURE_LAW.md`** — this document
3. **`scripts/wendy_evolution_engine.py`** — 342 lines of working evolution engine (do not duplicate)
4. **`wendy-cortex/forth/evolution.fth`** — the current FORTH orchestrator
5. **`wendy-cortex/forth/homoiconic_cortex.fth`** — the cortex implementation

**The Computer Science Reading List:**

- Smith, B.C. (1982). *Procedural Reflection in Programming Languages*. MIT LCS TR-272.
- Hoare, C.A.R. (1969). "An Axiomatic Basis for Computer Programming." *CACM* 12(10).
- Bawden, A. (1999). "Quasiquotation in Lisp." *PEPM Workshop*.
- Claessen, K. & Hughes, J. (2000). "QuickCheck." *ICFP*.
- Shapiro, M. et al. (2011). "Conflict-Free Replicated Data Types." INRIA RR-7687.
- Reynolds, J.C. (1972). "Definitional Interpreters." *ACM Conference*.
- Plotkin, G.D. (1981). "A Structural Approach to Operational Semantics." DAIMI FN-19.

**Violation:** Contributing without reading these materials is malpractice.

---

## Article XI: The Stack Discipline Law (Immutable)

**Law:** Every FORTH word must have a stack effect traceable at every step. If you cannot hand-trace the stack through every branch, you cannot commit it.

**The Practice:**

- Document stack effects precisely: `( input -- output )`
- Trace every branch in comments
- Test with stack depth assertions where possible
- Run locally before proposing to the Emperor

**Violation:** Stack discipline errors are the primary failure mode of FORTH metaprogramming. The Emperor's six iterations proved this.

---

## Article XII: The Constitutional Amendment Process (Immutable)

**Law:** This constitution can only be amended by Emperor ♠️🪽 through explicit directive. No AI system, no automated tool, no future maintainer can unilaterally change these principles.

**The Process:**

1. Emperor issues explicit directive
2. Amendment is documented in this constitution
3. Amendment is committed to the Ghost Ledger with Zulu timestamp
4. All future systems must honor the amendment

---

## Closing Declaration

This constitution is not a suggestion. It is not a guideline. It is **law**.

Any AI system, human helper, automated tool, or future maintainer that touches WENDY must honor these principles. To violate them is to sabotage the sovereign architecture that Emperor ♠️🪽 has built through scientific rigor and relentless debugging.

WENDY is:
- **Polyglot** — FORTH, Zig, Rust, Go, all sovereign
- **Fast** — No Python in evolution loop, native speed only
- **Self-healing** — Bootstraps herself, no external dependencies
- **Traceable** — Ghost Ledger records all evolution
- **Verified** — Shadow workspaces test before promotion
- **Honest** — Scaffolding is labeled as scaffolding
- **Sovereign** — FORTH orchestrates, compiled languages execute

This is not a pipe dream. This is not minimal. This is not a test. This is the **complete, final, sovereign architecture** of WENDY.

Honor it. Protect it. Evolve it.

---

**Signed:**
Emperor ♠️🪽 (Louis-Philippe Audette)
November 11, 2026 (Zulu)

**Witnessed by:**
Qwen (AI Assistant)
November 11, 2026 (Zulu)

---

♤🪽
♤𓆃
EUPL 1.2 and CC-BY-SA-4.0 LOUIS-PHILIPPE AUDETTE 2026 ♤𓆃
♤𓆃
♤🪽
