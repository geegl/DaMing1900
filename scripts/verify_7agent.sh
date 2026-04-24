#!/bin/bash
# verify_7agent.sh - 验证指定章节是否完成全部7个Agent步骤
# Usage: ./scripts/verify_7agent.sh 125

CHAPTER=$1

if [ -z "$CHAPTER" ]; then
    echo "Usage: ./scripts/verify_7agent.sh <chapter_number>"
    exit 1
fi

echo "=== 7-Agent 验证: 第${CHAPTER}章 ==="
echo ""

MISSING=0

# Step 1: Context Pack
PACK_FILE="context/generated/chapter_${CHAPTER}/write_pack.md"
if [ -f "$PACK_FILE" ]; then
    echo "✓ Step 1 Context Pack: $PACK_FILE"
else
    echo "✗ Step 1 Context Pack: MISSING - $PACK_FILE"
    MISSING=$((MISSING+1))
fi

# Step 2: Writer
CHAPTER_FILE="chapters/chapter_${CHAPTER}.md"
if [ -f "$CHAPTER_FILE" ]; then
    WORDS=$(grep -o '[一-龥]' "$CHAPTER_FILE" | wc -l | tr -d ' ')
    echo "✓ Step 2 Writer: $CHAPTER_FILE ($WORDS 汉字)"
else
    echo "✗ Step 2 Writer: MISSING - $CHAPTER_FILE"
    MISSING=$((MISSING+1))
fi

# Step 4: Consistency Review
CONSISTENCY_FILE="reviews/consistency/review_bce_consistency_${CHAPTER}.md"
if [ -f "$CONSISTENCY_FILE" ]; then
    echo "✓ Step 4 Consistency: $CONSISTENCY_FILE"
else
    echo "✗ Step 4 Consistency: MISSING - $CONSISTENCY_FILE"
    MISSING=$((MISSING+1))
fi

# Step 5: Codex Review
CODEX_FILE="reviews/codex/review_codex_${CHAPTER}.md"
if [ -f "$CODEX_FILE" ]; then
    echo "✓ Step 5 Codex: $CODEX_FILE"
else
    echo "✗ Step 5 Codex: MISSING - $CODEX_FILE"
    MISSING=$((MISSING+1))
fi

# Step 6: Final Check
FINAL_FILE="reviews/final/review_bce_final_${CHAPTER}.md"
if [ -f "$FINAL_FILE" ]; then
    echo "✓ Step 6 Final: $FINAL_FILE"
else
    echo "✗ Step 6 Final: MISSING - $FINAL_FILE"
    MISSING=$((MISSING+1))
fi

# Step 7: Meta Log
META_FILE="context/generated/chapter_${CHAPTER}/bce_write_meta.json"
if [ -f "$META_FILE" ]; then
    echo "✓ Step 7 Meta: $META_FILE"
else
    echo "✗ Step 7 Meta: MISSING - $META_FILE"
    MISSING=$((MISSING+1))
fi

echo ""
if [ $MISSING -eq 0 ]; then
    echo "=== ✅ 全部通过: 第${CHAPTER}章已完成全部7个步骤 ==="
    exit 0
else
    echo "=== ❌ 缺失 $MISSING 个文件: 第${CHAPTER}章未完成全部步骤 ==="
    exit 1
fi
