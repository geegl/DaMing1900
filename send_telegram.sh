#!/bin/bash
# 《大明1900》章节完成通知
# 用法: ./send_telegram.sh "第X章《标题》" XXXX X X "摘要内容" "问题列表或无"
#        参数:  $1=章节信息  $2=字数  $3=钩子评分  $4=Codex评分  $5=摘要  $6=待处理

CHAT_ID="6579837315"

# Token 必须通过环境变量传入，不在此文件硬编码
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
  echo "❌ 错误：未设置 TELEGRAM_BOT_TOKEN 环境变量"
  echo "   请在 ~/.zshrc 中加入: export TELEGRAM_BOT_TOKEN=\"你的token\""
  exit 1
fi

CHAPTER="$1"
WORD_COUNT="${2:-未知}"
HOOK_SCORE="${3:-?}"
CODEX_SCORE="${4:-?}"
SUMMARY="${5:-无摘要}"
ISSUES="${6:-无}"

MESSAGE="📖 <b>${CHAPTER}</b> 完成
字数：${WORD_COUNT} | 钩子评分：${HOOK_SCORE}/5 | Codex评分：${CODEX_SCORE}/5
📝 摘要：${SUMMARY}
⚠️ 待处理：${ISSUES}"

RESPONSE=$(curl -s -X POST \
  "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -d "chat_id=${CHAT_ID}" \
  --data-urlencode "text=${MESSAGE}" \
  -d "parse_mode=HTML")

# 检查是否成功
if echo "$RESPONSE" | grep -q '"ok":true'; then
  echo "✅ Telegram 通知已发送"
else
  echo "❌ 发送失败，响应：$RESPONSE"
  exit 1
fi
