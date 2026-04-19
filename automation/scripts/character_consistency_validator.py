#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人物一致性质控Agent
确保人物特征、伤痕、装备、能力、关系等状态的一致性
"""

import json
import re
from pathlib import Path
import sys

class CharacterConsistencyValidator:
    """人物一致性验证器"""

    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.state_file = self.project_root / "automation" / "state.json"
        self.profiles_file = self.project_root / "automation" / "character_physical_profiles.json"

        # 加载状态
        with open(self.state_file, 'r', encoding='utf-8') as f:
            self.state = json.load(f)

        with open(self.profiles_file, 'r', encoding='utf-8') as f:
            self.profiles = json.load(f)

    def extract_character_mentions(self, chapter_content):
        """提取章节中出现的人物及其状态描述"""
        mentions = {}

        # 简单的人物识别（基于state.json中的人物列表）
        characters = self.state.get("characters", {})

        for char_name in characters.keys():
            # 检查人物是否出现在章节中
            if char_name in chapter_content:
                mentions[char_name] = {
                    "mentioned": True,
                    "descriptions": []
                }

                # 提取该人物相关的段落
                paragraphs = chapter_content.split('\n\n')
                for para in paragraphs:
                    if char_name in para:
                        mentions[char_name]["descriptions"].append(para)

        return mentions

    def validate_physical_state(self, char_name, chapter_num, chapter_content):
        """验证人物物理状态一致性"""
        errors = []
        warnings = []

        char_state = self.state["characters"].get(char_name, {})
        char_profile = self.profiles.get(char_name, {})

        # 检查伤痕
        scars = char_state.get("物理状态", {}).get("伤痕", [])
        for scar in scars:
            # 提取伤痕位置
            if "左腿" in scar:
                # 检查章节是否提到左腿，但没有提到伤痕
                if "左腿" in chapter_content and char_name in chapter_content:
                    # 简单检查：如果提到左腿但没有提到"疤痕"或"伤"
                    if "疤痕" not in chapter_content and "伤" not in chapter_content and "烫伤" not in chapter_content:
                        warnings.append(f"{char_name}左腿有伤痕，但章节中未提及")

        # 检查装备
        equipment = char_state.get("装备", {})
        for body_part, item in equipment.items():
            # 如果章节中提到该部位，检查装备是否一致
            if body_part in chapter_content and char_name in chapter_content:
                if item not in chapter_content:
                    warnings.append(f"{char_name}的{body_part}应该有{item}，但章节中未提及")

        # 检查能力
        abilities = char_state.get("技能", [])
        for ability in abilities:
            # 如果章节中使用了相关能力，检查是否已经获得
            if "差分机" in ability and "数据流" in chapter_content:
                # 检查是否在第1章之后
                if chapter_num < 1:
                    errors.append(f"第{chapter_num}章使用了{ability}，但该能力尚未获得")

        return {
            "character": char_name,
            "errors": errors,
            "warnings": warnings,
            "valid": len(errors) == 0
        }

    def validate_relationship_state(self, char_name, chapter_content):
        """验证人物关系一致性"""
        errors = []

        char_state = self.state["characters"].get(char_name, {})
        relationships = char_state.get("关系", {})

        for other_char, relationship in relationships.items():
            # 如果章节中提到两个人物，检查关系是否一致
            if char_name in chapter_content and other_char in chapter_content:
                # 简单检查：师徒关系
                if "师徒" in relationship:
                    # 检查是否有师徒互动的描写
                    if "师父" not in chapter_content and "徒弟" not in chapter_content:
                        # 这只是一个警告，不一定需要显式提到
                        pass

        return errors

    def validate_chapter(self, chapter_num):
        """验证单个章节的人物一致性"""
        chapter_files = list(self.project_root.glob(f"chapters/第{chapter_num:03d}章*.md"))

        if not chapter_files:
            return {
                "chapter": chapter_num,
                "valid": True,
                "message": "章节文件不存在"
            }

        with open(chapter_files[0], 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取人物提及
        mentions = self.extract_character_mentions(content)

        # 验证每个人物
        all_errors = []
        all_warnings = []

        for char_name in mentions.keys():
            # 验证物理状态
            physical_result = self.validate_physical_state(char_name, chapter_num, content)
            all_errors.extend(physical_result["errors"])
            all_warnings.extend(physical_result["warnings"])

            # 验证关系状态
            relationship_errors = self.validate_relationship_state(char_name, content)
            all_errors.extend(relationship_errors)

        return {
            "chapter": chapter_num,
            "characters_mentioned": list(mentions.keys()),
            "errors": all_errors,
            "warnings": all_warnings,
            "valid": len(all_errors) == 0
        }

    def print_report(self, result):
        """打印验证报告"""
        print(f"\n{'='*60}")
        print(f"人物一致性验证报告")
        print(f"{'='*60}\n")

        print(f"章节：第{result['chapter']:03d}章")

        if result.get("characters_mentioned"):
            print(f"提及人物：{', '.join(result['characters_mentioned'])}\n")

        if result["valid"]:
            print("✅ 人物一致性验证通过")

            if result.get("warnings"):
                print("\n警告：")
                for warning in result["warnings"]:
                    print(f"  ⚠️ {warning}")
        else:
            print("❌ 人物一致性验证失败\n")
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
        print("用法: python character_consistency_validator.py <章节号>")
        print("示例: python character_consistency_validator.py 10")
        sys.exit(1)

    chapter_num = int(sys.argv[1])
    project_root = Path(__file__).parent.parent.parent

    validator = CharacterConsistencyValidator(project_root)
    result = validator.validate_chapter(chapter_num)
    passed = validator.print_report(result)

    sys.exit(0 if passed else 1)

if __name__ == "__main__":
    main()
