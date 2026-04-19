#!/usr/bin/env python3
"""
《大明1900》批次管理脚本
用途：管理每10章的工作日志、纠错日志、Git提交、Telegram通知
版本：v1.0
"""

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

class BatchManager:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.batches_dir = self.project_root / "progress" / "batches"
        self.batches_dir.mkdir(parents=True, exist_ok=True)

    def get_current_batch(self):
        """获取当前批次号（基于已完成章节数）"""
        # 读取当前进度
        state_file = self.project_root / "automation" / "state.json"
        if state_file.exists():
            with open(state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
            completed_chapters = state.get("completed_chapters", 0)
        else:
            completed_chapters = 0

        # 计算批次号（每10章一批）
        batch_number = (completed_chapters // 10) + 1
        return batch_number

    def create_batch_log(self, batch_number):
        """创建批次日志文件"""
        log_file = self.batches_dir / f"batch_{batch_number:02d}_log.md"

        if not log_file.exists():
            start_chapter = (batch_number - 1) * 10 + 1
            end_chapter = batch_number * 10

            content = f"""# Batch {batch_number:02d} 工作日志

**时间范围**: {datetime.now().strftime('%Y-%m-%d')}
**章节范围**: 第{start_chapter:03d}章 - 第{end_chapter:03d}章

---

## 一、写作进度

| 章节 | 标题 | 字数 | Codex审查得分 | 状态 |
|------|------|------|--------------|------|
| 第{start_chapter:03d}章 | - | - | - | ⏳ 待写 |
"""

            for ch in range(start_chapter + 1, end_chapter + 1):
                content += f"| 第{ch:03d}章 | - | - | - | ⏳ 待写 |\n"

            content += """
---

## 二、Codex审查记录

### 第X章审查结果
- **时间**: YYYY-MM-DD HH:MM
- **得分**: XX/50
- **P0问题**: X个
- **P1问题**: X个
- **修正次数**: X次

**审查详情**：
```
[Codex输出]
```

---

## 三、纠错日志

### 错误1：[错误类型]
- **章节**: 第X章
- **问题描述**: ...
- **修正方案**: ...
- **修正时间**: YYYY-MM-DD HH:MM

---

## 四、批次总结

### 数据统计
- 总字数：XXXX字
- 平均Codex得分：XX/50
- P0问题总数：X个
- P1问题总数：X个
- 修正总次数：X次

### 经验教训
1. ...

---

**创建时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(content)

        return log_file

    def update_chapter_status(self, batch_number, chapter_number, title, word_count, codex_score, status):
        """更新章节状态"""
        log_file = self.batches_dir / f"batch_{batch_number:02d}_log.md"

        if not log_file.exists():
            return False

        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 更新章节表格
        old_line = f"| 第{chapter_number:03d}章 | - | - | - | ⏳ 待写 |"
        new_line = f"| 第{chapter_number:03d}章 | {title} | {word_count} | {codex_score}/50 | {status} |"
        content = content.replace(old_line, new_line)

        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(content)

        return True

    def add_codex_review(self, batch_number, chapter_number, review_output, score, p0_count, p1_count, fix_count):
        """添加Codex审查记录"""
        log_file = self.batches_dir / f"batch_{batch_number:02d}_log.md"

        if not log_file.exists():
            return False

        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 在"二、Codex审查记录"后添加新记录
        review_section = f"""
### 第{chapter_number:03d}章审查结果
- **时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
- **得分**: {score}/50
- **P0问题**: {p0_count}个
- **P1问题**: {p1_count}个
- **修正次数**: {fix_count}次

**审查详情**：
```
{review_output}
```

"""

        # 找到插入位置
        insert_marker = "## 二、Codex审查记录\n\n"
        if insert_marker in content:
            parts = content.split(insert_marker, 1)
            content = parts[0] + insert_marker + review_section + parts[1]

            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(content)

        return True

    def add_error_log(self, batch_number, chapter_number, error_type, description, solution):
        """添加纠错记录"""
        log_file = self.batches_dir / f"batch_{batch_number:02d}_log.md"

        if not log_file.exists():
            return False

        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 在"三、纠错日志"后添加新记录
        error_section = f"""
### 错误：{error_type}
- **章节**: 第{chapter_number:03d}章
- **问题描述**: {description}
- **修正方案**: {solution}
- **修正时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

"""

        # 找到插入位置
        insert_marker = "## 三、纠错日志\n\n"
        if insert_marker in content:
            parts = content.split(insert_marker, 1)
            content = parts[0] + insert_marker + error_section + parts[1]

            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(content)

        return True

    def commit_batch(self, batch_number):
        """提交批次到Git"""
        log_file = self.batches_dir / f"batch_{batch_number:02d}_log.md"

        if not log_file.exists():
            return False

        # Git提交
        subprocess.run(["git", "add", str(log_file)], cwd=self.project_root)
        subprocess.run([
            "git", "commit", "-m",
            f"完成Batch {batch_number:02d}：第{(batch_number-1)*10+1:03d}-{batch_number*10:03d}章"
        ], cwd=self.project_root)
        subprocess.run(["git", "push"], cwd=self.project_root)

        return True

    def send_telegram_notification(self, batch_number, stats):
        """发送Telegram通知"""
        # Telegram通知由MCP工具处理
        # 这里只返回通知内容
        message = f"""📦 《大明1900》Batch {batch_number:02d} 完成

📊 数据统计：
- 章节：第{(batch_number-1)*10+1:03d}章 - 第{batch_number*10:03d}章
- 总字数：{stats['total_words']}字
- 平均Codex得分：{stats['avg_score']}/50
- P0问题：{stats['p0_count']}个
- P1问题：{stats['p1_count']}个

✅ 已同步到GitHub
"""
        return message


if __name__ == "__main__":
    manager = BatchManager()
    batch = manager.get_current_batch()
    print(f"当前批次: Batch {batch:02d}")
