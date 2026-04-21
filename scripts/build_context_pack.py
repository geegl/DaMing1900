#!/usr/bin/env python3
import argparse
import re
from pathlib import Path
from typing import Optional


ROOT = Path(__file__).resolve().parent.parent
OUTLINE = ROOT / "OUTLINE.md"
BIBLE = ROOT / "BIBLE.md"
STYLE = ROOT / "STYLE.md"


def extract_outline_block(chapter_num: int) -> str:
    text = OUTLINE.read_text()
    pattern = re.compile(
        rf"(?ms)^\*\*第{chapter_num}章：.*?(?=^\*\*第{chapter_num + 1}章：|^---|\Z)"
    )
    match = pattern.search(text)
    if not match:
        raise SystemExit(f"未在 OUTLINE.md 中找到第 {chapter_num} 章")
    return match.group(0).strip()


def extract_section(text: str, start_marker: str, end_marker: Optional[str] = None) -> str:
    start = text.find(start_marker)
    if start == -1:
        return ""
    if end_marker:
        end = text.find(end_marker, start + len(start_marker))
        if end == -1:
            end = len(text)
    else:
        end = len(text)
    return text[start:end].strip()


def extract_character_rules(names: list[str]) -> str:
    bible_text = BIBLE.read_text()
    style_text = STYLE.read_text()
    appendix = extract_section(bible_text, "## 十六、角色提取索引", None)
    blocks = []
    for name in names:
        bible_match = re.search(
            rf"(?ms)^### {re.escape(name)}.*?(?=^### |\Z)", appendix or bible_text
        )
        style_match = re.search(
            rf"(?ms)^\*\*{re.escape(name)}对话风格\*\*：.*?(?=^\*\*.*?对话风格\*\*：|^---|\Z)",
            style_text,
        )
        if bible_match:
            blocks.append(bible_match.group(0).strip())
        if style_match:
            blocks.append(style_match.group(0).strip())
    return "\n\n".join(blocks).strip()


def select_compact_character_names(chapter_brief: str, names: list[str]) -> list[str]:
    selected = ["谢长庚"]
    for name in names:
        if name == "谢长庚":
            continue
        if name in chapter_brief:
            selected.append(name)
    return selected


def build_forbidden_rules() -> str:
    style_text = STYLE.read_text()
    parts = [
        extract_section(style_text, "## 五、禁用词表", "## 六、场景描写规范"),
        extract_section(style_text, "## 六、场景描写规范", "## 七、章节内一致性检查清单"),
    ]
    return "\n\n".join([p for p in parts if p]).strip()


def build_current_state() -> str:
    text = OUTLINE.read_text()
    match = re.search(r"(?ms)<!-- LOG_START -->(.*?)<!-- LOG_END -->", text)
    if not match:
        return "# 最近日志与临近状态\n\n未找到 LOG 区。"
    block = match.group(1).strip()
    entries = [part.strip() for part in re.split(r"\n(?=\*\*第\d+章)", block) if part.strip()]
    recent = "\n\n".join(entries[-3:]) if entries else "LOG 区为空。"
    return "# 最近日志与临近状态\n\n" + recent.strip()


def build_current_state_compact() -> str:
    text = OUTLINE.read_text()
    match = re.search(r"(?ms)<!-- LOG_START -->(.*?)<!-- LOG_END -->", text)
    if not match:
        return "# 最近日志与临近状态（精简）\n\n未找到 LOG 区。"
    block = match.group(1).strip()
    entries = [part.strip() for part in re.split(r"\n(?=\*\*第\d+章)", block) if part.strip()]
    recent = entries[-2:] if entries else []
    compact_entries = []
    for entry in recent:
        lines = [line.rstrip() for line in entry.splitlines() if line.strip()]
        compact_entries.append("\n".join(lines[:2]))
    compact = "\n\n".join(compact_entries) if compact_entries else "LOG 区为空。"
    return "# 最近日志与临近状态（精简）\n\n" + compact.strip()


