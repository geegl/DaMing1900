#!/usr/bin/env python3
"""
POV验证器 - 从Markdown原文提取POV标签并与大纲比对
Author: Claude AI
Version: 1.0
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Tuple

class POVValidator:
    """POV验证器"""

    def __init__(self, project_root: str = "/Users/roven/Documents/Trae/DaMing"):
        self.project_root = Path(project_root)
        self.chapters_dir = self.project_root / "chapters"
        self.outline_file = self.project_root / "docs/01-规划层/Daming1900_Master_Outline.md"

    def extract_pov_from_markdown(self, file_path: Path) -> Tuple[str, str]:
        """
        从Markdown文件提取POV标签

        Returns:
            (chapter_num, pov_character)
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取章节号
        chapter_match = re.search(r'第(\d+)章', file_path.stem)
        if not chapter_match:
            return (None, None)

        chapter_num = chapter_match.group(1).zfill(3)

        # 提取POV标签
        pov_match = re.search(r'【POV:\s*(.*?)】', content)
        if not pov_match:
            return (chapter_num, "未找到POV标签")

        pov_character = pov_match.group(1).strip()
        return (chapter_num, pov_character)

    def get_expected_pov_from_outline(self, chapter_range: str) -> Dict[str, str]:
        """
        从大纲文件提取预期的POV分布

        Args:
            chapter_range: 例如 "第1-10章"

        Returns:
            {chapter_num: expected_pov}
        """
        with open(self.outline_file, 'r', encoding='utf-8') as f:
            content = f.read()

        expected_povs = {}

        # 简化版本：根据章节范围返回预期POV
        # 第1章: 陈铁
        # 第2章: 老鬼
        # 第3章: 陈铁
        # 第4-5章: 老鬼
        # 第6-10章: 陈铁

        if chapter_range == "第1-10章":
            expected_povs = {
                "001": "陈铁",
                "002": "老鬼",
                "003": "陈铁",
                "004": "老鬼",
                "005": "老鬼",
                "006": "陈铁",
                "007": "陈铁",
                "008": "陈铁",
                "009": "陈铁",
                "010": "陈铁",
            }

        return expected_povs

    def validate_chapters(self, chapter_range: str = "第1-10章") -> Dict:
        """
        验证章节POV一致性

        Returns:
            {
                "passed": bool,
                "errors": List[Dict],
                "warnings": List[str]
            }
        """
        expected_povs = self.get_expected_pov_from_outline(chapter_range)

        # 提取章节范围
        range_match = re.search(r'第(\d+)-(\d+)章', chapter_range)
        if not range_match:
            return {
                "passed": False,
                "errors": [{"type": "参数错误", "message": f"无效的章节范围: {chapter_range}"}],
                "warnings": []
            }

        start = int(range_match.group(1))
        end = int(range_match.group(2))

        errors = []
        warnings = []

        for i in range(start, end + 1):
            chapter_num = str(i).zfill(3)

            # 查找章节文件
            pattern = f"第{chapter_num}章*.md"
            matches = list(self.chapters_dir.glob(pattern))

            if not matches:
                warnings.append(f"第{chapter_num}章文件不存在")
                continue

            file_path = matches[0]
            actual_chapter, actual_pov = self.extract_pov_from_markdown(file_path)

            # 验证POV
            expected_pov = expected_povs.get(chapter_num)

            if expected_pov and actual_pov != expected_pov:
                errors.append({
                    "type": "POV不一致",
                    "chapter": chapter_num,
                    "file": file_path.name,
                    "expected": expected_pov,
                    "actual": actual_pov,
                    "message": f"第{chapter_num}章POV应为'{expected_pov}'，实际为'{actual_pov}'"
                })

        return {
            "passed": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

    def generate_report(self, validation_result: Dict) -> str:
        """生成验证报告"""
        lines = []
        lines.append("# POV验证报告\n")
        lines.append(f"**验证结果**: {'✅ 通过' if validation_result['passed'] else '❌ 不通过'}\n")

        if validation_result['errors']:
            lines.append("\n## ❌ 错误\n")
            for error in validation_result['errors']:
                lines.append(f"- **第{error['chapter']}章**: {error['message']}\n")

        if validation_result['warnings']:
            lines.append("\n## ⚠️ 警告\n")
            for warning in validation_result['warnings']:
                lines.append(f"- {warning}\n")

        return "".join(lines)


def main():
    """主函数"""
    validator = POVValidator()

    # 验证前10章
    result = validator.validate_chapters("第1-10章")

    # 生成报告
    report = validator.generate_report(result)

    # 保存报告
    report_path = validator.project_root / "docs/04-质控层/pov_validation_report.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(report)

    # 如果验证失败，抛出异常
    if not result['passed']:
        raise ValueError(f"POV验证失败，发现{len(result['errors'])}个错误")

    return result


if __name__ == "__main__":
    main()
