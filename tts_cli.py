#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import base64
import os
import sys
from pathlib import Path


def _load_dotenv() -> None:
    """Load .env file from the script directory into os.environ.

    Only sets variables that are not already present in the environment,
    so real env vars always take precedence.
    """
    env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.is_file():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


_load_dotenv()


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_VOICE = "en-US-AndrewMultilingualNeural"
FALLBACK_VOICE = "en-US-GuyNeural"

MIMO_PRESET_VOICES = [
    "mimo_default",
    "冰糖",
    "茉莉",
    "苏打",
    "白桦",
    "Mia",
    "Chloe",
    "Milo",
    "Dean",
]

MIMO_VOICES_TABLE = [
    ("mimo_default", "Auto", "Auto", "默认音色 (国内=冰糖, 海外=Mia)"),
    ("冰糖", "中文", "女性", "活泼少女"),
    ("茉莉", "中文", "女性", "知性女声"),
    ("苏打", "中文", "男性", "阳光少年"),
    ("白桦", "中文", "男性", "成熟男声"),
    ("Mia", "English", "Female", "Lively girl"),
    ("Chloe", "English", "Female", "Sweet Dreamy"),
    ("Milo", "English", "Male", "Sunny boy"),
    ("Dean", "English", "Male", "Steady Gentle"),
]

ENGINE_CHOICES = ["edge", "mimo", "mimo-design", "mimo-clone"]


# ---------------------------------------------------------------------------
# Edge-TTS helpers
# ---------------------------------------------------------------------------

async def edge_synthesize(
    text: str,
    output_path: Path,
    voice: str,
    rate: str,
    pitch: str,
    fallback_voice: str | None,
) -> str:
    """Synthesize speech using edge-tts with retry and fallback."""
    try:
        from edge_tts import Communicate
    except ImportError as exc:
        raise SystemExit(
            "edge-tts is not installed. Run ./tts once to auto-bootstrap dependencies."
        ) from exc

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


async def edge_print_voices() -> None:
    """List all available edge-tts voices."""
    try:
        from edge_tts import list_voices
    except ImportError as exc:
        raise SystemExit(
            "edge-tts is not installed. Run ./tts once to auto-bootstrap dependencies."
        ) from exc

    voices = await list_voices()
    voices = sorted(voices, key=lambda v: v.get("ShortName", ""))
    for voice in voices:
        short_name = voice.get("ShortName", "")
        locale = voice.get("Locale", "")
        gender = voice.get("Gender", "")
        friendly = voice.get("FriendlyName", "")
        print(f"{short_name}\t{locale}\t{gender}\t{friendly}")


# ---------------------------------------------------------------------------
# MiMo TTS helpers
# ---------------------------------------------------------------------------

def _build_mimo_client():
    """Create an OpenAI client for MiMo API."""
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise SystemExit(
            "openai is not installed. Run: pip install openai"
        ) from exc

    api_key = os.environ.get("MIMO_API_KEY")
    if not api_key:
        print("Error: MIMO_API_KEY is not set.", file=sys.stderr)
        print("Set it in .env file or environment variable.", file=sys.stderr)
        print("Get your API key at: https://platform.xiaomimimo.com/", file=sys.stderr)
        sys.exit(1)
    base_url = os.environ.get("MIMO_BASE_URL", "https://api.xiaomimimo.com/v1")
    return OpenAI(api_key=api_key, base_url=base_url)


def _encode_voice_file(file_path: str) -> str:
    """Encode a voice sample file to base64 data-URL for voice cloning."""
    path = Path(file_path)
    if not path.exists():
        raise SystemExit(f"Voice file not found: {file_path}")

    suffix = path.suffix.lower()
    mime_map = {".mp3": "audio/mpeg", ".wav": "audio/wav"}
    mime_type = mime_map.get(suffix)
    if not mime_type:
        raise SystemExit(f"Unsupported voice file format: {suffix}. Use mp3 or wav.")

    data = path.read_bytes()
    if len(data) > 10 * 1024 * 1024:
        raise SystemExit("Voice file too large (max 10 MB).")

    b64 = base64.b64encode(data).decode("utf-8")
    return f"data:{mime_type};base64,{b64}"


def mimo_synthesize(
    text: str,
    output_path: Path,
    engine: str,
    mimo_voice: str | None = None,
    context: str | None = None,
    voice_file: str | None = None,
    audio_format: str = "wav",
) -> str:
    """Synthesize speech using MiMo TTS API.

    Returns a description of the voice/engine used.
    """
    client = _build_mimo_client()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Build messages
    messages: list[dict] = []
    if context:
        messages.append({"role": "user", "content": context})
    messages.append({"role": "assistant", "content": text})

    # Build audio params & select model
    audio_params: dict = {"format": audio_format}

    if engine == "mimo":
        model = "mimo-v2.5-tts"
        audio_params["voice"] = mimo_voice
        label = f"mimo/{mimo_voice}"
    elif engine == "mimo-design":
        model = "mimo-v2.5-tts-voicedesign"
        label = "mimo-design"
    elif engine == "mimo-clone":
        model = "mimo-v2.5-tts-voiceclone"
        audio_params["voice"] = _encode_voice_file(voice_file)
        label = f"mimo-clone/{Path(voice_file).name}"
    else:
        raise SystemExit(f"Unknown MiMo engine: {engine}")

    # Call API
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        audio=audio_params,
    )

    message = completion.choices[0].message
    if message.audio is None or not getattr(message.audio, "data", None):
        raise SystemExit("MiMo API returned no audio data.")

    output_path.write_bytes(base64.b64decode(message.audio.data))
    return label


