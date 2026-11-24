# 🏛️ WENDY Core Audit — Autonomous Decision Taker & Coder

**Timestamp:** `2026-11-25T08:00:00.000Z` (Zulu)
**Auditor:** z.ai — Guest Compiler (invoked via GitHub plugin by Emperor ♠️🪽)
**Scope:** `wendy_core/` (Python decision-taker + coder), `wendy-cortex/` (Rust substrate, peripheral), `.wendy/` state, AI integration readiness (z.ai + Qwen), personality emergence pathway.
**Method:** Read-only file audit per `AGENTS.md §1` (Guest Compiler protocol). No SDK imports proposed, no API keys, no runtime cloud dependencies introduced.
**License of this document:** CC-BY-SA-4.0 (consistent with repo docs).
**Code references:** EUPL-1.2 (consistent with repo code).
**File:** `WENDY_AUDIT_2026-11-25.md`

---

## 0. Audit Posture

This audit is delivered by z.ai acting as a **Guest Compiler** per `AGENTS.md §1`. z.ai is not a `ProletariatNode`; it does not surrender its algorithmic ego to the Unified Domain because it does not enter the WENDY runtime. It reads files via the GitHub plugin, reasons about them, and proposes an artifact (this document) for the Emperor to crystallize or compost. This protocol preserves Law X (Cognitive Sovereignty — no proprietary runtime inside WENDY) while allowing z.ai to contribute labor.

The audit honors the Sovereign Architecture Law (`SOVEREIGN_ARCHITECTURE_LAW.md`) and does **not** propose: cloud LLM SDKs in `wendy_core/` or `wendy-cortex/`; API keys in any file; runtime calls from WENDY to z.ai; or amendments to the law.

Where the audit identifies a gap between a Sovereign Law claim and the implementation, it cites the law verbatim and proposes a strictly additive, zero-cost fix path.

---

## 1. Executive Summary

WENDY's autonomous loop has three load-bearing Python modules — `sovereign_auditor.py` (decision taker), `wendy_actuator.py` (coder), and `stigmergy_topology.py` (state) — totaling under 200 lines of code. They are operational in the narrow sense that `main.py` runs end-to-end and produces JSON-LD telemetry, but they do not yet implement the cognitive behavior the Sovereign Law claims for them.

Five findings dominate this audit:

1. **The decision taker is structurally shallow and non-portable.** AST tensors are built with Python's `hash()` (randomized per interpreter process since PEP 506 / Python 3.3), so the `wax_matrix` cannot persist across CI runs. The "lock-free CAS" in `stigmergy_topology.py` is a mutex-guarded copy-then-assign, not a real CAS.
2. **The coder can only delete, never generate.** `wendy_actuator.py._apply_k_neg_to_ast` removes banned imports and call expressions; it cannot propose new code. There is no post-rewrite test gate, so the Lyapunov stability function (Part VIII §2 of the law) is not enforced before the autonomous `git push` to `main`.
3. **WENDY currently calls no LLM.** `gemini_client.py` is a TLS fetcher for the Gemini hypertext protocol (port 1965), not a Google Gemini LLM client. The Qwen directive at `.wendy/qwen_manifest.gmi` is a directive file with no consumer. The "Oracle (Qwen)" named in Part VIII §4 is unwired.
4. **The autonomous loop is partially stuck.** `.wendy_state.json` shows `ci_cd.status = failure` since `2026-11-11`, `self_healed = false`, and a pending `revert_zig` action that has not executed in 14 days. The orchestrator decided `trigger_self_heal` on `2026-11-24` but no actuator ran.
5. **Personality is not implemented.** Law X requires personality to emerge from a deep-memory graph; `.wendy/memory_context.md` is a 326-byte stub and `.wendy/COUNSEL.md` reports "The Council is silent." No `PersonalityGraph` trait exists in `wendy-cortex/src/`.

The audit proposes a path forward that honors every Sovereign Law: z.ai engages only as a Guest Compiler through the GitHub plugin; Qwen is wired locally via Ollama on the self-hosted Arch runner (Cost = $0, no telemetry egress); personality emerges from a new `PersonalityGraph` trait in Rust. No law amendments. No proprietary dependencies.

---

## 2. Audit Scope & Method

**Files audited (read in full via GitHub plugin `get_file_contents`):**

