#!/usr/bin/env python3
"""
《大明1900》状态验证器
防止AI失忆综合征
"""

import json
from pathlib import Path
from typing import Dict, List, Set

PROJECT_ROOT = Path(__file__).parent.parent.parent
AUTOMATION_DIR = PROJECT_ROOT / "automation"
STATE_FILE = AUTOMATION_DIR / "state.json"
PHYSICAL_PROFILES_FILE = AUTOMATION_DIR / "character_physical_profiles.json"
CHECKPOINTS_DIR = AUTOMATION_DIR / "checkpoints"

class StateVerifier:
    """状态验证器 - 防止死人复活、断腿重生等Bug"""

    def __init__(self):
        self.state = self.load_json(STATE_FILE)
        self.physical_profiles = self.load_json(PHYSICAL_PROFILES_FILE)
        self.deaths: Set[str] = set()
        self.amputations: Dict[str, List[str]] = {}
        self.scars: Dict[str, List[str]] = {}

        self._initialize_immutable_state()

    def load_json(self, file_path: Path) -> dict:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _initialize_immutable_state(self):
        """初始化不可变状态"""
        for char_name, char_data in self.state["characters"].items():
            # 记录死亡
            if not char_data.get("存活", True):
                self.deaths.add(char_name)

            # 记录残疾
            if "残疾" in char_data.get("物理状态", {}):
                for disability in char_data["物理状态"]["残疾"]:
                    if char_name not in self.amputations:
                        self.amputations[char_name] = []
                    self.amputations[char_name].append(disability)

            # 记录伤痕
            if "伤痕" in char_data.get("物理状态", {}):
                if char_name not in self.scars:
                    self.scars[char_name] = []
                self.scars[char_name].extend(char_data["物理状态"]["伤痕"])

    def verify_chapter(self, chapter_content: str, chapter_num: int) -> List[str]:
        """验证章节内容的一致性"""
        errors = []

        # 1. 检查死人是否复活
        for dead_person in self.deaths:
            if self._person_acts_alive(chapter_content, dead_person):
                errors.append(
                    f"❌ 第{chapter_num}章：{dead_person}已死亡，但出现了行动描写"
                )

        # 2. 检查残疾是否被违反
        for char_name, disabilities in self.amputations.items():
            for disability in disabilities:
                if self._disability_violated(chapter_content, char_name, disability):
                    errors.append(
                        f"❌ 第{chapter_num}章：{char_name}{disability}，但使用了缺失肢体"
                    )

        # 3. 检查伤痕是否被遗忘
        for char_name, scars in self.scars.items():
            for scar in scars:
                # 如果章节提到该人物，检查是否提到关键伤痕（可选，不强制）
                pass

        return errors

    def _person_acts_alive(self, content: str, person: str) -> bool:
        """检查死人是否有行动描写"""
        # 简化版本：检查是否有"XX走了"、"XX拿起"等行动动词
        action_patterns = [
            f"{person}走", f"{person}跑", f"{person}拿", f"{person}说",
            f"{person}看", f"{person}想", f"{person}笑"
        ]
        return any(pattern in content for pattern in action_patterns)

    def _disability_violated(self, content: str, char_name: str, disability: str) -> bool:
        """检查残疾是否被违反"""
        if "缺失左臂" in disability:
            # 检查是否使用了左手
            violations = [
                f"{char_name}用左手", f"{char_name}的左手", f"{char_name}左手"
            ]
            return any(v in content for v in violations)
        return False

    def update_state_from_chapter(self, chapter_content: str, chapter_num: int):
        """从章节内容更新状态"""
        # 提取新死亡
        new_deaths = self._extract_deaths(chapter_content)
        for dead_person in new_deaths:
            self.deaths.add(dead_person)
            self.state["characters"][dead_person]["存活"] = False
            print(f"💀 第{chapter_num}章：{dead_person}死亡")

        # 提取新伤痕
        new_injuries = self._extract_injuries(chapter_content)
        for char_name, injury in new_injuries:
            if char_name not in self.scars:
                self.scars[char_name] = []
            self.scars[char_name].append(injury)
            print(f"🩸 第{chapter_num}章：{char_name}受伤 - {injury}")

        # 保存更新后的状态
        self._save_state()

    def _extract_deaths(self, content: str) -> List[str]:
        """提取死亡事件（简化版本）"""
        deaths = []
        # 实际需要NLP分析
        death_keywords = ["死了", "被杀", "阵亡", "牺牲"]
        for char_name in self.state["characters"].keys():
            if any(f"{char_name}{kw}" in content for kw in death_keywords):
                deaths.append(char_name)
        return deaths

    def _extract_injuries(self, content: str) -> List[tuple]:
        """提取受伤事件（简化版本）"""
        injuries = []
        # 实际需要NLP分析
        return injuries

    def _save_state(self):
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    def generate_state_summary(self) -> str:
        """生成状态摘要，供AI生成下一章时参考"""
        summary = "## 当前状态摘要\n\n"

        summary += "### 已死亡人物（不可复活）\n"
        for dead in self.deaths:
            summary += f"- {dead}\n"

        summary += "\n### 残疾人物（不可恢复）\n"
        for char_name, disabilities in self.amputations.items():
            summary += f"- {char_name}: {', '.join(disabilities)}\n"

        summary += "\n### 永久伤痕（不可消失）\n"
        for char_name, scars in self.scars.items():
            summary += f"- {char_name}: {', '.join(scars)}\n"

        return summary


def main():
    import argparse
    parser = argparse.ArgumentParser(description='状态验证器')
    parser.add_argument('--verify', type=str, help='验证指定章节文件')
    parser.add_argument('--summary', action='store_true', help='生成状态摘要')

    args = parser.parse_args()
    verifier = StateVerifier()

    if args.verify:
        with open(args.verify, 'r', encoding='utf-8') as f:
            content = f.read()
        errors = verifier.verify_chapter(content, chapter_num=1)
        if errors:
            print("❌ 发现一致性错误：")
            for e in errors:
                print(f"  {e}")
        else:
            print("✅ 一致性验证通过")
    elif args.summary:
        print(verifier.generate_state_summary())
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
