#!/bin/bash
# 《大明1900》Git初始化脚本
# 使用方法：bash setup_github.sh

echo "🎋 《大明1900》Git初始化"
echo "========================"
echo ""

# 检查是否已在Git仓库中
if [ -d ".git" ]; then
    echo "⚠️  已经是Git仓库了"
    echo ""
    echo "如果需要重新初始化，请先删除.git文件夹："
    echo "  rm -rf .git"
    exit 1
fi

# 初始化Git仓库
echo "📦 初始化Git仓库..."
git init

# 添加所有文件
echo "📝 添加所有文件..."
git add .

# 创建首次提交
echo "💾 创建首次提交..."
git commit -m "初始化《大明1900》项目

- 完成第001章《煤烟落在米饭上》（3,902字）
- 建立完整的项目文档体系
- 实现8层防护系统
- 创建自动化进度报告
- 总文档数：28个

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"

echo ""
echo "✅ Git仓库初始化完成！"
echo ""
echo "📋 下一步："
echo ""
echo "1. 在GitHub创建私有仓库："
echo "   访问：https://github.com/new"
echo "   Repository name: Daming1900"
echo "   选择：Private（私有）"
echo ""
echo "2. 连接远程仓库："
echo "   git remote add origin https://github.com/你的用户名/Daming1900.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "或者告诉我你的GitHub用户名，我可以帮你完成后续步骤！"
