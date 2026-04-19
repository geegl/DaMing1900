#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批次工作流程检查器
确保每完成一个批次后，所有必需的文档都已更新
"""

import json
import os
import sys
from pathlib import Path

class BatchWorkflowChecker:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.state_file = self.project_root / "automation" / "state.json"
        self.readme_file = self.project_root / "README.md"
        self.current_file = self.project_root / "progress" / "CURRENT.md"
        self.batches_dir = self.project_root / "progress" / "batches"

    def check_batch_completion(self, batch_num):
        """检查批次完成后的所有必需文档"""
        errors = []
        warnings = []

        # 1. 检查state.json
        if not self.state_file.exists():
            errors.append("❌ state.json不存在")
        else:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
                current_chapter = state.get("current_chapter", 0)
                expected_chapter = batch_num * 10

                if current_chapter != expected_chapter:
                    errors.append(f"❌ state.json中current_chapter={current_chapter}，应为{expected_chapter}")

                generation_state = state.get("generation_state", {})
                if generation_state.get("current_batch") != batch_num:
                    errors.append(f"❌ state.json中current_batch={generation_state.get('current_batch')}，应为{batch_num}")

        # 2. 检查README.md
        if not self.readme_file.exists():
            errors.append("❌ README.md不存在")
        else:
            with open(self.readme_file, 'r', encoding='utf-8') as f:
                readme_content = f.read()
                if f"Batch {batch_num:02d}" not in readme_content:
                    warnings.append(f"⚠️ README.md中未找到Batch {batch_num:02d}的记录")

        # 3. 检查progress/CURRENT.md
        if not self.current_file.exists():
            errors.append("❌ progress/CURRENT.md不存在")
        else:
            with open(self.current_file, 'r', encoding='utf-8') as f:
                current_content = f.read()
                expected_chapter = batch_num * 10
                if f"第{expected_chapter}章" not in current_content:
                    warnings.append(f"⚠️ CURRENT.md中未提到第{expected_chapter}章")

        # 4. 检查批次日志
        batch_log_file = self.batches_dir / f"batch_{batch_num:02d}_log.md"
        if not batch_log_file.exists():
            errors.append(f"❌ 批次日志不存在：{batch_log_file}")

        # 5. 检查章节文件
        start_chapter = (batch_num - 1) * 10 + 1
        end_chapter = batch_num * 10
        for ch in range(start_chapter, end_chapter + 1):
            chapter_file = self.project_root / "chapters" / f"第{ch:03d}章*.md"
            if not list(self.project_root.glob(f"chapters/第{ch:03d}章*.md")):
                errors.append(f"❌ 第{ch:03d}章文件不存在")

        return {
            "batch_num": batch_num,
            "errors": errors,
            "warnings": warnings,
            "passed": len(errors) == 0
        }

    def print_report(self, result):
        """打印检查报告"""
        print(f"\n{'='*60}")
        print(f"Batch {result['batch_num']:02d} 工作流程检查报告")
        print(f"{'='*60}\n")

        if result['passed']:
            print("✅ 通过：所有必需文档已更新\n")
        else:
            print("❌ 失败：存在遗漏的文档更新\n")

        if result['errors']:
            print("错误：")
            for error in result['errors']:
                print(f"  {error}")
            print()

        if result['warnings']:
            print("警告：")
            for warning in result['warnings']:
                print(f"  {warning}")
            print()

        print(f"{'='*60}\n")
        return result['passed']

def main():
    if len(sys.argv) < 2:
        print("用法: python batch_workflow_checker.py <batch_num>")
        print("示例: python batch_workflow_checker.py 7")
        sys.exit(1)

    batch_num = int(sys.argv[1])
    project_root = Path(__file__).parent.parent.parent

    checker = BatchWorkflowChecker(project_root)
    result = checker.check_batch_completion(batch_num)
    passed = checker.print_report(result)

    sys.exit(0 if passed else 1)

if __name__ == "__main__":
    main()
