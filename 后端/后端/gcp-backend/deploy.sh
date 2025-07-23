#!/bin/bash
# Google Cloud VM 部署脚本

echo "🚀 开始部署Trading Backend到Google Cloud VM..."

# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Python和pip
sudo apt install -y python3 python3-pip python3-venv

# 创建应用目录
mkdir -p ~/trading-backend
cd ~/trading-backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install fastapi uvicorn python-multipart python-dotenv pydantic httpx

# 创建systemd服务文件
sudo tee /etc/systemd/system/trading-backend.service > /dev/null <<EOF
[Unit]
Description=Trading Backend API
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/$USER/trading-backend
Environment=PATH=/home/$USER/trading-backend/venv/bin
ExecStart=/home/$USER/trading-backend/venv/bin/python -m uvicorn app:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# 启用并启动服务
sudo systemctl daemon-reload
sudo systemctl enable trading-backend
sudo systemctl start trading-backend

# 检查服务状态
sudo systemctl status trading-backend

echo "✅ 部署完成！"
echo "🌐 API地址: http://$(curl -s ifconfig.me):8000"
echo "📊 健康检查: http://$(curl -s ifconfig.me):8000/api/health"
echo "📱 查看日志: sudo journalctl -u trading-backend -f"
