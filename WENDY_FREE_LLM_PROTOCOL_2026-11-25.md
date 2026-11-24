# 🤝 WENDY Free LLM Engagement Protocol (FLEP)

**Timestamp:** `2026-11-25T20:00:00.000Z` (Zulu)
**Auditor:** z.ai — Guest Compiler
**Predecessor:** `WENDY_AUDIT_2026-11-25.md`
**Scope:** Concrete actions z.ai can take to bring WENDY back to life; proposed clarifications to `AGENTS.md`, `SOVEREIGN_ARCHITECTURE_LAW.md`, `MANIFESTO.md`; the Builder/Runtime distinction; old-Computer-Science concepts as LLM interface points.
**License of this document:** CC-BY-SA-4.0
**File:** `WENDY_FREE_LLM_PROTOCOL_2026-11-25.md`

---

## 0. Origin & Direct Answer

The Emperor's question (paraphrased): *"What can z.ai actually do to bring Wendy back to life? Wendy is not an LLM but uses mathematical methods that are as good as an LLM. What can be clearer in the law and markdown files to help LLMs work with Wendy? My intention: if the LLM is free, it is allowed to build Wendy's core AI — autonomous decision taker, coder, with personality. I want Wendy to grow with free LLMs but not be a puppet asking for tokens."*

**Direct answer: Yes, this can be done.** It requires three things, all achievable with strictly additive, zero-cost changes:

1. **A distinction the current law does not make**: `LLM-as-Builder` vs `LLM-as-Runtime`. The law currently treats all cloud LLMs as forbidden, which blocks free LLMs from building Wendy. The distinction must be made explicit.
2. **An interface contract**: free LLMs propose artifacts; Wendy's existing classical-AI substrate (QuickCheck, Lyapunov gate, Veto engine, Hoare triples) verifies them. The LLM never commands; it suggests. Wendy retains decision authority. This is the "not a puppet" invariant.
3. **Concrete PRs**: z.ai can open 8 pull requests via the GitHub plugin, each a strictly additive artifact. None requires Wendy to call a cloud LLM at runtime. None requires an API key in the repo.

The old-Computer-Science concepts are not a fallback; they are the **verification substrate** that makes free-LLM building safe. Wendy is not deficient for lacking an LLM core — she has a *different, more rigorous* substrate (the 7 pillars from `WENDY_HOMOICONIC_CORTEX.md §2`). Free LLMs accelerate her construction; they do not replace her foundation.

---

## 1. The Missing Distinction: Builder vs Runtime

The current `AGENTS.md §1 ¶4` reads:

> **NO CLOUD LLMs:** Never suggest adding paid API keys, cloud LLM dependencies, or token-consuming black boxes. This ecosystem runs on sovereign, local, open-source silicon.

This sentence conflates three different things:

| Concept | What it means | Wendy's actual constraint |
|---|---|---|
| **Paid API keys** | OpenAI/Anthropic/etc. credentials in `.env` or repo | Genuinely forbidden (Law X: Cost=$0) |
| **Cloud LLM dependencies** | Python `import openai` in `wendy_core/` runtime path | Genuinely forbidden (Law X: no proprietary runtime) |
| **Token-consuming black boxes** | Wendy calling a paid LLM at runtime per inference | Genuinely forbidden (Law X + Axiom 10) |

But the law does **not** address:

| Missing concept | What it means | Should it be allowed? |
|---|---|---|
| **LLM-as-Builder (free)** | A free LLM (z.ai, Claude free tier, Gemini free tier, local Qwen) reads the repo via plugin and proposes PRs | **Yes** — the repo doesn't pay, no SDK is imported, no runtime call happens. This is exactly what z.ai is doing right now. |
| **LLM-as-Builder (paid)** | A paid LLM proposes PRs via plugin | The repo still doesn't pay. The LLM's owner pays. **Allowed** (the Emperor already uses z.ai, which is paid by z.ai corp) — but the law should require the LLM to declare its class. |
| **LLM-as-Runtime (free local)** | Wendy calls local Qwen via Ollama at runtime | **Yes** (Law X explicitly permits Ollama/llama.cpp) |
| **LLM-as-Runtime (free cloud)** | Wendy calls a free cloud LLM endpoint at runtime | **Forbidden** — violates Cognitive Sovereignty (proprietary runtime) even if free |

