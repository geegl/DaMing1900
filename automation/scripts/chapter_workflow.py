#!/usr/bin/env python3
"""
《大明1900》章节生成+审查自动化脚本
用途：一章完整流程（8-agent写作 → Codex审查 → 修正 → 提交 → 通知）
版本：v1.0
"""

import subprocess
import sys
from pathlib import Path

def run_codex_review(chapter_file):
    """运行Codex审查"""
    prompt_file = Path(__file__).parent.parent / "prompts" / "codex_review_template.txt"

    if not prompt_file.exists():
        print(f"错误：找不到prompt模板 {prompt_file}")
        return None

    print(f"\n🔍 运行Codex审查: {chapter_file}")

    # Codex审查命令
    cmd = f'cat {prompt_file} | codex review --uncommitted'

    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        timeout=120
    )

    return result.stdout

def run_worldview_validation(chapter_file):
    """运行世界观验证"""
    print(f"\n✅ 运行世界观验证: {chapter_file}")

    result = subprocess.run(
        ["python3", "automation/scripts/worldview_validator.py", chapter_file],
        capture_output=True,
        text=True
    )

    return result.returncode == 0

def commit_chapter(chapter_number, title):
    """提交章节到Git"""
    print(f"\n📤 提交第{chapter_number:03d}章到Git")

    subprocess.run(["git", "add", f"chapters/第{chapter_number:03d}章_*.md"])
    subprocess.run([
        "git", "commit", "-m",
        f"完成第{chapter_number:03d}章：{title}\n\nCo-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
    ])
    subprocess.run(["git", "push"])

def main(chapter_number):
    """主流程"""
    print(f"""
╔════════════════════════════════════════════╗
║   《大明1900》章节生成+审查流程            ║
║   第{chapter_number:03d}章                              ║
╚════════════════════════════════════════════╝
""")

    # 注意：这个脚本只是框架
    # 实际写作由Claude Code的8-agent系统完成
    # 这里只负责审查、验证、提交流程

    print("\n⚠️  注意：此脚本需要配合Claude Code使用")
    print("实际写作流程：")
    print("1. Claude Code写章节（8-agent系统）")
    print("2. 运行此脚本进行Codex审查")
    print("3. 根据审查结果修正")
    print("4. 提交到Git")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 chapter_workflow.py <章节号>")
        print("示例: python3 chapter_workflow.py 004")
        sys.exit(1)

    chapter_num = int(sys.argv[1])
    main(chapter_num)
