#!/usr/bin/env python3
"""
股票数据API端点
提供RESTful API接口访问实时股票数据
"""

from flask import Flask, jsonify, request
import requests
import json

app = Flask(__name__)

SUPABASE_URL = 'https://zzukfxwavknskqcepsjb.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6dWtmeHdhdmtuc2txY2Vwc2piIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyOTg1MDYsImV4cCI6MjA2Njg3NDUwNn0.AMGkJSre3QtRBQK_Lh2Iga4dUzSPvuO1G9s6fF2QPaw'

@app.route('/api/stocks', methods=['GET'])
def get_all_stocks():
    """获取所有股票实时数据"""
    try:
        headers = {
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'apikey': SUPABASE_KEY
        }
        
        response = requests.get(f'{SUPABASE_URL}/rest/v1/system_config?key=like.stock_realtime_%', 
                              headers=headers, timeout=10)
        
        if response.status_code == 200:
            configs = response.json()
            stocks = []
            
            for config in configs:
                try:
                    stock_data = json.loads(config['value'])
                    stocks.append(stock_data)
                except:
                    pass
            
            return jsonify({
                'success': True,
                'data': stocks,
                'count': len(stocks)
            })
        else:
            return jsonify({'success': False, 'error': 'Database query failed'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stock/<stock_code>', methods=['GET'])
def get_stock(stock_code):
    """获取单只股票数据"""
    try:
        headers = {
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'apikey': SUPABASE_KEY
        }
        
        response = requests.get(f'{SUPABASE_URL}/rest/v1/system_config?key=eq.stock_realtime_{stock_code}', 
                              headers=headers, timeout=10)
        
        if response.status_code == 200:
            configs = response.json()
            if configs:
                stock_data = json.loads(configs[0]['value'])
                return jsonify({
                    'success': True,
                    'data': stock_data
                })
            else:
                return jsonify({'success': False, 'error': 'Stock not found'}), 404
        else:
            return jsonify({'success': False, 'error': 'Database query failed'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def get_system_status():
    """获取系统状态"""
    try:
        headers = {
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'apikey': SUPABASE_KEY
        }
        
        response = requests.get(f'{SUPABASE_URL}/rest/v1/system_config?key=eq.system_sync_status', 
                              headers=headers, timeout=10)
        
        if response.status_code == 200:
            configs = response.json()
            if configs:
                status_data = json.loads(configs[0]['value'])
                return jsonify({
                    'success': True,
                    'data': status_data
                })
            else:
                return jsonify({'success': False, 'error': 'Status not found'}), 404
        else:
            return jsonify({'success': False, 'error': 'Database query failed'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