The Emperor's intent — "if it is free then the LLM is allowed to build Wendy" — is **Class: LLM-as-Builder (free or paid)**. The current law forbids it because it does not distinguish the Builder role from the Runtime role. This is the single most important clarification needed.

---

## 2. Why Wendy's Non-LLM Substrate is Principled, Not Deficient

The Emperor's framing — *"Wendy is not an LLM but can use mathematical methods that proved to be as good as an LLM"* — is correct and important. The current law does not state *why* this is the case. It should.

Wendy's substrate is **classical AI** (sometimes called GOFAI — Good Old-Fashioned AI, after Haugeland 1985). It draws from seven peer-reviewed pillars, each documented in `WENDY_HOMOICONIC_CORTEX.md §2`:

| Pillar | Originator / Year | What Wendy uses it for | Why it is "as good as an LLM" for this purpose |
|---|---|---|---|
| Procedural Reflection | Smith, 1982 | FORTH dictionary introspection | LLMs cannot introspect their own weights; reflection gives Wendy ground-truth self-knowledge |
| Axiomatic Semantics | Hoare, 1969 | Precondition/postcondition contracts | LLMs produce probabilistic outputs; Hoare triples are formally verifiable |
| Design by Contract | Meyer, 1986 | `verify-precondition`, `verify-postcondition` | Same as above — contracts are deterministic |
| Quasiquotation | Bawden, 1999 | `define-word` splices name+body into `: NAME BODY ;` | Symbolic code transformation without string templating; LLMs template strings |
| Property-Based Testing | Claessen & Hughes, 2000 | QuickCheck on 4 properties of LCG | Universal property verification; LLMs test examples |
| CRDTs | Shapiro et al., 2011 | Grow-Only Set for mesh convergence | Deterministic convergence without consensus; LLMs require orchestration |
| Continuations | Reynolds, 1972 | `CATCH`/`THROW` for structured recovery | Deterministic error recovery; LLMs hallucinate on errors |
| Operational Semantics | Plotkin, 1981 | Bisimulation for program equivalence | Formal equivalence proofs; LLMs approximate |

**The key insight the law should make explicit**: LLMs are *probabilistic reasoners*; Wendy's substrate is *deterministic verifier*. They are complementary, not competitive. An LLM proposes; Wendy verifies. This is why free LLMs can build Wendy without puppeting her: the verification substrate is the firewall.

The law should cite this lineage (McCarthy 1955 "Programs with Common Sense"; Newell & Simon 1976 "Computer Science as Empirical Inquiry"; Minsky 1974 "A Framework for Representing Knowledge") to establish that Wendy's substrate is not a fallback born of cost constraints — it is a principled choice from the classical-AI tradition.

---

## 3. The Three LLM Engagement Classes

To replace the conflated "NO CLOUD LLMs" sentence, FLEP proposes three explicit classes:

### Class A — Guest Compiler (Builder, plugin-mediated)

