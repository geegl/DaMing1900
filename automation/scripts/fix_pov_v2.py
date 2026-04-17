#!/usr/bin/env python3
"""
批量修复第1-30章视角错误 v2
- 统一POV标记格式为【POV: 角色名】
- 将叙述中的"我"替换为对应角色名
"""

import os
import re
import glob

CHAPTERS_DIR = "/Users/roven/Documents/Trae/DaMing/chapters"

def extract_pov_character(pov_line):
    """从POV标记中提取角色名"""
    # 匹配各种格式：
    # 【POV: 陈铁】
    # 【POV: 陈铁 - 第一视角】
    # **【POV: 陈铁 - 第一人称】**
    # 【POV: 老鬼 - 第一视角回忆】
    
    # 提取角色名（在POV: 之后，第一个空格或】之前）
    match = re.search(r'POV:\s*([^\s】\-]+)', pov_line)
    if match:
        return match.group(1)
    return None

def fix_pov_line(line):
    """修复POV标记行，统一格式为【POV: 角色名】"""
    character = extract_pov_character(line)
    if character:
        # 去除markdown粗体标记
        return f"【POV: {character}】"
    return None

def replace_first_person(text, character_name):
    """将第一人称'我'替换为角色名，跳过引号内的对话"""
    result = []
    i = 0
    in_quote = False
    quote_chars = {'「': '」', '"': '"', '"': '"', '『': '』'}
    current_quote_end = None
    
    while i < len(text):
        char = text[i]
        
        # 检测引号
        if char in quote_chars and not in_quote:
            in_quote = True
            current_quote_end = quote_chars[char]
            result.append(char)
        elif in_quote and char == current_quote_end:
            in_quote = False
            current_quote_end = None
            result.append(char)
        elif not in_quote and char == '我':
            # 检查是否是"我们"
            if i + 1 < len(text) and text[i + 1] == '们':
                result.append("他们")
                i += 1  # 跳过"们"
            else:
                result.append(character_name)
        else:
            result.append(char)
        
        i += 1
    
    return ''.join(result)

def process_chapter(filepath):
    """处理单个章节"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    new_lines = []
    character = None
    pov_fixed = False
    
    for i, line in enumerate(lines):
        # 检查是否是POV标记行
        if 'POV:' in line and ('【' in line or '**【' in line):
            fixed_pov = fix_pov_line(line)
            if fixed_pov:
                character = extract_pov_character(line)
                new_lines.append(fixed_pov)
                pov_fixed = True
                continue
        
        # 如果已经找到POV角色，替换第一人称
        if character and not pov_fixed:
            pass  # 还没修复POV行
        
        new_lines.append(line)
    
    # 替换第一人称
    if character:
        content = '\n'.join(new_lines)
        content = replace_first_person(content, character)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return character
    
    return None

def main():
    chapter_files = sorted(glob.glob(os.path.join(CHAPTERS_DIR, "第*章*.md")))
    
    print(f"找到 {len(chapter_files)} 个章节文件")
    print("=" * 50)
    
    for filepath in chapter_files:
        filename = os.path.basename(filepath)
        character = process_chapter(filepath)
        if character:
            print(f"✓ {filename} -> POV: {character}")
        else:
            print(f"✗ {filename} -> 未找到POV标记")
    
    print("\n" + "=" * 50)
    print("修复完成！")

if __name__ == "__main__":
    main()
