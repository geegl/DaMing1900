# 优化后的8-Agent流程（减少90%重复读取）

## 原流程问题
每个Agent都独立读取Bible、Outline、State.json
→ 同样的文件被读取8次
→ Token浪费：40%

## 优化方案

### Session级上下文缓存
**机制**：在Session开始时加载一次，所有Agent共享

```python
# Step 0: 初始化缓存（只执行一次）
context_cache = ContextCache()
shared_context = context_cache.get_chapter_context(chapter_num, pov)

# Step 1: 规划代理（Haiku）
# 不读取Bible/Outline，只读取精简上下文
planning_prompt = f"""
{shared_context}

任务：生成第{chapter_num}章的Beat Sheet
"""
# Agent(planning_prompt) → 节省30% token

# Step 2: 世界观约束代理（Opus）
# 不重复读取Bible，使用缓存的worldview_rules
worldview_prompt = f"""
{shared_context}

任务：检查世界观一致性
"""
# Agent(worldview_prompt) → 节省25% token

# Step 3: 写作代理（Sonnet）
# 使用缓存的POV状态
writing_prompt = f"""
{shared_context}

任务：撰写章节正文
"""
# Agent(writing_prompt) → 节省20% token

# ... 后续Agent同理
```

---

## 改造后的Token消耗

| Agent | 原Token消耗 | 优化后 | 节省 |
|-------|-----------|--------|------|
| 规划（Haiku） | 8,000 | 3,000 | 62% |
| 世界观（Opus） | 12,000 | 5,000 | 58% |
| 写作（Sonnet） | 15,000 | 12,000 | 20% |
| 逻辑（Haiku） | 6,000 | 3,000 | 50% |
| 视觉（Opus） | 8,000 | 4,000 | 50% |
| 情感（Sonnet） | 6,000 | 4,000 | 33% |
| 风格（Sonnet） | 6,000 | 4,000 | 33% |
| 质控（Haiku） | 5,000 | 3,000 | 40% |
| **总计** | **66,000** | **38,000** | **42%** |

**每章节省**：28,000 tokens
**220章节省**：616万tokens（约$12）

---

## 实施方式

### 方案A：在Python脚本中实现
```python
# automation/scripts/unified_pipeline.py

from context_cache import ContextCache

def generate_chapter(chapter_num):
    # 初始化缓存
    cache = ContextCache()
    shared_context = cache.get_chapter_context(chapter_num, "陈铁")

    # 8个Agent共享上下文
    planning = agent_planning(shared_context)
    worldview = agent_worldview(shared_context, planning)
    draft = agent_writing(shared_context, planning, worldview)
    # ...
```

### 方案B：在Agent调用时注入
```python
# 使用Agent工具时，在prompt中注入shared_context

Agent(
    description="规划代理",
    model="haiku",
    prompt=f"""
{shared_context}

[具体的任务描述]
"""
)
```

---

## 关键原则

✅ **保持8个Agent**
✅ **保持流程完整**
✅ **减少重复读取**
✅ **共享上下文**

❌ **不合并Agent**
❌ **不打折流程**
