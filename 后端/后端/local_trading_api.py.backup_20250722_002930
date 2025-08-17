"""
本地交易API服务器
接收云端agent的买卖指令并执行本地交易操作
"""

from flask import Flask, request, jsonify
from trader_export import export_holdings, export_transactions, export_orders
from trader_buy_sell import buy_stock, sell_stock
from fixed_balance_reader import get_balance_fixed
import os
import glob
import json
from datetime import datetime
import threading
import time

app = Flask(__name__)

# 全局状态
server_status = {
    "running": True,
    "last_export_time": None,
    "last_balance_time": None,
    "total_requests": 0
}

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "server_info": server_status
    })

@app.route('/balance', methods=['GET'])
def get_balance():
    """获取账户余额"""
    try:
        print(f"\n📊 [API] 收到余额查询请求")
        balance = get_balance_fixed()
        
        if balance:
            server_status["last_balance_time"] = datetime.now().isoformat()
            server_status["total_requests"] += 1
            
            print(f"✅ [API] 余额获取成功: {balance['available_cash']:,.2f}")
            return jsonify({
                "success": True,
                "data": balance,
                "timestamp": datetime.now().isoformat()
            })
        else:
            print(f"❌ [API] 余额获取失败")
            return jsonify({
                "success": False,
                "error": "余额获取失败",
                "timestamp": datetime.now().isoformat()
            }), 500
            
    except Exception as e:
        print(f"❌ [API] 余额获取异常: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/export', methods=['POST'])
def export_data():
    """导出交易数据"""
    try:
        data = request.get_json()
        export_type = data.get('type', 'all')  # holdings, transactions, orders, all
        
        print(f"\n📊 [API] 收到导出请求: {export_type}")
        
        results = {}
        
        if export_type in ['holdings', 'all']:
            print("   导出持仓数据...")
            results['holdings'] = export_holdings()
            
        if export_type in ['transactions', 'all']:
            print("   导出成交数据...")
            results['transactions'] = export_transactions()
            
        if export_type in ['orders', 'all']:
            print("   导出委托数据...")
            results['orders'] = export_orders()
        
        # 获取最新的CSV文件
        csv_files = {}
        if results.get('holdings'):
            holdings_files = glob.glob("持仓数据_*.csv")
            if holdings_files:
                latest_holdings = max(holdings_files, key=os.path.getmtime)
                csv_files['holdings_file'] = latest_holdings
                
        if results.get('transactions'):
            transaction_files = glob.glob("成交数据_*.csv")
            if transaction_files:
                latest_transactions = max(transaction_files, key=os.path.getmtime)
                csv_files['transactions_file'] = latest_transactions
                
        if results.get('orders'):
            order_files = glob.glob("委托数据_*.csv")
            if order_files:
                latest_orders = max(order_files, key=os.path.getmtime)
                csv_files['orders_file'] = latest_orders
        
        server_status["last_export_time"] = datetime.now().isoformat()
        server_status["total_requests"] += 1
        
        print(f"✅ [API] 导出完成: {results}")
        return jsonify({
            "success": True,
            "data": {
                "export_results": results,
                "files": csv_files
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ [API] 导出异常: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/trade', methods=['POST'])
def execute_trade():
    """执行买卖交易"""
    try:
        data = request.get_json()
        action = data.get('action')  # 'buy' or 'sell'
        code = data.get('code')
        price = data.get('price', '市价')
        quantity = data.get('quantity')
        
        print(f"\n🚀 [API] 收到交易指令:")
        print(f"   操作: {action}")
        print(f"   代码: {code}")
        print(f"   价格: {price}")
        print(f"   数量: {quantity}")
        
        if not all([action, code, quantity]):
            return jsonify({
                "success": False,
                "error": "缺少必要参数: action, code, quantity",
                "timestamp": datetime.now().isoformat()
            }), 400
        
        # 执行交易
        if action.lower() == 'buy':
            result = buy_stock(code, price, quantity)
            operation = "买入"
        elif action.lower() == 'sell':
            result = sell_stock(code, price, quantity)
            operation = "卖出"
        else:
            return jsonify({
                "success": False,
                "error": "无效的操作类型，只支持 'buy' 或 'sell'",
                "timestamp": datetime.now().isoformat()
            }), 400
        
        server_status["total_requests"] += 1
        
        if result:
            print(f"✅ [API] {operation}操作完成")
            return jsonify({
                "success": True,
                "data": {
                    "action": action,
                    "code": code,
                    "price": price,
                    "quantity": quantity,
                    "operation": operation,
                    "message": f"{operation}指令已发送到交易软件"
                },
                "timestamp": datetime.now().isoformat()
            })
        else:
            print(f"❌ [API] {operation}操作失败")
            return jsonify({
                "success": False,
                "error": f"{operation}操作失败",
                "timestamp": datetime.now().isoformat()
            }), 500
            
    except Exception as e:
        print(f"❌ [API] 交易异常: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/files/<filename>', methods=['GET'])
def get_file_content(filename):
    """获取CSV文件内容"""
    try:
        if not filename.endswith('.csv'):
            return jsonify({
                "success": False,
                "error": "只支持CSV文件",
                "timestamp": datetime.now().isoformat()
            }), 400
            
        if not os.path.exists(filename):
            return jsonify({
                "success": False,
                "error": "文件不存在",
                "timestamp": datetime.now().isoformat()
            }), 404
            
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            
        return jsonify({
            "success": True,
            "data": {
                "filename": filename,
                "content": content,
                "size": len(content)
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

def run_server():
    """运行服务器"""
    print("🚀 启动本地交易API服务器...")
    print("📡 服务地址: http://localhost:5000")
    print("📋 可用接口:")
    print("   GET  /health - 健康检查")
    print("   GET  /balance - 获取余额")
    print("   POST /export - 导出数据")
    print("   POST /trade - 执行交易")
    print("   GET  /files/<filename> - 获取文件内容")
    print("-" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == "__main__":
    run_server()
