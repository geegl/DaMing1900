#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REVIEWS_DIR="$ROOT_DIR/reviews/final"
MODEL="${2:-ernie-4.5-turbo-20260402}"

usage() {
  cat <<'EOF'
用法:
  ./scripts/run_bce_final_check.sh <draft_file> [model] [output_file]
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
OUTPUT_FILE="${3:-$REVIEWS_DIR/review_bce_final_${CHAPTER_ID}.md}"
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
你现在是《大明1900》的终稿质检器。请只输出最终质检报告，不要输出修改后正文。

重点检查：
1. 连载感：读者是否会自然追下一章
2. 流畅度：段落是否顺，是否有解释腔和明显机械拼接感
3. 人物可信度：谢长庚、朱载机等角色是否像自己
4. 结尾钩子：是否足够强，是否值得追更

输出格式：
- 终检摘要（3-5 句）
- 主要问题（如无则写“无重大问题”）
- 连载感评分：X/5
- 最终结论：PASS / REVISE

以下是章节草稿：

$(cat "$DRAFT_INPUT")
EOF

python3 "$ROOT_DIR/scripts/bce_client.py" \
  --model "$MODEL" \
  --prompt-file "$PROMPT_FILE" \
  --output-file "$OUTPUT_FILE" \
  --max-tokens 6000 >/dev/null

echo "BCE 终检完成：$OUTPUT_FILE"
