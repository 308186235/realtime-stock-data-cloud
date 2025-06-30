#!/bin/bash
# AI股票交易系统 - 子域名部署脚本

echo "🚀 开始部署子域名架构..."

# 检查Git状态
if [ -n "$(git status --porcelain)" ]; then
    echo "📝 提交当前更改..."
    git add .
    git commit -m "子域名架构部署: $(date '+%Y-%m-%d %H:%M:%S')"
fi

# 推送到GitHub
echo "📤 推送到GitHub..."
git push origin main

echo "✅ 部署完成！"
echo "📋 下一步:"
echo "1. 在Cloudflare Pages中为每个子域名创建项目"
echo "2. 配置DNS记录"
echo "3. 设置自定义域名"

echo ""
echo "🌐 子域名列表:"
echo "• app.aigupiao.me - 主前端应用"
echo "• api.aigupiao.me - 后端API服务"
echo "• mobile.aigupiao.me - 移动端应用"
echo "• admin.aigupiao.me - 管理后台"
echo "• ws.aigupiao.me - WebSocket服务"
echo "• docs.aigupiao.me - 文档中心"
