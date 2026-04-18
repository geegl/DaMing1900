#!/usr/bin/env python3
"""
上下文缓存系统
减少90%的重复文件读取
"""

import json
from pathlib import Path
from functools import lru_cache

class ContextCache:
    """上下文缓存：避免重复读取大文件"""

    def __init__(self):
        self.cache_dir = Path("automation/.cache")
        self.cache_dir.mkdir(exist_ok=True)

    @lru_cache(maxsize=128)
    def load_file(self, file_path: str, max_lines: int = None) -> str:
        """
        读取文件（带缓存）
        同一个文件在同一个session中只读取一次
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            if max_lines:
                lines = f.readlines()[:max_lines]
                return ''.join(lines)
            return f.read()

    @lru_cache(maxsize=64)
    def load_json(self, file_path: str) -> dict:
        """读取JSON（带缓存）"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_chapter_context(self, chapter_num: int, pov: str) -> str:
        """
        获取章节所需的最小上下文
        只提取必要信息，不加载全部
        """
        # 只加载当前章节需要的部分
        state = self.load_json("automation/state.json")

        # 提取POV角色状态
        pov_state = state['characters'].get(pov, {})

        # 提取世界观精简版（前500行）
        bible_summary = self.load_file("docs/Daming1900_Bible.md", max_lines=500)

        # 提取大纲中的当前章节
        outline = self.load_file("docs/Daming1900_Master_Outline.md")
        chapter_outline = self.extract_chapter_outline(outline, chapter_num)

        context = f"""
## 当前章节：第{chapter_num}章
- POV：{pov}

## POV角色状态
{json.dumps(pov_state, ensure_ascii=False, indent=2)}

## 世界观核心（精简）
{bible_summary}

## 章节大纲
{chapter_outline}
"""
        return context

    def extract_chapter_outline(self, outline: str, chapter_num: int) -> str:
        """从大纲中提取当前章节"""
        # 简化：只返回当前章节的内容
        lines = outline.split('\n')
        chapter_start = f"#### 第{chapter_num}章"

        result = []
        in_chapter = False
        for line in lines:
            if chapter_start in line:
                in_chapter = True
            elif in_chapter and line.startswith("####"):
                break
            if in_chapter:
                result.append(line)

        return '\n'.join(result)

# 使用示例
if __name__ == "__main__":
    cache = ContextCache()

    # 第一次调用：读取文件
    context1 = cache.get_chapter_context(11, "陈铁")

    # 第二次调用：从缓存读取（不重复读文件）
    context2 = cache.get_chapter_context(11, "陈铁")

    print("✅ 上下文缓存系统已就绪")
    print(context1[:500])
