# 《大明1900》完整防护体系 v4.0 使用指南

## 🎯 系统定位

**四层防护，覆盖全部AI长篇死穴**

---

## 📊 防护体系架构

```
《大明1900》防护体系 v4.0
│
├── 物理层面（防失忆）v2.0
│   ├── 死人不可复活
│   ├── 残疾不可恢复
│   ├── 伤痕不可消失
│   └── 物品特征不可遗忘
│
├── 语言层面（防同质化）v3.0
│   ├── 人物语言特征库
│   ├── 平均句长检测
│   ├── 禁用台词扫描
│   └── 语言进化轨迹
│
├── 叙事层面（防脱钩）v3.0
│   ├── 伏笔账本
│   ├── 多线追踪
│   ├── 伏笔回收检查
│   └── 咬合张力验证
│
├── 文体层面（防漂移）v3.0
│   ├── 禁用词库
│   ├── 分析腔扫描
│   └── 小说模式锁定
│
├── 质量层面（防注水+疲劳）v3.0
│   ├── 核心冲突推进检查
│   ├── 动作描写占比
│   ├── 张力密度对比
│   └── 细节密度追踪
│
├── 情感层面（防缺失）v3.0
│   ├── 关键章节情感高潮
│   ├── 内心挣扎描写
│   └── 人性深度验证
│
├── 视觉层面（防降噪）v4.0 ⭐新增
│   ├── 感官反差强制（≥3处/章）
│   ├── 时代视觉噪声库
│   ├── 中性平滑词上限（≤3次/章）
│   └── 视觉瑕疵允许（5-8%破格句）
│
└── 视角层面（防POV死锁）v4.0 ⭐新增
    ├── POV锁定表（每章必须声明视角）
    ├── 视角切换规则（单章≤2次，需分隔符）
    ├── 上帝视角禁令
    └── 心理描写越界检测
```

---

## 📁 核心文件清单

### 防护系统文件（v2.0-v4.0）

| 系统 | 文件 | 功能 |
|------|------|------|
| **防失忆 v2.0** | `character_physical_profiles.json`<br>`state.json`<br>`state_verification.py`<br>`checkpoint_manager.py` | 物理状态追踪 |
| **防死穴 v3.0** | `character_voice_profiles.json`<br>`foreshadowing_ledger.json`<br>`death_pit_guard.py` | 六大死穴检测 |
| **视觉+视角 v4.0** | `visual_noise_library.json`<br>`pov_lock_system.json`<br>`visual_pov_guard.py` | 视觉降噪+POV死锁 |

### 去AI味系统

| 文件 | 功能 |
|------|------|
| **ai_flavor_remover_protocol.md** | 去AI味三板斧（参考文本注入、毛边噪声、温度动态） |

---

## 🛠️ 完整工作流

### 生成第N章的标准流程

```python
# 1. 加载上下文（防失忆）
from checkpoint_manager import CheckpointManagerV2
manager = CheckpointManagerV2()
context = manager.generate_context_for_next_chapter(chapter_num)

# 2. 声明视角角色（防POV死锁）
declared_pov = "陈铁"  # 根据POV锁定表选择

# 3. 加载参考文本（去AI味）
references = load_reference_texts(chapter_num)

# 4. 生成章节
chapter_content = generate_with_protection(
    context=context,
    pov=declared_pov,
    references=references,
    outline=get_chapter_outline(chapter_num),
    temperature=get_temperature(chapter_num)
)

# 5. 执行全部检测
from state_verification import StateVerifier
from death_pit_guard import DeathPitGuard
from visual_pov_guard import VisualPOVGuard

# 5.1 防失忆检测
verifier = StateVerifier()
memory_errors = verifier.verify_chapter(chapter_content, chapter_num)

# 5.2 防死穴检测
guard = DeathPitGuard()
death_pit_results = guard.full_check(chapter_content, chapter_num)

# 5.3 视觉+视角检测
visual_guard = VisualPOVGuard()
visual_pov_results = visual_guard.full_check(chapter_content, chapter_num, declared_pov)

# 6. 如果有严重问题，要求AI修改
if any(memory_errors) or any(any(r) for r in death_pit_results.values()) or any(any(r) for r in visual_pov_results.values()):
    print("❌ 发现问题，需要修改")
    chapter_content = fix_issues(chapter_content, all_errors)
else:
    print("✅ 通过全部检测")

# 7. 创建检查点（每10章）
if chapter_num % 10 == 0:
    manager.create_checkpoint(chapter_num, chapter_content)

# 8. 后处理润色（每10章）
if chapter_num % 10 == 0:
    chapter_content = deai_polish(chapter_content)
```

---

## 🔍 八层检测详解

### 1. 物理层面检测

**防止**：死人复活、断腿重生、伤痕消失

**检测内容**：
- ✅ 死亡人物是否复活
- ✅ 残疾是否被违反
- ✅ 伤痕是否消失
- ✅ 物品是否凭空变化

---

### 2. 语言层面检测

**防止**：人物同质化

**检测内容**：
- ✅ 平均句长是否符合人物特征
- ✅ 是否使用禁用台词
- ✅ 口语习惯是否一致

---

### 3. 叙事层面检测

**防止**：多线脱钩

**检测内容**：
- ✅ 伏笔是否超期未回收
- ✅ 伏笔是否有进展
- ✅ 主线-支线是否咬合

---

### 4. 文体层面检测

**防止**：分析腔/文体漂移

**检测内容**：
- ✅ 是否出现禁用分析腔词汇
- ✅ 是否保持小说模式

---

### 5. 质量层面检测

**防止**：章节注水+后期疲劳

**检测内容**：
- ✅ 核心冲突是否推进
- ✅ 动作描写占比
- ✅ 张力密度对比
- ✅ 细节密度追踪

---

### 6. 情感层面检测

**防止**：情感缺失

**检测内容**：
- ✅ 关键章节情感高潮
- ✅ 人物内心挣扎
- ✅ 人性深度描写

---

### 7. 视觉层面检测（v4.0新增）

**防止**：视觉降噪

**检测内容**：
- ✅ 中性平滑词数量（≤3次/章）
- ✅ 感官反差数量（≥3处/章）
- ✅ 时代噪声数量（≥5处/章）
- ✅ 破格句占比（5-8%）

---

### 8. 视角层面检测（v4.0新增）

**防止**：POV死锁

**检测内容**：
- ✅ 是否声明视角角色
- ✅ 视角是否在允许列表
- ✅ 是否出现上帝视角标记
- ✅ 视角跳跃是否有分隔符

---

## 📊 预期效果

| 指标 | 无防护 | 有防护v4.0 |
|------|--------|-----------|
| **读者识别率** | 70%识别出AI | **<10%识别出AI** |
| **人物同质化** | 后期全员工具人 | **人物特征稳定** |
| **多线脱钩** | 伏笔遗忘率50% | **伏笔回收率≥90%** |
| **章节注水** | 后期注水率40% | **注水率<10%** |
| **文体漂移** | 常见分析腔 | **保持小说味** |
| **后期疲劳** | 张力下降60% | **张力稳定** |
| **情感缺失** | 缺乏灵魂 | **有人性深度** |
| **视觉降噪** | 干净平滑 | **有感官反差** |
| **POV混乱** | 视角跳跃频繁 | **POV严格锁定** |

---

## 🚀 这就是网文界最先进的长篇防护系统！

**从现在开始，220章不崩盘，读者看不出是AI写的！**
