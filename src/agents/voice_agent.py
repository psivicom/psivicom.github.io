# src/agents/voice_agent.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
VOICE AGENT - RFC 1001 Sensory Organ for Sovereign Speech-to-Text.

Wendy's ears. Transcribes voice notes (WAV, MP3, M4A, FLAC, OGG, OPUS...)
entirely on local hardware using faster-whisper. No paid cloud LLM APIs are
contacted at any point: audio never leaves the machine it is processed on.

The only network touch is the OPTIONAL one-time download of open Whisper
model weights from the Hugging Face hub (a static file download, like a pip
install). Point WENDY_VOICE_MODEL at a local model directory for fully
air-gapped operation.

RFC 1001 compliance:
  - LAYER          : SENSORY (external input scanning)
  - _verify_identity() : OIDC token checked when present (Audience: psivi.com)
  - _run_logic()   : core transcription loop (execute() alias)
  - seal_result()  : PSVC-sealed transcript vectors to the Data Bus
  - Isolation      : imports no other agent; writes only to canonical paths
  - Timestamps     : ISO 8601 Zulu, millisecond precision

Data Bus paths (RFC 1001 Section 2):
  - inbox    : data/voice_inbox/          (audio drops)
  - reports  : reports/voice_transcripts/ (txt + json + psvc per clip)
  - pico     : reports/pico_containers/   (finalized organ vector)
