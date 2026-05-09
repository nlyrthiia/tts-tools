# tts-cli

一个独立的命令行 TTS 工具，支持 **edge-tts** 和 **MiMo V2.5 TTS** 双引擎，用于把文本快速生成语音文件。

这个项目是独立目录，可单独发布和使用。

## 功能

- 双引擎支持：`edge-tts`（默认）和 `MiMo V2.5 TTS`
- `--text`：单条文本转语音
- `--txt`：从 `.txt` 批量生成（每行一条）
- `--list-voices`：列出可用音色
- `--format`：可选输出格式（mp3 / wav）
- `.env` 文件管理 API Key，避免密钥泄露
- 自动创建本地虚拟环境并安装依赖（首次运行）

### Edge-TTS 特性

- 主音色失败时自动回退，降低生成中断概率
- 支持语速、音高调节

### MiMo V2.5 TTS 特性

- **预置音色**（`--engine mimo`）：9 款精品中英文音色（含默认音色），支持唱歌
- **音色设计**（`--engine mimo-design`）：通过文本描述生成全新音色
- **音色克隆**（`--engine mimo-clone`）：提供音频样本复刻目标音色
- 自然语言风格控制：情绪、语气、语速、导演模式
- 音频标签控制：句内情绪切换、方言、角色扮演

> MiMo V2.5 TTS 官方文档：https://platform.xiaomimimo.com/docs/zh-CN/usage-guide/speech-synthesis-v2.5

## 依赖与安装方式

运行时依赖：`edge-tts` 和 `openai`（见 `requirements.txt`）。

入口脚本是 `./tts`，行为如下：

- 首次运行自动创建 `.venv/`
- 自动安装 `requirements.txt` 里的依赖
- 后续直接调用 `tts_cli.py`

所以通常你不需要手动 `pip install`。

## 配置

### .env 文件

项目使用 `.env` 文件管理配置，启动时自动加载。`.env` 已在 `.gitignore` 中，不会被提交到 git。

首次使用时，复制模板并填入你的密钥：

```bash
cp .env.example .env
```

然后编辑 `.env` 文件：

```env
# MiMo TTS API
MIMO_API_KEY=your-mimo-api-key-here
MIMO_BASE_URL=https://api.xiaomimimo.com/v1
```

| 变量 | 说明 | 必需 |
|---|---|---|
| `MIMO_API_KEY` | MiMo API 密钥 | 使用 MiMo 引擎时必需 |
| `MIMO_BASE_URL` | MiMo API 地址 | 可选，默认 `https://api.xiaomimimo.com/v1` |

API Key 获取地址：https://platform.xiaomimimo.com/

> **注意**：也可以通过环境变量直接设置（`export MIMO_API_KEY=xxx`），环境变量优先级高于 `.env` 文件。

## 快速开始

```bash
cd /path/to/tts-cli

# 查看帮助
./tts --help

# 列出 edge-tts 可用音色
./tts --list-voices

# 列出 MiMo 预置音色
./tts --engine mimo --list-voices
```

## 引擎选择（--engine）

| 引擎值 | 说明 | 输出默认格式 |
|---|---|---|
| `edge`（默认） | 微软 Edge TTS | mp3 |
| `mimo` | MiMo 预置音色 | wav |
| `mimo-design` | MiMo 音色设计（文本描述生成音色） | wav |
| `mimo-clone` | MiMo 音色克隆（音频样本复刻） | wav |

可通过 `--format mp3` 或 `--format wav` 覆盖默认格式。

---

## Edge-TTS 用法

### 单条文本模式（--text）

```bash
./tts --text "Welcome to VexLand" --out ./out/1.mp3
```

必填参数：

- `--text` 文本内容
- `--out` 输出文件路径

### 批量模式（--txt）

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

输出文件：`line_1.mp3`、`line_2.mp3`、`line_3.mp3`

### Edge-TTS 关键参数