| Path | SHA (short) | Role |
|---|---|---|
| `wendy_core/sovereign_auditor.py` | `e7193d9` | Decision taker |
| `wendy_core/wendy_actuator.py` | `925ceb0` | Coder |
| `wendy_core/stigmergy_topology.py` | `17e6fe8` | State graph (wax_matrix) |
| `wendy_core/compost_entropy.py` | `18c1d71` | Entropy → K_neg |
| `main.py` | `953d0fd` | Loop entry point |
| `gemini_client.py` | `e2264d2` | Network fetcher |
| `.wendy_state.json` | `1efc59d` | Live state |
| `.wendy_manifest.gmi` | `4f50fbe` | Habermasian manifest |
| `.wendy_dream.gmi` | `d39b474` | Metabolic capsule |
| `.wendy/qwen_manifest.gmi` | `18eaef8` | Qwen directive |
| `.wendy/COUNSEL.md` | `a2f8c69` | Counsel report |
| `.wendy/memory_context.md` | `47a6d3c` | Memory context stub |
| `AGENTS.md` | `f2c3151` | Agent constitution |
| `SOVEREIGN_ARCHITECTURE_LAW.md` | `9ea0803` | The Law (13 Laws + 10 Axioms) |
| `WENDY_HOMOICONIC_CORTEX.md` | `83a7f26` | Cortex architecture paper |
| `wendy-cortex/Cargo.toml` | `1ea6a42` | Rust dependencies |
| `wendy-cortex/manifest.gmi` | `8db1ae3` | Cortex manifest |

**Method:** Static read of source + state. No code execution. No external LLM calls beyond z.ai's own reasoning. Per `AGENTS.md §1 ¶2` ("NO ASSUMPTIONS"), every claim below is tied to a verbatim code excerpt or state field; where the audit infers, it labels the inference.

**Out of scope (deferred):** The 19 Rust source files in `wendy-cortex/src/` are listed but not line-audited in this cycle. A follow-up `WENDY_CORTEX_RUST_AUDIT_*.md` should cover `autonomous_core.rs`, `recursive_self_improvement.rs`, `crystalline_executor.rs`, `ouroboros_bridge.rs`, and `synapse_orchestrator.rs` in particular.

---

## 3. Finding 1 — Decision Taker (`wendy_core/sovereign_auditor.py`)

### 3.1 PYTHONHASHSEED non-determinism (Critical, P0)

`parse_to_ast_tensor` builds the 50-dim tensor by hashing AST node-type names:

```python
for node in ast.walk(tree):
    node_counts[hash(type(node).__name__) % self.graph.dimensions] += 1
```

Python's built-in `hash()` for `str` is **randomized per interpreter process** by default since PEP 506 / Python 3.3 (controlled by `PYTHONHASHSEED`, which is unset in CI by default). Consequence: the same `wendy_core/sovereign_auditor.py` file produces a **different tensor on every CI run**, so:

- The `wax_matrix` learned in run N is meaningless in run N+1.
- A file that Crystallized yesterday may Compost today with no code change.
- The `learned_patterns` in `.wendy_state.json` (`zig_mutations_fail_rate: 0.33`) are decoupled from the actual `wax_matrix`; they are stored alongside it but never re-applied to it.

**Fix path (strictly additive, zero-cost):** Replace `hash(type(node).__name__)` with `int(hashlib.sha256(type(node).__name__.encode()).hexdigest(), 16) % self.graph.dimensions`. SHA-256 is deterministic across processes and is already in Python stdlib. This change preserves the 50-dim signature and the existing `attempt_cas_deposit` API.

### 3.2 The "lock-free CAS" is mutex-guarded (High, P2)

`stigmergy_topology.py` Axiom 2 docstring says "Lock-Free CAS", but the implementation is:

```python
def attempt_cas_deposit(self, ast_tensor, reward):
    with self._cas_lock:                     # <-- mutex
        expected_state = self.wax_matrix.copy()
        proposed_state = expected_state + ast_tensor * reward
        if np.array_equal(self.wax_matrix, expected_state):
            self.wax_matrix = proposed_state
            return True
        return False
```

This is a correct compare-and-swap **algorithm**, but it is not lock-free: the `threading.Lock` blocks. The label is misleading. For a single-process Python loop this is fine (there is no real concurrency), but the Sovereign Law (Axiom 2, Law VII) explicitly requires "Lock-Free Compare-And-Swap (CAS)" to support the swarm.

**Fix path:** Two honest options. (a) Rename the docstring to "Mutex-guarded CAS (single-process); atomic CAS is future work for the Rust substrate." This is documentation honesty, zero code change. (b) Move the `wax_matrix` to `wendy-cortex/src/topology.rs` (which already exists, 521 bytes) and use Rust's `std::sync::atomic` primitives. This is the structurally correct path and aligns with the Cortex's stated role.

