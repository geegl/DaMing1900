#!/usr/bin/env python3
"""
Gemini章节审核脚本
自动发送章节给Gemini进行深度审计
"""

import os
import json
import subprocess
from pathlib import Path

class GeminiAuditor:
    """Gemini审核器"""

    def __init__(self, chapter_path: str):
        self.chapter_path = Path(chapter_path)
        self.bible_path = Path("docs/Daming1900_Bible.md")
        self.outline_path = Path("docs/Daming1900_Master_Outline.md")
        self.state_path = Path("automation/state.json")

    def read_chapter(self) -> str:
        """读取章节内容"""
        with open(self.chapter_path, 'r', encoding='utf-8') as f:
            return f.read()

    def read_bible_summary(self) -> str:
        """读取Bible摘要（前200行）"""
        with open(self.bible_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()[:200]
            return ''.join(lines)

    def read_state(self) -> dict:
        """读取当前状态"""
        with open(self.state_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def construct_prompt(self) -> str:
        """构建Gemini审核prompt"""
        chapter_content = self.read_chapter()
        bible_summary = self.read_bible_summary()
        state = self.read_state()

        prompt = f"""你是《大明1900》的深度审核专家。请审核以下章节，找出所有逻辑问题、世界观冲突、物理不合理之处。

## 章节内容

{chapter_content}

## 核心世界观设定（节选）

{bible_summary}

## 当前人物状态

{json.dumps(state['characters'], ensure_ascii=False, indent=2)}

## 审核要求

请按以下维度进行深度审核：

### 1. 世界观一致性
- 是否符合明朝设定（无清朝元素、明朝官制）
- 技术水平是否符合1900年
- 货币系统是否合理（铁币氧化、汇率）

### 2. 物理逻辑
- 人物伤痕是否一致（第3章阿牛之死时陈铁左腿烫伤）
- 装备是否突然变化
- 时间线是否合理

### 3. POV死锁
- 是否写了其他角色的内心
- 是否有上帝视角

### 4. 深层逻辑
- 人物动机是否合理
- 经济计算是否正确
- 技术代差是否符合设定

### 5. 伏笔一致性
- 是否与前文章节矛盾
- 是否有未回收的伏笔

## 输出格式

请按以下格式输出审核结果：

**【通过项】**
- [列出通过的检查项]

**【问题项】**
1. [问题描述]
   - 位置：第X行
   - 问题：具体说明
   - 修正建议：如何修改

**【总体评分】**
- 世界观一致性：X/10
- 物理逻辑：X/10
- POV死锁：X/10
- 深层逻辑：X/10
- 总分：X/40

**【是否通过】**
PASS / FAIL
"""
        return prompt

    def send_to_gemini(self) -> str:
        """发送给Gemini进行审核"""
        prompt = self.construct_prompt()

        # 使用gemini CLI工具
        result = subprocess.run(
            ['gemini', 'audit'],
            input=prompt,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        return result.stdout

    def save_audit_report(self, report: str):
        """保存审核报告"""
        report_path = self.chapter_path.parent / f"{self.chapter_path.stem}_gemini_audit.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"# Gemini审核报告\n\n")
            f.write(f"**章节**: {self.chapter_path.name}\n\n")
            f.write(report)

        print(f"✅ 审核报告已保存：{report_path}")

def main():
    import sys

    if len(sys.argv) < 2:
        print("用法: python3 gemini_audit.py <章节路径>")
        print("示例: python3 gemini_audit.py chapters/第010章_兰芳的梦.md")
        sys.exit(1)

    chapter_path = sys.argv[1]

    auditor = GeminiAuditor(chapter_path)
    report = auditor.send_to_gemini()
    auditor.save_audit_report(report)

    print("\n" + report)

if __name__ == "__main__":
    main()
