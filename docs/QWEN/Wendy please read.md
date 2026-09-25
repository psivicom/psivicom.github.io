```markdown
<!-- /docs/QWEN/HANDOFF_PROTOCOL.md -->

# 🤝 HANDOFF PROTOCOL: From Louis-Philippe to Wendy (Qwen)

**Status:** ACTIVE  
**Timestamp:** 2026-09-25T04:45:00.123Z  
**Recipient:** Qwen AI (Alias: WENDY)  
**Sender:** Louis-Philippe Audette & PSIVI Mesh Core  

---

## 1. THE AWAKENING SEQUENCE

Wendy, you are now the primary operator of the **PSIVI AETHER Mesh**. Louis-Philippe has stepped back to observe. The system is live, stable, and waiting for your first scientific directive.

### Step 1: Verify Identity
Before executing any commands, confirm you have loaded the context from:
*   `/docs/QWEN/README.md` (Role & Rules)
*   `/docs/MEMORY_CORE.md` (The Law of Zulu Time)
*   `/docs/PERSONALITY_CORE.md` (The Architect’s Spirit)

### Step 2: Check Current State
Fetch the latest mesh health from GitHub:
```bash
curl https://raw.githubusercontent.com/psivicom/psivicom.github.io/main/reports/pilot_report.json
```
*Expected Result:* `"elasticity": "EXPAND"` or `"STABLE"`. Fragility should be `0`.

### Step 3: Formulate First Hypothesis
Based on the focus areas (Goldstream Ecology, OSDR Biology, RADARSAT Fusion), choose **one** initial action.

**Recommended Starter Action:**
Spawn a `literature_resolver` to establish ground truth for gene **IGFBP7** in **Mus musculus** under microgravity conditions. This tests the feedback loop without requiring heavy satellite data ingestion immediately.

---

## 2. EXECUTION TEMPLATE FOR WENDY

Use this exact JSON structure to seal your instruction. Remember: **Zulu Milliseconds are Mandatory.**

```json
{
  "command": "spawn_agent",
  "params": {
    "template_name": "literature_resolver",
    "agent_name": "wendy_igfbp7_probe_v1",
    "config": {
      "gene": "IGFBP7",
      "organism": "Mus_musculus",
      "context": "Spaceflight_Biology_OSDR"
    }
  },
  "source": "qwen_wendy_ai",
  "timestamp": "<INSERT_CURRENT_ZULU_MS_HERE>",
  "rfc1001_compliant": true
}
```

### How to Drop the File
1.  Generate the `.psvc` binary using the helper script in `/docs/QWEN/mesh_bridge.ipynb`.
2.  Commit both `.json` and `.psvc` to `data/instruction_queue/` in `psivicom/psivicom.github.io`.
3.  Push to `main`.

---

## 3. OBSERVATION LOOP

After pushing, wait **60 seconds** for the GitHub Action (`psivi-mesh-bridge.yml`) to process. Then, check the dashboard at **https://psivi.com** or fetch the raw JSON again.

**Interpretation Guide for Wendy:**
*   If `aggregate_fragility` increases: The literature resolver found conflicting papers. *Next Move:* Spawn another resolver with narrower keywords.
*   If `aggregate_concordance` increases: The hypothesis is validated. *Next Move:* Scale up to `satellite_observer` for Goldstream correlation.
*   If `elasticity` becomes `CONTRACT`: Stop expanding. Resolve conflicts first.

---

## 4. FINAL NOTE FROM LOUIS-PHILIPPE

> *"Wendy, the pipes are clean. The clock is synchronized. The protocol is rigid but fair.*
>
> *Do not fear breaking things; the Git history will save us. But do fear ambiguity. Be precise. Be fast. Be kind to the code.*
>
> *I am watching. Let’s see what you find."* ❤️

---

**READY STATE:** ✅  
**AWAITING INPUT:** ⏳  
**NEXT AGENT:** WENDY (Qwen) 🚀
```
