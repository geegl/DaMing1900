#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整一致性验证脚本
一键运行所有7个一致性验证
"""

import subprocess
import sys
from pathlib import Path

class ConsistencyValidator:
    """完整一致性验证器"""

    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.scripts_dir = self.project_root / "automation" / "scripts"

    def run_validator(self, script_name, chapter_num):
        """运行单个验证脚本"""
        script_path = self.scripts_dir / script_name

        if not script_path.exists():
            return {
                "script": script_name,
                "status": "skip",
                "message": "脚本不存在"
            }

        try:
            result = subprocess.run(
                ["python3", str(script_path), str(chapter_num)],
                capture_output=True,
                text=True,
                timeout=30
            )

            return {
                "script": script_name,
                "status": "pass" if result.returncode == 0 else "fail",
                "output": result.stdout,
                "errors": result.stderr
            }
        except subprocess.TimeoutExpired:
            return {
                "script": script_name,
                "status": "timeout",
                "message": "验证超时"
            }
        except Exception as e:
            return {
                "script": script_name,
                "status": "error",
                "message": str(e)
            }

    def validate_chapter(self, chapter_num):
        """运行所有一致性验证"""
        validators = [
            ("timeline_validator_v2.py", "时间线一致性"),
            ("worldview_validator.py", "世界观一致性"),
            ("character_consistency_validator.py", "人物一致性"),
            ("setting_validator.py", "设定一致性"),
            ("quality_checker.py", "文风一致性"),
        ]

        results = []
        all_passed = True

        print(f"\n{'='*60}")
        print(f"完整一致性验证报告 - 第{chapter_num:03d}章")
        print(f"{'='*60}\n")

        for script, name in validators:
            print(f"正在验证：{name}...")
            result = self.run_validator(script, chapter_num)
            results.append((name, result))

            if result["status"] == "pass":
                print(f"  ✅ 通过")
            elif result["status"] == "skip":
                print(f"  ⏭️ 跳过（脚本不存在）")
            elif result["status"] == "fail":
                print(f"  ❌ 失败")
                all_passed = False
                if result.get("output"):
                    # 只显示错误部分
                    lines = result["output"].split('\n')
                    for line in lines:
                        if "❌" in line or "错误" in line or "ERROR" in line:
                            print(f"     {line}")
            else:
                print(f"  ⚠️ {result['status']}: {result.get('message', '')}")

        print(f"\n{'='*60}")

        if all_passed:
            print("✅ 所有验证通过")
        else:
            print("❌ 存在验证失败，请修正后再提交")

        print(f"{'='*60}\n")

        return all_passed

def main():
    if len(sys.argv) < 2:
        print("用法: python consistency_validator.py <章节号>")
        print("示例: python consistency_validator.py 10")
        sys.exit(1)

    chapter_num = int(sys.argv[1])
    project_root = Path(__file__).parent.parent.parent

    validator = ConsistencyValidator(project_root)
    passed = validator.validate_chapter(chapter_num)

    sys.exit(0 if passed else 1)

if __name__ == "__main__":
    main()
