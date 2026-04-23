#!/usr/bin/env python3
"""详细字数统计：汉字、标点、字母、数字"""
import re
import sys

def count_detailed(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 去除标题行（以#开头的行）
    lines = content.split('\n')
    content = '\n'.join([line for line in lines if not line.strip().startswith('#')])
    
    # 汉字（Unicode范围）
    hanzi = len(re.findall(r'[一-龥]', content))
    
    # 全角标点
    punct_full = len(re.findall(r'[，。！？、：；""''（）【】《》…—·]', content))
    
    # 半角标点
    punct_half = len(re.findall(r'[,\.!?;:\'"()\[\]{}<>]', content))
    
    # 英文字母
    letters = len(re.findall(r'[a-zA-Z]', content))
    
    # 数字
    digits = len(re.findall(r'[0-9]', content))
    
    # 总字符数
    total_chars = len(content)
    
    return {
        'hanzi': hanzi,
        'punct_full': punct_full,
        'punct_half': punct_half,
        'letters': letters,
        'digits': digits,
        'total': total_chars
    }

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python count_detailed.py <file>")
        sys.exit(1)
    
    result = count_detailed(sys.argv[1])
    print(f"汉字: {result['hanzi']}")
    print(f"全角标点: {result['punct_full']}")
    print(f"半角标点: {result['punct_half']}")
    print(f"字母: {result['letters']}")
    print(f"数字: {result['digits']}")
    print(f"总字符: {result['total']}")
