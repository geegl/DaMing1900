#!/usr/bin/env python3
"""
《大明1900》自动化生成流水线主控
版本: 4.2
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
AUTOMATION_DIR = PROJECT_ROOT / "automation"
SCRIPTS_DIR = AUTOMATION_DIR / "scripts"
OUTPUT_DIR = AUTOMATION_DIR / "output"
CHAPTERS_DIR = AUTOMATION_DIR / "chapters"
CHECKPOINTS_DIR = AUTOMATION_DIR / "checkpoints"
LOGS_DIR = AUTOMATION_DIR / "logs"

class Pipeline:
    """自动化流水线"""

    def __init__(self):
        self.ensure_directories()
        self.state = self.load_state()

    def ensure_directories(self):
        """确保目录存在"""
        for d in [OUTPUT_DIR, CHAPTERS_DIR, CHECKPOINTS_DIR, LOGS_DIR]:
            d.mkdir(parents=True, exist_ok=True)

    def load_state(self) -> dict:
        state_file = AUTOMATION_DIR / "state.json"
        with open(state_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_state(self):
        state_file = AUTOMATION_DIR / "state.json"
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    def log(self, message: str):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)

        log_file = LOGS_DIR / "pipeline.log"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_message + "\n")

    def step1_generate_prompt(self, chapter_num: int) -> str:
        """步骤1：生成Prompt"""
        self.log(f"📝 步骤1：生成第{chapter_num}章Prompt...")

        # 调用generate_chapter.py
        result = subprocess.run(
            ["python3", str(SCRIPTS_DIR / "generate_chapter.py"), "--chapter", str(chapter_num)],
            capture_output=True, text=True
        )

        prompt_file = OUTPUT_DIR / f"prompt_{chapter_num}.txt"
        if prompt_file.exists():
            self.log(f"✅ Prompt已生成：{prompt_file}")
            return str(prompt_file)
        else:
            self.log(f"❌ Prompt生成失败")
            return ""

    def step2_generate_content(self, chapter_num: int, prompt_file: str) -> str:
        """步骤2：调用AI生成正文（需要Claude Code执行）"""
        self.log(f"🤖 步骤2：生成第{chapter_num}章正文...")

        # 这里只是标记，实际生成需要Claude Code
        chapter_file = CHAPTERS_DIR / f"chapter_{chapter_num:03d}.md"
        self.log(f"⏳ 等待Claude Code生成正文：{chapter_file}")

        return str(chapter_file)

    def step3_quality_check(self, chapter_num: int, chapter_file: str) -> bool:
        """步骤3：质量检查"""
        self.log(f"🔍 步骤3：质量检查第{chapter_num}章...")

        result = subprocess.run(
            ["python3", str(SCRIPTS_DIR / "quality_checker.py"), "--file", chapter_file],
            capture_output=True, text=True
        )

        if "通过: True" in result.stdout:
            self.log(f"✅ 质量检查通过")
            return True
        else:
            self.log(f"⚠️ 质量检查发现问题：\n{result.stdout}")
            return False

    def step4_update_state(self, chapter_num: int, chapter_file: str):
        """步骤4：更新状态"""
        self.log(f"📊 步骤4：更新状态...")

        # 读取章节内容
        with open(chapter_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 更新状态
        self.state["generation_state"]["chapters_generated"] = chapter_num
        self.state["current_chapter"] = chapter_num
        self.save_state()

        self.log(f"✅ 状态已更新")

    def step5_create_checkpoint(self, chapter_num: int):
        """步骤5：创建检查点（每10章）"""
        if chapter_num % 10 == 0:
            self.log(f"💾 步骤5：创建检查点...")

            subprocess.run([
                "python3", str(SCRIPTS_DIR / "checkpoint_manager.py"),
                "--create", str(chapter_num)
            ])

            self.log(f"✅ 检查点已创建")

    def run_single_chapter(self, chapter_num: int):
        """生成单章完整流程"""
        self.log(f"\n{'='*50}")
        self.log(f"🚀 开始生成第{chapter_num}章")
        self.log(f"{'='*50}")

        # 步骤1
        prompt_file = self.step1_generate_prompt(chapter_num)
        if not prompt_file:
            return False

        # 步骤2（标记）
        chapter_file = self.step2_generate_content(chapter_num, prompt_file)

        # 步骤3-5需要实际章节内容后执行
        # 这里只是流程展示

        self.log(f"✅ 第{chapter_num}章Prompt准备完成，等待Claude Code生成正文")
        return True

    def run_batch(self, start: int, end: int):
        """批量生成"""
        self.log(f"\n🚀 开始批量生成第{start}-{end}章")

        for i in range(start, end + 1):
            self.run_single_chapter(i)

        self.log(f"\n✅ 批量生成完成")

    def status(self):
        """显示当前状态"""
        print(f"\n📊 《大明1900》生成状态")
        print(f"{'='*40}")
        print(f"  版本：{self.state['version']}")
        print(f"  已生成：{self.state['generation_state']['chapters_generated']} / {self.state['total_chapters']}")
        print(f"  当前篇章：{self.state['current_arc']}")
        print(f"  世界时间：{self.state['world_state']['year']}年{self.state['world_state']['month']}月")
        print(f"  当前事件：{self.state['world_state']['current_event']}")
        print(f"{'='*40}\n")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='《大明1900》自动化流水线')
    parser.add_argument('--chapter', type=int, help='生成指定章节')
    parser.add_argument('--batch', type=str, help='批量生成，格式: start-end')
    parser.add_argument('--status', action='store_true', help='查看状态')
    parser.add_argument('--init', action='store_true', help='初始化流水线')

    args = parser.parse_args()
    pipeline = Pipeline()

    if args.init:
        print("✅ 流水线已初始化")
        pipeline.status()
    elif args.status:
        pipeline.status()
    elif args.chapter:
        pipeline.run_single_chapter(args.chapter)
    elif args.batch:
        start, end = map(int, args.batch.split('-'))
        pipeline.run_batch(start, end)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
