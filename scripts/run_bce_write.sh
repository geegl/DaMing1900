#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
MODEL="${2:-deepseek-v3.2}"
CHAPTER_NUM_RAW="${1:-}"

usage() {
  cat <<'EOF'
用法:
  ./scripts/run_bce_write.sh <chapter_number> [model] [output_file]

示例:
  ./scripts/run_bce_write.sh 3
  ./scripts/run_bce_write.sh 3 glm-5
  ./scripts/run_bce_write.sh 3 glm-5 chapters/chapter_003_draft.md
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

CHAPTER_NUM="$(printf '%03d' "$CHAPTER_NUM_RAW")"
OUTPUT_FILE="${3:-$ROOT_DIR/chapters/chapter_${CHAPTER_NUM}_draft.md}"

python3 "$ROOT_DIR/scripts/build_context_pack.py" "$CHAPTER_NUM_RAW" >/dev/null

PACK_FILE="$ROOT_DIR/context/generated/chapter_${CHAPTER_NUM}/write_pack.md"
PROMPT_FILE="$(mktemp)"
trap 'rm -f "$PROMPT_FILE"' EXIT

cat > "$PROMPT_FILE" <<EOF
你现在是《大明1900》的章节写作模型。请根据以下压缩上下文直接写出本章正文。

写作要求：
1. 只输出正文，不解释，不做提纲，不做点评
2. 目标字数 3500-4500 字
3. 第三人称限制视角，紧贴谢长庚
4. 开头 200 字内必须进入具体场景
5. 结尾必须保留强钩子
6. 严禁出现 AI 痕迹词、满清词、现代说明腔

以下是压缩上下文包：

$(cat "$PACK_FILE")
EOF

python3 "$ROOT_DIR/scripts/bce_client.py" \
  --model "$MODEL" \
  --prompt-file "$PROMPT_FILE" \
  --output-file "$OUTPUT_FILE" \
  --max-tokens 12000 >/dev/null

echo "BCE 正文完成：$OUTPUT_FILE"
