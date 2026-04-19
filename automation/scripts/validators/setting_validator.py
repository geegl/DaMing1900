#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设定一致性质控Agent
确保货币、技术、官制、阶级等设定的一致性
"""

import re
import json
from pathlib import Path
import sys

class SettingValidator:
    """设定一致性验证器"""

    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.bible_file = self.project_root / "docs" / "00-宪法层" / "Daming1900_Bible.md"

        # 核心设定规则
        self.core_settings = {
            "货币设定": {
                "铁币氧化": "1年内氧化为铁粉",
                "锈税": "月贬值率10%"
            },
            "技术代差": {
                "落后西方": "8-20年"
            },
            "官制设定": {
                "三司制": ["布政使（民政）", "按察使（司法）", "都指挥使（军事）"],
                "禁止": ["总督", "巡抚"]
            },
            "阶级设定": {
                "工籍烙印": "左臂烙印，如'津铸丙字七十四号'",
                "贱籍": "比工籍更底层"
            }
        }

    def validate_currency_setting(self, chapter_content):
        """验证货币设定一致性"""
        errors = []
        warnings = []

        # 检查铁钱相关描述
        if "铁钱" in chapter_content or "铁币" in chapter_content:
            # 检查是否有矛盾的描述
            # 例如：如果提到"存了4年铁钱"，应该提到氧化或兑换
            if "存了" in chapter_content and "年" in chapter_content:
                # 检查是否提到氧化或兑换
                if "氧化" not in chapter_content and "兑换" not in chapter_content and "白银" not in chapter_content:
                    warnings.append("提到长期存铁钱，但未提及氧化问题或兑换行为")

        # 检查铁钱颜色
        if "铜绿色" in chapter_content and "铁钱" in chapter_content:
            errors.append("铁钱应为红褐色或黑色（铁锈），不是铜绿色")

        return {"errors": errors, "warnings": warnings}

    def validate_technology_setting(self, chapter_content):
        """验证技术设定一致性"""
        errors = []
        warnings = []

        # 检查技术代差
        # 如果提到德国技术，应该体现落后
        if "德国" in chapter_content and "技术" in chapter_content:
            if "领先" in chapter_content or "先进" in chapter_content:
                # 应该提到落后多少年
                if "落后" not in chapter_content and "代差" not in chapter_content:
                    warnings.append("提到德国技术领先，但未体现大明落后8-20年的设定")

        # 检查技术时间线
        # 蒸汽轮机：1890-1910年间开始应用
        if "蒸汽轮机" in chapter_content:
            # 提取年份
            year_match = re.search(r'(\d{4})年', chapter_content)
            if year_match:
                year = int(year_match.group(1))
                if year < 1890:
                    errors.append(f"蒸汽轮机在{year}年出现，但实际应该在1890年后")

        return {"errors": errors, "warnings": warnings}

    def validate_official_system(self, chapter_content):
        """验证官制设定一致性"""
        errors = []
        warnings = []

        # 检查清朝官职
        forbidden_officials = ["总督", "巡抚", "军机处", "军机大臣", "理藩院", "提督", "总兵"]

        for official in forbidden_officials:
            if official in chapter_content:
                errors.append(f"发现清朝官职'{official}'，应使用明朝官制（三司制）")

        # 检查明朝官职是否正确
        if "布政使" in chapter_content:
            # 应该是民政，不是"藩台"
            if "军事" in chapter_content and "布政使" in chapter_content:
                warnings.append("布政使负责民政，军事应由都指挥使负责")

        return {"errors": errors, "warnings": warnings}

    def validate_class_system(self, chapter_content):
        """验证阶级设定一致性"""
        errors = []
        warnings = []

        # 检查工籍烙印
        if "烙印" in chapter_content:
            # 应该在左臂
            if "右臂" in chapter_content and "烙印" in chapter_content:
                errors.append("工籍烙印应该在左臂，不是右臂")

        # 检查贱籍
        if "贱籍" in chapter_content or "丐户" in chapter_content:
            # 贱籍应该是最底层
            if "高于" in chapter_content and "工籍" in chapter_content:
                errors.append("贱籍应该比工籍更低，不能高于工籍")

        return {"errors": errors, "warnings": warnings}

    def validate_chapter(self, chapter_num):
        """验证单个章节的设定一致性"""
        chapter_files = list(self.project_root.glob(f"chapters/第{chapter_num:03d}章*.md"))

        if not chapter_files:
            return {
                "chapter": chapter_num,
                "valid": True,
                "message": "章节文件不存在"
            }

        with open(chapter_files[0], 'r', encoding='utf-8') as f:
            content = f.read()

        all_errors = []
        all_warnings = []

        # 验证货币设定
        currency_result = self.validate_currency_setting(content)
        all_errors.extend(currency_result["errors"])
        all_warnings.extend(currency_result["warnings"])

        # 验证技术设定
        tech_result = self.validate_technology_setting(content)
        all_errors.extend(tech_result["errors"])
        all_warnings.extend(tech_result["warnings"])

        # 验证官制设定
        official_result = self.validate_official_system(content)
        all_errors.extend(official_result["errors"])
        all_warnings.extend(official_result["warnings"])

        # 验证阶级设定
        class_result = self.validate_class_system(content)
        all_errors.extend(class_result["errors"])
        all_warnings.extend(class_result["warnings"])

        return {
            "chapter": chapter_num,
            "errors": all_errors,
            "warnings": all_warnings,
            "valid": len(all_errors) == 0
        }

    def print_report(self, result):
        """打印验证报告"""
        print(f"\n{'='*60}")
        print(f"设定一致性验证报告")
        print(f"{'='*60}\n")

        print(f"章节：第{result['chapter']:03d}章\n")

        if result["valid"]:
            print("✅ 设定一致性验证通过")

            if result.get("warnings"):
                print("\n警告：")
                for warning in result["warnings"]:
                    print(f"  ⚠️ {warning}")
        else:
            print("❌ 设定一致性验证失败\n")
            print("错误：")
            for error in result["errors"]:
                print(f"  🔴 {error}")

            if result.get("warnings"):
                print("\n警告：")
                for warning in result["warnings"]:
                    print(f"  ⚠️ {warning}")

        print(f"\n{'='*60}\n")
        return result["valid"]

def main():
    if len(sys.argv) < 2:
        print("用法: python setting_validator.py <章节号>")
        print("示例: python setting_validator.py 10")
        sys.exit(1)

    chapter_num = int(sys.argv[1])
    project_root = Path(__file__).parent.parent.parent

    validator = SettingValidator(project_root)
    result = validator.validate_chapter(chapter_num)
    passed = validator.print_report(result)

    sys.exit(0 if passed else 1)

if __name__ == "__main__":
    main()
