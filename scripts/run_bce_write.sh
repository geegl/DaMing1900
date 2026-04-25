#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CHAPTER_NUM_RAW="${1:-}"

usage() {
  cat <<'EOF'
用法:
  ./scripts/run_bce_write.sh <chapter_number> [model] [output_file]

示例:
  ./scripts/run_bce_write.sh 3
  ./scripts/run_bce_write.sh 3 glm-5
  ./scripts/run_bce_write.sh 3 glm-5 draft/chapter_003_draft.md
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
if [ $# -ge 2 ]; then
  MODEL="$2"
else
  MODEL="$(python3 - "$ROOT_DIR" "$CHAPTER_NUM" <<'PY'
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
chapter_num = sys.argv[2]
path = root / "design" / "chapter_types.json"
default_model = "deepseek-v3.2"
if not path.exists():
    print(default_model)
    raise SystemExit(0)

mapping = json.loads(path.read_text())
entry = mapping.get(chapter_num)
if not entry:
    print(default_model)
    raise SystemExit(0)

chapter_type = entry.get("chapter_type", "normal")
print("glm-5" if chapter_type == "key" else default_model)
PY
)"
fi
CHAPTER_TYPE="$(python3 - "$ROOT_DIR" "$CHAPTER_NUM" <<'PY'
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
chapter_num = sys.argv[2]
path = root / "design" / "chapter_types.json"
if not path.exists():
    raise SystemExit("缺少 design/chapter_types.json")

mapping = json.loads(path.read_text())
entry = mapping.get(chapter_num)
if not entry:
    raise SystemExit(f"chapter_types.json 缺少第 {chapter_num} 章")

chapter_type = entry.get("chapter_type")
if chapter_type not in {"normal", "key"}:
    raise SystemExit(f"第 {chapter_num} 章 chapter_type 非法：{chapter_type}")

print(chapter_type)
PY
)"
if [ "$CHAPTER_TYPE" = "key" ]; then
  TARGET_RANGE="5000-6500汉字"
else
  TARGET_RANGE="3500-5500汉字"
fi
OUTPUT_FILE="${3:-$ROOT_DIR/draft/chapter_${CHAPTER_NUM}_draft.md}"
META_FILE="$ROOT_DIR/context/generated/chapter_${CHAPTER_NUM}/bce_write_meta.json"

python3 "$ROOT_DIR/scripts/build_context_pack.py" "$CHAPTER_NUM_RAW" >/dev/null

PACK_FILE="$ROOT_DIR/context/generated/chapter_${CHAPTER_NUM}/write_pack.md"
PROMPT_FILE="$(mktemp)"
trap 'rm -f "$PROMPT_FILE"' EXIT

cat > "$PROMPT_FILE" <<EOF
你现在是《大明1900》的章节写作模型。请根据以下压缩上下文直接写出本章正文。

写作要求：
1. 只输出正文，不解释，不做提纲，不做点评
2. 本章类型为 ${CHAPTER_TYPE}，目标字数 ${TARGET_RANGE}
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
  --output-meta-file "$META_FILE" \
  --require-provider-name BCE \
  --max-tokens 12000 >/dev/null

python3 "$ROOT_DIR/scripts/validate_chapter_gate.py" \
  --draft "$OUTPUT_FILE" \
  --meta "$META_FILE" >/dev/null

echo "BCE 正文完成并通过硬门槛：$OUTPUT_FILE"
