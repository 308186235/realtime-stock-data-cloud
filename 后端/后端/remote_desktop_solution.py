#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
远程桌面解决方案
在云端Windows服务器上运行交易软件
"""

import subprocess
import time
import os
from pathlib import Path

class RemoteDesktopDeployer:
    """远程桌面部署器"""
    
    def __init__(self):
        self.cloud_providers = {
            "aws": {
                "name": "Amazon EC2 Windows",
                "cost": "$20-50/月",
                "setup_complexity": "中等",
                "performance": "高"
            },
            "azure": {
                "name": "Azure Windows VM",
                "cost": "$25-60/月", 
                "setup_complexity": "中等",
                "performance": "高"
            },
            "vultr": {
                "name": "Vultr Windows VPS",
                "cost": "$10-30/月",
                "setup_complexity": "简单",
                "performance": "中等"
            },
            "linode": {
                "name": "Linode Windows",
                "cost": "$15-40/月",
                "setup_complexity": "简单", 
                "performance": "中等"
            }
        }
    
    def show_options(self):
        """显示云服务器选项"""
        print("🖥️ 云端Windows服务器选项:")
        print("=" * 60)
        
        for key, provider in self.cloud_providers.items():
            print(f"\n{key.upper()}:")
            print(f"  服务商: {provider['name']}")
            print(f"  费用: {provider['cost']}")
            print(f"  设置难度: {provider['setup_complexity']}")
            print(f"  性能: {provider['performance']}")
    
    def create_deployment_script(self):
        """创建部署脚本"""
        
        # Windows服务器部署脚本
        windows_setup = """
@echo off
echo 🖥️ Windows云服务器交易环境设置
echo =====================================

echo 1. 安装Python...
curl -o python-installer.exe https://www.python.org/ftp/python/3.9.13/python-3.9.13-amd64.exe
python-installer.exe /quiet InstallAllUsers=1 PrependPath=1

echo 2. 安装Git...
curl -o git-installer.exe https://github.com/git-for-windows/git/releases/download/v2.42.0.windows.2/Git-2.42.0.2-64-bit.exe
git-installer.exe /SILENT

echo 3. 克隆项目...
git clone https://github.com/308186235/Bei-fen.git trading-system
cd trading-system

echo 4. 安装依赖...
pip install -r backend/requirements.txt
pip install pywin32 win32gui win32api win32con

echo 5. 配置自动启动...
schtasks /create /tn "TradingSystem" /tr "python %cd%\\backend\\app.py" /sc onstart /ru SYSTEM

echo 6. 启动服务...
python backend/app.py

echo ✅ 部署完成!
echo 🌐 服务地址: http://localhost:8000
echo 📱 可通过远程桌面访问交易软件

pause
"""
        
        with open("windows_server_setup.bat", "w", encoding="utf-8") as f:
            f.write(windows_setup)
        
        # Linux服务器部署脚本(用于API服务)
        linux_setup = """#!/bin/bash
echo "🐧 Linux服务器API部署"
echo "===================="

# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Python和依赖
sudo apt install -y python3 python3-pip git nginx

# 克隆项目
git clone https://github.com/308186235/Bei-fen.git trading-system
cd trading-system

# 安装Python依赖
pip3 install -r backend/requirements.txt

# 配置Nginx
sudo tee /etc/nginx/sites-available/trading-api << EOF
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# 启用站点
sudo ln -s /etc/nginx/sites-available/trading-api /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# 配置系统服务
sudo tee /etc/systemd/system/trading-api.service << EOF
[Unit]
Description=Trading API Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/trading-system
Environment=PATH=/usr/bin:/usr/local/bin
ExecStart=/usr/bin/python3 backend/app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 启动服务
sudo systemctl daemon-reload
sudo systemctl enable trading-api
sudo systemctl start trading-api

echo "✅ Linux API服务部署完成!"
echo "🌐 API地址: http://$(curl -s ifconfig.me):80"
"""
        
        with open("linux_server_setup.sh", "w") as f:
            f.write(linux_setup)
        
        os.chmod("linux_server_setup.sh", 0o755)
        
        print("✅ 部署脚本已创建:")
        print("  - windows_server_setup.bat (Windows服务器)")
        print("  - linux_server_setup.sh (Linux API服务器)")

def main():
    deployer = RemoteDesktopDeployer()
    
    print("🖥️ 远程桌面解决方案")
    print("=" * 50)
    print("此方案将交易软件运行在云端Windows服务器上")
    print("您可以通过远程桌面连接操作交易软件")
    print()
    
    deployer.show_options()
    print()
    
    choice = input("是否创建部署脚本? (y/n): ").lower()
    if choice == 'y':
        deployer.create_deployment_script()
        
        print("\n📋 部署步骤:")
        print("1. 选择云服务商创建Windows服务器")
        print("2. 通过远程桌面连接到服务器")
        print("3. 运行 windows_server_setup.bat")
        print("4. 安装您的交易软件")
        print("5. 配置交易软件自动登录")
        print("6. 测试交易功能")
        
        print("\n💡 优点:")
        print("- 交易软件在云端24/7运行")
        print("- 不依赖本地电脑")
        print("- 网络稳定,延迟低")
        
        print("\n⚠️ 注意:")
        print("- 需要付费云服务器")
        print("- 需要配置交易软件自动登录")
        print("- 需要确保服务器安全")

if __name__ == "__main__":
    main()
