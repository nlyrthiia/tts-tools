# tts-cli

一个独立的命令行 TTS 工具，基于 `edge-tts`，用于把文本快速生成 `.mp3`。

这个项目是独立目录，可单独发布和使用。

## 功能

- `--text`：单条文本转语音
- `--txt`：从 `.txt` 批量生成（每行一条）
- `--list-voices`：列出可用音色
- 自动创建本地虚拟环境并安装依赖（首次运行）
- 主音色失败时自动回退，降低生成中断概率

## 依赖与安装方式

运行时依赖只有一个：`edge-tts`（见 `requirements.txt`）。

入口脚本是 `./tts`，行为如下：

- 首次运行自动创建 `.venv/`
- 自动安装 `requirements.txt` 里的依赖
- 后续直接调用 `tts_cli.py`

所以通常你不需要手动 `pip install`。

## 快速开始

```bash
cd /path/to/tts-cli

# 查看帮助
./tts --help

# 列出所有可用音色
./tts --list-voices
```

## 单条文本模式（--text）

```bash
./tts --text "Welcome to VexLand" --out ./out/1.mp3
```

必填参数：

- `--text` 文本内容
- `--out` 输出 mp3 路径

## 批量模式（--txt）

`txt` 文件规则：

- 每个非空行生成一个音频
- 空行会跳过
- 以 `#` 开头的行会跳过（可当注释行）

示例文件 `voice_lines.txt`：

```text
Welcome to VexLand.
This is season one.
# this line will be ignored
Start your adventure today.
```

生成命令：

```bash
./tts \
  --txt ./voice_lines.txt \
  --out-dir ./out \
  --prefix line_ \
  --start-index 1
```

输出文件会是：

- `line_1.mp3`
- `line_2.mp3`
- `line_3.mp3`

## 关键参数

- `--voice` 主音色，默认：`en-US-AndrewMultilingualNeural`
- `--fallback-voice` 回退音色，默认：`en-US-GuyNeural`
- `--rate` 语速，例如：`+0%`、`+10%`、`-10%`
- `--pitch` 音高，例如：`+0Hz`、`+10Hz`、`-20Hz`
- `--prefix` 批量文件名前缀，默认：`clip_`
- `--start-index` 批量起始序号，默认：`1`

## 推荐用法（更像真人）

- 男声优先：`en-US-AndrewMultilingualNeural`
- 如果你希望回退也尽量接近男声：用 `--fallback-voice en-US-GuyNeural`
- 通常先用默认 `--rate +0% --pitch +0Hz`，再按素材微调

示例：

```bash
./tts \
  --text "A brand new version has been launched." \
  --out ./out/5.mp3 \
  --voice en-US-AndrewMultilingualNeural \
  --fallback-voice en-US-GuyNeural \
  --rate +0% \
  --pitch +0Hz
```

## 隐私说明

- 该工具基于 `edge-tts` 在线服务，文本内容会发送到微软语音服务后返回音频结果。
- 本项目本身不保存 API Key，也不依赖本地数据库。
- 如需更高隐私控制，请避免输入敏感文本，或使用离线 TTS 方案。

## tiny 是什么？和这个项目有什么关系？

很多人会混淆 `tiny`。

- `tiny` 通常指的是 **Whisper tiny**，属于 **语音识别（STT）模型**
- 本项目是 **文本转语音（TTS）**，使用的是 `edge-tts`

也就是说：

- Whisper tiny：把音频转文字
- edge-tts：把文字转音频

本项目不需要 Whisper tiny 才能工作。

## 常见问题

- `Connection reset by peer` / 无法连接语音服务
  - 这是网络波动或远端服务问题，重试通常可恢复
  - 工具已经内置多次重试和回退音色

- 指定音色失败
  - 用 `./tts --list-voices` 先确认当前可用音色
  - 更换为可用音色，或设置 `--fallback-voice`

- 首次运行慢
  - 首次需要创建 `.venv` 和安装依赖，后续会快很多

## 一条命令检查工具是否正常

```bash
./tts --text "health check" --out /tmp/tts-health.mp3
```

如果成功生成 `/tmp/tts-health.mp3`，说明工具可用。
