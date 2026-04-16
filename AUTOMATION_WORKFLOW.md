# 《大明1900》自动化流水线工作流程

## 📁 最终项目结构（精简版）

```
DaMing/
├── docs/                              # 核心文档（6个文件）
│   ├── 00-宪法层/
│   │   ├── CLAUDE.md                  # AI操作宪法
│   │   └── Daming1900_Bible.md        # 终极设定圣经 (v4.2)
│   ├── 01-规划层/
│   │   ├── Daming1900_Master_Outline.md # 唯一大纲 (v4.2)
│   │   └── character-database.md      # 人物数据库
│   ├── 02-执行层/
│   │   └── CHAPTER_ENGINE.md          # 章节生成引擎
│   └── 04-质控层/
│       └── Daming1900_Engine_Rules.md # 生成规范（含开篇结构、钩子、谍战设计）
│
└── automation/                        # 自动化系统（核心）
    ├── state.json                     # 当前状态（位置、健康、物品）
    ├── character_physical_profiles.json # 物理档案（永久伤痕、残疾）
    ├── character_voice_profiles.json   # 语言特征库
    ├── foreshadowing_ledger.json       # 伏笔账本
    ├── visual_noise_library.json       # 视觉噪声库
    ├── pov_lock_system.json            # POV锁定系统
    ├── ming_vocabulary_library.json    # 大明词汇库
    ├── reference_text_library.md       # 参考文本库（无满清元素）
    ├── ANTI_AMNESIA_SYSTEM.md          # 防失忆指南
    ├── DEATH_PIT_GUARD_SYSTEM.md       # 防死穴指南
    ├── ai_flavor_remover_protocol.md   # 去AI味协议
    ├── COMPLETE_PROTECTION_SYSTEM_V4.md # 完整防护指南
    └── scripts/
        ├── pipeline.py                 # 主控流水线 ⭐
        ├── generate_chapter.py         # 章节生成器
        ├── checkpoint_manager.py       # 检查点管理
        ├── state_verification.py       # 状态验证器
        ├── death_pit_guard.py          # 防死穴检测器
        ├── visual_pov_guard.py         # 视觉+视角检测器
        └── quality_checker.py          # 质量检查器
```

---

## 🚀 自动化流水线工作流程

### 阶段一：准备阶段（每次生成前）

#### 1. 读取核心文档

**AI需要读取的文件**：
1. `docs/00-宪法层/CLAUDE.md` - AI操作宪法
2. `docs/00-宪法层/Daming1900_Bible.md` - 终极设定圣经
3. `docs/01-规划层/Daming1900_Master_Outline.md` - 当前进度的章节大纲
4. `docs/01-规划层/character-database.md` - 出场人物信息
5. `automation/state.json` - 当前状态
6. `automation/character_physical_profiles.json` - 人物物理档案

#### 2. 加载防护系统

**AI需要加载的JSON文件**：
1. `automation/character_voice_profiles.json` - 人物语言特征
2. `automation/foreshadowing_ledger.json` - 伏笔账本
3. `automation/visual_noise_library.json` - 视觉噪声库
4. `automation/pov_lock_system.json` - POV锁定规则
5. `automation/ming_vocabulary_library.json` - 大明词汇库

---

### 阶段二：生成阶段（单章生成）

#### Step 1: 提取章节上下文

**运行命令**：
```bash
python3 automation/scripts/pipeline.py --chapter 1
```

**输出**：
```json
{
  "chapter_number": 1,
  "title": "煤烟里的铸造厂",
  "pov_character": "陈铁",
  "core_event": "陈铁在铸造厂打工，吃劣质窝头",
  "suspense_hook": "老鬼说：'小陈，你那炮管，里面有砂眼。'",
  "characters": [
    {"name": "陈铁", "location": "天津卫铸造厂", "health": "良好"},
    {"name": "老鬼", "location": "炸酱面馆", "health": "缺失左臂"},
    {"name": "施罗德", "location": "铸造厂监工室", "health": "良好"}
  ],
  "world_state": {
    "time": "1900年庚子年春",
    "location": "天津卫铸造厂",
    "key_events": ["八国联军逼宫", "兰芳省被封锁"]
  }
}
```

