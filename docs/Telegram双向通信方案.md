# Telegram双向通信方案

## 一、技术可行性分析

### Telegram Bot API限制

| 模式 | 发送消息 | 接收回复 | 要求 |
|------|---------|---------|------|
| **单向通知** | ✅ 支持 | ❌ 不支持 | 仅需Bot Token |
| **Webhook模式** | ✅ 支持 | ✅ 支持 | 需要公网服务器+HTTPS |
| **Polling模式** | ✅ 支持 | ✅ 支持 | 本地运行，定期轮询 |

### 结论

**Polling模式最适合本地使用**

---

## 二、Polling模式实现

### 工作原理

```
用户发送消息给Bot
    ↓
Telegram服务器存储消息
    ↓
本地脚本定期调用 getUpdates API
    ↓
解析新消息，执行命令
    ↓
发送回复
```

### 支持的命令

| 命令 | 功能 |
|------|------|
| `/status` | 查看当前进度 |
| `/next` | 继续写下一章 |
| `/pause` | 暂停写作 |
| `/review [章节号]` | 对指定章节进行Review |
| `/fix [问题描述]` | 修正问题 |
| `/outline [章节号]` | 查看章节大纲 |
| `/help` | 显示帮助 |

---

## 三、实现代码

见 `automation/scripts/telegram_command_listener.py`

---

## 四、使用方式

### 启动监听（后台运行）

```bash
python3 automation/scripts/telegram_command_listener.py &
```

### 发送命令

在Telegram中向Bot发送消息：

```
/status          # 查看进度
/next            # 继续写第4章
/review 3        # Review第3章
```

---

## 五、安全性

### 限制

1. **只有授权用户可以控制**
   - 脚本检查 `chat_id` 是否匹配
   - 非授权用户的消息会被忽略

2. **命令白名单**
   - 只允许预定义的命令
   - 防止注入攻击

---

## 六、局限性

1. **需要保持脚本运行**
   - 关机后停止工作
   - 可用systemd/pm2保持后台运行

2. **响应延迟**
   - Polling间隔默认5秒
   - 紧急命令可能延迟

3. **无法主动触发Claude Code**
   - 只能记录命令到文件
   - 需要Claude Code主动检查命令队列

---

## 七、推荐工作流

### 方案A：命令队列（推荐）

```
Telegram → 命令队列文件 → Claude Code检查 → 执行
```

- 用户通过Telegram发送命令
- 脚本将命令写入 `automation/command_queue.json`
- Claude Code每次启动时检查队列
- 执行命令后发送结果

### 方案B：Webhook + 云服务器

```
Telegram → 云服务器Webhook → 触发GitHub Action → Claude Code执行
```

- 更稳定，但需要云服务器
- 适合生产环境

---

## 八、当前状态

✅ 单向通知已实现（章节完成、批次完成、错误报告）
⏳ 双向通信脚本已创建，需要后台运行
⏳ 命令队列机制已设计，待集成
