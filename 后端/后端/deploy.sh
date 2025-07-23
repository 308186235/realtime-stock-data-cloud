#!/bin/bash
# 项目自动部署脚本

echo "🚀 开始部署AI股票交易系统..."

# 检查Git状态
if [ -n "$(git status --porcelain)" ]; then
    echo "📝 提交当前更改..."
    git add .
    git commit -m "配置修复部署: $(date '+%Y-%m-%d %H:%M:%S')"
fi

# 推送到GitHub
echo "📤 推送到GitHub..."
git push origin main

echo "✅ 部署完成！"
echo "🌐 访问地址: https://app.aigupiao.me"
