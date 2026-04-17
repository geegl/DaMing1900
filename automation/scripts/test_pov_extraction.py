#!/usr/bin/env python3
"""测试POV提取"""

import re
from pathlib import Path

chapters_dir = Path("/Users/roven/Documents/Trae/DaMing/chapters")

for i in range(1, 11):
    chapter_num = str(i).zfill(3)
    pattern = f"第{chapter_num}章*.md"
    matches = list(chapters_dir.glob(pattern))

    if not matches:
        print(f"第{chapter_num}章: 文件不存在")
        continue

    file_path = matches[0]

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    pov_match = re.search(r'【POV:\s*(.*?)】', content)

    if pov_match:
        pov = pov_match.group(1).strip()
        print(f"第{chapter_num}章: {pov}")
    else:
        print(f"第{chapter_num}章: 未找到POV标签")
