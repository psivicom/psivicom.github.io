# WENDY VOICE — Sovereign Speech-to-Text Organ

**Status:** Active | **Layer:** SENSORY | **RFC:** 1001 | **Policy:** NO_CLOUD_LLM

Wendy's ears. A voice note goes in, a transcript comes out — transcribed
entirely on local hardware. The audio never leaves the machine. No paid
cloud LLM APIs, no keys, no metering. WENDY WILL NOT ASK DO YOU HAVE
MONEY, SHE IS NOT A COKE MACHINE — and now she listens for free too.

---

## 1. Why This Organ Exists

Voice memos are the fastest way to capture field observations at the
apiary — hive condition, forage sightings, experiment ideas — but they
are locked inside opaque audio files that no mesh organ can read. The
Voice Organ converts speech into the platform's native currencies: plain
text for humans, RFC 1002 PSVC vectors for the bus. It closes the loop
between the iPhone in your pocket and the cognitive organs in `src/agents/`.

The design principle is sovereignty first: inference runs on your CPU via
faster-whisper (CTranslate2, int8-quantized). The only network touch is the
optional one-time download of open model weights from the Hugging Face hub
— a static file fetch, equivalent to a pip install. After that first fetch
the organ is fully offline. Fully air-gapped nodes can point
`WENDY_VOICE_MODEL` at a local model directory and never touch the network
at all.

## 2. Install

```bash
# 1. Python stack (faster-whisper + CTranslate2)
pip install -r requirements-voice.txt

# 2. One system dependency: ffmpeg (audio decoding)
brew install ffmpeg        # macOS
sudo apt install ffmpeg    # Debian/Ubuntu
```

That is the entire dependency surface. The organ deliberately decodes
audio through the ffmpeg CLI instead of the PyAV binding — ffmpeg handles
every voice-memo codec (AAC/M4A, MP3, WAV, FLAC, OGG, OPUS) without
version churn.

## 3. Usage

### Daily driver (CLI)

```bash
# Transcribe one voice note (iPhone .m4a works natively)
python scripts/voice_transcribe.py Audio-Oct-23.m4a

# Transcribe a whole folder of field recordings
python scripts/voice_transcribe.py ~/Recordings/october/

# Inbox mode: drop clips in data/voice_inbox/, then run
python scripts/voice_transcribe.py
# -> transcribes everything, archives processed clips to processed/

# Heavier local model for tricky audio (wind, bees, mumbling)
python scripts/voice_transcribe.py --model small hive_check.wav
```

### Organ API (RFC 1001)

```python
from src.agents.voice_agent import VoiceAgent

agent = VoiceAgent()                      # model: WENDY_VOICE_MODEL or 'base'
record = agent.transcribe_file("note.m4a")
print(record["text"])                     # the transcript
print(record["vector"]["content_hash"])   # PSVC vector hash for the bus
```

### Environment overrides

| Variable | Default | Purpose |
|---|---|---|
| `WENDY_VOICE_MODEL` | `base` | Model size (`tiny`/`base`/`small`/`medium`/`large-v3`) or local model directory |
| `WENDY_VOICE_INBOX` | `data/voice_inbox` | Where inbox mode listens |
| `WENDY_VOICE_OUT` | `reports/voice_transcripts` | Where transcripts are sealed |

## 4. What It Emits (Data Bus Contract)

Per clip, three artifacts share one stem in `reports/voice_transcripts/`:

| File | Track | Contents |
|---|---|---|
| `<stem>.txt` | Human | Plain transcript |
| `<stem>.json` | Bus | Full record: Zulu timestamps, language + confidence, segments, durations, source SHA-256, vector hash, sovereignty attestation |
| `<stem>.psvc` | RFC 1002 Track A | 4096-dim int8 transcript vector (deterministic text embedding, mesh-searchable) |

Example record header:

```json
{
  "created_at": "2026-10-24T01:17:03.659Z",
  "language": "en",
  "language_probability": 0.7411,
  "duration_seconds": 8.173,
  "transcription_seconds": 2.603,
  "sovereignty": { "local_inference": true, "policy": "NO_CLOUD_LLM" }
}
```

## 5. RFC 1001 Compliance

- **Layer:** `SENSORY` — external input scanning, sibling to the Pilot Agent.
- **Identity:** `_verify_identity()` validates the OIDC token when one is
  presented (Audience `psivi.com`); local runs without a token stay in
  sovereign mode.
- **Isolation:** imports no other agent; communicates only through Data Bus
  files (`data/voice_inbox/`, `reports/voice_transcripts/`,
  `reports/pico_containers/`).
- **Time:** every timestamp is ISO 8601 Zulu with millisecond precision.
- **Sealing:** `finalize()` seals the organ vector into
  `reports/pico_containers/` like every other organ; transcripts are sealed
  as PSVC containers via `src/core/psvc_reference.py`.
- **Language:** auto-detection by default (Whisper handles 90+ languages);
  pin with `--language en` / `--language fr` when you want to force it.

## 6. Model Selection

| Model | Size | Character | Use when |
|---|---|---|---|
| `tiny` | ~75 MB | Fastest, realtime | Quick commands, powerful machine |
| `base` | ~142 MB | Best speed/accuracy balance | **Default.** Daily voice notes |
| `small` | ~466 MB | Markedly better | Noisy field audio, accents |
| `medium` | ~1.5 GB | Best CPU accuracy | Important recordings, patience |

CPU inference is fast: a 30-second memo transcribes in a few seconds with
`base`. Every model runs int8-quantized via CTranslate2 — the same
quantization discipline as the PSVC Track A mesh format.

## 7. Tests

```bash
python -m pytest tests/test_voice_agent.py -v
```

Seven tests cover the RFC 1001 contract, Zulu timestamp format, PSVC
roundtrip determinism, the voice-memo extension whitelist, ffmpeg
decoding, and a full pipeline pass (auto-skipped where faster-whisper or
ffmpeg is absent).

## 8. Roadmap

- `voice-agent.yml`: optional GitHub Actions workflow so volunteer runners
  can transcribe sealed audio containers from `mesh/inbox`.
- TTS counterpart (Wendy's voice) as a MOTOR-layer organ.
- Streaming microphone capture on the Raspberry Pi apiary node.