def mimo_print_voices() -> None:
    """Print MiMo preset voice table."""
    print("Voice\tLanguage\tGender\tStyle")
    print("-" * 50)
    for name, lang, gender, style in MIMO_VOICES_TABLE:
        print(f"{name}\t{lang}\t\t{gender}\t{style}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tts",
        description="Multi-engine TTS CLI — supports edge-tts and MiMo V2.5 TTS",
    )

    # Engine selection
    parser.add_argument(
        "--engine",
        choices=ENGINE_CHOICES,
        default="edge",
        help="TTS engine: edge (default), mimo, mimo-design, mimo-clone",
    )

    # Input source (mutually exclusive)
    source_group = parser.add_mutually_exclusive_group()
    source_group.add_argument("--text", help="Single text input")
    source_group.add_argument(
        "--txt",
        help="Path to txt file (one non-empty line per output clip)",
    )

    # Output
    parser.add_argument("--out", help="Output file path (required with --text)")
    parser.add_argument(
        "--out-dir",
        help="Output directory (required with --txt)",
    )
    parser.add_argument(
        "--format",
        choices=["mp3", "wav"],
        default=None,
        help="Output audio format. Default: mp3 for edge, wav for mimo",
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

    # Edge-TTS options
    edge_group = parser.add_argument_group("edge-tts options")
    edge_group.add_argument(
        "--voice",
        default=DEFAULT_VOICE,
        help=f"Edge-TTS voice short name (default: {DEFAULT_VOICE})",
    )
    edge_group.add_argument(
        "--fallback-voice",
        default=FALLBACK_VOICE,
        help=f"Fallback voice if primary fails (default: {FALLBACK_VOICE})",
    )
    edge_group.add_argument(
        "--rate",
        default="+0%",
        help="Speech rate, e.g. +0%%, +15%%, -10%%",
    )
    edge_group.add_argument(
        "--pitch",
        default="+0Hz",
        help="Pitch, e.g. +0Hz, +15Hz, -20Hz",
    )

    # MiMo TTS options
    mimo_group = parser.add_argument_group("MiMo TTS options")
    mimo_group.add_argument(
        "--mimo-voice",
        choices=MIMO_PRESET_VOICES,
        help="MiMo preset voice (required with --engine mimo)",
    )
    mimo_group.add_argument(
        "--context",
        default="",
        help="Natural language style control / voice description / director script",
    )
    mimo_group.add_argument(
        "--voice-file",
        help="Voice sample audio file for cloning (mp3/wav, max 10MB, required with --engine mimo-clone)",
    )

    # Common
    parser.add_argument(
        "--list-voices",
        action="store_true",
        help="List all available voices for the selected engine and exit",
    )

    return parser


def _resolve_format(args) -> str:
    """Determine audio format: user override > engine default."""
    if args.format:
        return args.format
    if args.engine.startswith("mimo"):
        return "wav"
    return "mp3"


def _validate_mimo_args(args, parser) -> None:
    """Validate MiMo-specific argument requirements."""
    if args.engine == "mimo" and not args.mimo_voice:
        parser.error("--mimo-voice is required when using --engine mimo")
    if args.engine == "mimo-design" and not args.context:
        parser.error("--context is required when using --engine mimo-design")
    if args.engine == "mimo-clone" and not args.voice_file:
        parser.error("--voice-file is required when using --engine mimo-clone")


async def run() -> int:
    parser = build_parser()
    args = parser.parse_args()

    is_mimo = args.engine.startswith("mimo")

    # --- list-voices ---
    if args.list_voices:
        if is_mimo:
            mimo_print_voices()
        else:
            await edge_print_voices()
        return 0

    # --- require input ---
    if not args.text and not args.txt:
        parser.error("you must provide either --text or --txt (or use --list-voices)")

    # --- validate MiMo args ---
    if is_mimo:
        _validate_mimo_args(args, parser)

    fmt = _resolve_format(args)

    # === Single text mode ===
    if args.text:
        if not args.out:
            parser.error("--out is required when using --text")

        output_path = Path(args.out)

        if is_mimo:
            label = mimo_synthesize(
                text=args.text,
                output_path=output_path,
                engine=args.engine,
                mimo_voice=args.mimo_voice,
                context=args.context,
                voice_file=args.voice_file,
                audio_format=fmt,
            )
            print(f"Generated: {output_path} (engine: {label})")
        else:
            chosen = await edge_synthesize(
                text=args.text,
                output_path=output_path,
                voice=args.voice,
                rate=args.rate,
                pitch=args.pitch,
                fallback_voice=args.fallback_voice,
            )
            print(f"Generated: {output_path} (voice: {chosen})")
        return 0

    # === Batch txt mode ===
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

        output_file = output_dir / f"{args.prefix}{idx}.{fmt}"

        if is_mimo:
            label = mimo_synthesize(
                text=line,
                output_path=output_file,
                engine=args.engine,
                mimo_voice=args.mimo_voice,
                context=args.context,
                voice_file=args.voice_file,
                audio_format=fmt,
            )
            print(f"Generated: {output_file} (engine: {label})")
        else:
            chosen = await edge_synthesize(
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
