#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
MODEL="${2:-ernie-4.5-turbo-20260402}"
REVIEWS_DIR="$ROOT_DIR/reviews/consistency"

usage() {
  cat <<'EOF'
用法:
  ./scripts/run_bce_consistency_review.sh <draft_file> [model] [output_file]
EOF
}

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
  usage
  exit 0
fi

if [ $# -lt 1 ] || [ $# -gt 3 ]; then
  usage
  exit 1
fi

DRAFT_INPUT="$1"
if [ ! -f "$DRAFT_INPUT" ]; then
  DRAFT_INPUT="$ROOT_DIR/$DRAFT_INPUT"
fi

if [ ! -f "$DRAFT_INPUT" ]; then
  echo "错误：找不到草稿文件：$1" >&2
  exit 1
fi

mkdir -p "$REVIEWS_DIR"
BASENAME="$(basename "$DRAFT_INPUT")"
CHAPTER_ID="$(printf '%s' "$BASENAME" | sed -E 's/[^0-9]*([0-9]{1,}).*/\1/')"
[ -n "$CHAPTER_ID" ] || CHAPTER_ID="manual"
META_FILE="$ROOT_DIR/context/generated/chapter_$(printf '%03d' "$CHAPTER_ID")/bce_write_meta.json"
OUTPUT_FILE="${3:-$REVIEWS_DIR/review_bce_consistency_${CHAPTER_ID}.md}"
case "$OUTPUT_FILE" in
  /*) ;;
  *) OUTPUT_FILE="$ROOT_DIR/$OUTPUT_FILE" ;;
esac

python3 "$ROOT_DIR/scripts/validate_chapter_gate.py" \
  --draft "$DRAFT_INPUT" \
  --meta "$META_FILE" >/dev/null

PROMPT_FILE="$(mktemp)"
trap 'rm -f "$PROMPT_FILE"' EXIT

cat > "$PROMPT_FILE" <<EOF
你现在是《大明1900》的第一层硬约束校对器。请只输出校对报告，不要输出修改后正文。

检查项目：
1. 世界观一致性：对照 BIBLE.md 中的技术、政治和禁止内容
2. 人物音色一致性：对照 BIBLE.md 和 STYLE.md 的人物说话规则
3. 禁用词扫描：扫描 AI 痕迹词、满清词、时代错误词
4. 结尾钩子强度：1-5 分

输出格式：
- 问题清单（按类别）
- 满清内容扫描结果：PASS / FAIL
- 结尾钩子评分：X/5
- 综合建议：PASS / REVISE

以下是 BIBLE.md：

$(cat "$ROOT_DIR/BIBLE.md")

以下是 STYLE.md：

$(cat "$ROOT_DIR/STYLE.md")

以下是章节草稿：

$(cat "$DRAFT_INPUT")
EOF

python3 "$ROOT_DIR/scripts/bce_client.py" \
  --model "$MODEL" \
  --prompt-file "$PROMPT_FILE" \
  --output-file "$OUTPUT_FILE" \
  --max-tokens 8000 >/dev/null

echo "BCE 一致性校对完成：$OUTPUT_FILE"
