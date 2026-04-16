#!/usr/bin/env python3
"""
《大明1900》检查点管理器 v2.0
强化版：强制存档物理状态变化
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

PROJECT_ROOT = Path(__file__).parent.parent.parent
AUTOMATION_DIR = PROJECT_ROOT / "automation"
CHECKPOINTS_DIR = AUTOMATION_DIR / "checkpoints"
STATE_FILE = AUTOMATION_DIR / "state.json"
PHYSICAL_PROFILES_FILE = AUTOMATION_DIR / "character_physical_profiles.json"

class CheckpointManagerV2:
    """检查点管理器 v2.0 - 强化物理状态追踪"""

    def __init__(self):
        self.state = self.load_json(STATE_FILE)
        self.physical_profiles = self.load_json(PHYSICAL_PROFILES_FILE)

    def load_json(self, file_path: Path) -> dict:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_json(self, file_path: Path, data: dict):
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def create_checkpoint(self, chapter_num: int, chapter_content: str = ""):
        """创建检查点 - 强制提取物理状态变化"""

        # 提取状态变化
        deaths = self._extract_deaths(chapter_content)
        injuries = self._extract_injuries(chapter_content)
        item_changes = self._extract_item_changes(chapter_content)
        location_changes = self._extract_location_changes(chapter_content)

        checkpoint = {
            "章节": chapter_num,
            "时间戳": datetime.now().isoformat(),

            "世界状态": {
                "年份": self.state["world_state"]["时间"]["年份"],
                "月份": self.state["world_state"]["时间"]["月份"],
                "当前事件": self.state["world_state"]["当前事件"]
            },

            "物理状态变化": {
                "死亡": deaths,
                "受伤": injuries,
                "物品变化": item_changes
            },

            "位置变化": location_changes,

            "人物状态快照": self._create_character_snapshot(),

            "剧情进展": {
                "揭露的秘密": self.state["plot_state"]["已揭露秘密"],
                "进行中阴谋": self.state["plot_state"]["进行中阴谋"],
                "待复仇事件": self.state["plot_state"]["待复仇事件"]
            }
        }

        # 保存检查点
        CHECKPOINTS_DIR.mkdir(parents=True, exist_ok=True)
        checkpoint_file = CHECKPOINTS_DIR / f"checkpoint_{chapter_num:03d}.json"
        self.save_json(checkpoint_file, checkpoint)

        # 更新主状态文件
        self._update_main_state(deaths, injuries, item_changes, location_changes, chapter_num)

        print(f"✅ 检查点已创建：第{chapter_num}章")
        if deaths:
            print(f"  💀 死亡: {', '.join(deaths)}")
        if injuries:
            print(f"  🩸 受伤: {len(injuries)}起")

        return checkpoint

    def _extract_deaths(self, content: str) -> List[Dict]:
        """提取死亡事件"""
        deaths = []
        # 简化版本，实际需要NLP
        death_keywords = ["死了", "被杀", "阵亡", "牺牲", "断气"]
        for char_name in self.state["characters"].keys():
            if any(f"{char_name}{kw}" in content for kw in death_keywords):
                deaths.append({
                    "人物": char_name,
                    "章节": "需要NLP提取具体情节"
                })
        return deaths

    def _extract_injuries(self, content: str) -> List[Dict]:
        """提取受伤事件"""
        injuries = []
        # 简化版本，实际需要NLP
        return injuries

    def _extract_item_changes(self, content: str) -> List[Dict]:
        """提取物品变化"""
        changes = []
        # 简化版本
        return changes

    def _extract_location_changes(self, content: str) -> List[Dict]:
        """提取位置变化"""
        changes = []
        # 简化版本
        return changes

    def _create_character_snapshot(self) -> Dict:
        """创建人物状态快照"""
        snapshot = {}
        for char_name, char_data in self.state["characters"].items():
            snapshot[char_name] = {
                "位置": char_data["基本信息"]["位置"],
                "状态": char_data["基本信息"]["状态"],
                "存活": char_data.get("存活", True),
                "伤痕": char_data.get("物理状态", {}).get("伤痕", []),
                "残疾": char_data.get("物理状态", {}).get("残疾", [])
            }
        return snapshot

    def _update_main_state(self, deaths, injuries, item_changes, location_changes, chapter_num):
        """更新主状态文件"""
        # 更新死亡状态
        for death in deaths:
            char_name = death["人物"]
            if char_name in self.state["characters"]:
                self.state["characters"][char_name]["存活"] = False
                self.state["characters"][char_name]["基本信息"]["状态"] = "死亡"

        # 更新生成状态
        self.state["generation_state"]["last_checkpoint"] = chapter_num
        self.state["generation_state"]["chapters_generated"] = chapter_num

        # 保存
        self.save_json(STATE_FILE, self.state)

    def load_checkpoint(self, chapter_num: int) -> dict:
        """加载检查点"""
        checkpoint_file = CHECKPOINTS_DIR / f"checkpoint_{chapter_num:03d}.json"
        if checkpoint_file.exists():
            return self.load_json(checkpoint_file)
        return None

    def generate_context_for_next_chapter(self, chapter_num: int) -> str:
        """为下一章生成上下文"""
        checkpoint = self.load_checkpoint(chapter_num - 1)
        if not checkpoint:
            return "这是第一章，无前文状态"

        context = f"""
## 第{chapter_num - 1}章状态存档

### 世界状态
- 时间: {checkpoint['世界状态']['年份']}年{checkpoint['世界状态']['月份']}月
- 当前事件: {checkpoint['世界状态']['当前事件']}

### 物理状态变化
- 死亡: {checkpoint['物理状态变化']['死亡']}
- 受伤: {checkpoint['物理状态变化']['受伤']}
- 物品变化: {checkpoint['物理状态变化']['物品变化']}

### 关键人物状态
"""
        for char_name, char_data in checkpoint['人物状态快照'].items():
            context += f"- {char_name}: {char_data['状态']}, 位置: {char_data['位置']}\n"
            if char_data['伤痕']:
                context += f"  伤痕: {', '.join(char_data['伤痕'])}\n"
            if char_data['残疾']:
                context += f"  残疾: {', '.join(char_data['残疾'])}\n"

        return context


def main():
    import argparse
    parser = argparse.ArgumentParser(description='检查点管理器 v2.0')
    parser.add_argument('--create', type=int, help='创建指定章节的检查点')
    parser.add_argument('--load', type=int, help='加载指定章节的检查点')
    parser.add_argument('--context', type=int, help='生成下一章的上下文')

    args = parser.parse_args()
    manager = CheckpointManagerV2()

    if args.create:
        manager.create_checkpoint(args.create)
    elif args.load:
        checkpoint = manager.load_checkpoint(args.load)
        if checkpoint:
            print(json.dumps(checkpoint, ensure_ascii=False, indent=2))
        else:
            print(f"❌ 检查点不存在: 第{args.load}章")
    elif args.context:
        print(manager.generate_context_for_next_chapter(args.context))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
