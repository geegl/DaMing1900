#!/usr/bin/env python3
"""
I-Lang Runner for 《大明1900》
执行I-Lang技能文件，优化Agent协作流程

用法：
    python3 automation/scripts/ilang_runner.py --skill chapter_gen.ilang --chapter 004 --pov 老鬼
"""

import os
import sys
import re
import json
import argparse
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent

# 缓存存储
CACHE: Dict[str, Any] = {}

# 支持的动词
VERBS = {
    "READ": "读取文件",
    "CACHE": "缓存数据",
    "FILT": "过滤数据",
    "GEN": "生成内容",
    "CHECK": "检查规则",
    "VERIFY": "验证结果",
    "APPLY": "应用修正",
    "SYNC": "同步状态",
    "COMMIT": "Git提交",
    "NOTIFY": "发送通知",
    "OUT": "输出结果",
    "SUM": "总结内容",
    "ANALYZE": "分析数据",
    "UPDATE": "更新文件",
    "WRITE": "写入文件"
}


def parse_ilang_line(line: str) -> Optional[Dict]:
    """解析I-Lang语法行"""
    # 移除注释
    line = re.sub(r'#.*$', '', line).strip()
    if not line:
        return None

    # 匹配 [VERB:SOURCE|params]=>[NEXT_VERB|params]=>...
    pattern = r'\[(\w+)(?::([^\]|]+))?(?:\|([^\]]+))?\]'
    matches = re.findall(pattern, line)

    if not matches:
        return None

    steps = []
    for verb, source, params in matches:
        step = {"verb": verb}
        if source:
            step["source"] = source
        if params:
            # 解析参数 param1=val1,param2=val2
            param_dict = {}
            for param in params.split(','):
                if '=' in param:
                    key, value = param.split('=', 1)
                    param_dict[key.strip()] = value.strip()
                else:
                    param_dict[param.strip()] = True
            step["params"] = param_dict
        steps.append(step)

    return {"steps": steps}


def resolve_variables(text: str, variables: Dict[str, str]) -> str:
    """替换变量"""
    for key, value in variables.items():
        text = text.replace(f"{{{key}}}", str(value))
    return text


def execute_read(source: str, params: Dict) -> Any:
    """执行READ操作"""
    source = resolve_variables(source, params)
    file_path = PROJECT_ROOT / source

    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"📖 READ: {source} ({len(content)} chars)")
        return content
    else:
        print(f"⚠️ READ: {source} not found")
        return None


def execute_cache(key: str, data: Any = None) -> Any:
    """执行CACHE操作"""
    if data:
        CACHE[key] = data
        print(f"💾 CACHE: {key} cached")
        return data
    elif key in CACHE:
        print(f"📂 CACHE: {key} retrieved")
        return CACHE[key]
    else:
        print(f"⚠️ CACHE: {key} not found")
        return None


def execute_filt(data: Any, params: Dict) -> Any:
    """执行FILT操作"""
    if not data:
        return None

    # 简单的关键词过滤
    if "key" in params:
        keys = params["key"].split(',')
        lines = data.split('\n')
        filtered = []
        for line in lines:
            for key in keys:
                if key.strip().lower() in line.lower():
                    filtered.append(line)
                    break
        result = '\n'.join(filtered)
        print(f"🔍 FILT: {len(filtered)} lines matched")
        return result

    return data


def execute_verify(source: str, params: Dict) -> Dict:
    """执行VERIFY操作"""
    source = resolve_variables(source, params)

    # 如果是世界观验证脚本
    if "worldview_validator" in source:
        file_path = params.get("file", "")
        cmd = f"python3 {PROJECT_ROOT / source} {PROJECT_ROOT / file_path}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(f"✅ VERIFY: {source}")
        print(result.stdout)
        return {"success": "错误" not in result.stdout, "output": result.stdout}

    return {"success": True, "message": "Verification not implemented"}


