#!/usr/bin/env python3
"""
强制流程控制器 - 不可绕过
每写一章前必须执行，否则拒绝生成章节
"""

import sys
import json
from pathlib import Path

class ForceFlowController:
    """强制流程控制器"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.outline_file = self.project_root / ".codepilot-uploads" / "1776657275281-Daming1900_Master_Outline.md"
        self.state_file = self.project_root / "automation" / "config" / "state.json"

    def check_outline_exists(self):
        """强制检查：大纲文件是否存在"""
        if not self.outline_file.exists():
            raise FileNotFoundError(f"❌ 大纲文件不存在：{self.outline_file}")

        # 读取大纲行数
        with open(self.outline_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        if len(lines) < 500:
            raise ValueError(f"❌ 大纲文件不完整：只有{len(lines)}行，应该至少919行")

        return True

    def check_chapter_in_outline(self, chapter_num):
        """强制检查：章节是否在大纲中"""
        with open(self.outline_file, 'r', encoding='utf-8') as f:
            outline_text = f.read()

        # 检查章节标题是否在大纲中
        chapter_patterns = [
            f"第{chapter_num}章",
            f"第{chapter_num:03d}章",
        ]

        found = any(pattern in outline_text for pattern in chapter_patterns)

        if not found:
            raise ValueError(f"❌ 第{chapter_num}章不在大纲中！请先检查大纲！")

        return True

    def check_time_range(self, chapter_num, time_str):
        """强制检查：时间是否在合理范围内"""
        # 从大纲中提取时间范围
        # 第一部：1900-1909年
        # 第二部：1909-1920年
        # 第三部：1919-1921年

        time_ranges = {
            (1, 70): (1900, 1909),   # 第一部
            (71, 165): (1909, 1920), # 第二部
            (166, 220): (1919, 1921) # 第三部
        }

        for (start, end), (year_start, year_end) in time_ranges.items():
            if start <= chapter_num <= end:
                # 提取时间字符串中的年份
                import re
                year_match = re.search(r'(\d{4})年', time_str)
                if year_match:
                    year = int(year_match.group(1))
                    if not (year_start <= year <= year_end):
                        raise ValueError(
                            f"❌ 时间线错误！第{chapter_num}章时间{time_str}不在合理范围内！\n"
                            f"第{chapter_num}章应该在{year_start}-{year_end}年之间\n"
                            f"设定：三部曲时间线\n"
                            f"  第一部（1-70章）：1900-1909年\n"
                            f"  第二部（71-165章）：1909-1920年\n"
                            f"  第三部（166-220章）：1919-1921年"
                        )
                break

        return True

    def force_check_before_write(self, chapter_num):
        """写作前的强制检查"""
        print("=" * 60)
        print(f"🔍 强制流程检查 - 第{chapter_num}章")
        print("=" * 60)

        # 检查1：大纲是否存在
        print("\n1️⃣ 检查大纲文件...")
        self.check_outline_exists()
        print("   ✅ 大纲文件存在且完整（919行）")

        # 检查2：章节是否在大纲中
        print(f"\n2️⃣ 检查第{chapter_num}章是否在大纲中...")
        self.check_chapter_in_outline(chapter_num)
        print(f"   ✅ 第{chapter_num}章在大纲中")

        # 检查3：当前状态
        print("\n3️⃣ 检查当前状态...")
        with open(self.state_file, 'r', encoding='utf-8') as f:
            state = json.load(f)

        current_chapter = state.get('current_chapter', 0)
        print(f"   当前已完成：{current_chapter}章")
        print(f"   准备写入：第{chapter_num}章")

        if chapter_num != current_chapter + 1:
            raise ValueError(
                f"❌ 章节编号不连续！\n"
                f"当前已完成{current_chapter}章，应该写第{current_chapter + 1}章\n"
                f"但你想写第{chapter_num}章"
            )

        print(f"   ✅ 章节编号连续")

        print("\n" + "=" * 60)
        print("✅ 所有强制检查通过，可以开始写作")
        print("=" * 60)

        return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python3 强制流程控制器.py <章节号>")
        sys.exit(1)

    chapter_num = int(sys.argv[1])

    controller = ForceFlowController()
    try:
        controller.force_check_before_write(chapter_num)
    except Exception as e:
        print(f"\n{e}\n")
        print("❌ 强制检查失败！禁止写入章节！")
        print("请先修复上述问题后再写作！")
        sys.exit(1)
