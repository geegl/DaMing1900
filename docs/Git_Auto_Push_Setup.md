# Git自动推送配置方案

## 问题诊断

### 当前状态
- ✅ Git仓库已配置
- ✅ 远程仓库已连接
- ❌ **没有自动推送机制**
- ❌ Git hooks只有sample文件，未启用

### 为什么没有自动推送？

**Claude Code默认行为**：
- Claude会自动提交（commit）
- 但**不会自动推送**（push）
- 需要手动执行 `git push`

---

## 解决方案

### 方案A：Git Post-Commit Hook（推荐）

**创建自动推送hook**：

```bash
# 创建post-commit hook
cat > .git/hooks/post-commit << 'EOF'
#!/bin/bash
# 自动推送到远程仓库

# 获取当前分支
branch=$(git rev-parse --abbrev-ref HEAD)

# 只在main分支自动推送
if [ "$branch" = "main" ]; then
    echo "🚀 自动推送到 origin/main..."
    git push origin main
fi
EOF

# 设置执行权限
chmod +x .git/hooks/post-commit
```

**优点**：
- 每次commit后自动push
- 无需手动操作
- 适合单机开发

**缺点**：
- 可能推送未完成的工作（如果连续commit多次）
- 不适合多人协作（可能推送冲突）

---

### 方案B：Claude设置配置（推荐）

**在settings.json中配置**：

```json
{
  "permissions": {
    "allow": [
      "git push"
    ]
  },
  "hooks": {
    "post_tool_use": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "git status --short && git diff --stat && git log -1 --oneline"
          }
        ]
      }
    ]
  }
}
```

**注意**：这需要Claude Code支持git push权限。

---

### 方案C：手动推送（当前方案）

**每次修改后执行**：

```bash
# 检查状态
git status

# 提交更改
git add -A
git commit -m "描述"

# 推送
git push origin main
```

**优点**：
- 完全控制
- 适合重要项目
- 可以review后再推送

---

## 推荐方案

### 对于这个项目：

**使用方案A（Git Hook）+ 方案C（关键节点手动）**

1. **日常修改** → 自动推送（Hook）
2. **重要节点**（如完成一章、完成一批次）→ 手动推送确认

### 实施步骤

```bash
# 1. 创建post-commit hook
cat > .git/hooks/post-commit << 'EOF'
#!/bin/bash
branch=$(git rev-parse --abbrev-ref HEAD)
if [ "$branch" = "main" ]; then
    echo "🚀 Auto-pushing to origin/main..."
    git push origin main 2>&1 || echo "⚠️ Push failed (可能网络问题)"
fi
EOF

chmod +x .git/hooks/post-commit

# 2. 测试
echo "test" > test.txt
git add test.txt
git commit -m "Test auto-push"
# 应该自动推送

# 3. 清理测试
git rm test.txt
git commit -m "Remove test file"
```

---

## 后续会自动推送吗？

| 场景 | 是否自动推送 |
|------|------------|
| **现在（无hook）** | ❌ 不会，需要手动 |
| **配置hook后** | ✅ 每次commit自动推送 |
| **写完一章后** | ✅ 自动推送（如果配置hook） |
| **修改Bible/大纲后** | ✅ 自动推送（如果配置hook） |

---

## 建议

**立即配置自动推送hook？**

如果配置，后续所有修改都会自动同步到GitHub，无需手动push。
