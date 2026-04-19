#!/usr/bin/env python3
"""
《大明1900》世界观验证脚本
用途：检查章节内容是否符合明朝设定，无清朝/现代元素
版本：v1.0
"""

import re
import sys
from pathlib import Path

# 禁用词列表
FORBIDDEN_WORDS = {
    # 清朝年号（致命错误）
    "光绪", "宣统", "咸丰", "同治", "乾隆", "康熙", "雍正",

    # 清朝官职（致命错误）
    "总督", "巡抚", "军机处", "军机大臣", "理藩院", "提督", "总兵",

    # 清朝服饰/习俗（致命错误）
    "辫子", "旗袍", "马褂", "奴才", "主子", "阿玛", "额娘",

    # 清朝制度（致命错误）
    "八旗", "绿营", "满城",

    # 现代元素（致命错误）
    "手机", "电脑", "互联网", "电视", "收音机", "地铁", "飞机", "高速公路",
    "公共公园", "公共图书馆",

    # AI痕迹词汇（风格问题）
    "微微", "淡淡", "心头一颤", "双目赤红", "总而言之", "综上所述",
}

# 允许的年号
ALLOWED_ERAS = ["天工", "洪威", "泰安"]

def validate_chapter(file_path):
    """验证单个章节文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    errors = []
    warnings = []

    # 1. 检查禁用词
    for word in FORBIDDEN_WORDS:
        if word in content:
            # 找到所有出现位置
            positions = [m.start() for m in re.finditer(word, content)]
            for pos in positions:
                # 提取上下文
                start = max(0, pos - 20)
                end = min(len(content), pos + len(word) + 20)
                context = content[start:end]
                errors.append(f"禁用词 '{word}' 出现位置: ...{context}...")

    # 2. 检查清朝年号（致命错误）
    # 改进：只检测已知的清朝年号，避免误报
    qing_eras = ["光绪", "宣统", "咸丰", "同治", "乾隆", "康熙", "雍正"]
    for era in qing_eras:
        pattern = rf'{era}(\d+)年'
        matches = re.findall(pattern, content)
        for year_num in matches:
            errors.append(f"发现清朝年号: {era}{year_num}年")

    # 3. 检查允许年号的格式正确性
    for era in ALLOWED_ERAS:
        pattern = rf'{era}(\d+)年'
        matches = re.findall(pattern, content)
        if matches:
            # 年号存在，无需额外警告
            pass

    # 3. 检查时间计算正确性
    tiangong_pattern = r'天工(\d+)年.*?(\d{4})年'
    matches = re.findall(tiangong_pattern, content)
    for year_num, western_year in matches:
        year_num = int(year_num)
        western_year = int(western_year)
        calculated = 1890 + year_num
        if calculated != western_year:
            errors.append(f"天工{year_num}年应为{calculated}年，而非{western_year}年")

    return errors, warnings

def main():
    if len(sys.argv) < 2:
        print("用法: python3 worldview_validator.py <章节文件路径>")
        sys.exit(1)

    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"错误: 文件不存在 {file_path}")
        sys.exit(1)

    print(f"正在验证: {file_path.name}")
    print("-" * 60)

    errors, warnings = validate_chapter(file_path)

    if errors:
        print("\n❌ 发现致命错误:")
        for error in errors:
            print(f"  - {error}")

    if warnings:
        print("\n⚠️  警告:")
        for warning in warnings:
            print(f"  - {warning}")

    if not errors and not warnings:
        print("✅ 通过世界观验证")

    print("-" * 60)

    # 返回状态码
    sys.exit(1 if errors else 0)

if __name__ == "__main__":
    main()
