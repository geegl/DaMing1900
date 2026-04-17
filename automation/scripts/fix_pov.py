#!/usr/bin/env python3
"""
批量修复第1-30章视角错误
- 将【POV: XXX - 第X视角】改为【POV: XXX】
- 将叙述中的"我"替换为对应角色名
"""

import os
import re
import glob

CHAPTERS_DIR = "/Users/roven/Documents/Trae/DaMing/chapters"

def get_pov_character(content):
    """从POV标记中提取角色名"""
    # 匹配【POV: XXX - 第X视角】或【POV: XXX】
    match = re.search(r'【POV:\s*([^\s】]+)', content)
    if match:
        return match.group(1)
    return None

def fix_pov_marker(content):
    """修复POV标记，去掉视角数"""
    # 【POV: 陈铁 - 第1视角】 -> 【POV: 陈铁】
    content = re.sub(r'【POV:\s*([^\s】]+)\s*-\s*第\d+视角】', r'【POV: \1】', content)
    return content

def replace_first_person(content, character_name):
    """将第一人称'我'替换为角色名"""
    lines = content.split('\n')
    result_lines = []
    
    in_dialogue = False
    
    for line in lines:
        # 检测对话开始和结束（中文引号）
        # 对话标记：「」或""或""
        
        # 对于每一行，我们需要逐字处理，判断是否在对话中
        new_line = ""
        i = 0
        in_quote = False
        
        while i < len(line):
            char = line[i]
            
            # 检测引号开始
            if char in '「"\""':
                in_quote = True
                new_line += char
            # 检测引号结束
            elif char in '」"\""':
                in_quote = False
                new_line += char
            # 如果不在引号中，且当前字符是"我"
            elif not in_quote and char == '我':
                # 检查下一个字符，避免替换"我们"中的"我"
                next_char = line[i+1] if i+1 < len(line) else ''
                
                # 如果是"我们"，替换为角色名+"们" -> 改为"他们"
                if next_char == '们':
                    new_line += "他们"
                    i += 1  # 跳过"们"
                else:
                    new_line += character_name
            else:
                new_line += char
            
            i += 1
        
        result_lines.append(new_line)
    
    return '\n'.join(result_lines)

def process_chapter(filepath):
    """处理单个章节"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 获取POV角色
    character = get_pov_character(content)
    if not character:
        print(f"  警告: 未找到POV标记 - {filepath}")
        return False
    
    print(f"  POV角色: {character}")
    
    # 修复POV标记
    content = fix_pov_marker(content)
    
    # 替换第一人称
    content = replace_first_person(content, character)
    
    # 写回文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def main():
    # 获取所有章节文件
    chapter_files = sorted(glob.glob(os.path.join(CHAPTERS_DIR, "第*章*.md")))
    
    print(f"找到 {len(chapter_files)} 个章节文件")
    print("=" * 50)
    
    for filepath in chapter_files:
        filename = os.path.basename(filepath)
        print(f"\n处理: {filename}")
        process_chapter(filepath)
    
    print("\n" + "=" * 50)
    print("批量修复完成！")

if __name__ == "__main__":
    main()
