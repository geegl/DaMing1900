#!/usr/bin/env python3
"""
《大明1900》质量检查器
检查生成的章节是否符合规范
"""

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
CHAPTERS_DIR = PROJECT_ROOT / "automation" / "chapters"

class QualityChecker:
    """质量检查器"""

    def __init__(self):
        self.errors = []
        self.warnings = []

    def check_chapter(self, content: str, chapter_num: int) -> dict:
        """检查单章"""
        self.errors = []
        self.warnings = []

        # 1. 检查禁用词
        self.check_banned_words(content)

        # 2. 检查心理标签
        self.check_psychological_tags(content)

        # 3. 检查上帝视角
        self.check_god_view(content)

        # 4. 检查日常细节
        self.check_daily_details(content)

        # 5. 检查字数
        self.check_word_count(content)

        # 6. 检查悬念钩子
        self.check_hook(content)

        return {
            "chapter": chapter_num,
            "errors": self.errors,
            "warnings": self.warnings,
            "passed": len(self.errors) == 0
        }

    def check_banned_words(self, content: str):
        """检查禁用词"""
        banned = [
            "辫子", "瓜皮帽", "旗袍",  # 满清元素
            "魔法", "霓虹灯", "全息", "赛博", "真空管",  # 魔幻/高科技
            "我理解", "好的", "没问题", "总而言之"  # 客服腔
        ]
        for word in banned:
            if word in content:
                self.errors.append(f"禁用词：'{word}'")

    def check_psychological_tags(self, content: str):
        """检查心理标签"""
        patterns = [
            r"他很(愤怒|绝望|害怕|悲伤|开心)",
            r"她很(愤怒|绝望|害怕|悲伤|开心)",
            r"他感到(愤怒|绝望|害怕|悲伤)",
            r"她感到(愤怒|绝望|害怕|悲伤)",
            r"心中(涌起|升起|充满)了"
        ]
        for pattern in patterns:
            if re.search(pattern, content):
                self.warnings.append(f"心理标签：'{pattern}'，请用动作代替")

    def check_god_view(self, content: str):
        """检查上帝视角"""
        # 简化检查，实际需要更复杂的NLP
        god_view_hints = [
            "与此同时，在紫禁城",
            "与此同时，在江南",
            "与此同时，在兰芳",
            "就在这时，远在"
        ]
        for hint in god_view_hints:
            if hint in content:
                self.warnings.append(f"疑似上帝视角：'{hint}'")

    def check_daily_details(self, content: str):
        """检查日常细节"""
        detail_keywords = [
            "煤烟", "铁锈", "机油", "蒸汽", "煤",
            "扳手", "齿轮", "管道", "阀门"
        ]
        found = sum(1 for kw in detail_keywords if kw in content)
        if found < 3:
            self.warnings.append(f"日常细节不足：仅找到{found}个重工关键词，建议≥3")

    def check_word_count(self, content: str):
        """检查字数"""
        # 中文按字符计数
        char_count = len(content)
        if char_count < 2000:
            self.errors.append(f"字数不足：{char_count}字，需要≥2000字")
        elif char_count > 4000:
            self.warnings.append(f"字数过多：{char_count}字，建议≤3500字")

    def check_hook(self, content: str):
        """检查悬念钩子"""
        # 检查结尾是否有悬念
        last_500 = content[-500:] if len(content) > 500 else content

        hook_indicators = [
            "？", "……", "突然", "就在这时", "但是",
            "不知道", "没有回答", "沉默", "死一般的寂静"
        ]
        found = sum(1 for ind in hook_indicators if ind in last_500)
        if found < 1:
            self.warnings.append("结尾缺乏悬念钩子")

    def check_pov_consistency(self, content: str, expected_pov: str) -> bool:
        """检查POV一致性"""
        # 简化版本
        other_povs = {
            "陈铁": ["朱靖镇", "张廷远", "林霜降"],
            "老鬼": ["朱靖镇", "张廷远"],
            "朱靖渊": []
        }

        if expected_pov in other_povs:
            for other in other_povs[expected_pov]:
                # 检查是否出现其他POV的内心活动
                pattern = f"{other}(想|知道|明白|意识到)"
                if re.search(pattern, content):
                    self.errors.append(f"POV越界：'{other}'的内心活动不应出现在'{expected_pov}'视角中")
                    return False
        return True

    def generate_report(self, results: list) -> str:
        """生成检查报告"""
        report = "# 质量检查报告\n\n"

        total = len(results)
        passed = sum(1 for r in results if r["passed"])
        failed = total - passed

        report += f"## 总览\n- 总章节：{total}\n- 通过：{passed}\n- 失败：{failed}\n\n"

        if failed > 0:
            report += "## 失败章节\n"
            for r in results:
                if not r["passed"]:
                    report += f"\n### 第{r['chapter']}章\n"
                    for e in r["errors"]:
                        report += f"- ❌ {e}\n"

        if any(r["warnings"] for r in results):
            report += "\n## 警告\n"
            for r in results:
                if r["warnings"]:
                    report += f"\n### 第{r['chapter']}章\n"
                    for w in r["warnings"]:
                        report += f"- ⚠️ {w}\n"

        return report


def main():
    import argparse
    parser = argparse.ArgumentParser(description='质量检查器')
    parser.add_argument('--chapter', type=int, help='检查指定章节')
    parser.add_argument('--batch', type=str, help='批量检查，格式: start-end')
    parser.add_argument('--file', type=str, help='检查指定文件')

    args = parser.parse_args()
    checker = QualityChecker()

    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            content = f.read()
        result = checker.check_chapter(content, 0)
        print(f"通过: {result['passed']}")
        if result['errors']:
            print("错误:")
            for e in result['errors']:
                print(f"  ❌ {e}")
        if result['warnings']:
            print("警告:")
            for w in result['warnings']:
                print(f"  ⚠️ {w}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
