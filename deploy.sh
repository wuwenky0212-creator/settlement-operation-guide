#!/bin/bash

# 结算操作指引系统 - 快速部署脚本

echo "🚀 开始部署结算操作指引系统..."

# 检查是否已初始化 Git
if [ ! -d .git ]; then
    echo "📦 初始化 Git 仓库..."
    git init
    git add .
    git commit -m "Initial commit: Settlement Operation Guide System"
else
    echo "✅ Git 仓库已存在"
fi

# 检查是否已添加远程仓库
if ! git remote | grep -q origin; then
    echo "❓ 请输入你的 GitHub 仓库 URL (例如: https://github.com/username/repo.git):"
    read REPO_URL
    git remote add origin $REPO_URL
    echo "✅ 已添加远程仓库"
else
    echo "✅ 远程仓库已配置"
fi

# 推送到 GitHub
echo "📤 推送代码到 GitHub..."
git branch -M main
git push -u origin main

echo ""
echo "✅ 代码已推送到 GitHub!"
echo ""
echo "📋 下一步操作："
echo "1. 访问 https://railway.app 并使用 GitHub 登录"
echo "2. 点击 'New Project' → 'Deploy from GitHub repo'"
echo "3. 选择你的仓库"
echo "4. 按照 RAILWAY_DEPLOYMENT.md 中的说明配置服务"
echo ""
echo "📖 详细部署指南请查看: RAILWAY_DEPLOYMENT.md"
