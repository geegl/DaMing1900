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


def count_body_chars(text: str) -> int:
    lines = text.splitlines()
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
    body = "\n".join(lines)
    return len(re.sub(r"\s+", "", body))


def main() -> int:
    parser = argparse.ArgumentParser(description="章节准入硬门槛校验")
    parser.add_argument("--draft", required=True, help="草稿文件")
    parser.add_argument("--meta", required=True, help="BCE 写作元数据文件")
    parser.add_argument("--min-chars", type=int, default=3500)
    parser.add_argument("--max-chars", type=int, default=4500)
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
    actual_chars = count_body_chars(draft_path.read_text())

    if provider_name != args.require_provider:
        raise SystemExit(f"FAIL: provider_name={provider_name}，要求 {args.require_provider}")
    if not model:
        raise SystemExit("FAIL: 未记录模型名")
    if actual_chars < args.min_chars or actual_chars > args.max_chars:
        raise SystemExit(
            f"FAIL: 字数 {actual_chars} 不在 {args.min_chars}-{args.max_chars} 范围内"
        )
    if output_chars <= 0:
        raise SystemExit("FAIL: BCE 元数据缺少有效输出长度")

    print(
        f"PASS: provider={provider_name} model={model} body_chars={actual_chars} meta_output_chars={output_chars}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
