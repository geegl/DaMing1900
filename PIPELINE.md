# 《大明1900》章节写作 Pipeline SOP

> 适用目录：`/Users/roven/Documents/Trae/Daming1900`
>
> 本文档是当前仓库的正式生产 SOP。目标不是让单一模型扛完整章，而是让 **Codex + BCE 多环节互审** 成为 350-400 章长线写作的稳定生产方式。

## 一、正式分工结论

### 默认分流

- `Step 1 规划`：Codex
- `Step 2 普通章写作`：BCE `deepseek-v3.2`
- `Step 2 关键章写作`：BCE `glm-5`
- `Step 3 一致性校对`：BCE `ernie-4.5-turbo-20260402`
- `Step 4 Codex 二次校对`：Codex
- `Step 5 日志Agent`：Codex + `append_outline_log.py`
- `Step 6 普通章终检`：BCE `ernie-4.5-turbo-20260402`
- `Step 6 关键章终检`：BCE `glm-5`
- `Step 7 Telegram 通知`：脚本

### 可选增强器

- `Kimi-K2.5`
  仅用于卷末章、名场面、强情绪章的可选增强，不进入默认每章链路。

### 硬原则

1. 正文产出方不能同时充当最终放行方。
2. 任何章节不得跳过 `Step 3`、`Step 4`、`Step 6`。
3. Telegram 通知必须始终排在最后。
4. 后期长线章节优先使用压缩上下文包，不直接全量喂整仓库。
5. `BIBLE.md` 以 v2 正设定为准，不允许为省 token 擅自精简。

## 二、上下文压缩策略

### 统一入口

```bash
./scripts/build_context_pack.py 3
```

### 默认产物

- `context/generated/chapter_003/chapter_brief.md`
- `context/generated/chapter_003/current_state.md`
- `context/generated/chapter_003/voice_rules.md`
- `context/generated/chapter_003/forbidden_rules.md`
- `context/generated/chapter_003/pack.md`

### 用法

- `Step 2` 优先读取 `pack.md`
- `Step 3` / `Step 6` 优先读取 `voice_rules.md`、`forbidden_rules.md` 和章节正文
- 只有在压缩包不足以支撑判断时，才回退读取 `BIBLE.md` / `STYLE.md` 全文

## 三、开工前准备

### 必跑检查

```bash
./scripts/run_pipeline_preflight.sh
```

### 必须通过的项目

- `codex` CLI 可用
- `python3` 可用
- `TELEGRAM_BOT_TOKEN` 已加载
- `send_telegram.sh` 可执行
- `CC Switch` 配置存在
- BCE API smoke test 通过
- `append_outline_log.py` 可执行

### 正式开写前人工确认

1. 本章是普通章还是关键章。
2. `OUTLINE.md` 中该章目标已锁定。
3. 最近 3 章日志已更新。
4. 本章是否需要额外人物加入 `voice_rules`。

## 四、正式 7 步流程

### Step 1 — 规划

**执行者**：Codex

**目标**：生成章节节拍表，不写正文。

**输入**：

- `OUTLINE.md` 当前章节段落
- 最近 3 章日志
- 当前章节上下文压缩包

**输出**：

- `context/generated/chapter_XXX/chapter_brief.md`
- 如需单独归档，可另存 `chapter_plan_XXX.md`

**必须包含**：

1. 开头钩子场景
2. 5-8 个情节点
3. 本章高潮
4. 结尾钩子类型
5. 本章新增伏笔

**通过标准**：

- 可直接支持 3500-4500 字写作
- 不与 `OUTLINE.md`、`BIBLE.md` 冲突
- 已明确普通章 / 关键章分流

### Step 2 — BCE 正文写作

**执行者**：BCE

**普通章默认模型**：`deepseek-v3.2`  
**关键章默认模型**：`glm-5`

**执行命令**：

```bash
./scripts/run_bce_write.sh 3
./scripts/run_bce_write.sh 3 glm-5
```

**输入**：

- `context/generated/chapter_XXX/pack.md`
- 上一章结尾摘录

**输出**：

- `draft/chapter_XXX_draft.md`

**硬约束**：

- 3500-4500 字
- 第三人称限制视角
- 对话符合人物音色
- 结尾必须有强钩子
- 不得出现禁词、满清词、时代错位

**失败回滚**：