#### Step 2: 生成章节正文

**AI生成时的约束**：
1. **时间锁**：本章时间跨度不超过2小时
2. **POV锁**：本章只能用"陈铁"视角
3. **语言锁**：陈铁说天津卫方言，内心独白也用方言
4. **细节强制**：必须有300字日常细节（煤渣、劣质窝头、蒸汽轰鸣）
5. **悬念钩子**：结尾必须有钩子

**参考文本注入**：
```
【参考文本1】《陶庵梦忆》片段（300字）
【参考文本2】《金瓶梅》对话片段（200字）
【参考文本3】《南明史》史料片段（100字）
```

#### Step 3: 质量检查

**运行命令**：
```bash
python3 automation/scripts/quality_checker.py --file chapters/第001章.md
```

**检查项**：
1. ✅ 禁用词扫描（手机、地铁、公园、汉服MM、奴才、主子）
2. ✅ 方言vs官话验证（陈铁说方言，朱靖镇说官话）
3. ✅ POV验证（本章是否只用陈铁视角）
4. ✅ 时间锁验证（本章时间跨度是否≤2小时）
5. ✅ 日常细节占比（是否≥300字）
6. ✅ 悬念钩子检查（结尾是否有钩子）

**输出**：
```json
{
  "passed": true,
  "warnings": ["中性平滑词'微微'出现2次，建议减少"],
  "suggestions": ["增加感官反差描写（脏/乱 vs 精致）"]
}
```

---

### 阶段三：存档阶段（每10章）

#### Step 1: 提取状态更新

**运行命令**：
```bash
python3 automation/scripts/checkpoint_manager.py --create 10
```

**AI需要输出**：
```json
{
  "chapter": 10,
  "changes": [
    {
      "character": "陈铁",
      "changes": {
        "health": "左腿烫伤（第3章阿牛之死时被蒸汽烫伤）",
        "location": "天津卫老鬼面馆",
        "items": ["生铁扳手（老鬼赠送）"]
      }
    },
    {
      "character": "阿牛",
      "changes": {
        "status": "死亡",
        "death_chapter": 3,
        "cause": "被高压蒸汽烫死"
      }
    }
  ],
  "plot_progress": {
    "foreshadowing_planted": ["老鬼的真实身份（前北洋水师锅炉长）"],
    "foreshadowing_resolved": []
  }
}
```

#### Step 2: 验证状态一致性

**运行命令**：
```bash
python3 automation/scripts/state_verification.py --verify
```

**检查项**：
1. ✅ 死人是否复活（阿牛不能在第11章出现）
2. ✅ 残疾是否恢复（老鬼不能长出左臂）
3. ✅ 伤痕是否消失（陈铁左腿烫伤不能消失）
4. ✅ 物品是否凭空消失/出现

**输出**：
```
✅ 所有状态一致性检查通过
⚠️ 警告：陈铁的生铁扳手在第8-10章未提及，建议在第11章补充
```

#### Step 3: 更新state.json

**自动化更新**：
```json
{
  "current_chapter": 10,
  "characters": {
    "陈铁": {
      "location": "天津卫老鬼面馆",
      "health": "左腿烫伤疤痕",
      "items": ["生铁扳手"],
      "permanent_features": {
        "左腿烫伤疤痕": {
          "source": "第3章阿牛之死时被蒸汽烫伤",
          "position": "左小腿外侧",
          "narrative_function": "提醒陈铁阿牛的死"
        }
      }
    },
    "阿牛": {
      "status": "死亡",
      "death_chapter": 3,
      "alive": false
    },
    "老鬼": {
      "location": "炸酱面馆",
      "health": "缺失左臂",
      "alive": true,
      "permanent_features": {
        "缺失左臂": {
          "source": "甲午战争（1894年）北洋水师锅炉爆炸",
          "position": "左肩以下全部缺失"
        }
      }
    }
  }
}
```

