#!/bin/bash
# Oracle Cloud OneDrive自动化部署脚本
# 账号：308186235@qq.com

set -e

echo "🚀 Oracle Cloud OneDrive自动化部署开始..."
echo "📧 OneDrive账号: 308186235@qq.com"
echo "⏰ 开始时间: $(date)"

# 更新系统
echo "📦 更新系统包..."
sudo apt update && sudo apt upgrade -y

# 安装基础依赖
echo "🔧 安装基础依赖..."
sudo apt install -y curl wget unzip python3 python3-pip fuse

# 安装rclone
echo "📥 安装rclone..."
curl https://rclone.org/install.sh | sudo bash

# 验证rclone安装
echo "✅ 验证rclone安装..."
rclone --version

# 创建目录结构
echo "📁 创建目录结构..."
sudo mkdir -p /mnt/onedrive
sudo mkdir -p /mnt/onedrive/TradingData
sudo mkdir -p /opt/onedrive-service
sudo mkdir -p /var/log/onedrive
sudo chmod 755 /mnt/onedrive
sudo chmod 755 /opt/onedrive-service

# 创建rclone配置目录
echo "🔧 创建rclone配置目录..."
mkdir -p ~/.config/rclone

# 创建OneDrive API服务
echo "🐍 创建OneDrive API服务..."
cat > /opt/onedrive-service/api_server.py << 'EOF'
#!/usr/bin/env python3
"""
Oracle Cloud OneDrive API服务
账号: 308186235@qq.com
挂载点: /mnt/onedrive
"""

import json
import os
import sys
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/onedrive/api.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

app = Flask(__name__)
CORS(app)  # 允许跨域访问

# 配置
ONEDRIVE_MOUNT = "/mnt/onedrive"
TRADING_DATA_PATH = f"{ONEDRIVE_MOUNT}/TradingData"

@app.route('/')
def status():
    """服务状态"""
    mount_exists = os.path.exists(ONEDRIVE_MOUNT)
    trading_exists = os.path.exists(TRADING_DATA_PATH)
    
    return jsonify({
        "service": "Oracle Cloud OneDrive API服务",
        "status": "running",
        "account": "308186235@qq.com",
        "mount_path": ONEDRIVE_MOUNT,
        "trading_data_path": TRADING_DATA_PATH,
        "onedrive_mount": "ok" if mount_exists else "error",
        "trading_folder": "ok" if trading_exists else "error",
        "timestamp": datetime.now().isoformat(),
        "server_info": {
            "platform": "Oracle Cloud",
            "service_type": "rclone_mount",
            "endpoints": ["/", "/api/positions", "/api/balance", "/api/status", "/api/files"]
        }
    })

@app.route('/api/positions')
def get_positions():
    """获取持仓数据"""
    try:
        positions_file = f"{TRADING_DATA_PATH}/latest_positions.json"
        
        if not os.path.exists(positions_file):
            logging.warning(f"持仓文件不存在: {positions_file}")
            return jsonify({
                "success": False,
                "error": "持仓文件不存在",
                "file_path": positions_file,
                "trading_folder_exists": os.path.exists(TRADING_DATA_PATH),
                "mount_exists": os.path.exists(ONEDRIVE_MOUNT)
            }), 404
        
        with open(positions_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 添加文件元数据
        file_stat = os.stat(positions_file)
        data['_metadata'] = {
            "file_path": positions_file,
            "file_mtime": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
            "file_age_seconds": (datetime.now().timestamp() - file_stat.st_mtime),
            "file_size": file_stat.st_size,
            "read_time": datetime.now().isoformat(),
            "source": "oracle_cloud_onedrive_mount",
            "server": "Oracle Cloud Free Tier"
        }
        
        logging.info(f"成功读取持仓数据: {len(data.get('positions', []))}条记录")
        
        return jsonify({
            "success": True,
            "data": data,
            "source": "oracle_cloud_onedrive_mount"
        })
        
    except Exception as e:
        logging.error(f"读取持仓数据失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "file_path": f"{TRADING_DATA_PATH}/latest_positions.json"
        }), 500

@app.route('/api/balance')
def get_balance():
    """获取余额数据"""
    try:
        balance_file = f"{TRADING_DATA_PATH}/latest_balance.json"
        
        if not os.path.exists(balance_file):
            logging.warning(f"余额文件不存在: {balance_file}")
            return jsonify({
                "success": False,
                "error": "余额文件不存在",
                "file_path": balance_file,
                "trading_folder_exists": os.path.exists(TRADING_DATA_PATH),
                "mount_exists": os.path.exists(ONEDRIVE_MOUNT)
            }), 404
        
        with open(balance_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 添加文件元数据
        file_stat = os.stat(balance_file)
        data['_metadata'] = {
            "file_path": balance_file,
            "file_mtime": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
            "file_age_seconds": (datetime.now().timestamp() - file_stat.st_mtime),
            "file_size": file_stat.st_size,
            "read_time": datetime.now().isoformat(),
            "source": "oracle_cloud_onedrive_mount",
            "server": "Oracle Cloud Free Tier"
        }
        
        logging.info(f"成功读取余额数据")
        
        return jsonify({
            "success": True,
            "data": data,
            "source": "oracle_cloud_onedrive_mount"
        })
        
    except Exception as e:
        logging.error(f"读取余额数据失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "file_path": f"{TRADING_DATA_PATH}/latest_balance.json"
        }), 500

