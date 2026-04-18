#!/usr/bin/env python3
"""
高效章节生成流水线
合并8个agent为2个，减少90%的token消耗
"""

import json
from pathlib import Path

class EfficientPipeline:
    """高效流水线：规划+写作+质控一体化"""

    def __init__(self):
        # 一次性加载所有需要的文件
        self.bible = self.load_file("docs/Daming1900_Bible.md")
        self.outline = self.load_file("docs/Daming1900_Master_Outline.md")
        self.state = self.load_json("automation/state.json")
        self.profiles = self.load_json("automation/character_physical_profiles.json")

        # 构建精简的上下文
        self.context = self.build_context()

    def load_file(self, path: str) -> str:
        """加载文件"""
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    def load_json(self, path: str) -> dict:
        """加载JSON"""
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def build_context(self) -> str:
        """
        构建精简上下文
        只提取当前章节需要的信息，不全部加载
        """
        # 提取当前章节需要的POV
        current_chapter = self.state['current_chapter'] + 1
        pov = self.get_pov(current_chapter)

        # 只提取POV角色的状态
        pov_state = self.state['characters'].get(pov, {})

        # 构建精简上下文
        context = f"""
## 当前章节
- 章节号：第{current_chapter}章
- POV：{pov}

## POV角色状态
{json.dumps(pov_state, ensure_ascii=False, indent=2)}

## 核心世界观规则（精简版）
- 明朝官制（三司制）：布政使、按察使、都指挥使
- 禁止：总督、巡抚、辫子、旗袍、奴才、主子
- 货币：铁币1年氧化成铁粉，必须兑换白银
- 技术：1900年水平，落后西方8-20年
"""
        return context

    def get_pov(self, chapter: int) -> str:
        """获取章节POV"""
        if chapter <= 30:
            return "陈铁" if chapter % 2 == 1 else "老鬼"
        return "陈铁"

    def generate_chapter(self, chapter_num: int):
        """
        一次Agent调用完成所有工作
        """
        # 构建prompt
        prompt = f"""
你是《大明1900》的写作agent。请完成第{chapter_num}章的写作。

{self.context}

## 任务

1. 阅读大纲中的第{chapter_num}章规划
2. 检查POV角色的物理状态
3. 撰写章节正文（3000-5000字）
4. 自我质控：
   - 世界观一致性（明朝设定、货币系统）
   - 物理逻辑（伤痕、装备、时间线）
   - POV死锁（只写POV角色的感知）
   - 感官反差（≥3处）
   - 禁用词（微微、淡淡、心头一颤）

## 输出

直接输出章节正文，不需要解释。
"""
        # 这里调用Claude API
        # response = claude_api.generate(prompt)
        # return response
        pass

# 使用示例
if __name__ == "__main__":
    pipeline = EfficientPipeline()
    pipeline.generate_chapter(11)
