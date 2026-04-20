# 大明1900

《大明1900》是一个面向番茄小说平台的长篇架空历史连载项目。仓库不仅保存正文，也保存世界观圣经、风格规则、平台标准、长线大纲，以及整套章节生产流水线。

当前正式工作方式不是“单模型单兵突进”，而是 **Codex + BCE 双系统协同**：

- `Codex` 负责规划、上下文压缩、二次校对、日志回填与流程编排
- `BCE` 负责正文主写、一致性校对与最终质检
- Telegram 只在全部质量 gate 通过后发送完成通知

## 仓库结构

```text
.
├── BIBLE.md
├── STYLE.md
├── FANQIE_STANDARDS.md
├── OUTLINE.md
├── PIPELINE.md
├── send_telegram.sh
├── chapters/
├── reviews/
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

### BCE 一致性校对

```bash
./scripts/run_bce_consistency_review.sh chapters/chapter_003_draft.md
```

### Codex 二次校对

```bash
./scripts/run_codex_review.sh chapters/chapter_003_draft.md
```

### BCE 终检

```bash
./scripts/run_bce_final_check.sh chapters/chapter_003_draft.md
./scripts/run_bce_final_check.sh chapters/chapter_003_draft.md glm-5
```

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

## 安全约束

- 不将任何 token、密钥或本地账号配置写入仓库
- `send_telegram.sh` 只读取环境变量 `TELEGRAM_BOT_TOKEN`
- BCE 访问配置从本机 `CC Switch` 当前 Claude-compatible provider 槽位读取，不在仓库硬编码
