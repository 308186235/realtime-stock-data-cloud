#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web配置管理器 - 提供Web界面管理北交所开关等配置
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import sys
import os
from datetime import datetime
import json

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from supabase_agent_simple import SupabaseClient, TRADING_CONFIG

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

class WebConfigManager:
    def __init__(self):
        self.supabase = SupabaseClient()
    
    def get_current_config(self):
        """获取当前配置"""
        return {
            'enable_beijing_exchange': TRADING_CONFIG['enable_beijing_exchange'],
            'trading_start_time': TRADING_CONFIG['trading_start_time'],
            'trading_end_time': TRADING_CONFIG['trading_end_time'],
            'analysis_interval': TRADING_CONFIG['analysis_interval'],
            'reconnect_interval': TRADING_CONFIG['reconnect_interval'],
            'max_reconnect_attempts': TRADING_CONFIG['max_reconnect_attempts']
        }
    
    def update_config(self, key, value):
        """更新配置"""
        try:
            if key == 'enable_beijing_exchange':
                TRADING_CONFIG[key] = value.lower() == 'true'
            elif key in ['analysis_interval', 'reconnect_interval', 'max_reconnect_attempts']:
                TRADING_CONFIG[key] = int(value)
            else:
                TRADING_CONFIG[key] = value
            
            return True
        except Exception as e:
            print(f"配置更新失败: {e}")
            return False
    
    def get_system_status(self):
        """获取系统状态"""
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        is_trading_day = now.weekday() < 5
        
        start_time = TRADING_CONFIG['trading_start_time']
        end_time = TRADING_CONFIG['trading_end_time']
        is_trading_time = is_trading_day and start_time <= current_time <= end_time
        
        return {
            'current_time': now.strftime('%Y-%m-%d %H:%M:%S'),
            'is_trading_day': is_trading_day,
            'is_trading_time': is_trading_time,
            'trading_window': f"{start_time} - {end_time}",
            'beijing_exchange_enabled': TRADING_CONFIG['enable_beijing_exchange']
        }
    
    def get_recent_decisions(self, limit=10):
        """获取最近决策"""
        try:
            decisions = self.supabase.select('agent_decisions', limit=limit)
            return decisions if decisions else []
        except Exception as e:
            print(f"获取决策失败: {e}")
            return []

# 创建配置管理器实例
config_manager = WebConfigManager()

@app.route('/')
def index():
    """主页"""
    config = config_manager.get_current_config()
    status = config_manager.get_system_status()
    decisions = config_manager.get_recent_decisions(5)
    
    return render_template('config_dashboard.html', 
                         config=config, 
                         status=status, 
                         decisions=decisions)

@app.route('/api/config', methods=['GET'])
def get_config():
    """获取配置API"""
    return jsonify(config_manager.get_current_config())

@app.route('/api/config', methods=['POST'])
def update_config():
    """更新配置API"""
    data = request.get_json()
    
    success = True
    for key, value in data.items():
        if not config_manager.update_config(key, value):
            success = False
    
    return jsonify({
        'success': success,
        'config': config_manager.get_current_config()
    })

@app.route('/api/toggle_beijing', methods=['POST'])
def toggle_beijing():
    """切换北交所权限API"""
    current_status = TRADING_CONFIG['enable_beijing_exchange']
    new_status = not current_status
    
    success = config_manager.update_config('enable_beijing_exchange', str(new_status).lower())
    
    return jsonify({
        'success': success,
        'enabled': TRADING_CONFIG['enable_beijing_exchange'],
        'message': f"北交所权限已{'开启' if TRADING_CONFIG['enable_beijing_exchange'] else '关闭'}"
    })

@app.route('/api/status')
def get_status():
    """获取系统状态API"""
    return jsonify(config_manager.get_system_status())

@app.route('/api/decisions')
def get_decisions():
    """获取决策API"""
    limit = request.args.get('limit', 10, type=int)
    decisions = config_manager.get_recent_decisions(limit)
    return jsonify(decisions)

if __name__ == '__main__':
    # 创建模板目录
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    if not os.path.exists(template_dir):
        os.makedirs(template_dir)
    
    print("🌐 启动Web配置管理器...")
    print("📱 访问地址: http://localhost:5000")
    print("🔧 功能: 北交所开关,交易配置管理")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