| 参数 | 说明 | 默认值 |
|---|---|---|
| `--voice` | 主音色 | `en-US-AndrewMultilingualNeural` |
| `--fallback-voice` | 回退音色 | `en-US-GuyNeural` |
| `--rate` | 语速 | `+0%` |
| `--pitch` | 音高 | `+0Hz` |
| `--prefix` | 批量文件名前缀 | `clip_` |
| `--start-index` | 批量起始序号 | `1` |

### 推荐用法（更像真人）

```bash
./tts \
  --text "A brand new version has been launched." \
  --out ./out/5.mp3 \
  --voice en-US-AndrewMultilingualNeural \
  --fallback-voice en-US-GuyNeural \
  --rate +0% \
  --pitch +0Hz
```

---

## MiMo V2.5 TTS 用法

### 预置音色

| 音色名 | Voice ID | 语言 | 性别 | 风格 |
|---|---|---|---|---|
| MiMo-默认 | `mimo_default` | 自动 | 自动 | 默认音色（国内=冰糖，海外=Mia） |
| 冰糖 | `冰糖` | 中文 | 女性 | 活泼少女 |
| 茉莉 | `茉莉` | 中文 | 女性 | 知性女声 |
| 苏打 | `苏打` | 中文 | 男性 | 阳光少年 |
| 白桦 | `白桦` | 中文 | 男性 | 成熟男声 |
| Mia | `Mia` | English | Female | Lively girl |
| Chloe | `Chloe` | English | Female | Sweet Dreamy |
| Milo | `Milo` | English | Male | Sunny boy |
| Dean | `Dean` | English | Male | Steady Gentle |

### 基础用法（预置音色）

```bash
# 使用指定音色
./tts --engine mimo --text "你好，今天天气真不错。" --out ./out/hello.wav --mimo-voice 冰糖

# 使用默认音色（自动根据区域选择）
./tts --engine mimo --text "你好世界" --out ./out/hello.wav --mimo-voice mimo_default
```

### 自然语言风格控制（--context）

通过 `--context` 传入自然语言描述，让模型理解并生成对应风格的语音。支持多风格切换、多情绪混合、多粒度控制。

```bash
./tts --engine mimo \
  --text "没关系，慢慢来，我等你。" \
  --out ./out/gentle.wav \
  --mimo-voice 冰糖 \
  --context "用温柔的语气，语速稍慢"
```

**导演模式**——从角色、场景、指导三个维度全方位刻画：

```bash
./tts --engine mimo \
  --text "你们求我垂怜，求我降下甘霖洗净这浊世。可这世间的沉疴，唯有烈火能剔骨刮毒。" \
  --out ./out/director.wav \
  --mimo-voice 白桦 \
  --context "角色：曾是守护九天的神祇。场景：悬浮于崩塌的祭坛之上。指导：充分打开胸腔共鸣，声音如古钟般低沉。"
```

### 音频标签控制

在文本中直接用括号标记情绪和语气，支持全角 `（）`、半角 `()`、方括号 `[]`：

```bash
./tts --engine mimo \
  --text "（紧张，深呼吸）呼……冷静，冷静。不就是一个面试吗……（语速加快，碎碎念）自我介绍已经背了五十遍了。（小声）哎呀，领带歪没歪？" \
  --out ./out/interview.wav \
  --mimo-voice 冰糖
```

**常用标签参考：**

| 类别 | 标签示例 |
|---|---|
| 基础情绪 | `开心` `悲伤` `愤怒` `恐惧` `惊讶` `兴奋` `平静` |
| 复合情绪 | `怅然` `无奈` `愧疚` `释然` `忐忑` `动情` |
| 语调 | `温柔` `高冷` `活泼` `严肃` `慵懒` `俏皮` |
| 音色 | `磁性` `沙哑` `清亮` `空灵` `甜美` |
| 人设 | `夹子音` `御姐音` `正太音` `大叔音` `台湾腔` |
| 方言 | `东北话` `四川话` `河南话` `粤语` |
| 角色 | `孙悟空` `林黛玉` |
| 节奏 | `[停顿]` `[长停顿]` `[急促]` `[拖音]` `[语速加快]` |
| 情绪动作 | `[轻声]` `[低语]` `[叹气]` `[哽咽]` `[笑]` `[爽朗大笑]` |

