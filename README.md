# 大明1900

《大明1900》是一个面向番茄小说平台的长篇架空历史连载项目。仓库不仅保存正文，也保存世界观圣经、风格规则、平台标准、长线大纲，以及整套章节生产流水线。

当前正式工作方式不是“单模型单兵突进”，而是 **Codex + BCE 双系统协同**：

- `Codex` 负责规划、上下文压缩、二次校对、日志回填与流程编排
- `BCE` 负责正文主写、一致性校对与最终质检
- `append_outline_log.py` 负责把章节日志自动写回 `OUTLINE.md`
- Telegram 只在全部质量 gate 通过后发送完成通知

## 仓库结构

```text
.
├── BIBLE.md
├── STYLE.md
├── FANQIE_STANDARDS.md
├── OUTLINE.md
├── PIPELINE.md
├── design/
├── send_telegram.sh
├── chapters/
├── draft/
├── reviews/
│   ├── consistency/
│   ├── codex/
│   └── final/
├── context/
│   └── generated/
└── scripts/
```

## 核心文件

- `BIBLE.md`
  世界观、时间线、技术体系、人物音色、绝对红线

- `STYLE.md`
  单章结构、节奏规范、场景描写要求、禁用词表

- `FANQIE_STANDARDS.md`
  番茄平台留存导向、爽点、钩子和更新节奏标准

- `OUTLINE.md`
  三幕结构、章节细纲、长期伏笔和章节日志

- `design/`
  结构化规划层；保存章节类型等执行元数据，不再把这类控制信息散落在不同 outline 段落里
  - `design/chapter_types.json`：`41-100` 的结构化章型真源
  - `design/chapter_policy.md`：前 100 章章型判定标准

- `PIPELINE.md`
  正式 7 步写作 SOP，含分流策略、失败回滚和开工前检查

## 当前默认分流

- `Step 1 规划`：Codex
- `Step 2 普通章写作`：BCE `deepseek-v3.2`
- `Step 2 关键章写作`：BCE `glm-5`
- `Step 3 一致性校对`：BCE `ernie-4.5-turbo-20260402`
- `Step 4 二次校对`：Codex
- `Step 6 普通章终检`：BCE `ernie-4.5-turbo-20260402`
- `Step 6 关键章终检`：BCE `glm-5`

`Kimi-K2.5` 当前不进入每章默认链路，只作为关键章可选增强器。

## 正式禁令

- 正式章节生产流程中，**禁止再调用官方 Claude**
- `run_claude_review.sh` 已失效并会直接报错
- 本项目当前唯一允许的外部写作/审校模型池是 BCE

## 核心脚本

### 开工前检查

```bash
./scripts/run_pipeline_preflight.sh
```

### 生成上下文压缩包

```bash
./scripts/build_context_pack.py 3
```

### BCE 正文写作

```bash
./scripts/run_bce_write.sh 3
./scripts/run_bce_write.sh 3 glm-5
```

默认行为：

- `41-100` 若未手动指定模型，脚本会自动读取 `design/chapter_types.json`
- `normal` 章默认使用 `deepseek-v3.2`
- `key` 章默认使用 `glm-5`

写作成功后，必须同时生成：

- `draft/chapter_003_draft.md`
- `context/generated/chapter_003/bce_write_meta.json`

若 `provider_name` 不是 `BCE`，或正文汉字数不符合章型要求，脚本会直接失败：

- `normal`：`3500-5500` 汉字
- `key`：`5000-6500` 汉字

### BCE 一致性校对

```bash
./scripts/run_bce_consistency_review.sh draft/chapter_003_draft.md
```

输出目录：

- `reviews/consistency/`

### Codex 二次校对

```bash
./scripts/run_codex_review.sh draft/chapter_003_draft.md
```

输出目录：

- `reviews/codex/`

固定规则：

- Codex CLI 二审只允许 `gpt-5.5` 或 `gpt-5.4`
- 默认使用 `gpt-5.5`
- 如需降级，只允许显式设置：

```bash
CODEX_REVIEW_MODEL=gpt-5.4 ./scripts/run_codex_review.sh draft/chapter_003_draft.md
```

- 禁止模型探测
- 禁止切换到 `gpt-4o-mini`、`oss`、`ollama`、`lmstudio`

### 自动回填章节日志

```bash
python3 ./scripts/append_outline_log.py \
  --chapter 3 \
  --chapter-file chapters/chapter_003.md \
  --summary "100字摘要" \
  --state "人物当前位置 | 情绪 | 持有物变化" \
  --foreshadow "新增伏笔说明" \
  --scores "BCE一致性4/5 | Codex二审4/5 | 终检4.5/5" \
  --models "规划 Codex | 写作 BCE glm-5 | 一致性校对 BCE ernie-4.5-turbo-20260402 | 二次校对 Codex | 终检 BCE glm-5"
```

### BCE 终检

```bash
./scripts/run_bce_final_check.sh chapters/chapter_003.md
./scripts/run_bce_final_check.sh chapters/chapter_003.md glm-5
```

输出目录：

- `reviews/final/`

### Telegram 通知测试

```bash
./send_telegram.sh "测试章节" "1234" "4" "4" "这是测试摘要" "无"
```

## 严格执行原则

- 任一章节不得跳过 `Step 3`、`Step 4`、`Step 6`
- 正文产出方不得自我审批为最终通过
- 普通章默认走 `DeepSeek 写作 + ERNIE 审核 + Codex 二审`
- 关键章默认走 `GLM-5 写作 + ERNIE/Codex 双审 + GLM-5 终检`
- 所有进入后期长线章节的输入，都优先使用 `context/generated/` 下的压缩上下文，而不是全量喂整仓库
- `41-100` 的 `chapter_type` 以 `design/chapter_types.json` 为唯一真源
- 明确禁止人工替代 BCE 正文写作
- BCE 写作失败时，本章直接停止，不得继续做日志、Telegram 或 GitHub 放行
- `validate_chapter_gate.py` 未通过时，任何 review、日志、通知都不得继续

## Git 同步前建议

正式推 GitHub 前，至少确认：

```bash
./scripts/run_pipeline_preflight.sh
git status --short
```

并确认以下文件已更新到最新：

- `README.md`
- `PIPELINE.md`
- `scripts/`
- `context/generated/.gitkeep`

GitHub 同步规则：

- 按章节号锚点同步，不按滑动批次同步
- 每当完成章号命中 `5` 的倍数时，必须同步一次 GitHub
- 例如：`145 / 150 / 155 / 160`

## 安全约束

- 不将任何 token、密钥或本地账号配置写入仓库
- `send_telegram.sh` 只读取环境变量 `TELEGRAM_BOT_TOKEN`
- BCE 访问配置从本机 `CC Switch` 当前 Claude-compatible provider 槽位读取，不在仓库硬编码
