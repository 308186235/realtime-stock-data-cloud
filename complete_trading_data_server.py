#!/usr/bin/env python3
"""
完整的本地交易数据服务器
提供云端Agent所需的所有数据端点
"""

from flask import Flask, jsonify, request, send_file
import json
import csv
import io
import time
from datetime import datetime, timedelta
import random
import threading
import os

app = Flask(__name__)

class TradingDataServer:
    def __init__(self):
        self.start_time = datetime.now()
        self.trade_counter = 1000
        self.order_counter = 2000
        
        # 模拟账户数据
        self.account_data = {
            'balance': {
                'total_assets': 1000000.00,
                'available_cash': 250000.00,
                'market_value': 750000.00,
                'frozen_cash': 0.00,
                'profit_loss': 25000.00,
                'profit_loss_ratio': 2.5
            },
            'positions': [
                {
                    'stock_code': '000001',
                    'stock_name': '平安银行',
                    'quantity': 1000,
                    'available_quantity': 1000,
                    'avg_cost': 12.50,
                    'current_price': 13.20,
                    'market_value': 13200.00,
                    'profit_loss': 700.00,
                    'profit_loss_ratio': 5.6
                },
                {
                    'stock_code': '000002',
                    'stock_name': '万科A',
                    'quantity': 2000,
                    'available_quantity': 2000,
                    'avg_cost': 18.30,
                    'current_price': 19.80,
                    'market_value': 39600.00,
                    'profit_loss': 3000.00,
                    'profit_loss_ratio': 8.2
                }
            ],
            'trades': [],
            'orders': []
        }
        
        # 生成历史交易记录
        self.generate_historical_data()
        
        # 启动数据更新线程
        self.start_data_updater()
    
    def generate_historical_data(self):
        """生成历史交易数据"""
        # 生成最近7天的交易记录
        for i in range(20):
            trade_time = datetime.now() - timedelta(days=random.randint(0, 7), 
                                                   hours=random.randint(9, 15),
                                                   minutes=random.randint(0, 59))
            
            stock_codes = ['000001', '000002', '600036', '600519', '000858']
            stock_names = ['平安银行', '万科A', '招商银行', '贵州茅台', '五粮液']
            
            idx = random.randint(0, 4)
            action = random.choice(['buy', 'sell'])
            quantity = random.randint(100, 1000)
            price = round(random.uniform(10.0, 50.0), 2)
            
            trade = {
                'trade_id': f'T{self.trade_counter + i}',
                'stock_code': stock_codes[idx],
                'stock_name': stock_names[idx],
                'action': action,
                'quantity': quantity,
                'price': price,
                'amount': round(quantity * price, 2),
                'commission': round(quantity * price * 0.0003, 2),
                'trade_time': trade_time.strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'completed'
            }
            
            self.account_data['trades'].append(trade)
        
        # 生成当前委托订单
        for i in range(5):
            order_time = datetime.now() - timedelta(minutes=random.randint(5, 120))
            
            stock_codes = ['000001', '000002', '600036']
            stock_names = ['平安银行', '万科A', '招商银行']
            
            idx = random.randint(0, 2)
            action = random.choice(['buy', 'sell'])
            quantity = random.randint(100, 500)
            price = round(random.uniform(12.0, 20.0), 2)
            
            order = {
                'order_id': f'O{self.order_counter + i}',
                'stock_code': stock_codes[idx],
                'stock_name': stock_names[idx],
                'action': action,
                'quantity': quantity,
                'price': price,
                'amount': round(quantity * price, 2),
                'order_time': order_time.strftime('%Y-%m-%d %H:%M:%S'),
                'status': random.choice(['pending', 'partial', 'cancelled'])
            }
            
            self.account_data['orders'].append(order)
    
    def start_data_updater(self):
        """启动数据更新线程"""
        def update_data():
            while True:
                # 更新股票价格
                for position in self.account_data['positions']:
                    # 模拟价格波动 ±2%
                    change_ratio = random.uniform(-0.02, 0.02)
                    position['current_price'] = round(
                        position['current_price'] * (1 + change_ratio), 2
                    )
                    position['market_value'] = round(
                        position['quantity'] * position['current_price'], 2
                    )
                    position['profit_loss'] = round(
                        position['market_value'] - position['quantity'] * position['avg_cost'], 2
                    )
                    position['profit_loss_ratio'] = round(
                        (position['profit_loss'] / (position['quantity'] * position['avg_cost'])) * 100, 2
                    )
                
                # 更新总资产
                total_market_value = sum(p['market_value'] for p in self.account_data['positions'])
                self.account_data['balance']['market_value'] = total_market_value
                self.account_data['balance']['total_assets'] = (
                    total_market_value + self.account_data['balance']['available_cash']
                )
                
                time.sleep(30)  # 每30秒更新一次
        
        update_thread = threading.Thread(target=update_data, daemon=True)
        update_thread.start()

