#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
进度报告自动生成器
每天运行一次，生成进度报告并更新README
"""

import os
import json
from datetime import datetime
from pathlib import Path

def count_chinese_chars(text):
    """统计汉字数量"""
    return sum(1 for char in text if '\u4e00' <= char <= '\u9fff')

def generate_daily_report():
    """生成每日进度报告"""

    # 读取state.json
    state_file = Path("automation/state.json")
    with open(state_file, 'r', encoding='utf-8') as f:
        state = json.load(f)

    # 统计章节文件
    chapters_dir = Path("chapters")
    chapter_files = list(chapters_dir.glob("第*章*.md"))

    # 统计总字数
    total_chars = 0
    chapter_stats = []

    for chapter_file in sorted(chapter_files):
        with open(chapter_file, 'r', encoding='utf-8') as f:
            content = f.read()
            chars = count_chinese_chars(content)
            total_chars += chars

            # 提取章节号
            chapter_num = int(chapter_file.stem.split('第')[1].split('章')[0])

            chapter_stats.append({
                'number': chapter_num,
                'file': chapter_file.name,
                'chars': chars
            })

    # 生成报告
    report_date = datetime.now().strftime("%Y-%m-%d")
    report_time = datetime.now().strftime("%H:%M:%S")

    report = f"""# 《大明1900》每日进度报告

**日期**：{report_date}
**时间**：{report_time}

---

## 📊 总体进度

| 指标 | 数值 |
|------|------|
| **已完成章节** | {len(chapter_files)} / 220章 |
| **完成百分比** | {len(chapter_files) / 220 * 100:.1f}% |
| **总字数** | {total_chars:,}字 |
| **平均每章** | {total_chars // len(chapter_files) if chapter_files else 0:,}字 |

---

## 📝 章节详情

"""

    for stat in chapter_stats:
        report += f"- 第{stat['number']:03d}章：{stat['chars']:,}字\n"

    report += f"""
---

## 🎯 下一步计划

- [ ] 继续生成第{len(chapter_files) + 1}章
- [ ] 质量检查
- [ ] 状态存档

---

## 📁 文件更新

- 最后更新：{report_time}
- 状态文件：automation/state.json
- 质量报告：automation/quality_reports/
"""

    # 保存报告
    progress_dir = Path("progress")
    progress_dir.mkdir(exist_ok=True)

    report_file = progress_dir / f"daily_{report_date}.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)

    # 更新最新报告
    latest_report = progress_dir / "daily.md"
    with open(latest_report, 'w', encoding='utf-8') as f:
        f.write(report)

    # 更新统计数据
    stats = {
        'last_update': report_date + " " + report_time,
        'total_chapters': len(chapter_files),
        'total_chars': total_chars,
        'chapters': chapter_stats
    }

    stats_file = progress_dir / "stats.json"
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    # 更新README
    update_readme(len(chapter_files), total_chars)

    print(f"✅ 进度报告已生成：{report_file}")
    print(f"📊 当前进度：{len(chapter_files)}章 / {total_chars:,}字")

    return report

def update_readme(chapter_count, total_chars):
    """更新README.md"""

    readme_path = Path("README.md")

    if not readme_path.exists():
        return

    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 更新进度信息
    lines = content.split('\n')
    new_lines = []

    for line in lines:
        if line.startswith('- **当前进度**：'):
            new_lines.append(f"- **当前进度**：第{chapter_count}章 / 220章")
        elif line.startswith('- **总字数**：'):
            new_lines.append(f"- **总字数**：{total_chars:,}字")
        elif line.startswith('- **最后更新**：'):
            new_lines.append(f"- **最后更新**：{datetime.now().strftime('%Y-%m-%d')}")
        else:
            new_lines.append(line)

    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))

if __name__ == "__main__":
    generate_daily_report()
