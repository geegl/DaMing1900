#!/usr/bin/env python3
"""
Telegram命令监听器
用途：接收用户通过Telegram发送的命令，写入命令队列

启动方式：
    python3 automation/scripts/telegram_command_listener.py

命令队列：automation/command_queue.json
"""

import os
import sys
import json
import time
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# Telegram配置
BOT_TOKEN = "8143117746:AAG25K1aaP4_nU6ESxWRbodfN-ry70V5ob8"
AUTHORIZED_CHAT_ID = "6579837315"

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent

# 命令队列文件
COMMAND_QUEUE = PROJECT_ROOT / "automation" / "command_queue.json"

# 上次处理的update_id
LAST_UPDATE_ID_FILE = PROJECT_ROOT / "automation" / ".last_update_id"

# Polling间隔（秒）
POLLING_INTERVAL = 5


def get_updates(offset: Optional[int] = None, timeout: int = 10) -> List[Dict]:
    """获取Telegram更新"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    params = {"timeout": timeout}

    if offset:
        params["offset"] = offset

    data = urllib.parse.urlencode(params).encode()

    try:
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=timeout + 5) as response:
            result = json.loads(response.read().decode())
            if result.get("ok"):
                return result.get("result", [])
    except Exception as e:
        print(f"❌ 获取更新失败: {e}")

    return []


def send_message(chat_id: str, text: str) -> bool:
    """发送Telegram消息"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }).encode()

    try:
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            return result.get("ok", False)
    except Exception as e:
        print(f"❌ 发送消息失败: {e}")
        return False


def load_last_update_id() -> int:
    """加载上次处理的update_id"""
    if LAST_UPDATE_ID_FILE.exists():
        with open(LAST_UPDATE_ID_FILE, 'r') as f:
            return int(f.read().strip())
    return 0


def save_last_update_id(update_id: int):
    """保存上次处理的update_id"""
    with open(LAST_UPDATE_ID_FILE, 'w') as f:
        f.write(str(update_id))


def add_to_command_queue(command: Dict):
    """添加命令到队列"""
    # 确保文件存在
    if not COMMAND_QUEUE.exists():
        with open(COMMAND_QUEUE, 'w', encoding='utf-8') as f:
            json.dump({"commands": []}, f, ensure_ascii=False, indent=2)

    # 读取现有队列
    with open(COMMAND_QUEUE, 'r', encoding='utf-8') as f:
        queue = json.load(f)

    # 添加新命令
    command["timestamp"] = datetime.now().isoformat()
    command["status"] = "pending"
    queue["commands"].append(command)

    # 保存
    with open(COMMAND_QUEUE, 'w', encoding='utf-8') as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)

    print(f"📝 命令已添加到队列: {command['command']}")


def parse_command(text: str) -> Optional[Dict]:
    """解析命令"""
    text = text.strip()

    if text.startswith("/status"):
        return {"command": "status"}

    elif text.startswith("/next"):
        parts = text.split()
        count = int(parts[1]) if len(parts) > 1 else 1
        return {"command": "next", "count": count}

    elif text.startswith("/pause"):
        return {"command": "pause"}

    elif text.startswith("/resume"):
        return {"command": "resume"}

    elif text.startswith("/review"):
        parts = text.split()
        if len(parts) > 1:
            return {"command": "review", "chapter": int(parts[1])}
        return {"command": "review", "chapter": None}

    elif text.startswith("/fix"):
        parts = text.split(maxsplit=1)
        if len(parts) > 1:
            return {"command": "fix", "description": parts[1]}
        return None

    elif text.startswith("/outline"):
        parts = text.split()
        if len(parts) > 1:
            return {"command": "outline", "chapter": int(parts[1])}
        return {"command": "outline", "chapter": None}

    elif text.startswith("/batch"):
        parts = text.split()
        if len(parts) > 1:
            return {"command": "batch", "number": int(parts[1])}
        return {"command": "batch", "number": None}

    elif text.startswith("/help"):
        return {"command": "help"}

    elif text.startswith("/"):
        return {"command": "unknown", "text": text}

    return None


