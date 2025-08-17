#!/bin/bash
# Render启动脚本

echo "🚀 启动交易系统后端服务..."

# 设置环境变量
export PYTHONPATH="/opt/render/project/src"
export PORT="${PORT:-10000}"

# 创建必要目录
mkdir -p data logs

# 启动服务
echo "📡 启动API服务在端口 $PORT"
python backend/app.py
