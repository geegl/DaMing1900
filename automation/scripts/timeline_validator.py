#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
时间线验证脚本
验证章节中的年号计算是否正确，防止时间线混乱
"""

import re
import sys
from pathlib import Path

class TimelineValidator:
    """时间线验证器"""

    # 时间线设定（来自MEMORY.md）
    TIMELINE_RULES = {
        "天工": {
            "start_year": 1891,
            "end_year": 1909,
            "formula": lambda x: 1890 + x,  # 天工X年 = 1890 + X
            "emperor": "天工帝朱靖镇"
        },
        "洪威": {
            "start_year": 1909,
            "end_year": 1920,
            "formula": lambda x: 1908 + x,  # 洪威X年 = 1908 + X
            "emperor": "洪威帝朱靖渊"
        },
        "泰安": {
            "start_year": 1919,
            "end_year": 1921,
            "formula": lambda x: 1918 + x,  # 泰安X年 = 1918 + X
            "emperor": "泰安帝"
        }
    }

    def __init__(self, project_root):
        self.project_root = Path(project_root)

    def extract_year_markers(self, text):
        """提取文本中的所有年号标记"""
        pattern = r'(天工|洪威|泰安)(\d+|元|二|三|四|五|六|七|八|九|十|十一|十二|十三|十四|十五|十六|十七|十八|十九|二十)年'
        matches = re.findall(pattern, text)
        return matches

    def chinese_num_to_int(self, chinese_num):
        """中文数字转阿拉伯数字"""
        mapping = {
            "元": 1, "一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
            "六": 6, "七": 7, "八": 8, "九": 9, "十": 10,
            "十一": 11, "十二": 12, "十三": 13, "十四": 14, "十五": 15,
            "十六": 16, "十七": 17, "十八": 18, "十九": 19, "二十": 20
        }
        return mapping.get(chinese_num, int(chinese_num) if chinese_num.isdigit() else None)

    def validate_chapter(self, chapter_num):
        """验证单个章节的时间线"""
        chapter_files = list(self.project_root.glob(f"chapters/第{chapter_num:03d}章*.md"))

        if not chapter_files:
            return {
                "chapter": chapter_num,
                "valid": True,
                "message": "章节文件不存在或未找到年号"
            }

        chapter_file = chapter_files[0]
        with open(chapter_file, 'r', encoding='utf-8') as f:
            content = f.read()

        year_markers = self.extract_year_markers(content)
        errors = []

        for era_name, year_text in year_markers:
            year_num = self.chinese_num_to_int(year_text)
            if year_num is None:
                errors.append(f"无法解析年号：{era_name}{year_text}年")
                continue

            # 计算实际年份
            if era_name in self.TIMELINE_RULES:
                rule = self.TIMELINE_RULES[era_name]
                actual_year = rule["formula"](year_num)

                # 检查章节号是否匹配时间线
                expected_chapter_range = self.get_chapter_range(era_name)
                if expected_chapter_range:
                    start_ch, end_ch = expected_chapter_range
                    if not (start_ch <= chapter_num <= end_ch):
                        errors.append(
                            f"时间线错误：第{chapter_num}章出现'{era_name}{year_text}年'（{actual_year}年），"
                            f"但该年号应在第{start_ch}-{end_ch}章出现"
                        )

        return {
            "chapter": chapter_num,
            "year_markers": year_markers,
            "errors": errors,
            "valid": len(errors) == 0
        }

    def get_chapter_range(self, era_name):
        """获取年号对应的章节范围"""
        if era_name == "天工":
            return (1, 70)  # 第1-70章是天工纪
        elif era_name == "洪威":
            return (71, 165)  # 第71-165章是洪威纪
        elif era_name == "泰安":
            return (166, 220)  # 第166-220章是泰安纪
        return None

    def validate_batch(self, batch_num):
        """验证整个批次的时间线"""
        start_chapter = (batch_num - 1) * 10 + 1
        end_chapter = batch_num * 10

        results = []
        for ch in range(start_chapter, end_chapter + 1):
            result = self.validate_chapter(ch)
            results.append(result)

        return {
            "batch": batch_num,
            "chapters": results,
            "valid": all(r["valid"] for r in results)
        }

    def print_report(self, result):
        """打印验证报告"""
        print(f"\n{'='*60}")
        print(f"时间线验证报告")
        print(f"{'='*60}\n")

        if "batch" in result:
            print(f"批次：Batch {result['batch']:02d}")
            print(f"章节范围：第{(result['batch']-1)*10+1}-{result['batch']*10}章\n")

            for ch_result in result["chapters"]:
                if not ch_result["valid"]:
                    print(f"❌ 第{ch_result['chapter']:03d}章：")
                    for error in ch_result["errors"]:
                        print(f"   {error}")

            if result["valid"]:
                print("✅ 所有章节时间线正确")
        else:
            if result["valid"]:
                print(f"✅ 第{result['chapter']:03d}章时间线正确")
            else:
                print(f"❌ 第{result['chapter']:03d}章时间线错误：")
                for error in result["errors"]:
                    print(f"   {error}")

        print(f"\n{'='*60}\n")
        return result["valid"]

def main():
    if len(sys.argv) < 2:
        print("用法: python timeline_validator.py <章节号或批次号>")
        print("示例:")
        print("  python timeline_validator.py 70        # 验证第70章")
        print("  python timeline_validator.py batch 7   # 验证Batch 07")
        sys.exit(1)

    project_root = Path(__file__).parent.parent.parent
    validator = TimelineValidator(project_root)

    if sys.argv[1] == "batch":
        if len(sys.argv) < 3:
            print("错误：需要提供批次号")
            sys.exit(1)
        batch_num = int(sys.argv[2])
        result = validator.validate_batch(batch_num)
    else:
        chapter_num = int(sys.argv[1])
        result = validator.validate_chapter(chapter_num)

    passed = validator.print_report(result)
    sys.exit(0 if passed else 1)

if __name__ == "__main__":
    main()
