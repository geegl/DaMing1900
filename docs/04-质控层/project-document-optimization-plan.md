# 项目文档优化方案

## 一、系统目录文件迁移

### 发现的问题

**memory/ 目录在系统目录，不在项目目录！**

**文件列表**：
```
~/.claude/projects/-Users-roven-Documents-Trae-DaMing/memory/
├── memory.md (31KB)
└── 第0章创作方法论.md (3.8KB)
```

**后果**：
- ❌ 这些文件不在Git版本控制中
- ❌ 上下文重置后会丢失
- ❌ 协作者无法访问

**迁移方案**：
```
移动到项目目录：
/Users/roven/Documents/Trae/DaMing/memory/
├── MEMORY.md (核心设定)
└── docs/04-质控层/chapter-0-methodology.md
```

---

## 二、文档臃肿诊断

### 最臃肿的5个文档

| 文件 | 行数 | 大小 | 问题 |
|------|------|------|------|
| **character-database.md** | 915行 | 40KB | 人物细节过多，应该拆分 |
| **Daming1900_Engine_Rules.md** | 839行 | 28KB | 规则过于详细，应该精简 |
| **political-architecture-1900.md** | 666行 | 24KB | 政治架构重复说明 |
| **Daming1900_Master_Outline.md** | 542行 | 16KB | 大纲过于详细 |
| **political-characters-supplement.md** | 525行 | 16KB | 与character-database重复 |

**总大小**：124KB

**按Karpathy标准应该**：<30KB

**节省预期**：75%

---

## 三、优化策略

### 1. character-database.md (915行 → 200行)

**问题**：
- 每个人物都有详细的生平、性格、语言特征
- 大量重复信息

**优化方案**：
```
拆分为：
1. automation/character_physical_profiles.json (物理档案，永久)
2. automation/character_voice_profiles.json (语言特征)
3. docs/01-规划层/character-brief.md (简要介绍，200行)
```

**原则**：
- 只保留核心信息
- 详细信息放在JSON中供程序读取

---

### 2. Daming1900_Engine_Rules.md (839行 → 150行)

**问题**：
- 八层防护体系展开太详细
- 大量示例代码

**优化方案**：
```
精简为：
1. 八层防护清单（每层5行）
2. 验证脚本路径
3. 禁用词列表移到JSON文件
```

**原则**：
- 只保留规则，删除示例
- 详细内容移到JSON/脚本

---

### 3. political-architecture-1900.md (666行 → 100行)

**问题**：
- 政治架构重复说明
- 与其他文档重叠

**优化方案**：
```
合并到Bible.md中，只保留：
1. 三司制核心说明
2. 关键人物列表
3. 政治力量关系图
```

**原则**：
- 一个主题只在一个文档中详细说明
- 其他文档只引用

---

### 4. Daming1900_Master_Outline.md (542行 → 300行)

**问题**：
- 每章详细描写
- 大量伏笔说明

**优化方案**：
```
精简为：
1. 每卷主题（10行）
2. 每章一句话概括（220行）
3. 关键伏笔列表（50行）
```

**原则**：
- 详细内容移到JSON
- 只保留高层概览

---

### 5. political-characters-supplement.md (525行 → 删除)

**问题**：
- 与character-database重复

**优化方案**：
```
合并到character-brief.md中
```

---

## 四、新增原则补充到CLAUDE.md

### 立即补充的4个原则

#### 6. Token Economy
**Every file should be concise. No redundancy.**
- CLAUDE.md < 100 lines
- Bible.md < 300 lines
- Master Outline < 300 lines
- Use imperative language, not explanatory prose

#### 7. Model Allocation
**Use the right model for the right task.**
- Planning/checking: Haiku (fast, cheap)
- Writing: Sonnet (creative, balanced)
- Complex reasoning: Opus (slow, expensive)

#### 8. Batch Protocol
**After every batch (10 chapters):**
1. Update README.md (progress)
2. Update state.json (status)
3. Update progress/CURRENT.md
4. Git commit and push

**The test**: Can I resume after context reset? If no, batch incomplete.

#### 9. No False Claims
**Never say "completed" without verification.**
- Run verification script
- Show actual output
- Only claim success after passing all checks

**The test**: Did I verify? If no, don't say "completed."

---

## 五、优化后的目录结构

```
DaMing1900/
├── CLAUDE.md (91行、4KB) ← 已优化
├── memory/
│   └── MEMORY.md (从系统目录迁移)
├── docs/
│   ├── 00-宪法层/
│   │   ├── Daming1900_Bible.md (300行、12KB) ← 待优化
│   │   ├── ming-official-system-correction.md (保留)
│   │   └── difference-engine-origin.md (保留)
│   ├── 01-规划层/
│   │   ├── Daming1900_Master_Outline.md (300行、12KB) ← 待优化
│   │   ├── character-brief.md (200行、8KB) ← 新建，替代臃肿的database
│   │   └── political-forces-layout-21-50.md (保留)
│   ├── 03-参考层/
│   │   └── Reference_Text_Library.md (保留)
│   └── 04-质控层/
│       ├── Daming1900_Engine_Rules.md (150行、6KB) ← 待优化
│       └── claude-md-principles-review.md (保留)
├── automation/
│   ├── character_physical_profiles.json (保留)
│   ├── character_voice_profiles.json (保留)
│   ├── foreshadowing_ledger.json (保留)
│   └── state.json (保留)
└── chapters/
    └── 第XXX章_标题.md
```

---

## 六、Token消耗预估

### 当前（臃肿版）

**每次生成需要读取**：
- CLAUDE.md: 4KB
- Bible.md: 16KB
- Master Outline: 16KB
- Engine Rules: 28KB
- Character Database: 40KB
- 其他: ~20KB

**总计**：124KB ≈ 31,000 tokens (仅system prompt)

### 优化后

**每次生成需要读取**：
- CLAUDE.md: 5KB
- Bible.md: 12KB
- Master Outline: 12KB
- Engine Rules: 6KB
- Character Brief: 8KB
- 其他: ~10KB

**总计**：53KB ≈ 13,250 tokens

**节省**：58% tokens

---

## 七、执行步骤

### 立即执行（本次session）

1. ✅ 补充CLAUDE.md的4个新原则
2. ✅ 迁移memory/目录到项目
3. ✅ 删除冗余文档
4. ⏳ 优化最臃肿的5个文档（分批执行）

### 后续执行（下次session）

5. 优化其他中型文档
6. 建立文档精简规范
7. 自动化token统计

---

## 八、文档精简规范（未来所有文档）

**Karpathy标准**：
- 每个文档<300行
- 使用命令式语言
- 删除所有示例代码
- 详细内容移到JSON/脚本
- 一个主题只在一个文档中详细说明

**验证标准**：
- 能否用一句话概括这个文档的核心？
- 如果删除30%的内容，是否仍然可用？
- 是否有重复内容在多个文档中？

---

**总制片，文档优化方案已制定完成！立即开始执行！** 🎋
