#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def resolve_path(raw: str) -> Path:
    p = Path(raw)
    if not p.is_absolute():
        p = ROOT / p
    return p


def count_body_hanzi(text: str) -> int:
    lines = text.splitlines()
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
    body = "\n".join(lines)
    return len(re.findall(r"[一-龥]", body))


def validate_title_format(text: str, chapter_num: str) -> tuple[bool, str]:
    """验证首行是否为正确格式的章节标题。

    返回: (is_valid, error_message)
    """
    lines = text.strip().splitlines()
    if not lines:
        return False, "草稿文件为空"

    first_line = lines[0].strip()

    # 检查标题格式：# 第X章 章名
    title_pattern = rf"^#\s*第{chapter_num}章\s+.+$"
    if not re.match(title_pattern, first_line):
        # 检查是否有任何标题格式
        if not first_line.startswith("# "):
            return False, f"首行缺少标题，当前首行: {first_line[:50]}..."
        # 有标题但格式不对
        if not re.match(r"^#\s*第\d+章\s+.+$", first_line):
            return False, f"标题格式错误，应为 '# 第{chapter_num}章 章名'，实际为: {first_line[:50]}..."
        # 章节号不对
        return False, f"标题章节号错误，应为第{chapter_num}章"

    return True, ""


def infer_chapter_number(path: Path) -> str:
    m = re.search(r"chapter_(\d{3})", path.name)
    if not m:
        raise SystemExit(f"FAIL: 无法从文件名推断章节号 {path.name}")
    return m.group(1)


def load_chapter_type(chapter_num: str) -> str:
    chapter_types = ROOT / "design" / "chapter_types.json"
    if not chapter_types.exists():
        raise SystemExit(f"FAIL: 找不到章节类型真源 {chapter_types}")
    data = json.loads(chapter_types.read_text())
    entry = data.get(chapter_num)
    if not entry:
        raise SystemExit(f"FAIL: chapter_types.json 缺少第 {chapter_num} 章条目")
    chapter_type = entry.get("chapter_type")
    if chapter_type not in {"normal", "key"}:
        raise SystemExit(f"FAIL: 第 {chapter_num} 章 chapter_type 非法：{chapter_type}")
    return chapter_type


def main() -> int:
    parser = argparse.ArgumentParser(description="章节准入硬门槛校验")
    parser.add_argument("--draft", required=True, help="草稿文件")
    parser.add_argument("--meta", required=True, help="BCE 写作元数据文件")
    parser.add_argument("--chapter-type", choices=["normal", "key"], help="可选；不传则按章节号自动读取")
    parser.add_argument("--require-provider", default="BCE")
    args = parser.parse_args()

    draft_path = resolve_path(args.draft)
    meta_path = resolve_path(args.meta)

    if not draft_path.exists():
        raise SystemExit(f"FAIL: 找不到草稿文件 {draft_path}")
    if not meta_path.exists():
        raise SystemExit(f"FAIL: 找不到 BCE 元数据文件 {meta_path}")

    meta = json.loads(meta_path.read_text())
    provider_name = meta.get("provider_name", "")
    model = meta.get("model", "")
    output_chars = int(meta.get("output_chars", 0))
    chapter_num = infer_chapter_number(draft_path)
    chapter_type = args.chapter_type or load_chapter_type(chapter_num)

    # 验证标题格式
    draft_text = draft_path.read_text()
    title_valid, title_error = validate_title_format(draft_text, chapter_num)
    if not title_valid:
        raise SystemExit(f"FAIL: {title_error}")

    # 提取标题用于输出
    first_line = draft_text.strip().splitlines()[0] if draft_text.strip() else ""
    title_display = first_line[2:] if first_line.startswith("# ") else "无标题"
    thresholds = {
        "normal": (3500, 7000),
        "key": (5000, 8000),
    }
    warn_thresholds = {
        "normal": 5500,
        "key": 6500,
    }
    min_chars, max_chars = thresholds[chapter_type]
    warn_chars = warn_thresholds[chapter_type]
    actual_chars = count_body_hanzi(draft_path.read_text())

    if provider_name != args.require_provider:
        raise SystemExit(f"FAIL: provider_name={provider_name}，要求 {args.require_provider}")
    if not model:
        raise SystemExit("FAIL: 未记录模型名")
    if actual_chars < min_chars:
        raise SystemExit(
            f"FAIL: 第 {chapter_num} 章类型 {chapter_type}，汉字数 {actual_chars} 低于下限 {min_chars}"
        )
    if output_chars <= 0:
        raise SystemExit("FAIL: BCE 元数据缺少有效输出长度")

    status = "PASS"
    note = ""
    if actual_chars > warn_chars:
        status = "WARN"
        note = f" warn=超出建议上限{warn_chars}，但仍在可放行范围内"
    if actual_chars > max_chars:
        status = "WARN"
        note = f" warn=超出宽松上限{max_chars}，建议人工复核节奏"

    print(
        f"{status}: chapter={chapter_num} type={chapter_type} provider={provider_name} model={model} hanzi={actual_chars} title=\"{title_display}\" meta_output_chars={output_chars}{note}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
