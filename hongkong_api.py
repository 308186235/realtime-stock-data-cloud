#!/usr/bin/env python3
"""
香港云服务器API - 提供真实股票数据
端口: 5000
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import json
import time
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Supabase配置
SUPABASE_URL = 'https://zzukfxwavknskqcepsjb.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6dWtmeHdhdmtuc2txY2Vwc2piIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjE3MjQwNzEsImV4cCI6MjAzNzMwMDA3MX0.VwGgVJKH8rh_f6lNlhkdBqfJQgFJyOJXzJvJQgFJyOI'

def is_trading_time():
    """检查是否在交易时间"""
    now = datetime.now()
    hour = now.hour
    minute = now.minute
    day = now.weekday()  # 0=周一, 6=周日
    
    # 周末不交易
    if day >= 5:  # 周六、周日
        return False
    
    # 交易时间：9:30-11:30, 13:00-15:00
    current_time = hour * 60 + minute
    morning_start = 9 * 60 + 30
    morning_end = 11 * 60 + 30
    afternoon_start = 13 * 60
    afternoon_end = 15 * 60
    
    return (morning_start <= current_time <= morning_end) or \
           (afternoon_start <= current_time <= afternoon_end)

def get_real_stock_data():
    """从Supabase获取真实股票数据"""
    try:
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json'
        }
        
        # 获取最新的真实股票数据
        url = f'{SUPABASE_URL}/rest/v1/stock_data'
        params = {
            'select': '*',
            'order': 'created_at.desc',
            'limit': '20'
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # 过滤真实数据
            real_stocks = []
            for item in data:
                if item.get('raw_data', {}).get('source') == 'realtime_update':
                    stock = {
                        'code': item['symbol'],
                        'name': item.get('raw_data', {}).get('name', item['symbol']),
                        'price': float(item['price']),
                        'change': float(item['price']) - float(item.get('raw_data', {}).get('prev_close', item['price'])),
                        'change_percent': float(item.get('change_percent', 0)),
                        'volume': item.get('volume', 0),
                        'timestamp': item['timestamp']
                    }
                    real_stocks.append(stock)
            
            return real_stocks[:10]  # 最多返回10只股票
        else:
            logger.error(f'Supabase请求失败: {response.status_code}')
            return []
            
    except Exception as e:
        logger.error(f'获取股票数据失败: {e}')
        return []

@app.route('/')
def root():
    """根路径"""
    return jsonify({
        'service': '香港云服务器API',
        'version': '1.0.0',
        'status': 'running',
        'server_location': 'Hong Kong',
        'timestamp': datetime.now().isoformat(),
        'endpoints': [
            '/api/health',
            '/api/realtime',
            '/api/virtual-account/accounts',
            '/api/agent-analysis/status'
        ]
    })

@app.route('/api/health')
def health():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'service': '香港云服务器API',
        'server_location': 'Hong Kong',
        'timestamp': datetime.now().isoformat(),
        'trading_time': is_trading_time()
    })

@app.route('/api/realtime')
def realtime_data():
    """实时股票数据"""
    try:
        if not is_trading_time():
            return jsonify({
                'success': True,
                'data': {
                    'stocks': [],
                    'total_count': 0,
                    'message': '非交易时间',
                    'timestamp': datetime.now().isoformat()
                }
            })
        
        # 获取真实数据
        stocks = get_real_stock_data()
        
        return jsonify({
            'success': True,
            'data': {
                'stocks': stocks,
                'total_count': len(stocks),
                'data_source': 'supabase_real_data',
                'server_location': 'Hong Kong',
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f'实时数据API错误: {e}')
        return jsonify({
            'success': False,
            'data': {'stocks': [], 'total_count': 0},
            'error': str(e)
        }), 500

@app.route('/api/virtual-account/accounts')
def virtual_accounts():
    """虚拟账户数据"""
    return jsonify({
        'success': True,
        'data': [{
            'id': 'hk-virtual-account',
            'account_name': '香港云端虚拟账户',
            'broker_type': 'virtual',
            'total_assets': 100000.00,
            'available_cash': 50000.00,
            'market_value': 50000.00,
            'profit_loss': 0.00,
            'profit_loss_ratio': 0.00,
            'last_sync_time': datetime.now().isoformat(),
            'data_source': 'hongkong_server'
        }]
    })

@app.route('/api/agent-analysis/status')
def agent_status():
    """Agent状态"""
    return jsonify({
        'success': True,
        'data': {
            'status': 'running',
            'active_strategies': 3,
            'cpu_usage': '15.6',
            'server_location': 'Hong Kong',
            'last_update': datetime.now().isoformat()
        }
    })

if __name__ == '__main__':
    print("🌐 启动香港云服务器API...")
    print("📊 API端点:")
    print("  GET  /api/health           - 健康检查")
    print("  GET  /api/realtime         - 实时股票数据")
    print("  GET  /api/virtual-account/accounts - 虚拟账户")
    print("  GET  /api/agent-analysis/status - Agent状态")
    print("🌐 服务地址: http://0.0.0.0:5000")
    print("🏢 服务器位置: 香港云服务器")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
