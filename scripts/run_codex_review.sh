#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REVIEWS_DIR="$ROOT_DIR/reviews"

usage() {
  cat <<'EOF'
用法:
  ./scripts/run_codex_review.sh <draft_file> [output_file]

示例:
  ./scripts/run_codex_review.sh chapters/chapter_003_draft.md
  ./scripts/run_codex_review.sh chapters/chapter_003_draft.md reviews/review_codex_003.md
EOF
}

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
  usage
  exit 0
fi

if [ $# -lt 1 ] || [ $# -gt 2 ]; then
  usage
  exit 1
fi

DRAFT_INPUT="$1"
if [ ! -f "$DRAFT_INPUT" ]; then
  if [ -f "$ROOT_DIR/$DRAFT_INPUT" ]; then
    DRAFT_INPUT="$ROOT_DIR/$DRAFT_INPUT"
  else
    echo "错误：找不到草稿文件：$1" >&2
    exit 1
  fi
fi

mkdir -p "$REVIEWS_DIR"

if [ $# -eq 2 ]; then
  OUTPUT_FILE="$2"
  case "$OUTPUT_FILE" in
    /*) ;;
    *) OUTPUT_FILE="$ROOT_DIR/$OUTPUT_FILE" ;;
  esac
else
  BASENAME="$(basename "$DRAFT_INPUT")"
  CHAPTER_ID="$(printf '%s' "$BASENAME" | sed -E 's/[^0-9]*([0-9]{1,}).*/\1/')"
  if [ -z "$CHAPTER_ID" ]; then
    CHAPTER_ID="manual"
  fi
  OUTPUT_FILE="$REVIEWS_DIR/review_codex_${CHAPTER_ID}.md"
fi

mkdir -p "$(dirname "$OUTPUT_FILE")"

PROMPT_FILE="$(mktemp)"
trap 'rm -f "$PROMPT_FILE"' EXIT

cat > "$PROMPT_FILE" <<EOF
请对以下《大明1900》章节草稿做独立二次校对，重点检查叙事质量。只输出校对报告，不要输出修改后正文：

1. 叙事节奏——是否存在连续3段以上相同句式或段落长度过于均匀
2. 人物音色——台词是否有角色说话方式互换的情况（谢长庚说话像郑玄机等）
3. AI痕迹——特别检查以下词汇是否出现：
   深深地/不禁/油然而生/心潮澎湃/眸子/苦涩地笑了/嘴角微扬/蓦然/悄然/莫名地
4. 场景真实感——工业/战争场景的细节是否具体，是否有“大机器”等模糊描述

输出要求：
① 分类问题清单（每类最多3条最严重的问题）
② 综合评分 1-5 分
③ 不输出修改后全文

以下是 STYLE.md 中与节奏、禁词、场景有关的约束：

$(cat "$ROOT_DIR/STYLE.md")

以下是章节草稿：

$(cat "$DRAFT_INPUT")
EOF

codex exec \
  --skip-git-repo-check \
  --dangerously-bypass-approvals-and-sandbox \
  -C "$ROOT_DIR" \
  -o "$OUTPUT_FILE" \
  "$(cat "$PROMPT_FILE")"

echo "Codex 二次校对完成：$OUTPUT_FILE"