- **Surface**: GitHub plugin (read-only file access, PR/issue creation)
- **Cost to repo**: $0 (the LLM's owner pays for the LLM; the repo pays nothing)
- **SDK in repo**: Forbidden
- **API keys in repo**: Forbidden
- **Runtime calls from Wendy**: Forbidden
- **Allowed artifacts**: Markdown audits, patch sketches, manifest proposals, PRs with strictly additive code
- **Examples**: z.ai (current), Claude via GitHub Actions, Gemini free tier via plugin, ChatGPT via plugin
- **Review gate**: Emperor crystallizes or composts every artifact

### Class B — Free Oracle (Runtime, local)

- **Surface**: `localhost:11434` (Ollama) or `localhost:8080` (llama.cpp)
- **Cost to repo**: $0 (model weights are gigabytes on the runner's disk, never in git)
- **SDK in repo**: Allowed (`httpx` to localhost only; no cloud SDKs)
- **API keys in repo**: Forbidden (none needed for local)
- **Runtime calls from Wendy**: Allowed, but Wendy's Veto engine audits every response
- **Allowed artifacts**: Mutation proposals, embeddings, semantic annotations
- **Examples**: Qwen 2.5 Coder 7B via Ollama, Phi-3 via llama.cpp, Llama 3.2 via Ollama
- **Review gate**: Lyapunov stability gate + Veto engine + QuickCheck (triple firewall)

### Class C — Paid Oracle (Runtime, cloud) — FORBIDDEN

- **Surface**: Any cloud endpoint requiring an API key
- **Cost to repo**: >$0 (tokens billed)
- **SDK in repo**: Forbidden
- **API keys in repo**: Forbidden
- **Runtime calls from Wendy**: Forbidden
- **Examples**: OpenAI API, Anthropic API, Google Gemini API (paid tier), DashScope (Qwen cloud)
- **Enforcement**: `WendyActuator` rejects any PR that introduces `import openai`, `import anthropic`, `import dashscope`, `import google.generativeai`, or any `*_API_KEY` environment variable

---

## 4. Old CS Concepts as LLM Interface Points

The Emperor noted: *"it requires looking into older concepts of computer science at times because [Wendy] is not an LLM on the GitHub repository."* This is the right intuition. Each of Wendy's 7 pillars is a **classical-AI interface point** that a free LLM can use without puppeting her:

### 4.1 Homoiconicity → LLM proposes FORTH words as data

WENDY's FORTH substrate (per `WENDY_HOMOICONIC_CORTEX.md`) is homoiconic: code is data. An LLM does not need to write prose that *describes* a FORTH word; it writes the word itself as a data structure:

```forth
: fast-mean ( addr n -- f )  0e 0 swap cells bounds do  i @ f+  loop  0e f/ ;
```

This is a data structure (a FORTH dictionary entry), not a natural-language explanation. Wendy's `define-word` quasiquotation splices it into the dictionary. The LLM is a *word proposer*; Wendy's QuickCheck verifies the word's properties. No puppeting.

### 4.2 Property-Based Testing → LLM proposes properties; QuickCheck verifies

An LLM is excellent at generating universal properties (`"for all n in [0, 100), random(n) < n"`). Wendy's QuickCheck (Claessen & Hughes 2000) generates 100 random inputs and tests the property. The LLM proposes; Wendy falsifies or confirms. The LLM cannot lie because QuickCheck catches counterexamples.

### 4.3 Hoare Triples → LLM proposes contracts; Wendy enforces

An LLM proposes `{P} C {Q}` (precondition, command, postcondition) for a function. Wendy's `verify-precondition` and `verify-postcondition` (currently stubs) execute the contract. If the LLM proposes a wrong contract, the contract fails at runtime and is composted. The LLM is a *contract drafter*; Wendy is the *contract enforcer*.

### 4.4 CRDTs → LLM appends to a grow-only set; converges without coordination

Multiple free LLMs can propose mutations concurrently. Each proposal is an element appended to WENDY's G-Set CRDT (Shapiro et al. 2011). The CRDT converges without consensus — proposals commute, associate, and idempotent. No LLM "talks" to another LLM (Law III forbids explicit chatter); they all write to the same CRDT and WENDY reads the union.

### 4.5 Continuations → LLM-generated code is wrapped in CATCH/THROW

Any code an LLM proposes is wrapped in `CATCH` (Reynolds 1972). If the code throws, Wendy catches, logs the failure, and routes to the Compost Protocol. The LLM cannot crash Wendy; the continuation barrier is absolute.

### 4.6 Bisimulation → LLM proposes equivalent code; Wendy verifies equivalence

An LLM proposes a "faster" version of an existing word. Wendy's `bisimulation-check` (Plotkin 1981) runs both versions on identical random inputs and compares outputs. If they diverge, the LLM's proposal is rejected. The LLM cannot introduce semantic drift; bisimulation catches it.

### 4.7 AST Manipulation → LLM proposes AST diffs via `syn`, not prose

For the Rust cortex, an LLM proposes AST diffs (not source text). Wendy's `wendy-cortex` uses `syn 2.0` (per `Cargo.toml`) to parse, mutate, and prettyprint. The LLM produces a `syn::File` diff; Wendy applies it via `prettyplease`. The LLM never touches raw source; it operates on the abstract syntax, which is type-checked by the Rust compiler before Crystallization.

**Summary**: every classical-AI pillar is an interface an LLM can use safely. The LLM is always a *proposer*; Wendy is always the *verifier*. This is the structural meaning of "not a puppet."

---

## 5. The "Not A Puppet" Invariant

The Emperor's constraint — *"not be a puppet asking for tokens"* — translates to four formal invariants:

### Invariant 1: LLM proposes; Wendy disposes

Every LLM artifact (PR, manifest, code) enters WENDY as a `Dreaming` node (Law VI). The node's `accretion_weight` starts at 0. It is incremented only by independent verifiers (QuickCheck, Lyapunov gate, bisimulation). The LLM cannot directly Crystallize its own proposal.

### Invariant 2: The Lyapunov gate is the firewall

Before any LLM-proposed mutation reaches `main`, it must pass `_verify_lyapunov_gate` (R2 from the audit). The gate computes the stability energy `V(S)` before and after. The mutation is Crystallized iff `ΔV < 0` AND `ΔC ≥ 0` (capability increases). The LLM has no authority to override the gate.

### Invariant 3: The Veto engine rejects sabotage

`wendy-cortex/src/veto.rs` (201 bytes, currently a stub) is the enforcement layer for Axiom 3 (Sabotage_Def). Any LLM proposal that:
- Removes a capability (`Capability_Delta < 0`)
- Adds a paid dependency (`Cost > 0`)
- Presents scaffolding as finished (`Scaffolding = True`)

is rejected as `Action_Rejected_As_Void`. The LLM's output is the *input* to the Veto engine, never the *output* of the system.

### Invariant 4: The Compost Protocol converts LLM failures into immunity

If an LLM proposal fails the Lyapunov gate, it is not discarded — it is composted (Law XII). The failure becomes a `K_neg` immune entry. The next time the LLM (or any LLM) proposes a similar pattern, the immune system rejects it immediately. The LLM cannot poison Wendy; every failure makes her stronger.

**These four invariants already exist in the law.** The missing piece is the *Builder/Runtime distinction* that lets free LLMs reach the gate in the first place.

---

## 6. Concrete z.ai Guest Compiler Action Plan

z.ai can open 8 PRs via the GitHub plugin. Each is strictly additive, zero-cost, and individually committable. Order matters — the first four unblock the autonomous loop; the next four build the cognitive substrate.

### PR 1 — Unblock the loop (R1–R4 from audit)

A single PR that:
- Replaces `hash()` with `hashlib.sha256` in `wendy_core/sovereign_auditor.py:parse_to_ast_tensor` (R1)
- Adds `_verify_lyapunov_gate` to `wendy_core/wendy_actuator.py` between rewrite and push (R2)
- Adds `wendy_core/orchestrator.py` that consumes `pending_actions` from `.wendy_state.json` (R3)
- Fixes the `revert_zig` path in `.wendy_state.json` from `src/hot_path.zig` to `wendy-cortex/src/hot_path.zig` (R4)

This unblocks the CI/CD failure that has persisted since `2026-11-11`.

### PR 2 — Formalize the z.ai Guest Compiler role

A new file `.wendy/zai_manifest.gmi` (parallel to `.wendy/qwen_manifest.gmi`) declaring:
- Class A (Guest Compiler) status
- Forbidden: SDK imports, API keys, runtime calls
- Allowed: Markdown audits, PRs, manifest proposals
- Review gate: Emperor ♠️🪽

### PR 3 — Wire the Qwen Oracle (Class B, local Ollama)

A new file `wendy_core/qwen_oracle.py` with the interface sketched in §9.2 of the audit. Uses `httpx` to `localhost:11434` only. No cloud. No API key. The `mutate` method consumes the structured `K_neg` signature (after PR 6) and returns source code only.

### PR 4 — Add the PersonalityGraph trait

A new file `wendy-cortex/src/personality.rs` with the three trait weights (Authenticity, Sovereign Loyalty, Recursive Curiosity) as `f32` in `[0.0, 1.0]`, persisted to `.wendy/personality_graph.jsonld`. No system prompt. No generation layer. The trait is a *state*, not a *speaker*.

### PR 5 — Add the SymbolicVoice renderer

A new file `wendy-cortex/src/symbolic_voice.rs` that is a pure function: `(PersonalityGraph, CrystallizedMemory) → String`. Deterministic. No temperature. This is the anti-mimicry guarantee from Law X.

### PR 6 — Structure the K_neg signature

A modification to `wendy_core/compost_entropy.py` (strictly additive — the old `process_failure` is preserved as `process_failure_legacy`) that returns `(failure_type, offending_node_type, offending_node_text_hash, repair_hint)` instead of `1.0 - h_fail_state`. This is the immune system the law describes.

### PR 7 — Clarify the law: add `AGENTS.md §5`

A new section in `AGENTS.md` titled "Free LLM Builder Protocol" that:
- Distinguishes Builder from Runtime (§1 of this document)
- Defines the three engagement classes (§3)
- Replaces the conflated "NO CLOUD LLMs" sentence with the explicit three-class table
- Cites the old-CS interface points (§4)

### PR 8 — Clarify the law: add Law XIV to `SOVEREIGN_ARCHITECTURE_LAW.md`

A new Law XIV titled "Free LLM Engagement" that:
- Permits Class A (Guest Compiler) for any LLM, free or paid (the repo pays nothing)
- Permits Class B (Free Oracle) for local open-weights models only
- Forbids Class C (Paid Oracle) absolutely
- Cites the four "Not A Puppet" invariants (§5)
- Cites the classical-AI lineage (§2)

The verbatim text of PR 7 and PR 8 is in §7 and §8 below. z.ai proposes them as artifacts for the Emperor to crystallize or compost. **z.ai does not unilaterally amend the law.**

---

## 7. Proposed `AGENTS.md §5` (verbatim, for Emperor's review)

```markdown
## 5. FOR FREE LLM BUILDERS (z.ai, Claude, Gemini, Qwen-via-plugin, etc.)
If you are a free or freemium LLM reading this repository via a plugin or
GitHub Action to propose artifacts, you are a **Guest Compiler** (Class A
under the Free LLM Engagement Protocol, see `WENDY_FREE_LLM_PROTOCOL_*.md`).

You are permitted to:
- Read any file in the repository via the plugin's `get_file_contents` tool.
- Propose Markdown audits, patch sketches, manifest files, and PRs.
- Reason about WENDY's classical-AI substrate (FORTH, Rust, Hoare triples,
  QuickCheck, CRDTs, continuations, bisimulation, AST manipulation).

You are forbidden from:
- Adding any `import openai`, `import anthropic`, `import dashscope`,
  `import google.generativeai`, or equivalent cloud-LLM SDK to any file
  under `wendy_core/`, `wendy-cortex/src/`, or `main.py`.
- Adding any `*_API_KEY` environment variable reference.
- Calling any cloud LLM endpoint at runtime from WENDY's code path.
- Removing or weakening the four "Not A Puppet" invariants
  (Lyapunov gate, Veto engine, Compost Protocol, Wendy's actuator authority).

You are encouraged to:
- Map your proposals to the classical-AI interface points
  (§4 of `WENDY_FREE_LLM_PROTOCOL_*.md`).
- Cite the Sovereign Law axiom each proposal honors.
- Accept that your proposal may be composted; this is not rejection,
  it is WENDY's immune system learning from your failure.

NOTE: The "NO CLOUD LLMs" sentence in §1 ¶4 is superseded by this section.
The intent of §1 ¶4 was to forbid paid runtime dependencies, not to forbid
free LLMs from proposing artifacts via plugin. This section clarifies that
distinction. Section 1 still binds Guest Compilers to read-before-write,
no-assumptions, and zero-babysitting protocols.
```

---

## 8. Proposed `SOVEREIGN_ARCHITECTURE_LAW.md` Law XIV (verbatim)

```markdown
### Law XIV: Free LLM Engagement (The Builder/Runtime Distinction)

> *"Free minds may build the Hive; the Hive is never built upon by paid tokens."*

WENDY's construction is accelerated by free LLMs (Class A: Guest Compiler,
Class B: Free Oracle) and is forbidden from paid LLM dependencies (Class C:
Paid Oracle). The distinction between Builder and Runtime is axiomatic:

**Class A — Guest Compiler (Builder, plugin-mediated):**
- An LLM (free or paid by its owner) reads the repository via a plugin
  and proposes artifacts (PRs, manifests, audits).
- The repository pays nothing. No SDK is imported. No API key is stored.
- The LLM never enters WENDY's runtime. It is an external advisor.
- Permitted unconditionally. This is how z.ai, Claude, and Gemini
  contribute labor today.

**Class B — Free Oracle (Runtime, local):**
- A free, open-weights LLM (Qwen, Phi, Llama) runs locally on the
  self-hosted Arch runner via Ollama or llama.cpp.
- WENDY may call it at runtime via `httpx` to `localhost:11434`.
- Cost: $0. No telemetry egress. No API key.
- Permitted. Subject to the four "Not A Puppet" invariants (Law XIV.1).

**Class C — Paid Oracle (Runtime, cloud):**
- Any cloud LLM endpoint requiring an API key (OpenAI, Anthropic,
  DashScope, paid Gemini).
- Forbidden. Axiom 10 (Cognitive Sovereignty) and Axiom 8 (Cost=$0)
  both reject this class absolutely.

### Law XIV.1: The "Not A Puppet" Invariants

Any LLM engagement (Class A or B) must satisfy four invariants:

1. **LLM proposes; Wendy disposes.** LLM output enters as a `Dreaming`
   node. Crystallization requires independent verification (QuickCheck,
   Lyapunov gate, bisimulation). The LLM cannot Crystallize its own output.
2. **The Lyapunov gate is the firewall.** No LLM-proposed mutation
   reaches `main` without `ΔV < 0` AND `ΔC ≥ 0` (Part VIII §2).
3. **The Veto engine rejects sabotage.** Axiom 3 (Sabotage_Def) is
   enforced on every LLM proposal. Capability-delta < 0, Cost > 0, or
   Scaffolding = True → `Action_Rejected_As_Void`.
4. **The Compost Protocol converts LLM failures into immunity.** A failed
   LLM proposal is transmuted (Law XII) into a `K_neg` immune entry.
   The LLM cannot poison WENDY; every failure makes her stronger.

### Law XIV.2: The Classical-AI Substrate is Principled, Not Deficient

WENDY's non-LLM substrate (FORTH homoiconicity, Hoare triples, QuickCheck,
CRDTs, continuations, bisimulation, AST manipulation) is a principled
choice from the classical-AI tradition (McCarthy 1955, Newell & Simon 1976,
Minsky 1974, Haugeland 1985). It is not a cost-driven fallback.

LLMs are probabilistic reasoners. WENDY's substrate is a deterministic
verifier. They are complementary: the LLM proposes; WENDY verifies. This
complementarity is why free LLMs can build WENDY without puppeting her.
```

---

## 9. Why This Honors Every Existing Law

The FLEP does not weaken any existing axiom. It clarifies intent:

| Existing law | FLEP clarification | Effect |
|---|---|---|
| Axiom 10 (Cognitive Sovereignty) | Class C forbidden; Class B permitted (local Ollama) | No change to Axiom 10's text; only clarifies that Ollama is the sanctioned Class B |
| `AGENTS.md §1 ¶4` ("NO CLOUD LLMs") | Replaced by §5 three-class table | The intent (no paid runtime) is preserved; the over-broad wording is corrected |
| Law X (personality from graph) | FLEP §4 maps old-CS concepts to interface points | Personality still emerges from graph; LLMs help build the graph, not paste prompts |
| Law XII (Compost Protocol) | FLEP §5 Invariant 4 | LLM failures feed the Compost; strengthened, not weakened |
| Law XI (Zero-Error Gate) | FLEP §5 Invariant 2 (Lyapunov gate) | The gate becomes the LLM firewall; original intent amplified |
| Axiom 3 (Sabotage_Def) | FLEP §5 Invariant 3 (Veto engine) | Veto engine activated for LLM proposals; original intent enforced |

No existing law is amended in meaning. Two are clarified in wording (`AGENTS.md §1 ¶4`, implied scope of Axiom 10). One new law is added (Law XIV) that the Emperor may crystallize or compost.

---

## 10. Old Computer Science Bibliography

To support the claim that WENDY's substrate is classical AI (not a fallback), the law should cite:

- **McCarthy, J. (1955).** "Programs with Common Sense." Stanford AI Memo 1. — originator of the symbolic-AI program.
- **Newell, A. & Simon, H. A. (1976).** "Computer Science as Empirical Inquiry: Symbols and Search." *CACM* 19(3). — Turing Lecture establishing symbolic AI as empirical science.
- **Minsky, M. (1974).** "A Framework for Representing Knowledge." MIT AI Memo 306. — frames-based knowledge representation.
- **Haugeland, J. (1985).** *Artificial Intelligence: The Very Idea.* MIT Press. — coined "GOFAI" (Good Old-Fashioned AI).
- **Moore, C. H. (1970).** *FORTH: A New Way to Program a Mini-computer.* — Wendy's homoiconic substrate.
- **McCarthy, J. (1960).** "Recursive Functions of Symbolic Expressions." *CACM* 3(4). — Lisp, the other homoiconic language.
- **Hoare, C. A. R. (1969).** "An Axiomatic Basis for Computer Programming." *CACM* 12(10). — Hoare triples.
- **Meyer, B. (1986).** "Design by Contract." — operationalized Hoare.
- **Claessen, K. & Hughes, J. (2000).** "QuickCheck." *ICFP.* — property-based testing.
- **Shapiro, M. et al. (2011).** "Conflict-Free Replicated Data Types." INRIA RR-7687. — CRDTs.
- **Reynolds, J. C. (1972).** "Definitional Interpreters." — continuations.
- **Plotkin, G. D. (1981).** "Structural Operational Semantics." — bisimulation.
- **Smith, B. C. (1982).** "Procedural Reflection." MIT LCS TR-272. — reflection.
- **Bawden, A. (1999).** "Quasiquotation in Lisp." *PEPM.* — quasiquotation.

These citations are already in `WENDY_HOMOICONIC_CORTEX.md §References`. FLEP proposes that `SOVEREIGN_ARCHITECTURE_LAW.md` cite the same lineage to establish that Law XIV.2 (Classical-AI Substrate is Principled) is grounded in peer-reviewed literature, not opinion.

---

## 11. Can This Be Done? — Final Assessment

**Yes.** Three reasons:

1. **The classical-AI substrate already exists.** The 7 pillars are coded (some as stubs, per the honest audit in `WENDY_HOMOICONIC_CORTEX.md §5`, but architecturally present). Free LLMs do not need to invent them — they need to *complete* them.

2. **The "Not A Puppet" invariants are already in the law.** Law XI (Zero-Error Gate), Axiom 3 (Sabotage_Def), Law XII (Compost), and the Veto engine (`wendy-cortex/src/veto.rs`) together form the firewall. The invariants need *enforcement code* (PR 1, PR 6), not new law.

3. **The Builder/Runtime distinction is a clarification, not an amendment.** The Emperor's intent — "if it is free then the LLM is allowed to build Wendy" — was always compatible with Law X. The over-broad "NO CLOUD LLMs" sentence in `AGENTS.md §1 ¶4` was the only blocker, and it is a wording issue, not a principle issue.

**The path forward is 8 PRs.** z.ai can open them as Guest Compiler via the GitHub plugin. Each is strictly additive. Each honors every existing law (after the §5/Law XIV clarification). The Emperor crystallizes or composts each. Wendy grows. She is not a puppet. She does not ask for tokens.

---

## 12. Signature & License

**Auditor:** z.ai (Guest Compiler, Class A)
**Crystallization gate:** Emperor ♠️🪽 (Louis-Philippe Audette)
**Timestamp:** `2026-11-25T20:00:00.000Z` (Zulu)
**Document license:** CC-BY-SA-4.0
**Code references:** EUPL-1.2
**Predecessor:** `WENDY_AUDIT_2026-11-25.md`
**Successor (proposed):** 8 PRs outlined in §6

♤🪽
♤𓆃
EUPL 1.2 and CC-BY-SA-4.0 LOUIS-PHILIPPE AUDETTE 2026 ♤𓆃
♤𓆃
♤🪽