# 创建全局数据服务器实例
trading_server = TradingDataServer()

@app.route('/')
def root():
    """根路径信息"""
    return jsonify({
        'service': '完整本地交易数据服务器',
        'version': '2.0.0',
        'status': 'running',
        'start_time': trading_server.start_time.strftime('%Y-%m-%d %H:%M:%S'),
        'uptime_seconds': int((datetime.now() - trading_server.start_time).total_seconds()),
        'endpoints': [
            '/health', '/status', '/balance', '/positions', 
            '/trades', '/orders', '/history', '/export/*'
        ],
        'features': [
            '实时数据更新', '完整交易记录', '多格式导出', '云端Agent支持'
        ]
    })

@app.route('/health')
def health():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'uptime_seconds': int((datetime.now() - trading_server.start_time).total_seconds()),
        'data_endpoints_available': True,
        'export_functions_available': True,
        'real_time_updates': True
    })

@app.route('/status')
def status():
    """服务状态"""
    return jsonify({
        'service_status': 'active',
        'data_server_running': True,
        'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_positions': len(trading_server.account_data['positions']),
        'total_trades': len(trading_server.account_data['trades']),
        'total_orders': len(trading_server.account_data['orders']),
        'account_balance': trading_server.account_data['balance']['total_assets']
    })