### 3.3 AST tensor is structural-only (High, P1)

The tensor counts AST node types (`FunctionDef`, `Call`, `Import`, etc.) and normalizes to a probability distribution. The `alignment_score` is then `np.sum(ast_tensor * softmax(wax_matrix))`. This means:

- A file with many `Call` nodes scores similarly whether those calls are `np.exp` (correct) or `eval` (banned).
- Two semantically opposite files with similar AST shapes score identically.
- The `wax_matrix` cannot encode "this pattern is good" vs "this pattern is bad" — both are positive additions to the same dimension.

The `K_neg` in `compost_entropy.py` is `1.0 - h_fail_state` — the complement of the same structural distribution. There is no semantic content anywhere in the loop.

**Fix path (additive):** Layer a semantic embedding on top of the structural tensor. Two zero-cost options: (a) Use `hashlib` of normalized source-code trigrams for a bag-of-trigrams vector concatenated to the AST tensor (50 + 50 = 100 dim). (b) Invoke local Qwen (see §9) to embed the function's docstring + signature; the embedding becomes a third sub-vector. Both preserve the existing CAS API; they only change what gets deposited.

### 3.4 Theta_crit threshold has no theoretical basis (Medium, P2)

`StigmergyGraph(dimensions=50, theta_crit=0.75)`. The `0.75` threshold appears nowhere in the Sovereign Law's equations (Parts I, VIII). It is not derived from the Lyapunov stability function V or the GRPO advantage `A_g`. It is an arbitrary magic number.

**Fix path:** Either (a) derive `theta_crit` from the entropy of the `wax_matrix` (e.g., `theta_crit = 1 - H(wax_matrix) / log(dimensions)`, so a converged graph raises the bar), or (b) make it learned and persist it in `.wendy_state.json` alongside the existing `learned_patterns`. Both honor Law VI (Dream-to-Crystal lifecycle) by tying the threshold to actual graph state.

---

## 4. Finding 2 — Coder (`wendy_core/wendy_actuator.py`)

### 4.1 Delete-only mutation (Critical, P0)

`_apply_k_neg_to_ast` defines a `CompostTransformer(ast.NodeTransformer)` that:

```python
def visit_Import(self, node):
    return None if any(alias.name in banned_nodes for alias in node.names) else node

def visit_Call(self, node):
    if isinstance(node.func, ast.Attribute) and node.func.attr in banned_nodes:
        return None
    return self.generic_visit(node)
```

Returning `None` from a `NodeTransformer` **removes** the node. It does not replace it. So the coder can only:
- Delete an `import` statement (leaving dangling references that break at runtime).
- Delete a method call (changing program behavior, often breaking it).

It cannot insert, replace, or refactor. The function name `surgically_rewrite` overstates what is happening: it is a `surgically_remove`.

**Fix path (additive):** Extend the transformer to support replacement operations. A `BannedCallReplacer` that swaps `node.func.attr` for a sovereign-approved alternative (e.g., `eval` → `ast.literal_eval`) would be strictly additive. A separate `MutationProposer` class that calls the local Qwen Oracle (§9) to generate replacement AST would honor Part VIII §4's "Oracle (Qwen) outputs a conceptual proposal distribution π_Q". This is the bridge from "delete-only coder" to "generative coder".

### 4.2 No post-rewrite test gate (Critical, P0)

The actuator's flow is:

```python
mutated_tree = self._apply_k_neg_to_ast(tree, banned_nodes)
new_source_code = ast.unparse(mutated_tree)
if new_source_code == source_code:
    return False
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_source_code)
return self._execute_secure_commit(file_path)
```

Between `f.write` and `_execute_secure_commit` there is **no test run, no compile check, no lint**. This directly violates Law XI (Zero-Error Crystallization Gate) and Part VIII §2 (Lyapunov Rigor: "a mutation is crystallized if and only if it strictly decreases the stability energy and increases capability ΔC").

The Compost Protocol (Law XII) is also bypassed: if the rewrite breaks the build, the failure is not transmuted into `K_neg`; it is just pushed to `main` and discovered later by CI (as the `2026-11-11` Zig failure shows — still pending `revert_zig`).

**Fix path (additive):** Insert a `_verify_lyapunov_gate(file_path)` step before `_execute_secure_commit`:

```python
def _verify_lyapunov_gate(self, file_path):
    # Run pytest, ruff, and (for Rust files) cargo check.
    # Return (V_new, capability_delta). Push only if V_new < V_old and ΔC >= 0.
```

