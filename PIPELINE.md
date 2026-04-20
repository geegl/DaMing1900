# 《大明1900》章节写作 Pipeline SOP

> 适用目录：`/Users/roven/Documents/Trae/Daming1900`
>
> 本文档是当前仓库的正式生产 SOP。目标不是让单一模型“扛全场”，而是让 **Codex + BCE 多环节互审** 成为长期 350-400 章可持续的生产方式。

---

## 一、正式分工结论

### 默认分流

- `Step 1 规划`：Codex
- `Step 2 普通章写作`：BCE `deepseek-v3.2`
- `Step 2 关键章写作`：BCE `glm-5`
- `Step 3 一致性校对`：BCE `ernie-4.5-turbo-20260402`
- `Step 4 二次校对`：Codex
- `Step 5 日志回填`：Codex / 脚本
- `Step 6 普通章终检`：BCE `ernie-4.5-turbo-20260402`
- `Step 6 关键章终检`：BCE `glm-5`
- `Step 7 通知`：脚本

### 可选增强器

- `Kimi-K2.5`
  仅用于卷末章、名场面、强情绪章的可选增强，不进入每章必跑链路。

### 硬原则

1. 正文产出方不能同时充当最终放行方
2. 任何章节不得跳过 `Step 3`、`Step 4`、`Step 6`
3. 后期长线章节优先使用压缩上下文包，不直接全量喂整仓库
4. Telegram 必须始终排在最后

---

## 二、上下文压缩策略

长篇写到后期，真正容易崩的是“模型知道太多，却抓不住眼前最关键的那点”。因此本项目正式采用上下文压缩包。

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

---

## 三、开工前准备

### 必跑检查

```bash
./scripts/run_pipeline_preflight.sh
```

### 必须通过的项目

- `codex` CLI 可用
- `python3` 可用
- 当前 `CC Switch` 的 BCE provider 可读取
- BCE API 最小 smoke test 通过
- `TELEGRAM_BOT_TOKEN` 已加载
- `send_telegram.sh` 可执行
- `gstack-office-hours` / `superpowers` 是否存在只做记录，不作为阻塞项

### 正式开写前人工确认

1. 本章是普通章还是关键章
2. `OUTLINE.md` 中该章目标已锁定
3. 最近 3 章日志已更新
4. 本章是否需要额外人物角色加入 `voice_rules`

---

## 四、正式 7 步流程

## Step 1 — 规划

**执行者**：Codex

**目标**：生成章节拍表，不写正文。

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

---

## Step 2 — BCE 正文写作

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

- `chapters/chapter_XXX_draft.md`

**硬约束**：

- 3500-4500 字
- 第三人称限制视角
- 对话符合人物音色
- 结尾必须有强钩子
- 不得出现禁词与满清词

**失败回滚**：

- 返回 Step 1 或本步重跑
- 不得带着明显不达标草稿进入 Step 3

---

## Step 3 — BCE 一致性校对

**执行者**：BCE  
**默认模型**：`ernie-4.5-turbo-20260402`

**执行命令**：

```bash
./scripts/run_bce_consistency_review.sh chapters/chapter_003_draft.md
```

**目标**：作为第一层硬约束 gate，检查世界观、人物音色、禁词与钩子强度。

**输出**：

- `reviews/review_bce_consistency_XXX.md`

**通过标准**：

- 综合建议为 `PASS`
- 钩子评分 `>= 3/5`
- 无满清词
- 无重大设定矛盾

**失败回滚**：

- 必须返回 Step 2 重写

---

## Step 4 — Codex 二次校对

**执行者**：Codex

**执行命令**：

```bash
./scripts/run_codex_review.sh chapters/chapter_003_draft.md
```

**目标**：负责节奏、句式单调、人物音色漂移、AI 痕迹、场景真实感。

**输出**：

- `reviews/review_codex_XXX.md`

**通过标准**：

- 综合评分 `>= 3/5`

**失败回滚**：

- 返回 Step 2

---

## Step 5 — 日志回填与版本整理

**执行者**：Codex / 脚本

**目标**：

- 更新 `OUTLINE.md` LOG 区
- 保存当前章节产物
- 整理 review 文件路径

**要求**：

- 必须在进入终检前完成
- 日志中写清本章模型、评分、是否关键章

---

## Step 6 — BCE 终检

**执行者**：BCE

**普通章默认模型**：`ernie-4.5-turbo-20260402`  
**关键章默认模型**：`glm-5`

**执行命令**：

```bash
./scripts/run_bce_final_check.sh chapters/chapter_003_draft.md
./scripts/run_bce_final_check.sh chapters/chapter_003_draft.md glm-5
```

**目标**：做最终发布前 gate，检查追更欲、结尾牵引力、叙事流畅性和整体完成度。

**输出**：

- `reviews/review_bce_final_XXX.md`

**通过标准**：

- 最终结论 `PASS`
- 连载感评分 `>= 3/5`

**失败回滚**：

- 返回 Step 2 或 Step 5 之间的修订回路

**注意**：