def execute_sync(source: str, params: Dict) -> bool:
    """执行SYNC操作"""
    chapter = params.get("ch", "0")
    state_file = PROJECT_ROOT / source

    if state_file.exists():
        with open(state_file, 'r', encoding='utf-8') as f:
            state = json.load(f)

        state["current_chapter"] = int(chapter)
        state["chapters_generated"] = state.get("chapters_generated", 0) + 1

        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

        print(f"🔄 SYNC: state.json updated to chapter {chapter}")
        return True

    return False


def execute_commit(params: Dict) -> bool:
    """执行COMMIT操作"""
    msg = params.get("msg", "Auto commit")
    cmd = f"git add -A && git commit -m \"{msg}\""
    result = subprocess.run(cmd, shell=True, cwd=PROJECT_ROOT, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"📤 COMMIT: {msg}")
        # Push
        subprocess.run("git push", shell=True, cwd=PROJECT_ROOT)
        return True
    else:
        print(f"⚠️ COMMIT: {result.stderr}")
        return False


def execute_notify(params: Dict) -> bool:
    """执行NOTIFY操作"""
    msg = params.get("msg", "")

    # Telegram配置
    bot_token = "8143117746:AAG25K1aaP4_nU6ESxWRbodfN-ry70V5ob8"
    chat_id = "6579837315"

    import urllib.request
    import urllib.parse

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": msg,
        "parse_mode": "Markdown"
    }).encode()

    try:
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            if result.get("ok"):
                print(f"📨 NOTIFY: Telegram message sent")
                return True
    except Exception as e:
        print(f"⚠️ NOTIFY: {e}")

    return False


def run_skill(skill_file: str, variables: Dict[str, str]):
    """运行I-Lang技能文件"""
    skill_path = PROJECT_ROOT / skill_file

    if not skill_path.exists():
        print(f"❌ Skill file not found: {skill_file}")
        return

    print(f"\n{'='*50}")
    print(f"🚀 Running I-Lang Skill: {skill_file}")
    print(f"📊 Variables: {variables}")
    print(f"{'='*50}\n")

    with open(skill_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 替换变量
    content = resolve_variables(content, variables)

    # 解析并执行每一行
    current_data = None
    for line in content.split('\n'):
        parsed = parse_ilang_line(line)
        if not parsed:
            continue

        for step in parsed["steps"]:
            verb = step["verb"]
            source = step.get("source", "")
            params = step.get("params", {})

            # 执行动词
            if verb == "READ":
                current_data = execute_read(source, params)
            elif verb == "CACHE":
                if source:
                    current_data = execute_cache(source, current_data)
                elif current_data:
                    # 从缓存读取
                    current_data = execute_cache(params.get("key", ""), None)
            elif verb == "FILT":
                current_data = execute_filt(current_data, params)
            elif verb == "VERIFY":
                current_data = execute_verify(source, params)
            elif verb == "SYNC":
                execute_sync(source, params)
            elif verb == "COMMIT":
                execute_commit(params)
            elif verb == "NOTIFY":
                execute_notify(params)
            elif verb == "OUT":
                print(f"✅ OUT: {source or 'complete'}")

    print(f"\n{'='*50}")
    print(f"✅ I-Lang Skill Complete")
    print(f"{'='*50}\n")


def main():
    parser = argparse.ArgumentParser(description="I-Lang Runner for 《大明1900》")
    parser.add_argument("--skill", required=True, help="I-Lang技能文件路径")
    parser.add_argument("--chapter", default="001", help="章节编号")
    parser.add_argument("--pov", default="陈铁", help="POV角色")
    parser.add_argument("--vars", help="额外变量（JSON格式）")

    args = parser.parse_args()

    variables = {
        "chapter": args.chapter,
        "pov": args.pov
    }

    if args.vars:
        extra_vars = json.loads(args.vars)
        variables.update(extra_vars)

    run_skill(args.skill, variables)


if __name__ == "__main__":
    main()