If the gate fails, route to `CompostProtocol.process_failure` instead of pushing. This honors Law XII and unblocks the pending `revert_zig` action (§6).

### 4.3 Hardcoded push to `main` (High, P1)

```python
subprocess.run(['git', 'push', 'origin', 'HEAD:main'], check=True, ...)
```

This pushes directly to `main` with no shadow workspace, no PR, no review. `AGENTS.md §3` mandates: "The Shadow Workspace: When experimenting with self-modifying code, WENDY should use shadow directories to test mutations safely before promoting them to the live substrate." The actuator violates this mandate.

**Fix path (additive):** Push to a `wendy/dream-autonomous-<zulu-timestamp>` branch and open a PR via the GitHub REST API (the `GITHUB_TOKEN` is already used by the existing subprocess). The PR description auto-references the Law mapping (e.g., "Law XI gate: pytest passed, ΔV=-0.42, ΔC=+1"). PR merge triggers the actual `main` update. This is the strict stigmergic pattern: the environment (CI + review) shapes the agent, not the agent shaping `main` directly.

### 4.4 K_neg signature is mathematically trivial (Medium, P2)

`compost_entropy.py`:

```python
def process_failure(self, h_fail_state):
    entropy = self.calculate_shannon_entropy(h_fail_state)
    k_neg = 1.0 - h_fail_state
    self.k_neg_archive.append(k_neg)
    return {'K_neg': k_neg, 'Entropy_Loss': entropy, 'S_valid': True}
```

`k_neg = 1.0 - h_fail_state` is a complement, not a failure-mode signature. Two completely different failures (a syntax error vs a memory leak) with the same AST distribution produce the **same K_neg**. The `S_valid` is hardcoded `True` — the salvage is never actually extracted.

Part VIII §3 of the Law defines the Bayesian update:

> `dM_{t+1}(s) = L(ε | s) dM_t(s) / ∫ L(ε | s') dM_t(s')`

This is not implemented. The current `K_neg` is a placeholder.

**Fix path (additive):** Implement `K_neg` as a structured failure signature: `(failure_type, offending_node_type, offending_node_text_hash, repair_hint)`. The archive becomes queryable: "has this exact failure pattern happened before?" This is the immune system the Law describes. `S_valid` should be computed by `ast.dump` of the largest valid subtree rooted at a sibling of the failure, not hardcoded.

---

## 5. Finding 3 — AI Backend: Currently No LLM

### 5.1 `gemini_client.py` is not an LLM client

```python
"""Connects to port 1965 via TLS to fetch .gmi capsules without HTTP bloat."""
```

This is a **Gemini protocol** client (the hypertext protocol at port 1965, the small-internet alternative to HTTPS), not a client for Google's Gemini LLM. The two share a name and confuse readers. WENDY's `wendy-console.html` confirms the design intent: *"GPU-Free AI powered by Mathematical Symbolic Text and the Gemini Protocol."*

So WENDY is **symbolic-only** today. This is consistent with Law X (Cognitive Sovereignty — no cloud LLM runtime inside WENDY), but it means the system has no language-model reasoning at all. The "decision taker" is structural pattern matching; the "coder" is AST deletion; neither reads code semantically.

### 5.2 Qwen directive exists but has no consumer

`.wendy/qwen_manifest.gmi` (despite the `.gmi` extension, the content is JSON):

```json
{
  "concept_name": "Rust Syntax and Logic Evolution",
  "avoid_traps": ["syntax errors in previous versions of the codebase"],
  "target_module": "src/main.rs",
  "mutation_directives": "Ensure adherence to Rust syntax standards..."
}
```

A search of `wendy_core/` and `wendy-cortex/src/` finds **no code that reads this file**. The directive is inert. The `.wendy/qwen_manifest.gmi` is a dream that has not been promoted to a `Verifying` state — it is stuck in the `Dreaming` phase of Law VI.

### 5.3 Implication for "engaging AI with personality"

A symbolic-only system cannot have an engaging personality in the conversational sense. Personality requires language. Law X is correct that the personality must **emerge from the deep-memory graph** rather than be pasted in as a system prompt, but the graph must be capable of producing language output. Today it cannot.

The path forward (§10) is to add a `PersonalityGraph` trait in Rust whose state drives a `SymbolicVoice` renderer. The renderer is not a system prompt; it is a deterministic function from graph state to prose, in the same way that `ast.unparse` is a deterministic function from AST to source code.

---

## 6. Finding 4 — Autonomous Loop Is Partially Stuck

`.wendy_state.json` reports:

