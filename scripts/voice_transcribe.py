# scripts/voice_transcribe.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
WENDY VOICE CLI - daily driver for sovereign speech-to-text.

Usage (from repository root):

  # Transcribe one voice note (iPhone .m4a works natively)
  python scripts/voice_transcribe.py Audio-Oct-23.m4a

  # Transcribe several files
  python scripts/voice_transcribe.py a.m4a b.wav c.mp3

  # Inbox mode: process everything in data/voice_inbox/, then archive
  python scripts/voice_transcribe.py

  # Pick a different local model (tiny|base|small|medium|large-v3 or a path)
  python scripts/voice_transcribe.py --model small field_recording.wav

Outputs per clip, written to reports/voice_transcripts/:
  <stem>.txt    plain transcript (human)
  <stem>.json   full record: language, segments, timings, hash (bus)
  <stem>.psvc   RFC 1002 Track A transcript vector (mesh)

Everything runs locally. No paid cloud LLM APIs are ever contacted.
"""

import argparse
import logging
import sys
from pathlib import Path

# Bootstrap: run from any directory, always import the repo's src package.
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.agents.voice_agent import (  # noqa: E402
    AUDIO_EXTENSIONS, VoiceAgent, zulu_now,
)

logger = logging.getLogger("VOICE_CLI")


def find_audio(targets):
    """Expand positional args (files or directories) into a clip list."""
    clips = []
    for t in targets:
        p = Path(t)
        if p.is_dir():
            clips.extend(
                sorted(f for f in p.iterdir()
                       if f.is_file() and f.suffix.lower() in AUDIO_EXTENSIONS)
            )
        elif p.is_file():
            clips.append(p)
        else:
            logger.warning("⚠️  Skipping missing path: %s", p)
    return clips


def run_inbox(agent: VoiceAgent, keep: bool):
    """Process every audio file in the inbox, then archive processed clips."""
    inbox = agent.inbox
    inbox.mkdir(parents=True, exist_ok=True)
    done_dir = inbox / "processed"
    clips = sorted(
        f for f in inbox.iterdir()
        if f.is_file() and f.suffix.lower() in AUDIO_EXTENSIONS
    )
    if not clips:
        logger.info("👂 Voice inbox is empty: %s", inbox)
        return 0

    failures = 0
    for clip in clips:
        try:
            record = agent.transcribe_file(clip)
            print(f"\n📝 {clip.name}  [{record['language']}]  "
                  f"({record['duration_seconds']:.1f}s audio)")
            print(f"   {record['text']}\n")
            if not keep:
                done_dir.mkdir(parents=True, exist_ok=True)
                clip.rename(done_dir / clip.name)
        except Exception as e:
            failures += 1
            logger.error("❌ %s: %s", clip.name, e)
    return failures


def main():
    parser = argparse.ArgumentParser(
        description="WENDY voice organ - local speech-to-text, zero cloud."
    )
    parser.add_argument(
        "audio", nargs="*", help="audio file(s) or folder(s); omit for inbox mode"
    )
    parser.add_argument(
        "--model", default=None,
        help="tiny | base | small | medium | large-v3 | local path "
             "(default: WENDY_VOICE_MODEL env or 'base')",
    )
    parser.add_argument(
        "--language", default=None,
        help="ISO code like 'en' or 'fr'; omit for auto-detection",
    )
    parser.add_argument(
        "--inbox", default=None,
        help="inbox folder for inbox mode (default: data/voice_inbox)",
    )
    parser.add_argument(
        "--out", default=None,
        help="output folder (default: reports/voice_transcripts)",
    )
    parser.add_argument(
        "--keep", action="store_true",
        help="inbox mode: do not move processed clips to processed/",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

    agent = VoiceAgent(
        model_size=args.model,
        language=args.language,
        inbox=Path(args.inbox) if args.inbox else None,
        output_dir=Path(args.out) if args.out else None,
    )

    clips = find_audio(args.audio)
    if clips:
        failures = 0
        for clip in clips:
            try:
                record = agent.transcribe_file(clip)
                print(f"\n📝 {clip.name}  [{record['language']}]  "
                      f"({record['duration_seconds']:.1f}s audio)")
                print(f"   {record['text']}\n")
            except Exception as e:
                failures += 1
                logger.error("❌ %s: %s", clip.name, e)
        sys.exit(1 if failures else 0)
    else:
        failures = run_inbox(agent, keep=args.keep)
        sys.exit(1 if failures else 0)


if __name__ == "__main__":
    print(f"🎙️  WENDY VOICE CLI @ {zulu_now()}")
    main()
