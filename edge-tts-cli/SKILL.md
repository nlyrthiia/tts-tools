---
name: edge-tts-cli
description: Use when generating MP3 voiceovers from plain text or txt files via edge-tts, including single-line synthesis, batch synthesis, voice listing, and voice/rate/pitch tuning from CLI.
---

# edge-tts-cli

Generate speech audio with the bundled `edge-tts` wrapper scripts.

## Workflow

1. Determine mode:
- Use single mode when user provides one sentence/paragraph.
- Use batch mode when user provides a `.txt` file (one line per clip).
2. Use the launcher script so dependencies auto-bootstrap.
3. Prefer the default male voice unless user requests another voice.
4. Verify output file(s) exist after generation.

## Instructions

Run commands from this skill directory:

```bash
# show help
./scripts/tts --help

# list voices
./scripts/tts --list-voices

# single text -> one mp3
./scripts/tts --text "Welcome to VexLand" --out ./out/1.mp3

# txt batch -> multiple mp3 files
./scripts/tts --txt ./voice_lines.txt --out-dir ./out --prefix line_ --start-index 1
```

Default behavior:
- Primary voice: `en-US-AndrewMultilingualNeural`
- Fallback voice: `en-US-GuyNeural`
- Rate: `+0%`
- Pitch: `+0Hz`

Common tuning:

```bash
./scripts/tts --text "Season one starts now" --out ./out/5.mp3 --rate +10% --pitch +5Hz
```

## Notes

- This tool uses online edge-tts endpoints; input text is sent to Microsoft speech service.
- If generation fails due to network/timeout, retry once before changing voice.
- In batch mode, blank lines and lines starting with `#` are skipped.
