#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

try:
    from edge_tts import Communicate, list_voices
except ImportError as exc:
    raise SystemExit(
        "edge-tts is not installed. Run ./tts once to auto-bootstrap dependencies."
    ) from exc


DEFAULT_VOICE = "en-US-AndrewMultilingualNeural"
FALLBACK_VOICE = "en-US-GuyNeural"


async def synthesize(
    text: str,
    output_path: Path,
    voice: str,
    rate: str,
    pitch: str,
    fallback_voice: str | None,
) -> str:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    async def attempt(chosen_voice: str, tries: int) -> None:
        last_error: Exception | None = None
        for _ in range(tries):
            try:
                await Communicate(
                    text=text,
                    voice=chosen_voice,
                    rate=rate,
                    pitch=pitch,
                ).save(str(output_path))
                return
            except Exception as exc:
                last_error = exc
                await asyncio.sleep(0.6)

        if last_error is not None:
            raise last_error

    try:
        await attempt(voice, tries=3)
        return voice
    except Exception:
        if fallback_voice and fallback_voice != voice:
            await attempt(fallback_voice, tries=3)
            return fallback_voice
        raise


async def print_voices() -> None:
    voices = await list_voices()
    voices = sorted(voices, key=lambda v: v.get("ShortName", ""))
    for voice in voices:
        short_name = voice.get("ShortName", "")
        locale = voice.get("Locale", "")
        gender = voice.get("Gender", "")
        friendly = voice.get("FriendlyName", "")
        print(f"{short_name}\t{locale}\t{gender}\t{friendly}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tts",
        description="Standalone edge-tts CLI wrapper (text and txt batch modes)",
    )
    source_group = parser.add_mutually_exclusive_group()
    source_group.add_argument("--text", help="Single text input")
    source_group.add_argument(
        "--txt",
        help="Path to txt file (one non-empty line per output clip)",
    )

    parser.add_argument("--out", help="Output .mp3 path (required with --text)")
    parser.add_argument(
        "--out-dir",
        help="Output directory (required with --txt)",
    )
    parser.add_argument(
        "--prefix",
        default="clip_",
        help="Batch filename prefix (default: clip_)",
    )
    parser.add_argument(
        "--start-index",
        type=int,
        default=1,
        help="Batch starting index (default: 1)",
    )
    parser.add_argument(
        "--voice",
        default=DEFAULT_VOICE,
        help=f"Voice short name (default: {DEFAULT_VOICE})",
    )
    parser.add_argument(
        "--fallback-voice",
        default=FALLBACK_VOICE,
        help=f"Fallback voice if primary fails (default: {FALLBACK_VOICE})",
    )
    parser.add_argument(
        "--rate",
        default="+0%",
        help="Speech rate, e.g. +0%%, +15%%, -10%%",
    )
    parser.add_argument(
        "--pitch",
        default="+0Hz",
        help="Pitch, e.g. +0Hz, +15Hz, -20Hz",
    )
    parser.add_argument(
        "--list-voices",
        action="store_true",
        help="List all available voices and exit",
    )
    return parser


async def run() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.list_voices:
        await print_voices()
        return 0

    if not args.text and not args.txt:
        parser.error("you must provide either --text or --txt (or use --list-voices)")

    if args.text:
        if not args.out:
            parser.error("--out is required when using --text")

        chosen = await synthesize(
            text=args.text,
            output_path=Path(args.out),
            voice=args.voice,
            rate=args.rate,
            pitch=args.pitch,
            fallback_voice=args.fallback_voice,
        )
        print(f"Generated: {args.out} (voice: {chosen})")
        return 0

    if not args.out_dir:
        parser.error("--out-dir is required when using --txt")

    txt_path = Path(args.txt)
    if not txt_path.exists() or not txt_path.is_file():
        raise SystemExit(f"Input txt not found: {txt_path}")

    lines = txt_path.read_text(encoding="utf-8").splitlines()
    output_dir = Path(args.out_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    idx = args.start_index
    generated = 0
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue

        output_file = output_dir / f"{args.prefix}{idx}.mp3"
        chosen = await synthesize(
            text=line,
            output_path=output_file,
            voice=args.voice,
            rate=args.rate,
            pitch=args.pitch,
            fallback_voice=args.fallback_voice,
        )
        print(f"Generated: {output_file} (voice: {chosen})")
        idx += 1
        generated += 1

    if generated == 0:
        print(f"Warning: no non-empty lines found in {txt_path}", file=sys.stderr)
    else:
        print(f"Done. Generated {generated} file(s).")

    return 0


def main() -> None:
    raise SystemExit(asyncio.run(run()))


if __name__ == "__main__":
    main()
