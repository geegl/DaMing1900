#!/bin/bash
set -euo pipefail

cat <<'EOF' >&2
错误：
  官方 Claude 已从《大明1900》正式流水线中移除。

请改用：
  ./scripts/run_bce_consistency_review.sh <draft_file> [model] [output_file]

原因：
  本项目已切换为 BCE + Codex only，禁止在正式章节生产中再调用 claude -p。
EOF
exit 1