---

### 阶段四：批量生成（1-10章）

#### 运行命令

```bash
python3 automation/scripts/pipeline.py --batch 1-10
```

#### 工作流程

```
for chapter in range(1, 11):
    1. 提取章节上下文（读取大纲、state.json）
    2. 生成章节正文（遵守所有规则）
    3. 质量检查（禁用词、POV、时间锁、细节、钩子）
    4. 如果不通过，重新生成
    5. 如果通过，保存到 chapters/第{chapter:03d}章.md

    if chapter % 10 == 0:
        6. 创建检查点（提取状态更新）
        7. 验证状态一致性
        8. 更新state.json
```

---

## 🛡️ 八层防护系统如何工作

### 防护层级

| 层级 | 防护内容 | 检查脚本 |
|------|---------|---------|
| **物理层面** | 死人复活、残疾恢复、伤痕消失 | `state_verification.py` |
| **语言层面** | 人物同质化、语言特征消失 | `character_voice_profiles.json` |
| **叙事层面** | 多线脱钩、伏笔未回收 | `foreshadowing_ledger.json` |
| **文体层面** | 分析腔、AI味、满清元素 | `quality_checker.py` |
| **质量层面** | 章节注水、细节缺失 | `quality_checker.py` |
| **情感层面** | 情感缺失、灵魂不足 | 人工审查 |
| **视觉层面** | 视觉降噪、缺乏反差 | `visual_pov_guard.py` |
| **视角层面** | POV死锁、视角混乱 | `visual_pov_guard.py` |

---

## 📊 实战示例：生成第1章

### 1. 准备阶段

**读取核心文档**：
- CLAUDE.md
- Daming1900_Bible.md
- Daming1900_Master_Outline.md（第1章概要）
- character-database.md（陈铁、老鬼、施罗德）
- state.json（初始状态）

### 2. 生成阶段

**章节上下文**：
```json
{
  "chapter_number": 1,
  "title": "煤烟里的铸造厂",
  "pov_character": "陈铁",
  "core_event": "陈铁在铸造厂打工，吃劣质窝头",
  "suspense_hook": "老鬼说：'小陈，你那炮管，里面有砂眼。'"
}
```

**AI生成时遵守的规则**：
1. 时间锁：本章时间跨度≤2小时
2. POV锁：只用陈铁视角
3. 语言锁：陈铁说天津卫方言
4. 细节强制：≥300字日常细节
5. 悬念钩子：结尾必须有钩子

**参考文本注入**：
```
《陶庵梦忆》片段（市井生活）
《金瓶梅》片段（底层对话）
```

### 3. 质量检查

**运行命令**：
```bash
python3 automation/scripts/quality_checker.py --file chapters/第001章.md
```

**检查结果**：
```json
{
  "passed": true,
  "warnings": [],
  "suggestions": ["可以增加更多蒸汽管道的轰鸣声描写"]
}
```

### 4. 存档阶段（第10章后）

**创建检查点**：
```bash
python3 automation/scripts/checkpoint_manager.py --create 10
```

**验证状态**：
```bash
python3 automation/scripts/state_verification.py --verify
```

---

## 🎯 核心优势

| 优势 | 说明 |
|------|------|
| **防失忆** | 物理档案永久记录，写到第200章也不会忘记 |
| **防死穴** | 八层防护系统，六大死穴全覆盖 |
| **自动化** | 一键批量生成，自动检查，自动存档 |
| **高质量** | 人工审查 + AI检查双重保障 |
| **可追溯** | 每10章存档，随时回溯状态 |

---

**总制片，这就是我们的自动化流水线！从准备、生成、检查到存档，全程自动化，质量有保障！** 🎋⚔️
