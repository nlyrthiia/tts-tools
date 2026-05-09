---
name: edge-tts-cli
description: Use when generating MP3/WAV voiceovers from plain text or txt files. Supports two engines — edge-tts (fast, free) and MiMo V2.5 TTS (preset voices, voice design, voice clone, singing, style control). Includes single-line synthesis, batch synthesis, voice listing, and tuning.
---

# edge-tts-cli

Generate speech audio with the bundled TTS wrapper scripts. Supports **edge-tts** and **MiMo V2.5 TTS** dual engines.

## Workflow

1. Determine engine:
   - Use `edge` (default) for quick, free TTS with Microsoft voices.
   - Use `mimo` for high-quality Chinese/English preset voices with emotion/style control.
   - Use `mimo-design` to generate a brand-new voice from text description.
   - Use `mimo-clone` to clone a voice from an audio sample.
2. Determine mode:
   - Use single mode when user provides one sentence/paragraph.
   - Use batch mode when user provides a `.txt` file (one line per clip).
3. Use the launcher script so dependencies auto-bootstrap.
4. Verify output file(s) exist after generation.

## Instructions

Run commands from this skill directory:

```bash
# show help
./scripts/tts --help

# list edge-tts voices
./scripts/tts --list-voices

# list MiMo preset voices
./scripts/tts --engine mimo --list-voices
```

### Edge-TTS (default engine)

```bash
# single text -> one mp3
./scripts/tts --text "Welcome to VexLand" --out ./out/1.mp3

# txt batch -> multiple mp3 files
./scripts/tts --txt ./voice_lines.txt --out-dir ./out --prefix line_ --start-index 1

# tune rate and pitch
./scripts/tts --text "Season one starts now" --out ./out/5.mp3 --rate +10% --pitch +5Hz
```

Default behavior:
- Primary voice: `en-US-AndrewMultilingualNeural`
- Fallback voice: `en-US-GuyNeural`
- Rate: `+0%`
- Pitch: `+0Hz`

### MiMo V2.5 TTS

Requires `MIMO_API_KEY` environment variable. Get your key at https://platform.xiaomimimo.com/

Preset voices: `冰糖` `茉莉` `苏打` `白桦` `Mia` `Chloe` `Milo` `Dean`

```bash
# preset voice
./scripts/tts --engine mimo --text "你好世界" --out ./out/hello.wav --mimo-voice 冰糖

# preset voice + style control
./scripts/tts --engine mimo --text "没关系，慢慢来" --out ./out/gentle.wav --mimo-voice 冰糖 --context "用温柔的语气，语速稍慢"

# voice design (generate new voice from description)
./scripts/tts --engine mimo-design --text "你好世界" --out ./out/design.wav --context "中年男性，嗓音低沉有磁性"

# voice clone
./scripts/tts --engine mimo-clone --text "你好世界" --out ./out/clone.wav --voice-file ./sample.mp3

# singing
./scripts/tts --engine mimo --text "(唱歌)原谅我这一生不羁放纵爱自由" --out ./out/sing.wav --mimo-voice 冰糖

# batch mode with MiMo
./scripts/tts --engine mimo --txt ./lines.txt --out-dir ./out --mimo-voice Mia
```

### Output format

```bash
# Override default format (edge=mp3, mimo=wav)
./scripts/tts --engine mimo --text "你好" --out ./out/hello.mp3 --mimo-voice 冰糖 --format mp3
```

## Notes

- Edge-TTS uses online Microsoft endpoints; MiMo uses `api.xiaomimimo.com`.
- If generation fails due to network/timeout, retry once before changing voice.
- In batch mode, blank lines and lines starting with `#` are skipped.
- MiMo TTS supports audio tags in text: `（开心）你好` or `(excited) Hello`.