def previous_excerpt(chapter_num: int) -> str:
    prev = ROOT / "chapters" / f"chapter_{chapter_num - 1:03d}.md"
    if not prev.exists():
        return "无上一章正文文件。"
    text = prev.read_text()
    return text[-1200:].strip()


def previous_excerpt_compact(chapter_num: int) -> str:
    excerpt = previous_excerpt(chapter_num)
    return excerpt[-700:].strip()


def build_voice_rules_compact(full_text: str) -> str:
    text = full_text.strip()
    if len(text) <= 1100:
        return "# 人物音色规则（精简）\n\n" + text
    lines = [line for line in text.splitlines() if line.strip()]
    compact_lines = []
    bullet_count = 0
    for line in lines:
        if line.startswith("### ") or "对话风格" in line:
            compact_lines.append(line)
            bullet_count = 0
            continue
        if line.startswith("- ") and bullet_count < 2:
            compact_lines.append(line)
            bullet_count += 1
            continue
    compact = "\n".join(compact_lines).strip()
    return "# 人物音色规则（精简）\n\n" + compact[:1100].strip()


def build_forbidden_rules_compact(full_text: str) -> str:
    lines = [line.rstrip() for line in full_text.splitlines() if line.strip()]
    keep = []
    quote_count = 0
    for line in lines:
        if line.startswith("## ") or line.startswith("### "):
            keep.append(line)
            continue
        if line.startswith("```"):
            continue
        if quote_count < 8:
            keep.append(line)
            quote_count += 1
    return "# 禁用规则与场景约束（精简）\n\n" + "\n".join(keep).strip()


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="生成章节上下文压缩包。")
    parser.add_argument("chapter", type=int, help="章节号，例如 3")
    parser.add_argument(
        "--characters",
        default="谢长庚,朱载机,朱载昱,郑玄机,刘恩,沈青鸾,陆知微",
        help="逗号分隔的人物名",
    )
    args = parser.parse_args()

    chapter_num = args.chapter
    chapter_dir = ROOT / "context" / "generated" / f"chapter_{chapter_num:03d}"
    names = [name.strip() for name in args.characters.split(",") if name.strip()]

    chapter_brief = "# 章节目标\n\n" + extract_outline_block(chapter_num)
    current_state = build_current_state()
    voice_rules = "# 人物音色规则\n\n" + extract_character_rules(names)
    forbidden_rules = "# 禁用规则与场景约束\n\n" + build_forbidden_rules()
    prev_excerpt = "# 上一章结尾摘录\n\n" + previous_excerpt(chapter_num)
    current_state_compact = build_current_state_compact()
    compact_names = select_compact_character_names(chapter_brief, names)
    voice_rules_compact = build_voice_rules_compact(extract_character_rules(compact_names))
    forbidden_rules_compact = build_forbidden_rules_compact(build_forbidden_rules())
    prev_excerpt_compact = "# 上一章结尾短摘录\n\n" + previous_excerpt_compact(chapter_num)
    write_pack = "\n\n".join(
        [
            chapter_brief,
            current_state_compact,
            voice_rules_compact,
            forbidden_rules_compact,
            prev_excerpt_compact,
        ]
    )

    pack = "\n\n".join(
        [
            chapter_brief,
            current_state,
            voice_rules,
            forbidden_rules,
            prev_excerpt,
        ]
    )

    write(chapter_dir / "chapter_brief.md", chapter_brief)
    write(chapter_dir / "current_state.md", current_state)
    write(chapter_dir / "voice_rules.md", voice_rules)
    write(chapter_dir / "forbidden_rules.md", forbidden_rules)
    write(chapter_dir / "previous_excerpt.md", prev_excerpt)
    write(chapter_dir / "pack.md", pack)
    write(chapter_dir / "write_pack.md", write_pack)
    print(chapter_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
