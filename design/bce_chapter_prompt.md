# 大明1900 BCE 章节执行 Prompt

> 用途：给 Claude Code CLI / BCE 通道直接执行单章写作流程。
>
> 推荐用法有两种：
>
> 1. 直接把本文全文发给模型，并把 `{{chapter_no}}` 替换成实际章号  
>    例如：`148`
> 2. 更简单的说法：  
>    `请严格按 design/bce_chapter_prompt.md 执行第148章。`
>
> 若模型能读取仓库文件，推荐第 2 种；若你是手工复制 prompt 到外部窗口，推荐第 1 种。

---

你现在执行《大明1900》第 `{{chapter_no}}` 章写作任务。

如果你发现当前仓库规则与旧 prompt 冲突，一律以仓库当前文件为准，不得沿用旧规则。

## 一、先读这些真源文件

不要展开复述，只读取并执行：

1. `BIBLE.md`
2. `STYLE.md`
3. `OUTLINE.md`
4. `design/chapter_policy.md`
5. `design/chapter_types.json`
6. `design/review_checklist.md`
7. 若章节属于第二幕（101-280），额外读取：
   - `design/act2_architecture.md`
   - `design/act2_setting_notes.md`
   - `design/act2_detailed_outline_101_280.md`

先从 `design/chapter_types.json` 读取第 `{{chapter_no}}` 章的 `chapter_type`。  
如果没有 `chapter_type`，立即停止并报告，不允许继续。

## 二、字数硬规则

- `normal`：`3500-4500` 汉字
- `key`：`5000-6000` 汉字

## 三、7-Agent 流程（必须严格按顺序执行）

### Step 1 规划

执行：

```bash
python3 scripts/build_context_pack.py {{chapter_no}}
```

必须产出：

- `context/generated/chapter_{{chapter_no}}/write_pack.md`

### Step 2 BCE 写作

执行：

```bash
./scripts/run_bce_write.sh {{chapter_no}}
```

必须产出：

- `draft/chapter_{{chapter_no}}_draft.md`
- `context/generated/chapter_{{chapter_no}}/bce_write_meta.json`

硬要求：

- `provider_name` 必须是 `BCE`
- 必须通过 `scripts/validate_chapter_gate.py`
- 不允许人工代写正文
- 开头快速进入场景
- 结尾必须有钩子
- 禁止 AI 腔、总结腔、说明腔

### Step 3 一致性校对

执行：

```bash
./scripts/run_bce_consistency_review.sh draft/chapter_{{chapter_no}}_draft.md
```

必须产出：

- `reviews/consistency/review_bce_consistency_{{chapter_no}}.md`

结果必须为 `PASS`，否则停止。

### Step 4 Codex 二审

执行：

```bash
./scripts/run_codex_review.sh draft/chapter_{{chapter_no}}_draft.md
```

必须产出：

- `reviews/codex/review_codex_{{chapter_no}}.md`

硬要求：

- Codex CLI 二审只允许 `gpt-5.5` 或 `gpt-5.4`
- 默认固定 `gpt-5.5`
- 禁止检查“还有哪些可用模型”
- 禁止切换到 `gpt-4o-mini`、`oss`、`ollama`、`lmstudio`

结果必须为 `PASS` 或达标，否则停止。

### Step 5 日志回填

终稿保存到：

- `chapters/chapter_{{chapter_no}}.md`

然后执行日志脚本回填 `OUTLINE.md`。  
不允许手工跳过日志。

### Step 6 终检

执行：

```bash
./scripts/run_bce_final_check.sh chapters/chapter_{{chapter_no}}.md
```

必须产出：

- `reviews/final/review_bce_final_{{chapter_no}}.md`

结果必须为 `PASS`，否则停止。

### Step 7 Telegram 通知

只有前 6 步全部通过后，才能发送 Telegram。  
Telegram 失败要报告，但不能伪装成已发送。

## 四、红线禁令

1. 不允许跳过任何一步
2. 不允许 BCE 写作失败后人工代写正文继续放行
3. 不允许字数不达标仍继续日志、Telegram、GitHub
4. 不允许自己伪造审校结果
5. 不允许用旧字数标准（如 `6000-10000`）
6. 不允许把第二幕写成纯线性航海爽文，必须保留补给、组织、政治、思想代价
7. 不允许在 Codex 二审前后探测其他模型或 provider

## 五、问题处理规则

- BCE 不通：立即停止并报告
- 审校 `FAIL / REVISE`：返回修改，不得放行
- 缺少产出文件：补齐前不得继续下一步
- 任一步骤不确定：先查仓库文件，不允许臆造

## 六、完成前验证

必须执行：

```bash
./scripts/verify_7agent.sh {{chapter_no}}
```

只有 `verify_7agent` 通过，且三轮检查都通过，才允许报告“本章完成”。

## 七、输出要求

- 只汇报执行状态、失败点、产出文件
- 不要写多余解释
- 不要跳过验证
