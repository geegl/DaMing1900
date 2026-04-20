# 《大明1900》章节写作 Pipeline SOP

> 适用目录：`/Users/roven/Documents/Trae/Daming1900`
>  
> 本文档记录“当前仓库真实状态 + 当前本机真实环境”下可执行的章节流水线。

---

## 一、差异清单（目标方案 vs 当前真实环境）

### 已确认落地

- `send_telegram.sh` 已存在，且已按环境变量方式实现
- `PIPELINE.md` 已存在，本次升级为正式 SOP
- `TELEGRAM_BOT_TOKEN` 环境变量当前已加载
- `superpowers` 已按官方 Codex 安装方式接入
- `gstack` 已按 Codex host 安装，`office-hours` 已生成并接入

### 已确认差异

1. **`codex:rescue` 不是当前会话可见的内置 Skill**
   当前可执行做法：直接在 Codex 会话中使用固定二次校对 prompt，不依赖 `codex:rescue` 这个名字。

2. **`superpowers` 不是一个可直接调用的单一 Skill**
   它是一个 Skill 包。对本项目的“末尾检查”应映射到具体子 Skill。
   默认使用：`requesting-code-review`

3. **`office-hours` 在 Codex 环境中的真实名称不是裸名**
   当前安装结果为：`gstack-office-hours`

4. **Skill 安装后需要重启 Codex / 新开会话**
   否则当前会话的 available-skills 列表不一定刷新。

### 结论

Step 6 不能再写成：

```text
Skill("superpowers")
Skill("office-hours")
```

必须改成“按真实名称调用具体 Skill”：

```text
Skill("requesting-code-review")
Skill("gstack-office-hours")
```

如果新会话中 `requesting-code-review` 不可见，说明 superpowers Skill 包尚未被当前会话重新发现。

---

## 二、环境准备与验证

### 1. Telegram

确认变量存在：

```bash
printenv TELEGRAM_BOT_TOKEN | wc -c
```

人工要求：

- Token 不写入项目文件
- Token 仅写入 `~/.zshrc` 或 `~/.bashrc`
- 若旧 token 曾外泄，先到 `@BotFather` 重签

测试发送：

```bash
cd /Users/roven/Documents/Trae/Daming1900
./send_telegram.sh "测试章节" "1234" "4" "4" "这是测试摘要" "无"
```

### 2. Superpowers

当前安装方式来自官方 Codex 安装文档：

- 仓库：`https://github.com/obra/superpowers`
- 本机位置：`/Users/roven/.codex/superpowers`
- 发现路径：`/Users/roven/.agents/skills/superpowers`

验证：

```bash
ls -la /Users/roven/.agents/skills/superpowers
find /Users/roven/.agents/skills/superpowers -maxdepth 2 -name SKILL.md | sort
```

说明：

- superpowers 暴露的是一组子 Skill
- 本流程默认取其中最贴近“终稿审查”的 `requesting-code-review`

### 3. GStack / Office Hours

当前安装方式：

- 仓库：`https://github.com/garrytan/gstack`
- 生成仓库：`/Users/roven/.gstack/repos/gstack`
- 发现路径：`/Users/roven/.agents/skills/gstack-office-hours`

验证：

```bash
ls -la /Users/roven/.agents/skills/gstack-office-hours
sed -n '1,20p' /Users/roven/.agents/skills/gstack-office-hours/SKILL.md
```

说明：

- Codex host 下真实名称为 `gstack-office-hours`
- 不要再写裸名 `office-hours`

### 4. 重启要求

安装或更新 Skill 后，执行以下动作之一：

1. 完全退出 Codex App，再重新打开
2. 新开一个会话

然后在新会话里确认 available-skills 列表包含：

- `requesting-code-review`
- `gstack-office-hours`

---

## 三、标准 6 步流程

## Step 1 — 规划 Agent

**目标**：产出本章节拍表，不直接写正文。

**输入**：

- `OUTLINE.md` 当前章节目标
- `OUTLINE.md` LOG 区最近 3 条
- `BIBLE.md` 当前人物状态相关段落

**输出**：

- `chapter_plan_XXX.md`

**必须包含**：

1. 开头钩子场景
2. 5-8 个情节点
3. 本章高潮
4. 结尾钩子类型
5. 新伏笔

**通过标准**：

- 节拍可直接支持 3500-4500 字正文
- 结尾钩子已明确属于 4 类之一
- 不与 `BIBLE.md` 和 `OUTLINE.md` 冲突

---

## Step 2 — 写作 Agent

**目标**：按节拍表产出正文初稿。

**输入**：

- Step 1 节拍表
- `BIBLE.md`
- `STYLE.md`
- 上一章结尾 200 字

**输出**：

- `chapter_XXX_draft.md`

**硬约束**：

- 3500-4500 字
- 第三人称限制视角
- 对话必须符合人物音色
- 结尾必须留悬念
- 禁用 `STYLE.md` 中 AI 痕迹词和满清词

**通过标准**：

- 结构完整
- 至少 2 个有效爽点
- 结尾能明确回答“下一章必须知道什么”

---

## Step 3 — Claude 内部校对

**目标**：查一致性、查禁词、查钩子强度。

**输入**：

- Step 2 草稿
- `BIBLE.md`
- `STYLE.md`

**输出格式**：

- 问题清单
- 满清内容扫描结果
- 结尾钩子评分
- 综合建议：`PASS` / `REVISE`