@app.route('/api/files')
def list_files():
    """列出所有交易文件"""
    try:
        if not os.path.exists(TRADING_DATA_PATH):
            return jsonify({
                "success": False,
                "error": "TradingData文件夹不存在",
                "path": TRADING_DATA_PATH
            }), 404
        
        files = []
        for filename in os.listdir(TRADING_DATA_PATH):
            file_path = os.path.join(TRADING_DATA_PATH, filename)
            if os.path.isfile(file_path):
                file_stat = os.stat(file_path)
                files.append({
                    "name": filename,
                    "size": file_stat.st_size,
                    "mtime": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                    "age_seconds": (datetime.now().timestamp() - file_stat.st_mtime),
                    "type": "json" if filename.endswith('.json') else "other"
                })
        
        return jsonify({
            "success": True,
            "trading_data_path": TRADING_DATA_PATH,
            "files": sorted(files, key=lambda x: x['mtime'], reverse=True),
            "total_files": len(files)
        })
        
    except Exception as e:
        logging.error(f"列出文件失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/status')
def api_status():
    """详细状态检查"""
    try:
        # 检查挂载状态
        mount_status = os.path.exists(ONEDRIVE_MOUNT)
        trading_status = os.path.exists(TRADING_DATA_PATH)
        
        # 检查文件
        positions_exists = os.path.exists(f"{TRADING_DATA_PATH}/latest_positions.json")
        balance_exists = os.path.exists(f"{TRADING_DATA_PATH}/latest_balance.json")
        
        # 统计文件
        file_count = 0
        if trading_status:
            file_count = len([f for f in os.listdir(TRADING_DATA_PATH) if os.path.isfile(os.path.join(TRADING_DATA_PATH, f))])
        
        return jsonify({
            "oracle_cloud_status": "running",
            "onedrive_mount_status": "ok" if mount_status else "error",
            "trading_data_status": "ok" if trading_status else "error",
            "files_status": {
                "positions_file": "ok" if positions_exists else "missing",
                "balance_file": "ok" if balance_exists else "missing",
                "total_files": file_count
            },
            "paths": {
                "mount_point": ONEDRIVE_MOUNT,
                "trading_data": TRADING_DATA_PATH
            },
            "service_info": {
                "account": "308186235@qq.com",
                "server": "Oracle Cloud Free Tier",
                "service_type": "rclone_onedrive_mount"
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logging.error(f"状态检查失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    logging.info("🚀 启动Oracle Cloud OneDrive API服务...")
    logging.info(f"📁 OneDrive挂载点: {ONEDRIVE_MOUNT}")
    logging.info(f"📊 交易数据路径: {TRADING_DATA_PATH}")
    logging.info(f"📧 OneDrive账号: 308186235@qq.com")
    
    app.run(host='0.0.0.0', port=8080, debug=False)
EOF

# 安装Python依赖
echo "📦 安装Python依赖..."
sudo pip3 install flask flask-cors

# 创建systemd服务文件
echo "🔗 创建OneDrive挂载服务..."
sudo tee /etc/systemd/system/onedrive-mount.service > /dev/null << 'EOF'
[Unit]
Description=OneDrive Mount Service for Oracle Cloud
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/bin/rclone mount onedrive_trading: /mnt/onedrive --vfs-cache-mode writes --allow-other --daemon --log-level INFO --log-file /var/log/onedrive/mount.log
ExecStop=/bin/fusermount -u /mnt/onedrive
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "🔗 创建OneDrive API服务..."
sudo tee /etc/systemd/system/onedrive-api.service > /dev/null << 'EOF'
[Unit]
Description=OneDrive API Service for Oracle Cloud
After=onedrive-mount.service
Wants=onedrive-mount.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/onedrive-service
ExecStart=/usr/bin/python3 /opt/onedrive-service/api_server.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# 设置权限
sudo chmod +x /opt/onedrive-service/api_server.py
sudo chown -R root:root /opt/onedrive-service
sudo chown -R root:root /var/log/onedrive

# 重新加载systemd
sudo systemctl daemon-reload

echo "✅ Oracle Cloud OneDrive部署完成！"
echo ""
echo "📋 下一步操作："
echo "1. 配置OneDrive授权:"
echo "   rclone config"
echo "   - 选择 'n' 新建配置"
echo "   - 名称: onedrive_trading"
echo "   - 类型: onedrive"
echo "   - 账号: 308186235@qq.com"
echo ""
echo "2. 启动服务:"
echo "   sudo systemctl enable onedrive-mount"
echo "   sudo systemctl start onedrive-mount"
echo "   sudo systemctl enable onedrive-api"
echo "   sudo systemctl start onedrive-api"
echo ""
echo "3. 检查状态:"
echo "   sudo systemctl status onedrive-mount"
echo "   sudo systemctl status onedrive-api"
echo "   curl http://localhost:8080"
echo ""
echo "4. 查看日志:"
echo "   sudo journalctl -u onedrive-mount -f"
echo "   sudo journalctl -u onedrive-api -f"
echo ""
echo "🌐 服务器IP: $(curl -s ifconfig.me)"
echo "📧 OneDrive账号: 308186235@qq.com"