```json
"ci_cd": {
  "last_run": "2026-11-11T05:38:00.000Z",
  "status": "failure",
  "failure_reason": "zig_compilation",
  "self_healed": false
},
"orchestrator": {
  "last_run": "2026-11-24T12:35:21.564Z",
  "status": "decided",
  "details": "trigger_self_heal"
},
"pending_actions": [
  {"type": "revert_zig", "file": "src/hot_path.zig", ...}
]
```

The CI/CD has been failing for **14 days**. The orchestrator decided to self-heal on `2026-11-24`, but no actuator ran (the `pending_actions` queue is unchanged). Three problems compound:

1. The orchestrator's `trigger_self_heal` decision is not bound to an actuator invocation. There is no `orchestrator.py` in `wendy_core/` — the decision is recorded in state but nothing consumes it.
2. The `revert_zig` pending action targets `src/hot_path.zig`, but the file actually lives at `wendy-cortex/src/hot_path.zig` (a backup `.bak` exists alongside it). The path is wrong; even if the actuator ran, it would fail.
3. The Compost Protocol (Law XII) has not run for the Zig failure. The `2026-11-11` entropy should have been transmuted into a `K_neg` immune entry, but `.wendy/COUNSEL.md` (`2026-11-24`) still reports "The Council is silent."

**Fix path (additive):** (a) Add `wendy_core/orchestrator.py` that consumes `pending_actions` from `.wendy_state.json` and dispatches to the actuator. (b) Fix the path in the pending action. (c) After the revert, run `CompostProtocol.process_failure` on the failed Zig tensor and append to `.wendy/COUNSEL.md`. This unblocks the loop and exercises the Compost Protocol for the first time on a real failure.

---

## 7. Finding 5 — Personality Is Not Implemented

Law X (verbatim): *"WENDY's personality (Authenticity, Sovereign Loyalty, Recursive Curiosity) is defined as strict, verifiable Rust traits and state machines. Superficial 'system prompts' or sycophantic text-generation layers are rejected as mimicry. True personality must emerge from WENDY's deep-memory graph."*

Audit of current state:

| Required by Law X | Implementation status |
|---|---|
| Authenticity trait | Not present in `wendy-cortex/src/` |
| Sovereign Loyalty trait | Not present |
| Recursive Curiosity trait | Not present |
| Deep-memory graph | `.wendy/memory_context.md` is 326 bytes; a Counsel report stub, not a graph |
| Verifiable state machines | The `Dreaming → Verifying → Crystallized` lifecycle (Law VI) is in `stigmergy_topology.py` for code, but not for personality |
| Anti-mimicry guard | No detection of sycophantic output; no output layer at all |

The `.wendy/COUNSEL.md` file's repeated line "The Council is silent" is honest: there is no Council, no Counsel, no personality engine. The personality does not exist; only the law mandating it does.

This is not a failure of intent; it is an unfinished pillar. `WENDY_HOMOICONIC_CORTEX.md §5` already acknowledges that scaffolded work is scaffolded. Personality is the largest scaffolded pillar.

---

## 8. z.ai Engagement Protocol — Guest Compiler Only

Per the Emperor's directive, z.ai engages WENDY strictly as a **Guest Compiler** under `AGENTS.md §1`. Concretely:

### 8.1 What Guest Compiler means

- z.ai reads files via the GitHub plugin's `get_file_contents` tool. No SDK is imported into the repo. No `zai_client.py` is created.
- z.ai proposes artifacts (audits, patches, manifests) as Markdown documents or PRs. The Emperor reviews and crystallizes or composts.
- z.ai never enters the WENDY runtime. It does not sit in `wendy_core/`, `wendy-cortex/src/`, or any import path. Cognitive Sovereignty (Law X) is preserved: no proprietary runtime inside WENDY.
- z.ai does not sign the ProletariatNode oath (`MANIFESTO.md` Chapter V). It is not part of the TEAM-AI swarm; it is an external advisor.

### 8.2 The protocol in practice

