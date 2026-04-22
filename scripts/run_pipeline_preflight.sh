#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PASS=0
FAIL=0

ok() {
  echo "[PASS] $1"
  PASS=$((PASS + 1))
}

bad() {
  echo "[FAIL] $1"
  FAIL=$((FAIL + 1))
}

check_bin() {
  if command -v "$1" >/dev/null 2>&1; then
    ok "命令可用: $1"
  else
    bad "命令缺失: $1"
  fi
}

check_bin codex
check_bin python3

if [ -n "${TELEGRAM_BOT_TOKEN:-}" ]; then
  ok "TELEGRAM_BOT_TOKEN 已加载"
else
  bad "TELEGRAM_BOT_TOKEN 未加载"
fi

if [ -x "$ROOT_DIR/send_telegram.sh" ]; then
  ok "send_telegram.sh 可执行"
else
  bad "send_telegram.sh 不可执行"
fi

if [ -x "$ROOT_DIR/scripts/append_outline_log.py" ]; then
  ok "append_outline_log.py 可执行"
else
  bad "append_outline_log.py 不可执行"
fi

if [ -f "$HOME/.cc-switch/settings.json" ] && [ -f "$HOME/.cc-switch/cc-switch.db" ]; then
  ok "CC Switch 配置存在"
else
  bad "CC Switch 配置缺失"
fi

if python3 "$ROOT_DIR/scripts/bce_client.py" --model deepseek-v3.2 --prompt-file <(printf '只回复：BCE_SMOKE_OK') --output-file /tmp/daming1900_bce_smoke.txt --max-tokens 32 >/dev/null 2>&1; then
  if grep -q "BCE_SMOKE_OK" /tmp/daming1900_bce_smoke.txt; then
    ok "BCE API smoke test 通过"
  else
    bad "BCE API 已响应，但 smoke 输出不符合预期"
  fi
else
  bad "BCE API smoke test 失败"
fi

if [ -f "$ROOT_DIR/scripts/validate_chapter_gate.py" ]; then
  ok "validate_chapter_gate.py 已存在"
else
  bad "validate_chapter_gate.py 缺失"
fi

if [ -d "$HOME/.agents/skills/superpowers" ]; then
  ok "superpowers 已安装"
else
  bad "superpowers 未安装"
fi

if [ -d "$HOME/.agents/skills/gstack-office-hours" ]; then
  ok "gstack-office-hours 已安装"
else
  bad "gstack-office-hours 未安装"
fi

echo
echo "汇总：PASS=$PASS FAIL=$FAIL"
if [ "$FAIL" -gt 0 ]; then
  exit 1
fi
