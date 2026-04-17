# AI生成规范

**Quality > Speed. Slow is fine. Collapse is not.**

---

## 核心规则

### 1. No Superpowers
**Chen Tie has no magic abilities.**
- His power comes from: 20 years factory experience, deep understanding of mechanics, thousands of blueprints.
- Finding weaknesses: Requires stolen blueprints (Lin Shuangjiang), careful analysis, trial-and-error.

### 2. POV Lock (First 30 Chapters)
**Chapters 1-30: Only Chen Tie and Old Ghost POV.**
- Chapters 31-35: Add Zhu Jingyuan
- Chapter 36+: Relax, but still one POV per chapter

### 3. Early Micro-Wins
**First 3 chapters must have small victories.**
- Chapter 1: Chen Tie fixes valve, supervisor doesn't beat him
- Chapter 2: Old Ghost hears fort fell (setback)
- Chapter 3: Chen Tie "accidentally" burns supervisor's hand with steam leak

**Wins aren't "face-slapping" - they're "small resistance from the bottom."**

### 4. Daily Details (Required)
**Every chapter: 300 words of daily life details.**

| Perspective | Required Details |
|-------------|-----------------|
| **Workers** | Food (porridge, cold bread), coal soot, deaf ears |
| **Compradors** | Tea (Longjing), coffee, half-literary speech |

### 5. Hongwei Emperor Lives
**Zhu Jingyuan survives to the finale.**
- Final confrontation: Zhu Jingyuan vs Chen Tie at Forbidden City
- Former bunkmates, ultimate enemies

---

## Prohibited Elements

### Never Use
- ❌ "He felt angry" → "He gripped the wrench until knuckles turned white"
- ❌ Qing officials as permanent positions
- ❌ Modern concepts (手机, 地铁, 公共公园)
- ❌ AI clichés (心头一颤, 双目赤红, 总而言之, 微微, 淡淡)

### Always Verify
- Physical consistency (dead stay dead, scars stay)
- POV lock (one camera, one character)
- Ming accuracy (run `grep -i "总督\|巡抚\|手机" chapter.md`)
- AI flavor (run `grep -i "微微\|淡淡\|心头一颤" chapter.md`)

---

## Reference Files

**Read before writing**:
- `automation/character_physical_profiles.json` (permanent injuries)
- `automation/foreshadowing_ledger.json` (伏笔账本)
- `automation/visual_noise_library.json` (感官细节)

---

**The test**: Can a new AI agent understand and follow these rules immediately? If no, simplify.
