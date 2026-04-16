# 防失忆系统 v2.0 使用指南

## 🎯 核心功能

**防止AI长线生成时的"失忆综合征"**：
- 死人复活
- 断腿重生
- 伤痕消失
- 物品凭空变化
- 人物性格突变

---

## 📁 系统架构

### 1. **character_physical_profiles.json** - 人物物理档案（不可变）

**存储内容**：
- 永久伤痕（如陈铁左腿旧伤、林霜降虎口疤痕）
- 永久残疾（如老鬼缺失左臂）
- 标志性物品（如陈铁的生铁扳手）
- 身体特征（如天工帝的重金属中毒症状）

**规则**：一旦设定，永不改变

---

### 2. **state.json** - 当前状态（可变）

**存储内容**：
- 人物当前位置
- 人物当前健康值
- 人物当前装备
- 时间进度
- 剧情进展

**规则**：每章更新，随剧情推进变化

---

### 3. **checkpoint_manager.py** - 检查点管理器

**核心功能**：
- 每10章强制存档
- 提取物理状态变化（死亡、受伤、物品变化）
- 创建人物状态快照
- 生成下一章上下文

---

### 4. **state_verification.py** - 状态验证器

**核心功能**：
- 验证死人是否复活
- 验证残疾是否被违反
- 验证伤痕是否消失
- 验证物品是否凭空变化

---

## 🛠️ 使用方法

### 生成章节时

```python
from checkpoint_manager import CheckpointManagerV2

manager = CheckpointManagerV2()

# 1. 生成第N章前，加载上下文
context = manager.generate_context_for_next_chapter(chapter_num=10)

# 2. 生成章节内容（由AI完成）
chapter_content = generate_chapter_with_ai(context)

# 3. 生成后，验证一致性
from state_verification import StateVerifier
verifier = StateVerifier()
errors = verifier.verify_chapter(chapter_content, chapter_num=10)

if errors:
    print("❌ 发现一致性错误：", errors)
    # 修复章节
else:
    print("✅ 一致性验证通过")

# 4. 每10章创建检查点
if chapter_num % 10 == 0:
    manager.create_checkpoint(chapter_num, chapter_content)
```

---

### 恢复检查点时

```bash
# 加载第50章检查点
python3 automation/scripts/checkpoint_manager.py --load 50

# 生成第51章上下文
python3 automation/scripts/checkpoint_manager.py --context 51
```

---

### 验证一致性时

```bash
# 验证章节文件
python3 automation/scripts/state_verification.py --verify output/chapter_001.md

# 生成状态摘要
python3 automation/scripts/state_verification.py --summary
```

---

## 📊 防失忆效果

| 场景 | 无防失忆系统 | 有防失忆系统 |
|------|-------------|-------------|
| **第3章阿牛死亡** | 第50章阿牛突然出现 | ✅ 系统拒绝，提示"阿牛已死亡" |
| **老鬼缺失左臂** | 第30章老鬼用左手拿东西 | ✅ 系统拒绝，提示"老鬼缺失左臂" |
| **陈铁左腿旧伤** | 第60章陈铁跑得飞快 | ⚠️ 系统警告"陈铁左腿有旧伤" |
| **林霜降虎口疤痕** | 第40章疤痕消失 | ✅ 系统拒绝，提示"疤痕不可消失" |

---

## ⚠️ 注意事项

### 1. 物理档案不可变

**一旦设定，永不改变**：
- 陈铁左腿烫伤疤痕（第3章设定）
- 老鬼缺失左臂（背景设定）
- 林霜降虎口疤痕（背景设定）

### 2. 状态每章更新

**每章生成后必须**：
- 更新位置
- 更新健康值
- 更新装备
- 更新时间

### 3. 检查点强制存档

**每10章强制存档**：
- 第10章
- 第20章
- 第30章
- ...

---

## 🎯 示例：生成第10章

```python
# 1. 加载上下文
manager = CheckpointManagerV2()
context = manager.generate_context_for_next_chapter(10)
print(context)

# 输出：
## 第9章状态存档
- 时间: 1900年3月
- 当前事件: 南洋自沉战前夕
- 死亡: 阿牛（第3章）
- 陈铁: 健康, 位置: 天津卫铸造厂
  伤痕: 左腿旧伤（第3章烫伤）

# 2. AI生成第10章
chapter_10 = generate_chapter(context)

# 3. 验证一致性
verifier = StateVerifier()
errors = verifier.verify_chapter(chapter_10, chapter_num=10)

# 4. 创建检查点
manager.create_checkpoint(10, chapter_10)
```

---

## 🚀 这就是如何防止AI失忆！

**从现在开始，写到第200章，阿牛也不会复活，老鬼也不会长出左臂！**
