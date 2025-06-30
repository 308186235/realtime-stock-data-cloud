#!/bin/bash
# 云端实时数据测试部署脚本

echo "🚀 开始部署实时股票数据测试系统到云端..."

# 检查Git仓库
if [ ! -d ".git" ]; then
    echo "📁 初始化Git仓库..."
    git init
    git add .
    git commit -m "Initial commit: 实时股票数据测试系统"
fi

echo "📋 选择部署平台:"
echo "1. Railway (推荐)"
echo "2. Render"
echo "3. Docker部署"
echo "4. 全部部署"

read -p "请选择 (1-4): " choice

case $choice in
    1)
        echo "🚂 部署到Railway..."
        if command -v railway &> /dev/null; then
            railway login
            railway new
            railway up
        else
            echo "❌ 请先安装Railway CLI: npm install -g @railway/cli"
        fi
        ;;
    2)
        echo "🎨 部署到Render..."
        echo "请访问 https://render.com 并连接您的GitHub仓库"
        ;;
    3)
        echo "🐳 Docker部署..."
        docker build -t realtime-stock-test .
        docker run -p 8001:8001 realtime-stock-test
        ;;
    4)
        echo "🌐 全部部署..."
        echo "请按照README文档进行多平台部署"
        ;;
    *)
        echo "❌ 无效选择"
        ;;
esac

echo "✅ 部署脚本执行完成"