英文标签示例：`(whispering)` `(sighs)` `(laughs)` `[pause]` `[emphasis]`

### 唱歌

必须在文本最开头添加 `(唱歌)` 标签（也支持 `sing`、`singing`）：

```bash
./tts --engine mimo \
  --text "(唱歌)原谅我这一生不羁放纵爱自由，也会怕有一天会跌倒，Oh no。背弃了理想，谁人都可以，哪会怕有一天只你共我。" \
  --out ./out/singing.wav \
  --mimo-voice 冰糖
```

> **注意**：歌词要完整，残缺歌词会导致跑调、效果差。

### 音色设计（--engine mimo-design）

通过自然语言描述从零生成全新音色，无需任何参考音频。适合游戏 NPC、动画角色、虚拟主播等场景。

```bash
./tts --engine mimo-design \
  --text "当最后一缕阳光消失在地平线之下，这片大地开始显露它真正的面貌。" \
  --out ./out/narrator.wav \
  --context "中年男性，说标准普通话，嗓音低沉有磁性，带有轻微的沙哑质感，像纪录片旁白解说员，沉稳而有感染力。"
```

**音色描述建议**（必写项）：

1. **身份锚点**：年龄段 + 性别
2. **声音质感**：气息走向、共鸣位置、音色底色
3. **语速节奏**：稳 / 快 / 慢
4. **情绪底色**：高亢 / 松弛 / 温软 / 克制

更多描述样例：

```
青年男性，电竞解说风格，语速极快且连贯，带明显气口和爆发性强调。
中年男性，法庭陈词风格，声线沉稳偏正式，吐字工整字字顿挫，情绪克制。
一位年迈的老先生，带北方口音，语速缓慢而沉稳，嗓音略带沙哑和沧桑感。
```

### 音色克隆（--engine mimo-clone）

提供一段音频样本（mp3/wav，≤10MB）即可复刻目标音色：

```bash
./tts --engine mimo-clone \
  --text "你好世界" \
  --out ./out/cloned.wav \
  --voice-file ./sample.mp3
```

音色克隆 + 导演模式：

```bash
./tts --engine mimo-clone \
  --text "你以为我是谁，也敢在这儿跟我耍横？我告诉你，站在我身后的那个人，说出来吓死你。" \
  --out ./out/clone_director.wav \
  --voice-file ./sample.mp3 \
  --context "用尖锐刻薄的嗓音，带着狐假虎威的得意感说话，在提到大人物时故意放慢语速并加重语气"
```

> **技巧**：可以先用 `mimo-design` 生成满意的音色，保存音频，再用 `mimo-clone` 复刻到其他文本。

### MiMo 批量模式

MiMo 引擎同样支持批量模式，规则与 Edge-TTS 相同（空行跳过、`#` 注释行跳过）：

```bash
./tts --engine mimo \
  --txt ./voice_lines.txt \
  --out-dir ./out \
  --mimo-voice Mia \
  --prefix line_ \
  --start-index 1
```

批量模式也支持 `--context` 风格控制，同一份 context 会应用到所有行：

```bash
./tts --engine mimo \
  --txt ./voice_lines.txt \
  --out-dir ./out \
  --mimo-voice 冰糖 \
  --context "用轻快活泼的语气"
```

### 指定输出格式

```bash
# MiMo 引擎输出 mp3（默认 wav）
./tts --engine mimo --text "你好" --out ./out/hello.mp3 --mimo-voice 冰糖 --format mp3

# Edge 引擎输出 wav（默认 mp3）
./tts --text "Hello" --out ./out/hello.wav --format wav
```