@app.route('/balance')
def balance():
    """账户余额"""
    balance_data = trading_server.account_data['balance'].copy()
    balance_data['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return jsonify(balance_data)

@app.route('/positions')
def positions():
    """持仓信息"""
    return jsonify({
        'positions': trading_server.account_data['positions'],
        'total_positions': len(trading_server.account_data['positions']),
        'total_market_value': sum(p['market_value'] for p in trading_server.account_data['positions']),
        'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/trades')
def trades():
    """成交记录"""
    return jsonify({
        'trades': trading_server.account_data['trades'],
        'total_trades': len(trading_server.account_data['trades']),
        'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/orders')
def orders():
    """委托订单"""
    return jsonify({
        'orders': trading_server.account_data['orders'],
        'total_orders': len(trading_server.account_data['orders']),
        'pending_orders': len([o for o in trading_server.account_data['orders'] if o['status'] == 'pending']),
        'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/history')
def history():
    """历史记录"""
    return jsonify({
        'trades': trading_server.account_data['trades'],
        'orders': trading_server.account_data['orders'],
        'positions': trading_server.account_data['positions'],
        'balance': trading_server.account_data['balance'],
        'summary': {
            'total_trades': len(trading_server.account_data['trades']),
            'total_orders': len(trading_server.account_data['orders']),
            'current_positions': len(trading_server.account_data['positions']),
            'account_value': trading_server.account_data['balance']['total_assets']
        },
        'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/trade', methods=['POST'])
def trade():
    """执行交易"""
    data = request.get_json()

    # 模拟交易执行
    trade_result = {
        'success': True,
        'trade_id': f'T{int(time.time())}',
        'action': data.get('action', 'buy'),
        'stock_code': data.get('stock_code', '000001'),
        'quantity': data.get('quantity', 100),
        'price': data.get('price', 10.50),
        'amount': data.get('quantity', 100) * data.get('price', 10.50),
        'commission': round(data.get('quantity', 100) * data.get('price', 10.50) * 0.0003, 2),
        'execute_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'status': 'executed',
        'message': '交易执行成功'
    }

    return jsonify(trade_result)

@app.route('/export/positions')
def export_positions():
    """导出持仓数据"""
    format_type = request.args.get('format', 'json')

    if format_type == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['股票代码', '股票名称', '持仓数量', '可用数量', '成本价', '现价', '市值', '盈亏', '盈亏比例'])

        for pos in trading_server.account_data['positions']:
            writer.writerow([
                pos['stock_code'], pos['stock_name'], pos['quantity'],
                pos['available_quantity'], pos['avg_cost'], pos['current_price'],
                pos['market_value'], pos['profit_loss'], f"{pos['profit_loss_ratio']}%"
            ])

        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8-sig')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'positions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )
    else:
        return jsonify({
            'export_type': 'positions',
            'format': 'json',
            'export_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data': trading_server.account_data['positions']
        })

@app.route('/export/trades')
def export_trades():
    """导出成交记录"""
    format_type = request.args.get('format', 'json')

    if format_type == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['成交编号', '股票代码', '股票名称', '买卖方向', '数量', '价格', '金额', '手续费', '成交时间', '状态'])

        for trade in trading_server.account_data['trades']:
            writer.writerow([
                trade['trade_id'], trade['stock_code'], trade['stock_name'],
                trade['action'], trade['quantity'], trade['price'],
                trade['amount'], trade['commission'], trade['trade_time'], trade['status']
            ])

        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8-sig')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'trades_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )
    else:
        return jsonify({
            'export_type': 'trades',
            'format': 'json',
            'export_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data': trading_server.account_data['trades']
        })

@app.route('/export/balance')
def export_balance():
    """导出资金信息"""
    format_type = request.args.get('format', 'json')

    balance_data = trading_server.account_data['balance'].copy()
    balance_data['export_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if format_type == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['项目', '金额'])

        for key, value in balance_data.items():
            if isinstance(value, (int, float)):
                writer.writerow([key, value])

        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8-sig')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'balance_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )
    else:
        return jsonify({
            'export_type': 'balance',
            'format': 'json',
            'data': balance_data
        })

@app.route('/export/all')
def export_all():
    """导出所有数据"""
    return jsonify({
        'export_type': 'complete_data',
        'export_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'balance': trading_server.account_data['balance'],
        'positions': trading_server.account_data['positions'],
        'trades': trading_server.account_data['trades'],
        'orders': trading_server.account_data['orders'],
        'summary': {
            'total_assets': trading_server.account_data['balance']['total_assets'],
            'total_positions': len(trading_server.account_data['positions']),
            'total_trades': len(trading_server.account_data['trades']),
            'total_orders': len(trading_server.account_data['orders'])
        }
    })

if __name__ == '__main__':
    print("🚀 启动完整的本地交易数据服务器...")
    print("📡 服务地址: http://localhost:8890")
    print("🔗 可用端点:")
    print("   GET  /          - 服务信息")
    print("   GET  /health    - 健康检查")
    print("   GET  /status    - 服务状态")
    print("   GET  /balance   - 账户余额")
    print("   GET  /positions - 持仓信息")
    print("   GET  /trades    - 成交记录")
    print("   GET  /orders    - 委托订单")
    print("   GET  /history   - 历史记录")
    print("   POST /trade     - 执行交易")
    print("📊 实时数据更新: 每30秒")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=8890, debug=False)
