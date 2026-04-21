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


def previous_excerpt(chapter_num: int) -> str:
    prev = ROOT / "chapters" / f"chapter_{chapter_num - 1:03d}.md"
    if not prev.exists():
        return "无上一章正文文件。"
    text = prev.read_text()
    return text[-1200:].strip()


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
    write(chapter_dir / "pack.md", pack)
    print(chapter_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