---

## 全部参数速览

| 参数 | 说明 | 适用引擎 |
|---|---|---|
| `--engine` | TTS 引擎选择 | 通用 |
| `--text` | 单条文本输入 | 通用 |
| `--txt` | 批量 txt 文件路径 | 通用 |
| `--out` | 输出文件路径（单条模式） | 通用 |
| `--out-dir` | 输出目录（批量模式） | 通用 |
| `--format` | 输出格式 mp3/wav | 通用 |
| `--prefix` | 批量文件名前缀 | 通用 |
| `--start-index` | 批量起始序号 | 通用 |
| `--list-voices` | 列出可用音色 | 通用 |
| `--voice` | Edge-TTS 音色名 | edge |
| `--fallback-voice` | Edge-TTS 回退音色 | edge |
| `--rate` | Edge-TTS 语速 | edge |
| `--pitch` | Edge-TTS 音高 | edge |
| `--mimo-voice` | MiMo 预置音色 | mimo |
| `--context` | 自然语言风格控制 / 音色描述 | mimo / mimo-design / mimo-clone |
| `--voice-file` | 音色克隆参考音频 | mimo-clone |

---

## 项目结构

```
tts-tools/
├── tts                  # Bash 入口脚本（自动管理 venv + 依赖）
├── tts_cli.py           # Python 核心逻辑（edge-tts + MiMo 双引擎）
├── requirements.txt     # 依赖：edge-tts, openai
├── .env                 # API Key 配置（不提交到 git）
├── .env.example         # .env 模板文件
├── .gitignore
├── README.md
└── edge-tts-cli/        # AI Skill 定义（供 AI 助手调用）
    ├── SKILL.md
    └── scripts/         # 脚本副本
```

## 隐私说明

- **Edge-TTS**：基于 `edge-tts` 在线服务，文本内容会发送到微软语音服务。
- **MiMo TTS**：文本内容会发送到小米 MiMo API 服务（`api.xiaomimimo.com`）。
- API Key 存储在本地 `.env` 文件中，已通过 `.gitignore` 排除，不会提交到版本控制。
- 如需更高隐私控制，请避免输入敏感文本，或使用离线 TTS 方案。

## 常见问题

### `Connection reset by peer` / 无法连接语音服务

网络波动或远端服务问题，重试通常可恢复。Edge-TTS 已内置多次重试和回退音色。

### 指定音色失败

- Edge-TTS：用 `./tts --list-voices` 先确认当前可用音色
- MiMo：用 `./tts --engine mimo --list-voices` 查看预置音色

### `MIMO_API_KEY is not set`

使用 MiMo 引擎前需配置密钥，两种方式任选：

```bash
# 方式一：编辑 .env 文件
cp .env.example .env
# 然后编辑 .env 填入你的 API Key

# 方式二：直接设置环境变量
export MIMO_API_KEY="your-key"
```

### MiMo API 返回 No audio data

- 检查 API Key 是否正确
- 检查文本是否为空
- MiMo TTS 目前限时免费，确认账户状态正常

### 首次运行慢

首次需要创建 `.venv` 和安装依赖，后续会快很多。

### tiny 是什么？和这个项目有什么关系？

- `tiny` 通常指的是 **Whisper tiny**，属于 **语音识别（STT）模型**
- 本项目是 **文本转语音（TTS）**，使用的是 `edge-tts` 和 `MiMo TTS`
- Whisper tiny：把音频转文字；本项目：把文字转音频

## 一条命令检查工具是否正常

```bash
# 检查 edge-tts
./tts --text "health check" --out /tmp/tts-health.mp3

# 检查 MiMo TTS（需要配置 MIMO_API_KEY）
./tts --engine mimo --text "健康检查" --out /tmp/mimo-health.wav --mimo-voice 冰糖
```

如果成功生成对应文件，说明工具可用。
