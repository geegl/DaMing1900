#!/usr/bin/env python3
"""
Gemini深度审核Agent
完整的5维度审核 + 反向拷问 + 自动提问 + 拓展思考
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple

class GeminiDeepAuditor:
    """Gemini深度审核器"""

    def __init__(self):
        self.system_instruction_path = Path("automation/gemini_system_instruction.md")
        self.bible_path = Path("docs/Daming1900_Bible.md")
        self.outline_path = Path("docs/Daming1900_Master_Outline.md")
        self.state_path = Path("automation/state.json")
        self.profiles_path = Path("automation/character_physical_profiles.json")
        self.foreshadowing_path = Path("automation/foreshadowing_ledger.json")

        # 审核维度权重
        self.dimensions = {
            "worldview": {"weight": 10, "threshold": 8},
            "physical": {"weight": 10, "threshold": 8},
            "pov": {"weight": 10, "threshold": 9},
            "logic": {"weight": 10, "threshold": 7},
            "style": {"weight": 10, "threshold": 8}
        }

    def load_files(self, chapter_path: str) -> Dict:
        """加载所有需要的文件"""
        files = {
            "chapter": self._read_file(chapter_path),
            "bible": self._read_file(self.bible_path, max_lines=500),
            "state": self._read_json(self.state_path),
            "profiles": self._read_json(self.profiles_path),
            "foreshadowing": self._read_json(self.foreshadowing_path),
            "system_instruction": self._read_file(self.system_instruction_path)
        }
        return files

    def _read_file(self, path: Path, max_lines: int = None) -> str:
        """读取文件"""
        with open(path, 'r', encoding='utf-8') as f:
            if max_lines:
                lines = f.readlines()[:max_lines]
                return ''.join(lines)
            return f.read()

    def _read_json(self, path: Path) -> dict:
        """读取JSON"""
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def extract_pov(self, chapter_content: str) -> str:
        """从章节中提取POV角色"""
        # 简单匹配
        if "陈铁" in chapter_content[:500]:
            return "陈铁"
        elif "老鬼" in chapter_content[:500]:
            return "老鬼"
        return "未知"

    def extract_chapter_number(self, chapter_path: str) -> int:
        """提取章节号"""
        import re
        match = re.search(r'第(\d+)章', chapter_path)
        if match:
            return int(match.group(1))
        return 0

    def construct_audit_prompt(self, chapter_path: str) -> str:
        """构造完整的审核prompt"""

        files = self.load_files(chapter_path)
        chapter_num = self.extract_chapter_number(chapter_path)
        pov = self.extract_pov(files["chapter"])

        # 提取POV角色状态
        pov_state = files["state"]["characters"].get(pov, {})

        prompt = f"""# Gemini深度审核System Instruction

{files["system_instruction"]}

---

## 待审核章节

**章节**: 第{chapter_num}章
**POV**: {pov}

### 章节正文

{files["chapter"]}

---

## 审核依据

### 人物状态

{json.dumps(pov_state, ensure_ascii=False, indent=2)}

### 世界观设定（精简）

{files["bible"]}

### 物理档案

{json.dumps(files["profiles"], ensure_ascii=False, indent=2)}

### 伏笔账本

{json.dumps(files["foreshadowing"], ensure_ascii=False, indent=2)}

---

请严格按照System Instruction要求进行深度审核，包括：
1. 5维度结构化审核报告
2. 【反向拷问】（<100字）
3. 你可能想知道（3个问题）
4. 【拓展思考】
"""

        return prompt

    def audit_with_agent(self, chapter_path: str) -> str:
        """
        使用Claude Agent进行Gemini风格的深度审核
        （如果没有Gemini API，使用Claude Opus模拟）
        """
        prompt = self.construct_audit_prompt(chapter_path)

        # 这里返回prompt，实际使用时调用Agent
        return prompt

    def parse_audit_report(self, report: str) -> Dict:
        """解析审核报告"""
        # 提取评分
        import re

        scores = {}
        for dim in self.dimensions.keys():
            pattern = f"{dim}.*?评分.*?(\\d+)/10"
            match = re.search(pattern, report, re.DOTALL)
            if match:
                scores[dim] = int(match.group(1))

        total_score = sum(scores.values()) if scores else 0

        return {
            "scores": scores,
            "total_score": total_score,
            "pass": total_score >= 40 and all(
                scores.get(dim, 0) >= self.dimensions[dim]["threshold"]
                for dim in self.dimensions.keys()
            )
        }

    def save_audit_report(self, chapter_path: str, report: str):
        """保存审核报告"""
        chapter_path = Path(chapter_path)
        report_path = chapter_path.parent / f"{chapter_path.stem}_gemini_audit.md"

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"# Gemini深度审核报告\n\n")
            f.write(f"**章节**: {chapter_path.name}\n\n")
            f.write(f"**审核时间**: {self._get_timestamp()}\n\n")
            f.write("---\n\n")
            f.write(report)

        print(f"✅ 审核报告已保存：{report_path}")

    def _get_timestamp(self) -> str:
        """获取时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 使用示例
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法: python3 gemini_audit_agent.py <章节路径>")
        print("示例: python3 gemini_audit_agent.py chapters/第010章_兰芳的梦.md")
        sys.exit(1)

    auditor = GeminiDeepAuditor()
    prompt = auditor.audit_with_agent(sys.argv[1])

    print("=== 审核Prompt ===")
    print(prompt[:500] + "\n...\n")

    print("\n提示：此脚本生成审核prompt，实际审核需要调用Claude Agent或Gemini API")
