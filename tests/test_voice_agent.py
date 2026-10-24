# tests/test_voice_agent.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
RFC 1001 compliance tests for the Voice Organ.

Run from repository root:
    python -m pytest tests/test_voice_agent.py -v

The full speech-to-text pipeline test is skipped automatically when
faster-whisper or ffmpeg is not available on the machine.
"""

import os
import re
import sys
import wave
from pathlib import Path

import numpy as np
import pytest

# Bootstrap: load the repository's src package from repo root.
_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT))

from src.agents.voice_agent import (  # noqa: E402
    AUDIO_EXTENSIONS, VoiceAgent, decode_audio_ffmpeg, zulu_now,
)
from src.base.base_agent import AgentLayer, BaseAgent  # noqa: E402
from src.core.psvc_reference import (  # noqa: E402
    content_hash, encode_text, open_container, seal, validate_file,
    PRECISION_INT8, PRECISION_FLOAT32,
)

ZULU_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$")


# ---------------------------------------------------------------------------
# Contract tests (always run)
# ---------------------------------------------------------------------------
def test_agent_satisfies_rfc1001_contract():
    agent = VoiceAgent()
    assert isinstance(agent, BaseAgent)
    assert agent.LAYER == AgentLayer.SENSORY
    assert callable(agent._verify_identity)
    assert callable(agent._run_logic)
    assert callable(agent.seal_result)
    assert "speech-to-text" in agent.capabilities


def test_zulu_timestamp_has_millisecond_precision():
    stamp = zulu_now()
    assert ZULU_RE.match(stamp), f"Bad Zulu format: {stamp}"


def test_transcript_vector_roundtrip_is_deterministic():
    text = "The bees at the Goldstream apiary are active."
    vec = encode_text(text, dim=4096)
    assert vec.shape == (4096,)
    assert vec.dtype == np.float32
    h1 = content_hash(vec)

    # float32 track is lossless -> hash must survive the roundtrip
    restored = open_container(seal(vec, PRECISION_FLOAT32))
    assert content_hash(restored) == h1

    # int8 track (mesh default) is lossy by design -> bounded quantization error
    restored_i8 = open_container(seal(vec, PRECISION_INT8))
    max_err = float(np.max(np.abs(restored_i8 - vec)))
    assert max_err < 0.01


def test_audio_extension_whitelist_covers_voice_memos():
    for ext in (".m4a", ".wav", ".mp3", ".flac", ".ogg"):
        assert ext in AUDIO_EXTENSIONS


# ---------------------------------------------------------------------------
# ffmpeg decode test (skipped when ffmpeg is missing)
# ---------------------------------------------------------------------------
def _make_sine_wav(path: Path, seconds: float = 1.0, freq: int = 440, sr: int = 16000):
    """Write a tiny WAV using only the stdlib - no fixture files needed."""
    t = np.arange(int(sr * seconds), dtype=np.float32) / sr
    samples = (0.4 * np.sin(2 * np.pi * freq * t)).astype(np.float32)
    pcm16 = (samples * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm16.tobytes())
    return path


@pytest.fixture()
def sine_wav(tmp_path):
    return _make_sine_wav(tmp_path / "sine.wav")


def test_ffmpeg_available():
    try:
        decode_audio_ffmpeg  # import-level proof
        import subprocess
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
    except Exception:
        pytest.skip("ffmpeg not installed on this machine")


def test_decode_sine_wav_shape(sine_wav):
    audio = decode_audio_ffmpeg(str(sine_wav))
    assert audio.dtype == np.float32
    # 1.0 s at 16 kHz mono, allow decoder padding tolerance
    assert 15500 <= len(audio) <= 16500


# ---------------------------------------------------------------------------
# Full pipeline test (skipped without faster-whisper)
# ---------------------------------------------------------------------------
def test_full_pipeline(tmp_path, sine_wav):
    pytest.importorskip("faster_whisper")
    try:
        decode_audio_ffmpeg(str(sine_wav))
    except RuntimeError:
        pytest.skip("ffmpeg not installed on this machine")

    agent = VoiceAgent(model_size="tiny", output_dir=tmp_path / "out")
    record = agent.transcribe_file(sine_wav)

    out = tmp_path / "out"
    stem = sine_wav.stem
    assert (out / f"{stem}.txt").exists()
    assert (out / f"{stem}.json").exists()
    assert (out / f"{stem}.psvc").exists()

    # PSVC container must pass the repo's own validator
    meta = validate_file(str(out / f"{stem}.psvc"))
    assert meta["Magic"] == "PSVI"
    assert meta["Dimensions"] == 4096

    # JSON record must carry RFC 1001 Zulu time + sovereignty attestation
    import json
    data = json.loads((out / f"{stem}.json").read_text(encoding="utf-8"))
    assert ZULU_RE.match(data["created_at"])
    assert data["sovereignty"]["local_inference"] is True
    assert data["duration_seconds"] > 0.5
