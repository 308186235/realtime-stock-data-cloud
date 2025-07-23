#!/usr/bin/env python3
"""
OneDrive文件读取服务器
读取挂载的OneDrive文件,提供HTTP API给Cloudflare Worker访问
"""

import os
import json
import time
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # 允许跨域访问

# OneDrive挂载路径配置
ONEDRIVE_CONFIG = {
    'mount_path': 'C:/mnt/onedrive/TradingData',
    'positions_file': 'latest_positions.json',
    'balance_file': 'latest_balance.json'
}

def check_onedrive_mount():
    """检查OneDrive挂载状态"""
    mount_path = ONEDRIVE_CONFIG['mount_path']
    
    if not os.path.exists(mount_path):
        logger.error(f"OneDrive挂载路径不存在: {mount_path}")
        return False
    
    try:
        # 尝试列出目录内容
        files = os.listdir(mount_path)
        logger.info(f"OneDrive挂载正常,包含 {len(files)} 个文件")
        return True
    except Exception as e:
        logger.error(f"OneDrive挂载异常: {e}")
        return False

def read_onedrive_file(file_type):
    """从OneDrive挂载目录读取文件"""
    try:
        mount_path = ONEDRIVE_CONFIG['mount_path']
        
        if file_type == 'positions':
            file_name = ONEDRIVE_CONFIG['positions_file']
        elif file_type == 'balance':
            file_name = ONEDRIVE_CONFIG['balance_file']
        else:
            raise ValueError(f"未知的文件类型: {file_type}")
        
        file_path = os.path.join(mount_path, file_name)
        
        if not os.path.exists(file_path):
            logger.warning(f"文件不存在: {file_path}")
            return None
        
        # 检查文件修改时间
        file_mtime = os.path.getmtime(file_path)
        file_age = time.time() - file_mtime
        
        logger.info(f"读取文件: {file_path}, 文件年龄: {file_age:.1f}秒")
        
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 添加元数据
        data['_metadata'] = {
            'file_path': file_path,
            'file_mtime': datetime.fromtimestamp(file_mtime).isoformat(),
            'file_age_seconds': file_age,
            'read_time': datetime.now().isoformat(),
            'source': 'onedrive_mount'
        }
        
        logger.info(f"成功读取 {file_type} 数据")
        return data
        
    except Exception as e:
        logger.error(f"读取 {file_type} 文件失败: {e}")
        return None

@app.route('/')
def index():
    """服务状态"""
    mount_status = check_onedrive_mount()
    
    return jsonify({
        'service': 'OneDrive文件读取服务',
        'status': 'running',
        'onedrive_mount': 'ok' if mount_status else 'error',
        'mount_path': ONEDRIVE_CONFIG['mount_path'],
        'timestamp': datetime.now().isoformat(),
        'endpoints': [
            '/api/positions',
            '/api/balance',
            '/api/status'
        ]
    })

@app.route('/api/status')
def api_status():
    """详细状态检查"""
    mount_path = ONEDRIVE_CONFIG['mount_path']
    mount_status = check_onedrive_mount()
    
    file_status = {}
    if mount_status:
        for file_type in ['positions', 'balance']:
            file_name = ONEDRIVE_CONFIG[f'{file_type}_file']
            file_path = os.path.join(mount_path, file_name)
            
            if os.path.exists(file_path):
                file_mtime = os.path.getmtime(file_path)
                file_status[file_type] = {
                    'exists': True,
                    'path': file_path,
                    'mtime': datetime.fromtimestamp(file_mtime).isoformat(),
                    'age_seconds': time.time() - file_mtime,
                    'size_bytes': os.path.getsize(file_path)
                }
            else:
                file_status[file_type] = {
                    'exists': False,
                    'path': file_path
                }
    
    return jsonify({
        'onedrive_mount': mount_status,
        'mount_path': mount_path,
        'files': file_status,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/positions')
def api_positions():
    """获取持仓数据"""
    data = read_onedrive_file('positions')
    
    if data:
        return jsonify({
            'success': True,
            'data': data,
            'source': 'onedrive_mount'
        })
    else:
        return jsonify({
            'success': False,
            'error': '无法读取持仓数据',
            'source': 'onedrive_mount'
        }), 500

@app.route('/api/balance')
def api_balance():
    """获取余额数据"""
    data = read_onedrive_file('balance')
    
    if data:
        return jsonify({
            'success': True,
            'data': data,
            'source': 'onedrive_mount'
        })
    else:
        return jsonify({
            'success': False,
            'error': '无法读取余额数据',
            'source': 'onedrive_mount'
        }), 500

@app.route('/api/all')
def api_all():
    """获取所有数据"""
    positions_data = read_onedrive_file('positions')
    balance_data = read_onedrive_file('balance')
    
    return jsonify({
        'success': True,
        'data': {
            'positions': positions_data,
            'balance': balance_data
        },
        'source': 'onedrive_mount',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 启动OneDrive文件读取服务...")
    print(f"📁 OneDrive挂载路径: {ONEDRIVE_CONFIG['mount_path']}")
    
    # 检查挂载状态
    if check_onedrive_mount():
        print("✅ OneDrive挂载检查通过")
    else:
        print("❌ OneDrive挂载检查失败")
        print("请确保OneDrive已正确挂载到指定路径")
    
    print("🌐 服务将在 http://localhost:8080 启动")
    print("📋 API端点:")
    print("   - GET /api/positions  - 获取持仓数据")
    print("   - GET /api/balance    - 获取余额数据")
    print("   - GET /api/all        - 获取所有数据")
    print("   - GET /api/status     - 检查状态")
    
    app.run(host='0.0.0.0', port=8080, debug=True)