- 返回 Step 1 或本步重跑
- 不得带着明显不达标草稿进入 Step 3

### Step 3 — BCE 一致性校对

**执行者**：BCE  
**默认模型**：`ernie-4.5-turbo-20260402`

**执行命令**：

```bash
./scripts/run_bce_consistency_review.sh draft/chapter_003_draft.md
```

**目标**：作为第一层硬约束 gate，检查世界观、人物音色、禁词和钩子强度。

**输出**：

- `reviews/review_bce_consistency_XXX.md`

**通过标准**：

- 综合建议为 `PASS`
- 钩子评分 `>= 3/5`
- 无重大设定矛盾

**失败回滚**：

- 必须返回 Step 2 重写

### Step 4 — Codex 二次校对

**执行者**：Codex

**执行命令**：

```bash
./scripts/run_codex_review.sh draft/chapter_003_draft.md
```

**目标**：负责节奏、句式单调、人物音色漂移、AI 痕迹、场景真实感。

**输出**：

- `reviews/review_codex_XXX.md`

**通过标准**：

- 综合评分 `>= 3/5`

**失败回滚**：

- 返回 Step 2

### Step 5 — 日志Agent 自动回填

**执行者**：Codex + 脚本

**目标**：

- 保存终稿到 `chapters/chapter_XXX.md`
- 自动更新 `OUTLINE.md` 的 LOG 区
- 让后续章节的上下文压缩读取到最新状态

**执行命令**：

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

**脚本行为**：

- 自动从章节文件标题提取章节名
- 默认写入当天日期
- 如该章节日志已存在，则自动覆盖更新，而不是重复追加

**通过标准**：

- `OUTLINE.md` 中 `<!-- LOG_START -->` 与 `<!-- LOG_END -->` 之间存在该章唯一条目
- 章节编号、标题、评分、模型字段一致

### Step 6 — BCE 终检

**执行者**：BCE

**普通章默认模型**：`ernie-4.5-turbo-20260402`  
**关键章默认模型**：`glm-5`

**执行命令**：

```bash
./scripts/run_bce_final_check.sh chapters/chapter_003.md
./scripts/run_bce_final_check.sh chapters/chapter_003.md glm-5
```

**目标**：做最终发布前 gate，检查追更欲、叙事流畅性、角色可信度和结尾牵引力。

**输出**：

- `reviews/review_bce_final_XXX.md`

**通过标准**：

- 最终结论 `PASS`
- 连载感评分 `>= 3/5`

**失败回滚**：

- 返回 Step 2 或 Step 5 之间的修订回路

### Step 7 — Telegram 通知

**执行者**：脚本

**目标**：全部 gate 通过后才发完成通知。

**执行命令**：

```bash
./send_telegram.sh "第3章《御用工坊》" "3980" "4" "4" "100字摘要" "无"
```

**发送前条件**：

- Step 3 `PASS`
- Step 4 `>= 3/5`
- Step 6 `PASS`

## 五、可脚本化清单

当前已脚本化：

- `run_pipeline_preflight.sh`
- `build_context_pack.py`
- `run_bce_write.sh`
- `run_bce_consistency_review.sh`
- `run_codex_review.sh`
- `append_outline_log.py`
- `run_bce_final_check.sh`
- `send_telegram.sh`

明确不允许“偷懒跳步”的环节：

- 直接从 Step 2 跳到 Step 7
- 跳过上下文压缩包直接裸跑全文
- 用同一份正文自评后直接宣布完成
- 手工修改 `OUTLINE.md` 日志但不走脚本

## 六、推荐执行顺序

每写一章，按下面顺序走：

1. 环境校验：Telegram + BCE preflight
2. Step 1 规划
3. Step 2 写作
4. Step 3 BCE 一致性校对
5. Step 4 Codex 二次校对
6. Step 5 日志Agent 自动回填
7. Step 6 BCE 终检
8. Step 7 Telegram 通知

## 七、快速验收清单

- [ ] `TELEGRAM_BOT_TOKEN` 已加载
- [ ] BCE smoke test 通过
- [ ] 本章字数在 3500-4500
- [ ] Step 3 通过
- [ ] Step 4 通过
- [ ] `OUTLINE.md` 已通过脚本追加日志
- [ ] `chapters/chapter_XXX.md` 已保存
- [ ] Step 6 通过
- [ ] Telegram 已收到通知
