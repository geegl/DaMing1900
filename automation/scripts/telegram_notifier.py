#!/usr/bin/env python3
"""
Telegram工作进度通知系统
支持：章节完成、批次完成、中期Review、阶段Review

用法：
    python3 automation/scripts/telegram_notifier.py --type chapter --chapter 8
    python3 automation/scripts/telegram_notifier.py --type batch --batch 2
    python3 automation/scripts/telegram_notifier.py --type midterm --chapter 50
    python3 automation/scripts/telegram_notifier.py --type stage --part 1
"""

import os
import sys
import json
import argparse
import subprocess
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Telegram配置
BOT_TOKEN = "8143117746:AAG25K1aaP4_nU6ESxWRbodfN-ry70V5ob8"
CHAT_ID = "6579837315"

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent

# GitHub仓库
GITHUB_REPO = "https://github.com/geegl/DaMing1900"


def send_telegram_message(text: str, parse_mode: str = "Markdown") -> bool:
    """发送Telegram消息"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": parse_mode
    }).encode()

    try:
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            return result.get("ok", False)
    except Exception as e:
        print(f"❌ Telegram发送失败: {e}")
        return False


def get_github_link(file_path: str) -> str:
    """获取GitHub文件链接"""
    # 获取最新commit
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True, text=True, cwd=PROJECT_ROOT
    )
    commit = result.stdout.strip()[:7]
    return f"{GITHUB_REPO}/blob/{commit}/{file_path}"


def get_chapter_info(chapter: int) -> Dict[str, Any]:
    """获取章节信息"""
    # 查找章节文件
    pattern = f"第{chapter:03d}章*.md"
    import glob
    files = glob.glob(str(PROJECT_ROOT / "chapters" / pattern))

    if not files:
        return {"exists": False}

    file_path = files[0]
    file_name = Path(file_path).name

    # 读取章节内容
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 统计字数
    word_count = len(content.replace('\n', '').replace(' ', ''))

    # 提取标题
    title = file_name.replace(f"第{chapter:03d}章_", "").replace(".md", "")

    return {
        "exists": True,
        "title": title,
        "word_count": word_count,
        "file_name": file_name,
        "github_link": get_github_link(f"chapters/{file_name}")
    }


def get_state_info() -> Dict[str, Any]:
    """获取项目状态"""
    state_file = PROJECT_ROOT / "automation" / "state.json"

    if not state_file.exists():
        return {}

    with open(state_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def notify_chapter_complete(chapter: int, score: Optional[int] = None, issues: Optional[list] = None):
    """通知章节完成"""
    info = get_chapter_info(chapter)
    state = get_state_info()

    if not info.get("exists"):
        text = f"⚠️ 第{chapter}章未找到"
    else:
        issues_text = ""
        if issues:
            issues_text = f"\n\n📝 发现问题：\n" + "\n".join([f"• {i}" for i in issues[:5]])

        score_text = f"📊 评分：{score}/60\n" if score else ""

        text = f"""✅ 第{chapter:03d}章完成

📖 标题：{info['title']}
📝 字数：{info['word_count']:,}字
{score_text}
🔗 查看章节：{info['github_link']}
{issues_text}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}"""

    return send_telegram_message(text)


def notify_batch_complete(batch: int, start_chapter: int, end_chapter: int):
    """通知批次完成"""
    state = get_state_info()

    # 统计批次信息
    total_words = 0
    chapter_list = []

    for ch in range(start_chapter, end_chapter + 1):
        info = get_chapter_info(ch)
        if info.get("exists"):
            total_words += info.get("word_count", 0)
            chapter_list.append(f"第{ch:03d}章")

    # 批次报告链接
    report_file = f"progress/batches/batch_{batch:02d}_log.md"
    report_link = get_github_link(report_file)

    text = f"""📦 Batch {batch:02d} 完成

📊 统计：
• 章节：第{start_chapter:03d}-{end_chapter:03d}章
• 总字数：{total_words:,}字
• 平均：{total_words // (end_chapter - start_chapter + 1):,}字/章

📄 批次报告：{report_link}
🔗 GitHub：{GITHUB_REPO}/tree/main/chapters

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}"""

    return send_telegram_message(text)


def notify_midterm_review(chapter: int):
    """通知中期Review"""
    state = get_state_info()

    # 中期报告链接
    report_file = f"progress/midterm_{chapter}_review.md"

    text = f"""🎯 中期Review（第{chapter}章）

📈 评估内容：
• 结构完整性检查
• 读者留存预测
• 商业潜力评估
• 伏笔回收状态

📄 详细报告：{get_github_link(report_file)}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}"""

    return send_telegram_message(text)


def notify_stage_review(part: int, chapters: tuple):
    """通知阶段Review"""
    start, end = chapters

    part_names = {
        1: "天工纪（第1-70章）",
        2: "洪威纪（第71-165章）",
        3: "泰安纪（第166-220章）"
    }

    # 阶段报告链接
    report_file = f"progress/stage_{part}_review.md"

    text = f"""🏆 阶段Review - {part_names.get(part, f'第{part}部')}

📚 完成章节：第{start}-{end}章

🎯 评估内容：
• 主题深度分析
• 商业潜力评估
• IP改编建议
• 续作衔接规划

📄 详细报告：{get_github_link(report_file)}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}"""

    return send_telegram_message(text)


def notify_error(error_type: str, message: str, suggestion: str = ""):
    """通知错误"""
    text = f"""❌ 错误报告

类型：{error_type}
详情：{message}
{"建议：" + suggestion if suggestion else ""}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}"""

    return send_telegram_message(text)


def notify_progress(current: int, total: int = 220, message: str = ""):
    """通知进度"""
    percentage = (current / total) * 100
    bar_length = 20
    filled = int(bar_length * current / total)
    bar = "█" * filled + "░" * (bar_length - filled)

    text = f"""📊 进度更新

[{bar}] {percentage:.1f}%

当前：第{current}章 / 共{total}章
{message}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}"""

    return send_telegram_message(text)


def main():
    parser = argparse.ArgumentParser(description="Telegram工作进度通知系统")
    parser.add_argument("--type", required=True, choices=["chapter", "batch", "midterm", "stage", "error", "progress"],
                        help="通知类型")
    parser.add_argument("--chapter", type=int, help="章节编号")
    parser.add_argument("--batch", type=int, help="批次编号")
    parser.add_argument("--part", type=int, help="阶段编号")
    parser.add_argument("--score", type=int, help="章节评分")
    parser.add_argument("--message", help="附加消息")
    parser.add_argument("--error-type", help="错误类型")
    parser.add_argument("--suggestion", help="改进建议")

    args = parser.parse_args()

    success = False

    if args.type == "chapter" and args.chapter:
        success = notify_chapter_complete(args.chapter, args.score)
    elif args.type == "batch" and args.batch:
        start = (args.batch - 1) * 10 + 1
        end = args.batch * 10
        success = notify_batch_complete(args.batch, start, end)
    elif args.type == "midterm" and args.chapter:
        success = notify_midterm_review(args.chapter)
    elif args.type == "stage" and args.part:
        chapters_map = {1: (1, 70), 2: (71, 165), 3: (166, 220)}
        success = notify_stage_review(args.part, chapters_map.get(args.part, (1, 70)))
    elif args.type == "error":
        success = notify_error(args.error_type or "未知错误", args.message or "", args.suggestion or "")
    elif args.type == "progress" and args.chapter:
        success = notify_progress(args.chapter, 220, args.message or "")

    if success:
        print("✅ Telegram通知发送成功")
    else:
        print("❌ Telegram通知发送失败")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
