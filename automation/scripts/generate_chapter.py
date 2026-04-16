#!/usr/bin/env python3
"""
《大明1900》章节生成流水线
版本: 4.2
"""

import json
import os
from datetime import datetime
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
AUTOMATION_DIR = PROJECT_ROOT / "automation"
OUTPUT_DIR = AUTOMATION_DIR / "output"
CHAPTERS_DIR = AUTOMATION_DIR / "chapters"
CHECKPOINTS_DIR = AUTOMATION_DIR / "checkpoints"

class ChapterGenerator:
    """章节生成器"""

    def __init__(self):
        self.state = self.load_state()
        self.bible = self.load_bible()
        self.outline = self.load_outline()
        self.engine_rules = self.load_engine_rules()

    def load_state(self) -> dict:
        """加载当前状态"""
        state_file = AUTOMATION_DIR / "state.json"
        if state_file.exists():
            with open(state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def save_state(self):
        """保存当前状态"""
        state_file = AUTOMATION_DIR / "state.json"
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    def load_bible(self) -> str:
        """加载设定圣经"""
        bible_file = DOCS_DIR / "00-宪法层" / "Daming1900_Bible.md"
        if bible_file.exists():
            with open(bible_file, 'r', encoding='utf-8') as f:
                return f.read()
        return ""

    def load_outline(self) -> str:
        """加载大纲"""
        outline_file = DOCS_DIR / "01-规划层" / "Daming1900_Master_Outline.md"
        if outline_file.exists():
            with open(outline_file, 'r', encoding='utf-8') as f:
                return f.read()
        return ""

    def load_engine_rules(self) -> str:
        """加载生成规范"""
        rules_file = DOCS_DIR / "04-质控层" / "Daming1900_Engine_Rules.md"
        if rules_file.exists():
            with open(rules_file, 'r', encoding='utf-8') as f:
                return f.read()
        return ""

    def get_chapter_info(self, chapter_num: int) -> dict:
        """获取章节信息"""
        # 从大纲中提取章节信息
        # 这里简化处理，实际需要解析大纲
        return {
            "chapter": chapter_num,
            "title": f"第{chapter_num}章",
            "pov": self.get_pov_for_chapter(chapter_num),
            "time_lock": "2小时",
            "arc": self.get_arc_for_chapter(chapter_num)
        }

    def get_pov_for_chapter(self, chapter_num: int) -> str:
        """获取章节POV"""
        if chapter_num <= 30:
            # 前30章只允许陈铁和老鬼
            if chapter_num % 2 == 0:
                return "老鬼"
            return "陈铁"
        elif chapter_num <= 70:
            # 第一部后期可以切换
            return "陈铁"
        else:
            # 第二部开始放宽
            return "多POV"

    def get_arc_for_chapter(self, chapter_num: int) -> str:
        """获取章节所属卷"""
        if chapter_num <= 70:
            return "第一部：天工纪"
        elif chapter_num <= 165:
            return "第二部：洪威纪"
        else:
            return "第三部：泰安纪"

    def generate_prompt(self, chapter_num: int) -> str:
        """生成章节Prompt"""
        info = self.get_chapter_info(chapter_num)

        prompt = f"""
你是《大明1900》的主笔。请生成第{chapter_num}章。

## 当前状态
- 时间：{self.state['world_state']['year']}年{self.state['world_state']['month']}月
- 地点：{self.state['characters']['陈铁']['location']}
- 当前事件：{self.state['world_state']['current_event']}

## 章节要求
- POV（视角）：{info['pov']}
- 时间锁：{info['time_lock']}
- 字数：2500-3000字

## 核心规则
1. 严禁心理标签（如"他很愤怒"），用动作代替
2. 严禁上帝视角，只写POV角色能看到/听到的
3. 每章必须包含日常细节（煤烟味、铁锈味、机器轰鸣）
4. 结尾必须有悬念钩子

## 人物状态
{json.dumps(self.state['characters'], ensure_ascii=False, indent=2)}

请按照CHAPTER_ENGINE.md的格式生成正文。
"""
        return prompt

    def update_state_after_chapter(self, chapter_num: int, chapter_content: str):
        """章节生成后更新状态"""
        self.state['generation_state']['chapters_generated'] = chapter_num
        self.state['generation_state']['last_checkpoint'] = datetime.now().isoformat()
        self.state['current_chapter'] = chapter_num

        # 更新世界时间（每章推进约1-3天）
        self.state['world_state']['month'] = (self.state['world_state']['month'] + 1) % 12
        if self.state['world_state']['month'] == 0:
            self.state['world_state']['month'] = 1

        self.save_state()

    def create_checkpoint(self, chapter_num: int):
        """创建检查点（每10章）"""
        if chapter_num % 10 == 0:
            checkpoint = {
                "chapter": chapter_num,
                "timestamp": datetime.now().isoformat(),
                "state": self.state.copy(),
                "summary": f"第{chapter_num-9}-{chapter_num}章生成完成"
            }
            checkpoint_file = CHECKPOINTS_DIR / f"checkpoint_{chapter_num}.json"
            with open(checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint, f, ensure_ascii=False, indent=2)
            print(f"✅ 检查点已创建：第{chapter_num}章")

    def generate_chapter(self, chapter_num: int) -> str:
        """生成单章"""
        print(f"📝 正在生成第{chapter_num}章...")

        prompt = self.generate_prompt(chapter_num)

        # 保存prompt供AI调用
        prompt_file = OUTPUT_DIR / f"prompt_{chapter_num}.txt"
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(prompt)

        # 更新状态
        self.update_state_after_chapter(chapter_num, "")

        # 创建检查点
        self.create_checkpoint(chapter_num)

        print(f"✅ 第{chapter_num}章Prompt已生成：{prompt_file}")
        return prompt

    def generate_batch(self, start: int, end: int):
        """批量生成章节"""
        print(f"🚀 开始批量生成第{start}-{end}章...")
        for i in range(start, end + 1):
            self.generate_chapter(i)
        print(f"✅ 批量生成完成：第{start}-{end}章")


def main():
    """主函数"""
    import argparse
    parser = argparse.ArgumentParser(description='《大明1900》章节生成器')
    parser.add_argument('--chapter', type=int, help='生成指定章节')
    parser.add_argument('--batch', type=str, help='批量生成，格式: start-end')
    parser.add_argument('--status', action='store_true', help='查看当前状态')

    args = parser.parse_args()

    generator = ChapterGenerator()

    if args.status:
        print(f"📊 当前状态：")
        print(f"  - 已生成章节：{generator.state['generation_state']['chapters_generated']}")
        print(f"  - 当前时间：{generator.state['world_state']['year']}年{generator.state['world_state']['month']}月")
        print(f"  - 当前篇章：{generator.state['current_arc']}")
    elif args.chapter:
        generator.generate_chapter(args.chapter)
    elif args.batch:
        start, end = map(int, args.batch.split('-'))
        generator.generate_batch(start, end)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