**通过标准**：

- 钩子评分 `>= 3/5`
- 无满清相关词
- 无重大世界观矛盾

**失败回滚**：

- 返回 Step 2
- 附带明确修改意见

---

## Step 3.5 — Codex 二次校对

**目标**：独立于 Step 3 的第二双眼睛，重点抓叙事流畅度、人物音色、AI 痕迹和场景真实感。

**重要说明**：

- 当前不依赖 `codex:rescue`
- 直接使用 Codex 会话执行固定 prompt

**输入**：

- 经 Step 3 修订后的草稿

**固定 prompt**：

```text
请对以下章节草稿做独立二次校对，重点检查叙事质量：

1. 叙事节奏——是否存在连续3段以上相同句式或段落长度过于均匀
2. 人物音色——台词是否有角色说话方式互换的情况（谢长庚说话像郑玄机等）
3. AI痕迹——特别检查以下词汇是否出现：
   深深地/不禁/油然而生/心潮澎湃/眸子/苦涩地笑了/嘴角微扬/蓦然/悄然/莫名地
4. 场景真实感——工业/战争场景的细节是否具体，是否有“大机器”等模糊描述

输出要求：
① 分类问题清单（每类最多3条最严重的问题）
② 综合评分 1-5 分
③ 不输出修改后全文

[草稿内容]
```

**通过标准**：

- Codex 综合评分 `>= 3/5`

**失败回滚**：

- 返回 Step 2
- 标记为“Codex 二次校对未通过”

---

## Step 4 — 日志回填

**目标**：把本章结果沉淀到 `OUTLINE.md` LOG 区，并保存最终章文件。

**输入**：

- 最终通过版本
- 钩子评分
- Codex 评分

**动作**：

在 `OUTLINE.md` 的 `<!-- LOG_START -->` 和 `<!-- LOG_END -->` 之间追加：

```markdown
**第X章《章节标题》** | [完成日期]
- 摘要：[100字以内]
- 谢长庚状态：[位置] | [情绪] | [持有物变化]
- 新增伏笔：[如无则“无”]
- 评分：钩子[X]/5 | Codex[X]/5
```

同时保存正文到：

- `chapters/chapter_XXX.md`

**通过标准**：

- 日志和正文同步
- 章节编号一致

---

## Step 5 — Telegram 通知

**目标**：每章完成后推送摘要。

**命令**：

```bash
cd /Users/roven/Documents/Trae/Daming1900
./send_telegram.sh \
  "第X章《章节标题》" \
  "字数" \
  "钩子评分" \
  "Codex评分" \
  "100字摘要" \
  "待处理问题或无"
```

**通知格式**：

```text
📖 第X章《章节标题》 完成
字数：XXXX | 钩子评分：X/5 | Codex评分：X/5
📝 摘要：[100字章节摘要]
⚠️ 待处理：[问题列表或无]
```

**通过标准**：

- 脚本返回成功
- Telegram 实际收到通知

---

## Step 6 — superpowers + office-hours 终检

**目标**：在章节交付前做最后一道“外部视角”检查。

### 6A. superpowers 终检

**真实调用名**：

- `requesting-code-review`

**为什么不是 `superpowers`**：

- `superpowers` 是 Skill 包，不是单一 Skill 名
- 本流程里最贴近“终稿审查”的具体子 Skill 是 `requesting-code-review`

**检查重点**：

- 是否还有明显结构性问题
- 是否有未闭合的逻辑断口
- 是否存在“自以为清楚、读者其实不清楚”的段落

### 6B. office-hours 终检

**真实调用名**：

- `gstack-office-hours`

**为什么不是 `office-hours`**：

- 当前 Codex host 安装结果就是 `gstack-office-hours`

**检查重点**：

- 本章是否真有读下去的驱动力
- 信息投放是否过量或过早
- 本章作为连载产品的一章，是否值得用户追更

### 6C. 降级方案

如果新会话里看不到以上 Skill：

- 跳过 Step 6
- Telegram 文案末尾追加：

```text
⚠️ superpowers/gstack-office-hours 未执行，请手动触发
```

---

## 四、一步步执行模板

每写一章，按下面顺序走：

1. 环境校验：Telegram + 新会话 Skill 可见性
2. Step 1 产出节拍表
3. Step 2 产出初稿
4. Step 3 做一致性校对
5. Step 3.5 做 Codex 二次校对
6. Step 4 回填 `OUTLINE.md` 并保存终稿
7. Step 5 发 Telegram
8. Step 6 做终检或走降级方案

---

## 五、快速验收清单

- [ ] `TELEGRAM_BOT_TOKEN` 已加载
- [ ] 新会话能看到 `requesting-code-review`
- [ ] 新会话能看到 `gstack-office-hours`
- [ ] 本章字数在 3500-4500
- [ ] Step 3 钩子评分 `>= 3`
- [ ] Step 3.5 Codex 评分 `>= 3`
- [ ] `OUTLINE.md` 已追加日志
- [ ] `chapters/chapter_XXX.md` 已保存
- [ ] Telegram 已收到通知

---

## 六、当前建议

真正开始批量写作前，先做一次完整演练：

1. 新开 Codex 会话
2. 确认 Skill 列表
3. 以第 3 章为样本跑完整 6 步
4. 记录 Step 6 的真实调用手感与输出格式
5. 如有必要，再对本 SOP 做第二轮压缩
