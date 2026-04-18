#!/usr/bin/env python3
"""
Gemini API审核脚本
使用Google Generative AI API
"""

import os
import json
import google.generativeai as genai
from pathlib import Path

class GeminiAPIAuditor:
    """使用Gemini API进行审核"""

    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def audit_chapter(self, chapter_path: str, bible_path: str, state_path: str):
        """审核章节"""

        # 读取文件
        with open(chapter_path, 'r', encoding='utf-8') as f:
            chapter = f.read()

        with open(bible_path, 'r', encoding='utf-8') as f:
            bible = f.read()[:5000]  # 只读前5000字符

        with open(state_path, 'r', encoding='utf-8') as f:
            state = json.load(f)

        # 构建prompt
        prompt = f"""你是《大明1900》的审核专家。请深度审核以下章节：

## 章节内容
{chapter}

## 世界观设定（节选）
{bible}

## 人物状态
{json.dumps(state['characters'], ensure_ascii=False, indent=2)}

## 审核维度
1. 世界观一致性（明朝设定、货币系统、技术代差）
2. 物理逻辑（伤痕、装备、时间线）
3. POV死锁（是否写其他角色内心）
4. 深层逻辑（动机、经济计算、伏笔）

## 输出格式
**【问题列表】**
1. [问题] 位置：第X行 | 问题：... | 修正：...

**【评分】** 世界观：X/10 | 物理：X/10 | POV：X/10 | 逻辑：X/10

**【结论】** PASS / FAIL
"""

        # 调用Gemini API
        response = self.model.generate_content(prompt)
        return response.text

# 使用示例
if __name__ == "__main__":
    import sys

    # 从环境变量读取API Key
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("请设置环境变量 GEMINI_API_KEY")
        sys.exit(1)

    if len(sys.argv) < 2:
        print("用法: python3 gemini_api_audit.py <章节路径>")
        sys.exit(1)

    auditor = GeminiAPIAuditor(api_key)
    report = auditor.audit_chapter(
        sys.argv[1],
        "docs/Daming1900_Bible.md",
        "automation/state.json"
    )

    print(report)

    # 保存报告
    chapter_path = Path(sys.argv[1])
    report_path = chapter_path.parent / f"{chapter_path.stem}_gemini_audit.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"# Gemini审核报告\n\n{report}")

    print(f"\n✅ 报告已保存：{report_path}")
