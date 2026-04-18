# Gemini深度审核集成流程

> **版本**: v1.0 | **适用范围**: 第11章起所有章节

---

## 审核流程概览

```
8-Agent写作流程
    ↓
Gemini深度审核（第9步）
    ↓
修正循环
    ↓
最终通过
    ↓
Git提交
```

---

## 完整9步流程

### Step 1-8: 现有的8-Agent流程

```
1. 规划代理（Haiku）
2. 世界观约束代理（Opus）
3. 写作代理（Sonnet）
4. 逻辑检查代理（Haiku）
5. 视觉POV守护代理（Opus）
6. 情感高潮代理（Sonnet）
7. 风格润色代理（Sonnet）
8. 最终质控代理（Haiku）
```

### Step 9: Gemini深度审核（新增）

**触发条件**: 质控代理通过后

**执行方式**: 使用Agent调用，注入System Instruction

```python
# 调用方式
Agent(
    description="Gemini深度审核",
    model="opus",  # 使用Opus模拟Gemini深度推理
    prompt=gemini_auditor.construct_audit_prompt(chapter_path)
)
```

---

## 审核报告处理

### 评分判断

| 总分 | 判定 | 处理 |
|------|------|------|
| ≥ 40/50 | ✅ PASS | 进入Git提交流程 |
| 35-39/50 | ⚠️ CONDITIONAL | 进入修正循环 |
| ≤ 34/50 | ❌ FAIL | 回到写作代理重写 |

### 维度阈值

| 维度 | 阈值 | 不达标处理 |
|------|------|-----------|
| 世界观一致性 | ≥ 8/10 | 调用世界观约束代理 |
| 物理逻辑 | ≥ 8/10 | 调用逻辑检查代理 |
| POV死锁 | ≥ 9/10 | 调用POV守护代理 |
| 深层逻辑 | ≥ 7/10 | 调用写作代理重写 |
| 文风质量 | ≥ 8/10 | 调用风格润色代理 |

---

## 修正循环机制

```
Gemini审核
    ↓
[FAIL] → 提取问题列表
    ↓
调用对应Agent修正
    ↓
重新Gemini审核
    ↓
最多3轮
    ↓
[PASS] 或 [人工介入]
```

### 修正示例

```python
# 如果世界观一致性 < 8/10
if report["scores"]["worldview"] < 8:
    Agent(
        description="世界观修正",
        model="opus",
        prompt=f"""
{gemini_report}

问题：{report["worldview_issues"]}

请修正章节，确保世界观一致性。
"""
    )
```

---

## 与I-Lang集成

### 审核结果缓存

```
[READ:chapters/第011章.md]=>
[GEMINI_AUDIT|dimensions=5]=>
[CACHE:audit_result]=>
[CHECK:total_score|threshold=40]=>
[IF:pass]=>[COMMIT]=>
[IF:fail]=>[APPLY:修正]=>
[OUT]
```

### Agent间传递

```
# 质控代理 → Gemini审核
[READ:质控结果]=>[CACHE:qc_result]=>
[GEMINI_AUDIT|context=CACHE]=>
[OUT:gemini_report]
```

---

## Python脚本使用

```bash
# 单章审核
python3 automation/scripts/gemini_audit_agent.py chapters/第011章.md

# 批量审核（Batch 02）
python3 automation/scripts/gemini_audit_agent.py chapters/第01*.md
```

---

## Claude Code中的使用

```python
# 方式1: 直接调用Agent
from gemini_audit_agent import GeminiDeepAuditor

auditor = GeminiDeepAuditor()
prompt = auditor.audit_with_agent("chapters/第011章.md")

# 使用Agent工具
Agent(
    description="Gemini深度审核",
    model="opus",
    prompt=prompt
)

# 方式2: 我在conversation中直接执行
# 用户说："写第11章，用Gemini审核"
# 我会自动调用审核流程
```

---

## 审核报告保存

**位置**: `chapters/第XXX章_gemini_audit.md`

**内容结构**:
```markdown
# Gemini深度审核报告

**章节**: 第XXX章
**审核时间**: YYYY-MM-DD HH:MM:SS

---

## 【审核维度】

### 1. 世界观一致性
...

### 2. 物理逻辑
...

### 3. POV死锁
...

### 4. 深层逻辑
...

### 5. 文风质量
...

**总分**: XX/50

---

## 【反向拷问】

...

## 你可能想知道：

- ...

## 【拓展思考】

...
```

---

## 质量保证

### 双重审核机制

| 审核层 | 职责 | 覆盖范围 |
|--------|------|---------|
| **8-Agent质控** | 规则检查 | 显性规则、格式、禁用词 |
| **Gemini深度审核** | 逻辑推理 | 隐性逻辑、世界观深层、动机合理性 |

### 防止遗漏

8个Agent检查"有没有" → Gemini追问"合不合理"

**示例**:
- 8-Agent: ✅ 有左腿烫伤疤痕
- Gemini: ⚠️ 但第6章说"阴天时疤痕会痛"，第7章是晴天，为何还痛？

---

## 下一步

1. ✅ **System Instruction已创建** (`automation/gemini_system_instruction.md`)
2. ✅ **审核Agent已创建** (`automation/scripts/gemini_audit_agent.py`)
3. ✅ **I-Lang规范已升级** (CLAUDE.md第8条)
4. ⏳ **待执行**: 从第11章开始使用新流程

---

**准备就绪。等待您的指令开始第11章。**