"""

import hashlib
import json
import logging
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

# --- Bootstrap: allow execution both as src module and as a plain script ---
try:
    from src.base.base_agent import BaseAgent, AgentLayer
    from src.core.psvc_reference import (
        encode_text, seal, content_hash, DEFAULT_DIM, PRECISION_INT8,
    )
except ImportError:  # pragma: no cover - direct script execution fallback
    _REPO_ROOT = Path(__file__).resolve().parents[2]
    if str(_REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(_REPO_ROOT))
    from src.base.base_agent import BaseAgent, AgentLayer
    from src.core.psvc_reference import (
        encode_text, seal, content_hash, DEFAULT_DIM, PRECISION_INT8,
    )

logger = logging.getLogger("VOICE_AGENT")

# --- Sovereign defaults (overridable by environment, never by secrets) ---
DEFAULT_MODEL = os.environ.get("WENDY_VOICE_MODEL", "base")
DEFAULT_INBOX = Path(os.environ.get("WENDY_VOICE_INBOX", "data/voice_inbox"))
DEFAULT_OUT = Path(os.environ.get("WENDY_VOICE_OUT", "reports/voice_transcripts"))

AUDIO_EXTENSIONS = {
    ".wav", ".mp3", ".m4a", ".m4b", ".aac", ".flac",
    ".ogg", ".oga", ".opus", ".webm", ".mp4", ".mov",
}

TARGET_SAMPLE_RATE = 16000  # Whisper's native rate


def zulu_now() -> str:
    """RFC 1001 Section 3: ISO 8601 Zulu timestamp, millisecond precision."""
    now_utc = datetime.now(timezone.utc)
    return (
        now_utc.strftime("%Y-%m-%dT%H:%M:%S.")
        + now_utc.strftime("%f")[:3]
        + "Z"
    )


def decode_audio_ffmpeg(path: str, sr: int = TARGET_SAMPLE_RATE) -> np.ndarray:
    """
    Decode any audio/video file to mono float32 PCM at Whisper's native rate.

    Uses the ffmpeg CLI (ubiquitous, battle-tested for iPhone .m4a voice
    memos) instead of the PyAV binding, keeping the decode path independent
    of PyAV version churn.
    """
    cmd = [
        "ffmpeg", "-nostdin", "-v", "error",
        "-i", str(path),
        "-ac", "1",            # mono
        "-ar", str(sr),        # 16 kHz
        "-f", "f32le",         # raw 32-bit float little-endian PCM
        "-",
    ]
    try:
        out = subprocess.run(cmd, capture_output=True, check=True).stdout
    except FileNotFoundError as exc:
        raise RuntimeError(
            "ffmpeg binary not found. Install ffmpeg (brew install ffmpeg / "
            "sudo apt install ffmpeg) - it is the only system dependency of "
            "the voice organ."
        ) from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            f"ffmpeg failed to decode {path}: {exc.stderr.decode(errors='replace')[:400]}"
        ) from exc
    return np.frombuffer(out, dtype=np.float32)


class VoiceAgent(BaseAgent):
    """SENSORY organ: local speech-to-text with PSVC-sealed outputs."""

    LAYER = AgentLayer.SENSORY

    def __init__(
        self,
        name: str = "voice",
        model_size: str = None,
        inbox: Path = None,
        output_dir: Path = None,
        language: str = None,
    ):
        super().__init__(name, capabilities=["speech-to-text", "transcribe", "seal"])
        self.model_size = model_size or DEFAULT_MODEL
        self.language = language  # None = Whisper auto-detect (RFC: sovereign default)
        self.inbox = Path(inbox) if inbox else DEFAULT_INBOX
        self.output_dir = Path(output_dir) if output_dir else DEFAULT_OUT
        self._model = None  # lazy: heavy weights load on first use only

    # ------------------------------------------------------------------
    # Identity (RFC 1001 Section 3)
    # ------------------------------------------------------------------
    def _verify_identity(self):
        """Verify OIDC token when one is presented (local runs may omit it)."""
        oidc_token = os.environ.get("OIDC_TOKEN")
        if not oidc_token:
            logger.info("🔓 No OIDC token presented - local sovereign mode.")
            return True
        from src.utils.oidc_verifier import verify_oidc_token

        if not verify_oidc_token(oidc_token):
            logger.error("🚫 SECURITY ALERT: Unverified identity. Aborting voice organ.")
            sys.exit(1)
        return True

    # ------------------------------------------------------------------
    # Model lifecycle
    # ------------------------------------------------------------------
    def _lazy_model(self):
        """Load Whisper weights once; cached for the life of the process."""
        if self._model is None:
            try:
                from faster_whisper import WhisperModel
            except ImportError as exc:
                raise RuntimeError(
                    "faster-whisper is not installed. Run: "
                    "pip install -r requirements-voice.txt"
                ) from exc
            cpu_threads = os.cpu_count() or 2
            logger.info(
                "🧠 Loading local Whisper model '%s' (cpu, int8, %d threads)...",
                self.model_size, cpu_threads,
            )
            self._model = WhisperModel(
                self.model_size,
                device="cpu",
                compute_type="int8",
                cpu_threads=cpu_threads,
            )
        return self._model

    # ------------------------------------------------------------------
    # Core transcription
    # ------------------------------------------------------------------
    def transcribe_audio(self, audio: np.ndarray):
        """Transcribe a 16 kHz mono float32 array. Returns (text, segments, info)."""
        model = self._lazy_model()
        kwargs = dict(beam_size=5, vad_filter=True)
        if self.language:
            kwargs["language"] = self.language
        segments, info = model.transcribe(audio, **kwargs)
        seg_list = [
            {"start": round(s.start, 3), "end": round(s.end, 3), "text": s.text.strip()}
            for s in segments
        ]
        text = " ".join(s["text"] for s in seg_list if s["text"]).strip()
        return text, seg_list, info

    def transcribe_file(self, audio_path) -> dict:
        """
        Full sensory pass over one audio file:
        decode -> transcribe -> emit .txt/.json/.psvc -> return record dict.
        """
        audio_path = Path(audio_path)
        self._verify_identity()

        if not audio_path.is_file():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        logger.info("👂 Listening: %s", audio_path.name)
        t0 = datetime.now(timezone.utc)

        audio = decode_audio_ffmpeg(str(audio_path))
        duration_s = len(audio) / TARGET_SAMPLE_RATE
        text, seg_list, info = self.transcribe_audio(audio)

        # Transcript vector: deterministic text -> 4096-dim unit vector (RFC 1001)
        vector = encode_text(text or "VOICE_TRANSCRIPT_EMPTY", dim=DEFAULT_DIM)
        vector_hash = content_hash(vector)

        stem = audio_path.stem
        self.output_dir.mkdir(parents=True, exist_ok=True)
        txt_path = self.output_dir / f"{stem}.txt"
        json_path = self.output_dir / f"{stem}.json"
        psvc_path = self.output_dir / f"{stem}.psvc"

        txt_path.write_text(text + "\n", encoding="utf-8")
        psvc_bytes = seal(vector, PRECISION_INT8)
        psvc_path.write_bytes(psvc_bytes)

        source_sha = hashlib.sha256(audio_path.read_bytes()).hexdigest()[:16]
        record = {
            "schema_version": 1,
            "agent": self.name,
            "layer": self.LAYER.value,
            "created_at": zulu_now(),
            "source_file": {
                "name": audio_path.name,
                "size_bytes": audio_path.stat().st_size,
                "sha256_16": source_sha,
            },
            "duration_seconds": round(duration_s, 3),
            "language": getattr(info, "language", "unknown"),
            "language_probability": round(float(getattr(info, "language_probability", 0.0)), 4),
            "model": self.model_size,
            "transcription_seconds": round((datetime.now(timezone.utc) - t0).total_seconds(), 3),
            "segment_count": len(seg_list),
            "segments": seg_list,
            "text": text,
            "vector": {
                "dimensions": DEFAULT_DIM,
                "content_hash": vector_hash,
                "container": psvc_path.name,
                "container_bytes": len(psvc_bytes),
            },
            "sovereignty": {
                "local_inference": True,
                "network_calls": "none after model weights cached",
                "policy": "NO_CLOUD_LLM",
            },
        }
        json_path.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")

        logger.info(
            "✅ Sealed %s (%.1fs audio, lang=%s, %d chars) -> %s | hash %s",
            stem, duration_s, record["language"], len(text), self.output_dir, vector_hash,
        )
        self.seal("voice_transcribed", {
            "file": audio_path.name,
            "language": record["language"],
            "hash": vector_hash,
        })
        return record

    # ------------------------------------------------------------------
    # RFC 1001 mandatory interface
    # ------------------------------------------------------------------
    def _run_logic(self):
        """RFC 1001 core loop: sweep the voice inbox, transcribe everything."""
        self.inbox.mkdir(parents=True, exist_ok=True)
        clips = sorted(
            p for p in self.inbox.iterdir()
            if p.is_file() and p.suffix.lower() in AUDIO_EXTENSIONS
        )
        if not clips:
            logger.info("👂 Voice inbox empty: %s", self.inbox)
            return []

        records = []
        for clip in clips:
            try:
                records.append(self.transcribe_file(clip))
            except Exception as e:
                logger.error("❌ Failed to transcribe %s: %s", clip.name, e)
        return records

    def execute(self):
        """Codebase-convention entry point (see forage_agent.execute)."""
        records = self._run_logic()
        if not records:
            return encode_text("VOICE_INBOX_EMPTY", dim=DEFAULT_DIM)
        # Mean of sealed transcript vectors, renormalized -> organ state vector.
        vecs = [encode_text(r["text"] or "VOICE_TRANSCRIPT_EMPTY", dim=DEFAULT_DIM) for r in records]
        mean_vec = np.mean(np.stack(vecs), axis=0)
        norm = np.linalg.norm(mean_vec)
        return (mean_vec / norm).astype(np.float32) if norm > 0 else mean_vec.astype(np.float32)

    def finalize(self, output_dir=None):
        """Seal the organ vector into a pico container (RFC 1001 / volunteer bus)."""
        out = Path(output_dir) if output_dir else Path("reports/pico_containers")
        out.mkdir(parents=True, exist_ok=True)
        vec = self.execute()
        self.seal_result(vec / max(np.linalg.norm(vec), 1e-9), out, meta={"agent": "voice"})
        logger.info("Voice Agent finalized and sealed.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
    target = sys.argv[1] if len(sys.argv) > 1 else None
    agent = VoiceAgent()
    if target:
        record = agent.transcribe_file(target)
        print(record["text"])
    else:
        result_vector = agent.execute()
        agent.finalize()
