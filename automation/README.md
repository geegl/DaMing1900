# 《大明1900》自动化生成流水线

> **版本**: 4.2
> **创建日期**: 2026-04-16

---

## 📁 目录结构

```
automation/
├── state.json              # 当前状态（人物、世界、剧情）
├── scripts/                # 脚本目录
│   ├── pipeline.py         # 主控流水线
│   ├── generate_chapter.py # 章节生成器
│   ├── checkpoint_manager.py # 检查点管理
│   └── quality_checker.py  # 质量检查器
├── output/                 # 输出目录（Prompt文件）
├── chapters/               # 章节目录（生成的正文）
├── checkpoints/            # 检查点目录（每10章存档）
└── logs/                   # 日志目录
```

---

## 🚀 使用方法

### 1. 查看状态

```bash
python3 automation/scripts/pipeline.py --status
```

### 2. 生成单章

```bash
python3 automation/scripts/pipeline.py --chapter 1
```

### 3. 批量生成

```bash
python3 automation/scripts/pipeline.py --batch 1-10
```

### 4. 创建检查点

```bash
python3 automation/scripts/checkpoint_manager.py --create 10
```

### 5. 从检查点恢复

```bash
python3 automation/scripts/checkpoint_manager.py --load 10
```

### 6. 质量检查

```bash
python3 automation/scripts/quality_checker.py --file automation/chapters/chapter_001.md
```

---

## 🔄 完整工作流

```
┌─────────────────────────────────────────────────────────┐
│                     生成流程                              │
├─────────────────────────────────────────────────────────┤
│  步骤1: 生成Prompt                                       │
│     ↓                                                    │
│  步骤2: Claude Code生成正文                              │
│     ↓                                                    │
│  步骤3: 质量检查                                         │
│     ↓                                                    │
│  步骤4: 更新状态                                         │
│     ↓                                                    │
│  步骤5: 每10章创建检查点                                 │
└─────────────────────────────────────────────────────────┘
```

---

## 📊 状态文件说明

### state.json 结构

```json
{
  "project": "大明1900",
  "version": "4.2",
  "total_chapters": 220,
  "current_chapter": 0,
  "characters": {
    "陈铁": {
      "age": 18,
      "location": "天津卫铸造厂",
      "physical_state": "健康",
      "inventory": ["铸铁扳手", "粗布工装"],
      "relationships": {"老鬼": "师徒"}
    }
  },
  "world_state": {
    "year": 1900,
    "month": 1,
    "current_event": "八国联军集结大沽口外"
  },
  "plot_state": {
    "revealed_secrets": [],
    "active_conspiracies": ["钱四海倒卖图纸"],
    "pending_revenge": ["阿牛之死（陈铁）"]
  }
}
```

---

## ✅ 质量检查项

| 检查项 | 说明 |
|--------|------|
| 禁用词 | 满清元素、魔幻词汇、客服腔 |
| 心理标签 | "他很愤怒"等，需用动作代替 |
| 上帝视角 | 不允许写其他POV的内心活动 |
| 日常细节 | 每章至少3个重工关键词 |
| 字数 | 2000-3500字 |
| 悬念钩子 | 结尾必须有悬念 |

---

## 💾 检查点机制

**每10章强制存档，防止AI失忆：**

- 第10章、第20章、第30章...自动创建检查点
- 记录：人物状态、世界状态、剧情进展
- 可从任意检查点恢复

---

## 🎯 与Claude Code配合

1. **生成Prompt**：`pipeline.py --chapter 1` 生成Prompt文件
2. **Claude Code读取**：读取Prompt和状态文件
3. **Claude Code生成**：生成章节正文
4. **保存章节**：保存到 `automation/chapters/chapter_001.md`
5. **质量检查**：运行 `quality_checker.py`
6. **更新状态**：手动或自动更新 `state.json`

---

## 📝 注意事项

1. **每次生成前**：确认 `state.json` 中的状态正确
2. **每10章**：检查检查点是否正确创建
3. **发现Bug**：从最近的检查点恢复
4. **人物死亡**：必须在 `state.json` 中更新 `alive: false`
5. **物品转移**：必须在 `inventory` 中更新