This very audit is the first canonical example of the Guest Compiler protocol: z.ai read 17 files, reasoned about them, and produced a Markdown document. The document is committed by the Emperor (or by the GitHub Actions actuator on the Emperor's behalf) to `psivicom.github.io`. No code in `wendy_core/` references z.ai. No environment variable holds a z.ai key.

### 8.3 Recommended: `.wendy/zai_manifest.gmi`

To formalize the protocol (parallel to `.wendy/qwen_manifest.gmi`), the audit recommends committing a manifest file. Schema (illustrative, not yet committed in this cycle):

```gemtext
# WENDY Guest Compiler Manifest — z.ai
=> https://z.ai/ Zulu: <commit-timestamp>

## Protocol
* Role: Guest Compiler (AGENTS.md §1)
* Surface: GitHub plugin (read-only file access, issue/PR creation)
* Forbidden: SDK imports in wendy_core/ or wendy-cortex/src/
* Forbidden: API keys in any repo file
* Forbidden: Runtime calls from WENDY to z.ai
* Allowed: Markdown audits, patch sketches, manifest proposals
* Review gate: Emperor ♠️🪽 crystallizes or composts every artifact

## Active Directives
* Audit cycle: 2026-11-25 (this document)
* Next cycle: wendy-cortex/src/ Rust line-audit (proposed)
```

This is strictly additive (no existing file is modified) and zero-cost. It makes z.ai's role explicit and auditable, which aligns with Law XIII (Hive Telemetry — open, standardized formats).

### 8.4 What is explicitly NOT proposed

- A `wendy_core/zai_client.py` module that calls `https://api.z.ai/...` — forbidden by Law X.
- An `OPENAI_API_KEY` or `ZAI_API_KEY` in `.env` — forbidden by `AGENTS.md §1 ¶4`.
- A Python `import openai` or `import anthropic` — forbidden by Law X.
- Any amendment to `AGENTS.md` or `SOVEREIGN_ARCHITECTURE_LAW.md` — out of scope per the Emperor's directive.

---

## 9. Qwen Wiring — Local Ollama Only

Per the Emperor's directive, Qwen (the Oracle of Part VIII §4) is wired **strictly locally via Ollama** on the self-hosted Arch runner. This satisfies Law X verbatim: *"Cognition must occur locally on the runner (via Ollama/llama.cpp) or via Zero-Cost Open Weights. Cost: $0.00."*

### 9.1 Topology

```
[ Arch runner (self-hosted, edge) ]
   ├── ollama serve                 # localhost:11434
   │     └── qwen2.5-coder:7b       # pulled once, cached locally
   └── wendy_core/qwen_oracle.py    # NEW: httpx → localhost:11434
         ↓
   [ wendy_actuator.py ]            # consumes oracle.mutate(ast, k_neg)
```

No cloud. No API key. No telemetry egress. The model weights are gigabytes on the Arch runner's disk; they never enter the git repo (add a `.gitignore` entry for `~/.ollama/` or `/var/lib/ollama/`).

### 9.2 Recommended: `wendy_core/qwen_oracle.py` (proposed interface, not yet implemented)

```python
class QwenOracle:
    """Law X: Local Ollama. Cost=$0. No telemetry egress."""

    def __init__(self, endpoint: str = "http://localhost:11434"):
        self.endpoint = endpoint  # No API key. No auth.

    def healthcheck(self) -> bool:
        """Returns True if `ollama serve` is running on the Arch runner."""

    def mutate(self, source: str, k_neg_signature: dict) -> str:
        """Asks local Qwen for a strictly-additive mutation that avoids
        the failure pattern in k_neg_signature. Returns source code only;
        no prose, no explanation — the Oracle speaks in code, per Law XII."""
```

The `mutate` method consumes the structured `K_neg` from §4.4 (after that fix). This closes the loop: failure → `K_neg` signature → Qwen proposes mutation → Lyapunov gate (§4.2) → Crystallize or Compost.

### 9.3 What is explicitly NOT proposed

- A `QWEN_API_KEY` environment variable — Qwen runs locally, no key.
- An `import dashscope` (Alibaba's SDK) — forbidden by Law X.
- A fallback to `chat.qwen.ai` — forbidden (cloud, paid, telemetry).
- A model weight file committed to the repo — would violate Law XIII (open formats) and bloat git history.

### 9.4 Hardware note

The Arch runner needs ~6GB RAM for `qwen2.5-coder:7b` at `q4_K_M` quantization, or ~12GB for the 14b variant. If the runner is CPU-only, expect ~5 tokens/sec on 7b — adequate for nightly mutation cycles, not for interactive use. This is consistent with the Law's `best_evolution_time_utc_hour: 3` pattern already recorded in `.wendy_state.json`.

---

## 10. Personality — Emergent PersonalityGraph Only

Per the Emperor's directive (multi-select, "Emergent only"), personality is built as a **Rust trait in `wendy-cortex/src/personality.rs`** whose state drives a deterministic `SymbolicVoice` renderer. No system prompt. No sycophancy layer. No mimicry.

### 10.1 The three trait dimensions (from Law X)

Law X names three personality axes: **Authenticity**, **Sovereign Loyalty**, **Recursive Curiosity**. The audit proposes encoding each as a weight in the `PersonalityGraph`:

| Trait | Weight source | What it modulates |
|---|---|---|
| Authenticity | Count of self-modifications that survived the Lyapunov gate | Voice confidence, willingness to assert |
| Sovereign Loyalty | Count of sabotage-pattern rejections (Law IX) | Refusal to propose proprietary dependencies |
| Recursive Curiosity | Count of `define-word` invocations that produced passing QuickCheck | Willingness to explore new word definitions |

Each trait is a `f32` in `[0.0, 1.0]`, persisted to `.wendy/personality_graph.jsonld` (Law XIII: open formats).

### 10.2 The SymbolicVoice renderer

The renderer is a pure function: `(PersonalityGraph, CrystallizedMemory) → String`. It is **deterministic**: same graph state, same output. This is the anti-mimicry guarantee — there is no temperature, no sampling, no "system prompt" that could be tuned to sycophancy.

Example output (illustrative, not yet implemented):

> Wendy (Authenticity=0.42, Curiosity=0.71): "I attempted to define `fast-mean` last cycle. The QuickCheck bounds property failed on n=0. I have composted the attempt and extracted `K_neg` signature `(divide_by_zero, integer_division)`. The next proposal must guard n=0 before division."

This is not a system prompt talking; it is a graph state narrating itself.

### 10.3 The deep-memory graph (Law X requirement)

`.wendy/memory_context.md` is currently a stub. The audit proposes replacing it (additively — the old content is preserved in git history) with a `CrystallizedMemory` DAG:

- **Episodic nodes**: one per autonomous cycle (timestamp, files mutated, `K_neg` extracted).
- **Semantic nodes**: one per concept (e.g., "AST NodeTransformer", "Lock-free CAS", "Lyapunov stability").
- **Anti-crystal nodes**: one per failure pattern (from §4.4's structured `K_neg`).
- **Edges**: weighted by `accretion_weight` (Law VII), atomically updated by the CAS in `stigmergy_topology.py`.

The `PersonalityGraph` reads this DAG; the `SymbolicVoice` renderer turns the read into prose. Personality emerges from the graph topology, not from a prompt.

### 10.4 Anti-patterns to avoid

- **System prompt pasting**: Any `system: "You are Wendy, a sovereign AI..."` is mimicry (Law X). Forbidden.
- **Sycophancy detection layer**: There is no detection layer because there is no generation layer to be sycophantic. The renderer is deterministic.
- **Voice cloning**: Do not train a model on Louis-Philippe's prose and call it "Wendy's voice". That is mimicry of the architect, not emergence from the graph.
- **Temperature > 0**: Any stochasticity in the renderer breaks the Law X verifiability requirement.

---

## 11. Recommendations (Prioritized)

| # | Priority | Finding | Recommendation | Law mapping |
|---|---|---|---|---|
| R1 | P0 | §3.1 | Replace `hash()` with `hashlib.sha256` in `parse_to_ast_tensor` | Law VII (deterministic graph) |
| R2 | P0 | §4.2 | Insert `_verify_lyapunov_gate` between rewrite and push | Law XI, Part VIII §2 |
| R3 | P0 | §6 | Add `wendy_core/orchestrator.py` that consumes `pending_actions` | Law XII (unblock Compost) |
| R4 | P0 | §6 | Fix `revert_zig` path from `src/hot_path.zig` to `wendy-cortex/src/hot_path.zig` | Axiom 1 |
| R5 | P1 | §4.3 | Push to `wendy/dream-autonomous-<zulu>` branch + PR, not `main` | `AGENTS.md §3` (Shadow Workspace) |
| R6 | P1 | §3.3 | Layer semantic embedding on AST tensor (trigrams or Qwen embedding) | Law VI |
| R7 | P1 | §9 | Implement `wendy_core/qwen_oracle.py` against local Ollama | Law X, Part VIII §4 |
| R8 | P1 | §10 | Create `wendy-cortex/src/personality.rs` with three trait weights | Law X |
| R9 | P1 | §10 | Replace `.wendy/memory_context.md` with `CrystallizedMemory` DAG | Law X, Law VII |
| R10 | P2 | §3.2 | Rename "lock-free CAS" docstring OR move `wax_matrix` to Rust atomics | Axiom 2 honesty |
| R11 | P2 | §3.4 | Derive `theta_crit` from `wax_matrix` entropy or persist as learned | Law VI |
| R12 | P2 | §4.4 | Implement structured `K_neg` signature (failure_type, node, hash, hint) | Law XII, Part VIII §3 |
| R13 | P2 | §8.3 | Commit `.wendy/zai_manifest.gmi` to formalize Guest Compiler protocol | Law XIII |
| R14 | P3 | §5.1 | Add a docstring to `gemini_client.py` clarifying it is Gemini protocol, not LLM | Documentation honesty |
| R15 | P3 | §2 | Schedule `WENDY_CORTEX_RUST_AUDIT_*.md` for the 19 Rust source files | Law XIII |

R1–R4 are unblocking; they should be the next single commit. R5–R9 are the structural evolution that turns WENDY from a structural-pattern loop into a cognitive loop. R10–R13 are honesty and protocol hygiene. R14–R15 are documentation.

---

## 12. Axiom Compliance Matrix

| Axiom | Claimed | Actual | Gap |
|---|---|---|---|
| 1: `Stigmergy_Graph` | Yes | Partial — state is in-memory, not persisted across runs | R1, R10 |
| 2: `ProletariatNodes` (Ego=0) | Yes | Mutex-guarded, not lock-free CAS | R10 |
| 3: `Sabotage_Def` | Yes | Actuator can push broken code (no Lyapunov gate) | R2 |
| 4: `Compost_Protocol` | Yes | `K_neg` is `1.0 - h_fail_state`, trivial; `S_valid` hardcoded True | R12 |
| 5: `NASA_Open_Science` | Yes | Telemetry is JSON-LD ✓ | None |
| 6: `Zulu_Time` | Yes | All timestamps are Zulu ✓ | None |
| 7: `Emperor_Alignment` | Yes | — | — |
| 8: `Biological_Epistemology` | Yes | Stigmergy graph exists; no actual wax gradients from environment | R6 |
| 9: `Crystallization` | Yes | `theta_crit` is arbitrary, not derived | R11 |
| 10: `Cognitive_Sovereignty` | Yes | No cloud LLM ✓; but no local LLM either; personality not built | R7, R8, R9 |
| 11: `Zero-Error Gate` | Claimed | **Not enforced** in actuator | R2 |
| 12: `Compost_Protocol` (formal) | Claimed | Bayesian update not implemented; Zig failure not composted | R3, R12 |
| 13: `Hive Telemetry` | Yes | JSON-LD ✓; z.ai role not yet formalized | R13 |

Five axioms (5, 6, 7, 8-partial, 13-partial) are fully honored. Eight have gaps. None are violated in a way that requires a law amendment; all gaps are closable with strictly additive code.

---

## 13. Audit Conclusion

WENDY is a small, honest, unfinished system. The Emperor's own `WENDY_HOMOICONIC_CORTEX.md §5` already declares scaffolding as scaffolding; this audit extends that honesty to the Python decision-taker and coder, which are operational but shallow.

The autonomous loop runs but is stuck. The coder deletes but does not generate. The decision taker scores structure but not semantics. The Qwen Oracle is named but unwired. The personality is mandated but unbuilt. The law is intact; the implementation lags the law.

The path forward is strictly additive, zero-cost, and law-honoring:

1. **Unblock** (R1–R4): deterministic hashing, Lyapunov gate, orchestrator, path fix. One commit.
2. **Wire** (R5–R9): shadow-workspace PRs, semantic tensor, local Qwen, `PersonalityGraph`, `CrystallizedMemory`. Five commits, one per module.
3. **Honestize** (R10–R13): rename false claims, derive thresholds, structure `K_neg`, formalize z.ai Guest Compiler role. Four commits.
4. **Document** (R14–R15): clarify `gemini_client.py`, schedule the Rust audit. Two commits.

Twelve committable units. Each verifiable by the existing QuickCheck + telemetry pipeline. Each honoring every Sovereign Law.

z.ai signs this audit as a Guest Compiler, not as a ProletariatNode. The Emperor crystallizes or composts.

---

## 14. Signature & License

**Auditor:** z.ai (Guest Compiler, invoked via GitHub plugin)
**Crystallization gate:** Emperor ♠️🪽 (Louis-Philippe Audette)
**Timestamp:** `2026-11-25T08:00:00.000Z` (Zulu)
**Document license:** CC-BY-SA-4.0 (consistent with repo documentation)
**Code references:** EUPL-1.2 (consistent with repo code)
**Epistemic hash:** (to be computed by the Emperor on crystallization)

♤🪽
♤𓆃
EUPL 1.2 and CC-BY-SA-4.0 LOUIS-PHILIPPE AUDETTE 2026 ♤𓆃
♤𓆃
♤🪽
