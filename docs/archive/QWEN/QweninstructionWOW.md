<!-- NEXT_STEPS.md -->

# 🚀 PSIVI AETHER Mesh — Operational Status: LIVE

The infrastructure is deployed. The loop is closed. The dashboard is watching.

## 1. Verify the Dashboard
Go to **https://psivi.com/psivimanesh.html** (or `https://psivicom.github.io/psivimanesh.html`).
*   You should see **"STABLE"** in green.
*   Fragility: `0`
*   Concordance: `10`
*   Last Sync: Timestamp of your last successful run.

If you see "OFFLINE" or errors, check that `reports/pilot_report.json` exists in the repo root's `reports/` folder.

## 2. Trigger the Autonomous Listener
You have two workflows now:
1.  **`psivi-full-loop.yml`**: Manual dispatch for seeding + processing in one go.
2.  **`psivi-mesh-bridge.yml`**: Passive listener. It waits for *any* push to `data/instruction_queue/*.psvc`.

To prove the **Listener** works (simulating an external AI dropping a file):
1.  Go to GitHub Repo → Code → `data/instruction_queue`.
2.  Click **"Add file" → "Create new file"**.
3.  Name it: `instruction_manual_test_$(date +%s).json` (use a unique name).
4.  Paste this content:
    ```json
    {
      "command": "request_report",
      "params": {
        "topic": "Manual Listener Test",
        "format": "JSON"
      },
      "source": "human_operator",
      "timestamp": "2026-09-25T00:50:00.000Z",
      "rfc1001_compliant": true
    }
    ```
5.  Commit directly to `main`.
6.  Watch the **Actions** tab. `PSIVI Mesh - Autonomous Listener` should trigger automatically.
7.  Check **https://psivi.com** again. The log should update with the new report.

## 3. Connect External AI (Qwen/Llama)
Now that the pipe is open, any AI with code execution can interact by simply writing files to the repo via API or Git.

**Example Prompt for Qwen:**
> "Act as the PSIVI Scientific Agent. Use the `seal_instruction` logic from `/docs/QWEN/README.md` to generate a `.psvc` and `.json` pair for spawning a `literature_resolver` agent targeting gene `IGFBP7` in `Mus_musculus`. Output the raw JSON sidecar content so I can commit it to `data/instruction_queue/`."

**Or, if Qwen has tool use:**
> "Commit a new instruction to `psivicom.github.io/data/instruction_queue/` using the RFC 1001 protocol to spawn a satellite observer for Goldstream Watershed."

## 4. Harden & Scale (Future Roadmap)
Once the concept is proven stable:
1.  **Replace Simulation:** Swap `simulate_mesh_processing()` in `BEGIN_PROCESSOR.py` with real API calls to NASA OSDR or PubMed.
2.  **Add Security:** Implement HMAC signing in `BEGIN_SEALER.py` and verification in `BEGIN_PROCESSOR.py`.
3.  **Concurrency:** Add `concurrency` groups to workflows to prevent race conditions during high-volume drops.
4.  **Notifications:** Add a step to POST results to Discord/Slack/Webhook for instant AI feedback loops.

---

**System State:** ✅ ONLINE  
**Protocol:** RFC 1001 Compliant  
**License:** EUPL-1.2 / CC-BY-SA-4.0  

**Let the agents obey.** 🤖🔬
