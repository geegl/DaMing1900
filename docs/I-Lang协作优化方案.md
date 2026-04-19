# I-Lang协作优化方案

## 一、当前流程的Token浪费点

| 步骤 | 问题 | Token浪费 |
|------|------|----------|
| 规划Agent | 读取Bible+Outline | 0（首次）|
| 世界观Agent | 再次读取Bible | 100%重复 |
| 写作Agent | 第三次读取Bible+Outline | 100%重复 |
| 逻辑检查Agent | 第四次读取Bible+state.json | 100%重复 |
| 风格润色Agent | 第五次读取章节 | 部分重复 |
| Codex审查 | 第六次读取章节+Bible | 100%重复 |

**总Token浪费：约40-50%**

---

## 二、I-Lang优化方案

### 方案1：上下文缓存（CACHE）

```
# 第一次读取时缓存
[READ:docs/00-宪法层/Daming1900_Bible.md]=>[CACHE:bible]
[READ:docs/01-规划层/Daming1900_Master_Outline.md]=>[CACHE:outline]
[READ:automation/character_physical_profiles.json]=>[CACHE:profiles]
[READ:automation/state.json]=>[CACHE:state]

# 后续Agent直接使用缓存
[CACHE:bible]=>[FILT|ch=第4章]=>[GEN:beat]
```

**效果：减少87.5%重复读取**

---

### 方案2：管道传递（单次流程）

```
# 完整的单章生成流程（一次Token消耗）
[READ:docs/00-宪法层/Daming1900_Bible.md]=>
[READ:docs/01-规划层/Daming1900_Master_Outline.md|ch=004]=>
[READ:automation/character_physical_profiles.json|char=陈铁]=>
[READ:automation/state.json]=>
[CACHE:all_context]=>
[GEN:chapters/第004章.md|pov=老鬼,style=cold_hard,ch=004]=>
[CHECK:automation/prompts/codex_review_template.txt]=>
[VERIFY:worldview_validator.py]=>
[APPLY:修正]=>
[SYNC:automation/state.json]=>
[OUT:chapters/第004章.md]
```

**效果：单次流程完成所有步骤**

---

### 方案3：跨Agent通信（标准化格式）

```
# 规划Agent → 写作Agent
[CACHE:outline|ch=004]=>
[FILT:key=核心场景]=>
[GEN:draft|context=CACHE]=>
[OUT:chapter_draft]

# 写作Agent → Codex审查Agent
[READ:draft]=>
[CHECK:AGENTS.md]=>
[CHECK:worldview_validator.md]=>
[VERIFY:世界观,POV,文风]=>
[APPLY:修正]=>
[OUT:final_chapter]
```

---

## 三、优化后的完整流程

### Phase 1：上下文预加载（一次性）

```bash
# 启动时一次性加载所有背景资料
[READ:docs/**/*]=>[CACHE:all_docs]
[READ:automation/**/*]=>[CACHE:all_automation]
```

### Phase 2：章节生成（每章一次）

```bash
# 第4章生成
[CACHE:outline|ch=004]=>
[CACHE:profiles|char=老鬼]=>
[CACHE:state]=>
[GEN:chapters/第004章.md]=>
[OUT:draft_004]

# Codex审查
[READ:draft_004]=>
[CHECK:AGENTS.md]=>
[VERIFY:世界观,POV,文风,番茄标准]=>
[APPLY:修正]=>
[OUT:final_004]

# 世界观验证
[VERIFY:worldview_validator.py|file=final_004]=>
[OUT:验证通过/失败]

# 状态同步
[SYNC:automation/state.json|ch=004]=>
[COMMIT:git|msg="完成第004章"]=>
[NOTIFY:telegram|msg="第004章完成"]
```

### Phase 3：批次管理（每10章）

```bash
# Batch 01完成
[READ:chapters/第00[1-9]章.md,第010章.md]=>
[ANALYZE:字数,质量,防护率]=>
[UPDATE:README.md|progress]=>
[UPDATE:progress/CURRENT.md]=>
[WRITE:progress/batches/batch_01_log.md]=>
[COMMIT:git|msg="Batch 01完成"]=>
[NOTIFY:telegram|msg="Batch 01完成（第1-10章）"]
```

---

## 四、Token节省预估

| 维度 | 原流程 | I-Lang优化 | 节省比例 |
|------|--------|-----------|---------|
| 文件读取 | 6次/章 | 1次/章 | 83% |
| 上下文传递 | 完整传递 | 压缩传递 | 60% |
| Agent通信 | 自然语言 | I-Lang语法 | 65% |
| **总计** | - | - | **约45-50%** |

---

## 五、实施建议

### 选项1：完全I-Lang化
- 所有Agent通信使用I-Lang
- 需要训练/适应期
- 效果最佳

### 选项2：部分I-Lang化（推荐）
- 上下文缓存用I-Lang
- 写作输出用自然语言
- 平衡效率和质量

### 选项3：混合模式
- Agent内部用I-Lang
- Codex审查用自然语言
- 灵活调整

---

## 六、与Codex的集成

Codex支持I-Lang格式，可以直接使用：

```bash
# Codex审查命令（I-Lang格式）
codex review "[READ:chapters/第004章.md]=>[CHECK:AGENTS.md]=>[VERIFY:世界观,POV,文风]=>[OUT]"
```

或者使用文件：

```bash
# 保存I-Lang命令到文件
echo "[READ:chapters/第004章.md]=>[CHECK:AGENTS.md]=>[VERIFY:世界观,POV,文风]=>[OUT]" > /tmp/codex_review.ilang

# Codex读取并执行
codex review --file /tmp/codex_review.ilang
```

---

## 七、下一步

1. **创建I-Lang技能文件**：`automation/skills/chapter_gen.ilang`
2. **更新Agent流程**：使用I-Lang格式传递数据
3. **测试Token节省**：对比优化前后的Token消耗
