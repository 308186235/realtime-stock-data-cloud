#!/bin/bash
# 阿里云OneDrive挂载配置脚本
# 账号：308186235@qq.com
# 优化版本 - 适配Ubuntu 22.04

set -e  # 遇到错误立即退出

echo "🚀 开始配置阿里云OneDrive挂载服务..."
echo "📍 服务器信息: $(hostname -I | awk '{print $1}')"
echo "🐧 系统版本: $(lsb_release -d | cut -f2)"

# 1. 更新系统
echo "🔄 更新系统包..."
sudo apt update && sudo apt upgrade -y

# 2. 安装必要依赖
echo "📦 安装系统依赖..."
sudo apt install -y curl wget unzip fuse python3 python3-pip

# 3. 安装rclone
echo "📦 安装rclone..."
if ! command -v rclone &> /dev/null; then
    curl https://rclone.org/install.sh | sudo bash
else
    echo "✅ rclone已安装"
fi

# 4. 检查rclone版本
echo "✅ 检查rclone版本..."
rclone --version

# 5. 创建挂载目录
echo "📁 创建挂载目录..."
sudo mkdir -p /mnt/onedrive
sudo mkdir -p /mnt/onedrive/TradingData
sudo chmod 755 /mnt/onedrive
sudo chown root:root /mnt/onedrive

# 6. 创建rclone配置目录
echo "🔧 准备rclone配置..."
mkdir -p ~/.config/rclone

echo "⚠️  接下来需要手动配置OneDrive授权..."
echo "📧 账号: 308186235@qq.com"
echo "🔑 请准备好一次性密码"
echo ""
echo "配置步骤："
echo "1. 运行: rclone config"
echo "2. 选择 'n' 创建新配置"
echo "3. 名称输入: onedrive_trading"
echo "4. 选择 onedrive 类型"
echo "5. 使用默认设置，按提示完成授权"

# 7. 创建OneDrive挂载服务
echo "🔗 创建OneDrive挂载systemd服务..."
sudo tee /etc/systemd/system/onedrive-mount.service > /dev/null << 'EOF'
[Unit]
Description=OneDrive Mount Service for Trading Data
After=network-online.target
Wants=network-online.target

[Service]
Type=forking
User=root
ExecStartPre=/bin/mkdir -p /mnt/onedrive
ExecStart=/usr/bin/rclone mount onedrive_trading: /mnt/onedrive --vfs-cache-mode writes --allow-other --daemon --log-level INFO --log-file /var/log/rclone-onedrive.log
ExecStop=/bin/fusermount -u /mnt/onedrive
Restart=always
RestartSec=10
TimeoutStartSec=60

[Install]
WantedBy=multi-user.target
EOF

# 7. 创建OneDrive API服务
echo "🐍 创建OneDrive API服务..."
cat > /opt/onedrive_api.py << 'EOF'
#!/usr/bin/env python3
"""
OneDrive文件读取API服务
挂载点：/mnt/onedrive
"""

import json
import os
from datetime import datetime
from flask import Flask, jsonify
from pathlib import Path

app = Flask(__name__)

# 配置
ONEDRIVE_MOUNT = "/mnt/onedrive"
TRADING_DATA_PATH = f"{ONEDRIVE_MOUNT}/TradingData"

@app.route('/')
def status():
    return jsonify({
        "service": "OneDrive云端文件读取服务",
        "status": "running",
        "mount_path": ONEDRIVE_MOUNT,
        "trading_data_path": TRADING_DATA_PATH,
        "onedrive_mount": "ok" if os.path.exists(ONEDRIVE_MOUNT) else "error",
        "timestamp": datetime.now().isoformat(),
        "endpoints": ["/api/positions", "/api/balance", "/api/status"]
    })

@app.route('/api/positions')
def get_positions():
    try:
        positions_file = f"{TRADING_DATA_PATH}/latest_positions.json"
        
        if not os.path.exists(positions_file):
            return jsonify({
                "success": False,
                "error": "持仓文件不存在",
                "file_path": positions_file
            }), 404
        
        with open(positions_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 添加文件元数据
        file_stat = os.stat(positions_file)
        data['_metadata'] = {
            "file_path": positions_file,
            "file_mtime": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
            "file_age_seconds": (datetime.now().timestamp() - file_stat.st_mtime),
            "read_time": datetime.now().isoformat(),
            "source": "onedrive_cloud_mount"
        }
        
        return jsonify({
            "success": True,
            "data": data,
            "source": "onedrive_cloud_mount"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "file_path": f"{TRADING_DATA_PATH}/latest_positions.json"
        }), 500

@app.route('/api/balance')
def get_balance():
    try:
        balance_file = f"{TRADING_DATA_PATH}/latest_balance.json"
        
        if not os.path.exists(balance_file):
            return jsonify({
                "success": False,
                "error": "余额文件不存在",
                "file_path": balance_file
            }), 404
        
        with open(balance_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 添加文件元数据
        file_stat = os.stat(balance_file)
        data['_metadata'] = {
            "file_path": balance_file,
            "file_mtime": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
            "file_age_seconds": (datetime.now().timestamp() - file_stat.st_mtime),
            "read_time": datetime.now().isoformat(),
            "source": "onedrive_cloud_mount"
        }
        
        return jsonify({
            "success": True,
            "data": data,
            "source": "onedrive_cloud_mount"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "file_path": f"{TRADING_DATA_PATH}/latest_balance.json"
        }), 500

@app.route('/api/status')
def api_status():
    trading_files = []
    if os.path.exists(TRADING_DATA_PATH):
        for file in os.listdir(TRADING_DATA_PATH):
            if file.endswith('.json'):
                file_path = f"{TRADING_DATA_PATH}/{file}"
                file_stat = os.stat(file_path)
                trading_files.append({
                    "name": file,
                    "size": file_stat.st_size,
                    "mtime": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                    "age_seconds": (datetime.now().timestamp() - file_stat.st_mtime)
                })
    
    return jsonify({
        "onedrive_mount_status": "ok" if os.path.exists(ONEDRIVE_MOUNT) else "error",
        "trading_data_path": TRADING_DATA_PATH,
        "trading_files": trading_files,
        "mount_point": ONEDRIVE_MOUNT,
        "service_type": "cloud_onedrive_mount"
    })

if __name__ == '__main__':
    print(f"🚀 启动OneDrive云端API服务...")
    print(f"📁 挂载点: {ONEDRIVE_MOUNT}")
    print(f"📊 交易数据路径: {TRADING_DATA_PATH}")
    app.run(host='0.0.0.0', port=8080, debug=False)
EOF

# 8. 安装Python依赖
echo "📦 安装Python依赖..."
sudo apt update
sudo apt install -y python3 python3-pip
pip3 install flask

# 9. 创建API服务
sudo tee /etc/systemd/system/onedrive-api.service > /dev/null << 'EOF'
[Unit]
Description=OneDrive API Service
After=onedrive-mount.service
Requires=onedrive-mount.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt
ExecStart=/usr/bin/python3 /opt/onedrive_api.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 10. 设置权限
sudo chmod +x /opt/onedrive_api.py

echo "✅ 云端OneDrive配置完成！"
echo ""
echo "📋 下一步操作："
echo "1. 运行: rclone config"
echo "2. 配置OneDrive授权 (账号: 308186235@qq.com)"
echo "3. 启动服务: sudo systemctl enable onedrive-mount"
echo "4. 启动服务: sudo systemctl start onedrive-mount"
echo "5. 启动API: sudo systemctl enable onedrive-api"
echo "6. 启动API: sudo systemctl start onedrive-api"
echo "7. 测试: curl http://localhost:8080"