- 终检不能由 Step 2 的同一模型输出直接自评放行
- 关键章若 Step 2 用 `glm-5`，Step 6 也用 `glm-5` 时，必须保留 Step 4 的 Codex 否决权

---

## Step 7 — Telegram 通知

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

---

## 五、可脚本化清单

当前已脚本化：

- `run_pipeline_preflight.sh`
- `build_context_pack.py`
- `run_bce_write.sh`
- `run_bce_consistency_review.sh`
- `run_codex_review.sh`
- `run_bce_final_check.sh`
- `send_telegram.sh`

明确不允许“偷懒跳步”的环节：

- 直接从 Step 2 跳到 Step 7
- 跳过上下文压缩包直接裸跑全文
- 用同一份正文自评后直接宣布完成

---

## 六、正式开工前还需确认的事项

1. 第 3 章起是否统一采用新文件命名约定
   建议：正文初稿统一用 `chapters/chapter_XXX_draft.md`
2. `OUTLINE.md` 日志区是否补记模型与评分字段
3. 是否要为“关键章”单独建立一个标记字段，方便脚本自动选择 `glm-5`
4. 是否要在推 GitHub 前先跑一次第 3 章完整彩排，验证 7 步串联无断点

**备注**：

- 这一步是 **可读性/连载感 gate**
- 它和 Step 3 的分工不同，不重复做世界观主审

---

## Step 5 — 日志回填与终稿保存

**目标**：把本章正式写入项目状态。

**输入**：

- 最终通过版本
- BCE 一致性评分
- Codex 评分

**动作**：

1. 保存终稿到：

```text
chapters/chapter_XXX.md
```

2. 在 `OUTLINE.md` 的 `<!-- LOG_START -->` 与 `<!-- LOG_END -->` 之间追加：

```markdown
**第X章《章节标题》** | [完成日期]
- 摘要：[100字以内]
- 谢长庚状态：[位置] | [情绪] | [持有物变化]
- 新增伏笔：[如无则“无”]
- 评分：BCE一致性[X]/5 | Codex[X]/5 | 终检[X]/5
```

**通过标准**：

- 章节编号一致
- 日志与正文同步

---

## Step 6 — 小说终检

**目标**：在交付前做最后一道“读者视角”终检。

**检查重点**：

1. 追更欲  
   读者是否会因为结尾和本章推进自然想看下一章

2. 信息密度  
   是否一次塞入太多设定、信息、关系，压住了阅读快感

3. 节奏波形  
   是否出现连续平铺、连续解释、连续同类句式

4. 情绪落点  
   本章最后留给读者的是紧张、期待、担忧、震惊中的哪一种，是否足够清晰

5. 爽点兑现  
   本章 promised 的爽点是否真的兑现，而不是只铺不打

**输出格式建议**：

- 终检结论：PASS / REVISE
- 最大问题 1-3 条
- 追更欲评分：1-5
- 一句话判断：这章值不值得连载发布

**通过标准**：

- 追更欲评分 `>= 3/5`
- 无“虽然没错但不想追”的明显问题

**失败回滚**：

- 返回 Step 2 或 Step 4，视问题类型决定

### 可选顾问工具

以下工具可作为补充视角，但不是主流程 gate：

- `gstack-office-hours`
  适合在卡章纲、卡冲突设计、卡“这章值不值得这样写”时使用

- `requesting-code-review`
  不建议作为正文终检主工具，最多只作为流程纪律参考

---

## Step 7 — Telegram 通知

**目标**：只在章节真正通过全部 gate 后，再发送完成通知。

**命令**：

```bash
cd /Users/roven/Documents/Trae/Daming1900
./send_telegram.sh \
  "第X章《章节标题》" \
  "字数" \
  "BCE一致性评分" \
  "Codex评分" \
  "100字摘要" \
  "待处理问题或无"
```

**通过标准**：

- 命令返回成功
- Telegram 实际收到通知

---

## 四、推荐执行顺序

每写一章，按下面顺序走：

1. 环境校验：Telegram + BCE preflight
2. Step 1 规划
3. Step 2 写作
4. Step 3 BCE 一致性校对
5. Step 4 Codex 二次校对
6. Step 5 日志回填与终稿保存
7. Step 6 小说终检
8. Step 7 Telegram 通知

---

## 五、快速验收清单

- [ ] `TELEGRAM_BOT_TOKEN` 已加载
- [ ] BCE smoke test 通过
- [ ] 本章字数在 3500-4500
- [ ] Step 3 通过
- [ ] Step 4 通过
- [ ] `OUTLINE.md` 已追加日志
- [ ] `chapters/chapter_XXX.md` 已保存
- [ ] Step 6 通过
- [ ] Telegram 已收到通知

---

## 六、建议用法

真正批量写作前，先拿下一章做一次全流程彩排：

1. 生成章纲
2. 写初稿
3. 跑 BCE 一致性校对
4. 跑 Codex 二次校对
5. 做终检
6. 发 Telegram

如果这一轮顺畅，再进入后续连续产出。
