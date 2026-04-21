#!/usr/bin/env python3
import argparse
import re
from datetime import date
from pathlib import Path
from typing import Optional


ROOT = Path(__file__).resolve().parent.parent
OUTLINE = ROOT / "OUTLINE.md"


def resolve_path(raw: Optional[str]) -> Optional[Path]:
    if not raw:
        return None
    path = Path(raw)
    if not path.is_absolute():
        path = ROOT / path
    return path


def extract_title(chapter_file: Optional[Path], chapter_num: int, fallback: Optional[str]) -> str:
    if fallback:
        return fallback.strip()
    if chapter_file and chapter_file.exists():
        text = chapter_file.read_text()
        match = re.search(r"^#\s*第[一二三四五六七八九十百零0-9]+章\s+(.+)$", text, re.M)
        if match:
            return match.group(1).strip()
    return f"第{chapter_num}章"


def build_entry(
    chapter_num: int,
    title: str,
    summary: str,
    state: str,
    foreshadow: str,
    scores: str,
    models: str,
    completed_on: str,
) -> str:
    return "\n".join(
        [
            f"**第{chapter_num}章《{title}》** | {completed_on}",
            f"- 摘要：{summary.strip()}",
            f"- 谢长庚状态：{state.strip()}",
            f"- 新增伏笔：{foreshadow.strip()}",
            f"- 评分：{scores.strip()}",
            f"- 模型消耗：{models.strip()}",
        ]
    )


def replace_or_insert_log(outline_text: str, chapter_num: int, entry: str) -> str:
    match = re.search(r"(?ms)(<!-- LOG_START -->)(.*?)(<!-- LOG_END -->)", outline_text)
    if not match:
        raise SystemExit("OUTLINE.md 中未找到 LOG_START / LOG_END 标记")

    start_marker, log_body, end_marker = match.group(1), match.group(2), match.group(3)
    entries = [part.strip() for part in re.split(r"\n(?=\*\*第\d+章《)", log_body.strip()) if part.strip()]
    new_entries = []
    inserted = False

    for raw in entries:
        entry_match = re.match(r"\*\*第(\d+)章《", raw)
        if not entry_match:
            new_entries.append(raw)
            continue
        current_num = int(entry_match.group(1))
        if current_num == chapter_num:
            if not inserted:
                new_entries.append(entry)
                inserted = True
            continue
        if not inserted and current_num > chapter_num:
            new_entries.append(entry)
            inserted = True
        new_entries.append(raw)

    if not inserted:
        new_entries.append(entry)

    rebuilt = "\n".join(
        [
            start_marker,
            "\n".join(new_entries).strip(),
            end_marker,
        ]
    )
    return outline_text[: match.start()] + rebuilt + outline_text[match.end() :]


def main() -> int:
    parser = argparse.ArgumentParser(description="自动追加或更新 OUTLINE.md 写作日志。")
    parser.add_argument("--chapter", type=int, required=True, help="章节号，例如 3")
    parser.add_argument("--chapter-file", help="章节正文文件，用于自动提取标题")
    parser.add_argument("--title", help="章节标题；不传则优先从 chapter-file 标题提取")
    parser.add_argument("--summary", required=True, help="100字左右摘要")
    parser.add_argument("--state", required=True, help="人物当前状态")
    parser.add_argument("--foreshadow", required=True, help="新增伏笔")
    parser.add_argument("--scores", required=True, help="评分字段")
    parser.add_argument("--models", required=True, help="模型消耗字段")
    parser.add_argument(
        "--date",
        default=date.today().isoformat(),
        help="完成日期，默认今天",
    )
    args = parser.parse_args()

    chapter_file = resolve_path(args.chapter_file)
    title = extract_title(chapter_file, args.chapter, args.title)
    entry = build_entry(
        chapter_num=args.chapter,
        title=title,
        summary=args.summary,
        state=args.state,
        foreshadow=args.foreshadow,
        scores=args.scores,
        models=args.models,
        completed_on=args.date,
    )

    outline_text = OUTLINE.read_text()
    updated = replace_or_insert_log(outline_text, args.chapter, entry)
    OUTLINE.write_text(updated)
    print(f"OUTLINE 日志已更新：第{args.chapter}章《{title}》")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