def handle_command(chat_id: str, command: Dict) -> str:
    """处理命令并返回回复"""
    cmd = command.get("command")

    if cmd == "status":
        # 读取状态
        state_file = PROJECT_ROOT / "automation" / "state.json"
        if state_file.exists():
            with open(state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
            current = state.get("current_chapter", 0)
            total = state.get("total_chapters", 220)
            percentage = (current / total) * 100
            return f"📊 当前进度\n\n第{current}章 / 共{total}章\n完成率：{percentage:.1f}%"
        return "⚠️ 状态文件不存在"

    elif cmd == "next":
        count = command.get("count", 1)
        add_to_command_queue(command)
        return f"✅ 已加入队列：继续写{count}章\n\nClaude Code会在下次运行时执行"

    elif cmd == "pause":
        add_to_command_queue(command)
        return "⏸️ 已加入队列：暂停写作"

    elif cmd == "resume":
        add_to_command_queue(command)
        return "▶️ 已加入队列：恢复写作"

    elif cmd == "review":
        chapter = command.get("chapter")
        if chapter:
            add_to_command_queue(command)
            return f"🔍 已加入队列：Review第{chapter}章"
        return "用法：/review [章节号]"

    elif cmd == "fix":
        description = command.get("description")
        add_to_command_queue(command)
        return f"🔧 已加入队列：修正问题\n\n问题描述：{description}"

    elif cmd == "outline":
        chapter = command.get("chapter")
        if chapter:
            add_to_command_queue(command)
            return f"📋 已加入队列：查看第{chapter}章大纲"
        return "用法：/outline [章节号]"

    elif cmd == "batch":
        number = command.get("number")
        if number:
            add_to_command_queue(command)
            return f"📦 已加入队列：执行Batch {number}"
        return "用法：/batch [批次号]"

    elif cmd == "help":
        return """📖 可用命令：

/status - 查看当前进度
/next [数量] - 继续写N章（默认1章）
/pause - 暂停写作
/resume - 恢复写作
/review [章节] - Review指定章节
/fix [描述] - 修正问题
/outline [章节] - 查看章节大纲
/batch [批次] - 执行指定批次
/help - 显示帮助

💡 提示：命令会写入队列，Claude Code下次运行时执行"""

    elif cmd == "unknown":
        return f"⚠️ 未知命令：{command.get('text')}\n\n发送 /help 查看可用命令"

    return "⚠️ 命令解析失败"


def process_update(update: Dict):
    """处理单个更新"""
    message = update.get("message", {})
    chat = message.get("chat", {})
    chat_id = str(chat.get("id", ""))
    text = message.get("text", "")
    update_id = update.get("update_id")

    # 只处理授权用户的消息
    if chat_id != AUTHORIZED_CHAT_ID:
        print(f"⚠️ 忽略非授权用户消息: chat_id={chat_id}")
        return

    # 忽略非文本消息
    if not text:
        return

    print(f"📩 收到消息: {text}")

    # 解析命令
    command = parse_command(text)
    if command:
        # 处理命令
        reply = handle_command(chat_id, command)
        send_message(chat_id, reply)
    else:
        # 非命令消息，作为自由文本指令
        add_to_command_queue({
            "command": "free_text",
            "text": text
        })
        send_message(chat_id, f"💬 已记录您的指令：\n\n{text}\n\nClaude Code会在下次运行时处理")


def main():
    """主循环"""
    print(f"🤖 Telegram命令监听器启动")
    print(f"📱 授权用户: {AUTHORIZED_CHAT_ID}")
    print(f"⏱️ Polling间隔: {POLLING_INTERVAL}秒")
    print(f"📄 命令队列: {COMMAND_QUEUE}")
    print("-" * 50)

    last_update_id = load_last_update_id()
    print(f"📌 从update_id={last_update_id + 1}开始")

    try:
        while True:
            # 获取更新
            updates = get_updates(offset=last_update_id + 1 if last_update_id else None)

            for update in updates:
                update_id = update.get("update_id")

                if update_id and update_id > last_update_id:
                    process_update(update)
                    last_update_id = update_id
                    save_last_update_id(last_update_id)

            # 等待下次轮询
            time.sleep(POLLING_INTERVAL)

    except KeyboardInterrupt:
        print("\n⏹️ 监听器已停止")


if __name__ == "__main__":
    main()
