#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
时间线质控Agent
确保章节时间线连续性和一致性
"""

import re
import json
from datetime import datetime, timedelta
from pathlib import Path
import sys

class TimelineValidator:
    """时间线验证器"""

    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.timeline_file = Path(project_root) / "automation" / "config" / "timeline.json"

        # 加载时间线配置
        with open(self.timeline_file, 'r', encoding='utf-8') as f:
            self.timeline_config = json.load(f)

    def extract_chapter_time(self, chapter_content):
        """提取章节开头的时间标记"""
        # 匹配格式：1900年十月十五 或 1900年10月15日
        pattern = r'^(\d{4})年(\d{1,2}|十[一二]?|[一二三四五六七八九十]+)月(\d{1,2}|十[一二三四五六七八九]?|二?十[一二三四五六七八九]?|[一二三四五六七八九十]+)日?'
        lines = chapter_content.split('\n')

        for line in lines[:10]:  # 只检查前10行
            match = re.match(pattern, line.strip())
            if match:
                year = int(match.group(1))
                month = self.chinese_num_to_int(match.group(2))
                day = self.chinese_num_to_int(match.group(3))
                return (year, month, day)

        return None

    def chinese_num_to_int(self, chinese_num):
        """中文数字转阿拉伯数字"""
        if chinese_num.isdigit():
            return int(chinese_num)

        mapping = {
            "一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
            "六": 6, "七": 7, "八": 8, "九": 9, "十": 10,
            "十一": 11, "十二": 12, "十三": 13, "十四": 14, "十五": 15,
            "十六": 16, "十七": 17, "十八": 18, "十九": 19, "二十": 20,
            "二十一": 21, "二十二": 22, "二十三": 23, "二十四": 24, "二十五": 25,
            "二十六": 26, "二十七": 27, "二十八": 28, "二十九": 29, "三十": 30,
            "三十一": 31
        }
        return mapping.get(chinese_num, None)

    def validate_timeline_continuity(self, chapter_num, current_time):
        """验证时间连续性"""
        timeline_log = self.timeline_config.get("timeline_log", [])

        if not timeline_log:
            return {"valid": True, "message": "第一章，无需检查连续性"}

        # 获取上一章时间
        prev_entry = timeline_log[-1]
        prev_time = tuple(prev_entry["time_tuple"])

        prev_date = datetime(*prev_time)
        curr_date = datetime(*current_time)

        # 检查时间倒流
        if curr_date < prev_date:
            return {
                "valid": False,
                "error": "P0_TIME_REVERSAL",
                "message": f"时间倒流：第{chapter_num}章({curr_date.strftime('%Y年%m月%d日')}) 早于 第{prev_entry['chapter']}章({prev_date.strftime('%Y年%m月%d日')})"
            }

        # 检查时间间隔
        delta = curr_date - prev_date
        max_gap = self.timeline_config["constraints"]["max_gap_days"]
        warning_gap = self.timeline_config["constraints"]["warning_gap_days"]

        if delta.days > max_gap:
            return {
                "valid": False,
                "error": "P1_TIME_GAP_TOO_LARGE",
                "message": f"时间间隔过大：第{prev_entry['chapter']}章到第{chapter_num}章间隔{delta.days}天（建议<={max_gap}天）"
            }

        if delta.days > warning_gap:
            return {
                "valid": True,
                "warning": "P2_TIME_GAP_WARNING",
                "message": f"时间间隔警告：间隔{delta.days}天（建议<={warning_gap}天）"
            }

        return {
            "valid": True,
            "message": f"时间连续性正常，间隔{delta.days}天"
        }

    def validate_timeline_range(self, chapter_num, year):
        """验证章节号是否匹配时间线范围"""
        # 根据章节号确定预期年份范围
        if 1 <= chapter_num <= 70:
            expected_range = (1900, 1909)
            phase = "第一部（天工纪）"
        elif 71 <= chapter_num <= 165:
            expected_range = (1910, 1920)
            phase = "第二部（洪威纪）"
        elif 166 <= chapter_num <= 220:
            expected_range = (1920, 1921)
            phase = "第三部（泰安纪）"
        else:
            return {
                "valid": False,
                "error": "INVALID_CHAPTER_NUM",
                "message": f"章节号{chapter_num}超出范围（1-220）"
            }

        if not expected_range[0] <= year <= expected_range[1]:
            return {
                "valid": False,
                "error": "P0_TIME_OUT_OF_RANGE",
                "message": f"第{chapter_num}章年份{year}年不符合{phase}范围（{expected_range[0]}-{expected_range[1]}年）"
            }

        return {
            "valid": True,
            "message": f"年份{year}年符合{phase}范围"
        }

    def validate_chapter(self, chapter_num):
        """验证单个章节的时间线"""
        chapter_files = list(self.project_root.glob(f"chapters/第{chapter_num:03d}章*.md"))

        if not chapter_files:
            return {
                "chapter": chapter_num,
                "valid": True,
                "message": "章节文件不存在"
            }

        with open(chapter_files[0], 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取时间
        chapter_time = self.extract_chapter_time(content)

        if not chapter_time:
            return {
                "chapter": chapter_num,
                "valid": False,
                "error": "P0_NO_TIME_MARKER",
                "message": "章节未标注时间"
            }

        year, month, day = chapter_time

        # 验证时间线范围
        range_result = self.validate_timeline_range(chapter_num, year)

        # 验证时间连续性
        continuity_result = self.validate_timeline_continuity(chapter_num, chapter_time)

        # 综合结果
        errors = []
        warnings = []

        if not range_result.get("valid", True):
            errors.append(range_result)

        if not continuity_result.get("valid", True):
            if "error" in continuity_result:
                errors.append(continuity_result)
            elif "warning" in continuity_result:
                warnings.append(continuity_result)

        return {
            "chapter": chapter_num,
            "time": f"{year}年{month}月{day}日",
            "time_tuple": chapter_time,
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

    def update_timeline_log(self, chapter_num, time_tuple):
        """更新时间线日志"""
        self.timeline_config["last_chapter"] = chapter_num
        self.timeline_config["last_time"] = f"{time_tuple[0]}年{time_tuple[1]}月{time_tuple[2]}日"

        self.timeline_config["timeline_log"].append({
            "chapter": chapter_num,
            "time": f"{time_tuple[0]}年{time_tuple[1]}月{time_tuple[2]}日",
            "time_tuple": list(time_tuple)
        })

        # 保存
        with open(self.timeline_file, 'w', encoding='utf-8') as f:
            json.dump(self.timeline_config, f, ensure_ascii=False, indent=2)

    def print_report(self, result):
        """打印验证报告"""
        print(f"\n{'='*60}")
        print(f"时间线验证报告")
        print(f"{'='*60}\n")

        print(f"章节：第{result['chapter']:03d}章")

        if "time" in result:
            print(f"时间：{result['time']}\n")

        if result["valid"]:
            print("✅ 时间线验证通过")

            if result.get("warnings"):
                print("\n警告：")
                for warning in result["warnings"]:
                    print(f"  ⚠️ {warning['message']}")
        else:
            print("❌ 时间线验证失败\n")
            print("错误：")
            for error in result["errors"]:
                print(f"  🔴 [{error['error']}] {error['message']}")

        print(f"\n{'='*60}\n")
        return result["valid"]

def main():
    if len(sys.argv) < 2:
        print("用法: python timeline_validator.py <章节号>")
        print("示例: python timeline_validator.py 10")
        sys.exit(1)

    chapter_num = int(sys.argv[1])
    project_root = Path(__file__).parent.parent.parent

    validator = TimelineValidator(project_root)
    result = validator.validate_chapter(chapter_num)
    passed = validator.print_report(result)

    sys.exit(0 if passed else 1)

if __name__ == "__main__":
    main()
