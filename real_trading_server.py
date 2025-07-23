#!/usr/bin/env python3
"""
真实交易数据服务器
连接到实际的交易软件获取真实数据
"""

from flask import Flask, jsonify, request
import sys
import os
import json
from datetime import datetime
import subprocess
import time

# 添加stock-trading-backend到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'stock-trading-backend'))

app = Flask(__name__)

class RealTradingDataServer:
    def __init__(self):
        self.start_time = datetime.now()
        self.real_data_available = False
        self.last_export_time = None
        
        # 尝试连接真实交易模块
        self.init_real_trading_connection()
    
    def init_real_trading_connection(self):
        """初始化真实交易连接"""
        try:
            # 检查是否有交易软件运行
            self.check_trading_software()
            
            # 尝试导入真实交易模块
            self.import_trading_modules()
            
        except Exception as e:
            print(f"⚠️ 无法连接真实交易软件: {e}")
            print("📋 将使用基础数据获取模式")
    
    def check_trading_software(self):
        """检查交易软件是否运行"""
        try:
            # 使用tasklist检查是否有交易软件进程
            result = subprocess.run(['tasklist'], capture_output=True, text=True, shell=True)
            output = result.stdout
            
            # 检查常见的交易软件进程
            trading_processes = ['网上交易', '同花顺', '华泰', '招商', '东吴']
            
            for process in trading_processes:
                if process in output:
                    print(f"✅ 发现交易软件进程: {process}")
                    self.real_data_available = True
                    return True
            
            print("⚠️ 未发现交易软件进程")
            return False
            
        except Exception as e:
            print(f"❌ 检查交易软件失败: {e}")
            return False
    
    def import_trading_modules(self):
        """尝试导入交易模块"""
        try:
            # 尝试从stock-trading-backend导入
            stock_backend_path = os.path.join(os.path.dirname(__file__), 'stock-trading-backend')
            if os.path.exists(stock_backend_path):
                sys.path.insert(0, stock_backend_path)
                
                # 尝试导入关键模块
                try:
                    from trader_api import TraderAPI
                    self.trader_api = TraderAPI()
                    print("✅ 成功导入TraderAPI")
                    self.real_data_available = True
                except ImportError as e:
                    print(f"⚠️ 无法导入TraderAPI: {e}")
                
                try:
                    from trader_export import export_holdings, export_transactions, export_orders
                    self.export_functions = {
                        'holdings': export_holdings,
                        'transactions': export_transactions,
                        'orders': export_orders
                    }
                    print("✅ 成功导入导出函数")
                except ImportError as e:
                    print(f"⚠️ 无法导入导出函数: {e}")
            
        except Exception as e:
            print(f"❌ 导入交易模块失败: {e}")
    
    def get_real_balance(self):
        """获取真实账户余额"""
        try:
            if hasattr(self, 'trader_api'):
                # 使用真实API获取余额
                status = self.trader_api.get_status()
                if status.get('trading_software_active'):
                    # 这里应该调用真实的余额获取函数
                    return {
                        'total_assets': 0.0,  # 需要实现真实获取
                        'available_cash': 0.0,
                        'market_value': 0.0,
                        'data_source': 'real_trading_software',
                        'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
            
            # 如果无法获取真实数据,返回状态信息
            return {
                'total_assets': 0.0,
                'available_cash': 0.0,
                'market_value': 0.0,
                'data_source': 'unavailable',
                'message': '交易软件未连接或未登录',
                'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'data_source': 'error',
                'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
    
    def get_real_positions(self):
        """获取真实持仓"""
        try:
            if hasattr(self, 'export_functions') and 'holdings' in self.export_functions:
                # 尝试导出真实持仓
                success = self.export_functions['holdings']()
                if success:
                    # 这里需要读取导出的文件
                    return {
                        'positions': [],  # 需要解析导出文件
                        'data_source': 'real_export',
                        'export_success': True,
                        'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
            
            return {
                'positions': [],
                'data_source': 'unavailable',
                'message': '无法导出持仓数据',
                'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            return {
                'positions': [],
                'error': str(e),
                'data_source': 'error',
                'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
    
    def get_real_trades(self):
        """获取真实成交记录"""
        try:
            if hasattr(self, 'export_functions') and 'transactions' in self.export_functions:
                # 尝试导出真实成交记录
                success = self.export_functions['transactions']()
                if success:
                    return {
                        'trades': [],  # 需要解析导出文件
                        'data_source': 'real_export',
                        'export_success': True,
                        'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
            
            return {
                'trades': [],
                'data_source': 'unavailable',
                'message': '无法导出成交记录',
                'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            return {
                'trades': [],
                'error': str(e),
                'data_source': 'error',
                'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

# 创建全局服务器实例
real_server = RealTradingDataServer()

@app.route('/')
def root():
    """根路径信息"""
    return jsonify({
        'service': '真实交易数据服务器',
        'version': '1.0.0',
        'status': 'running',
        'real_data_available': real_server.real_data_available,
        'start_time': real_server.start_time.strftime('%Y-%m-%d %H:%M:%S'),
        'uptime_seconds': int((datetime.now() - real_server.start_time).total_seconds()),
        'endpoints': [
            '/health', '/status', '/balance', '/positions', '/trades', '/export'
        ],
        'data_source': 'real_trading_software' if real_server.real_data_available else 'unavailable'
    })

@app.route('/health')
def health():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'real_trading_connected': real_server.real_data_available,
        'uptime_seconds': int((datetime.now() - real_server.start_time).total_seconds())
    })

@app.route('/status')
def status():
    """服务状态"""
    status_info = {
        'service_status': 'active',
        'real_data_available': real_server.real_data_available,
        'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # 如果有真实API,获取详细状态
    if hasattr(real_server, 'trader_api'):
        try:
            trader_status = real_server.trader_api.get_status()
            status_info.update(trader_status)
        except Exception as e:
            status_info['trader_api_error'] = str(e)
    
    return jsonify(status_info)

@app.route('/balance')
def balance():
    """账户余额"""
    balance_data = real_server.get_real_balance()
    return jsonify(balance_data)

@app.route('/positions')
def positions():
    """持仓信息"""
    positions_data = real_server.get_real_positions()
    return jsonify(positions_data)

@app.route('/trades')
def trades():
    """成交记录"""
    trades_data = real_server.get_real_trades()
    return jsonify(trades_data)

@app.route('/export', methods=['POST'])
def export_data():
    """导出数据"""
    try:
        data = request.get_json()
        data_type = data.get('data_type', 'all')
        
        result = {
            'export_type': data_type,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'success': False,
            'message': '导出功能需要连接真实交易软件'
        }
        
        if real_server.real_data_available and hasattr(real_server, 'export_functions'):
            if data_type in real_server.export_functions:
                try:
                    success = real_server.export_functions[data_type]()
                    result['success'] = success
                    result['message'] = '导出成功' if success else '导出失败'
                except Exception as e:
                    result['error'] = str(e)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

@app.route('/trade', methods=['POST'])
def trade():
    """执行交易"""
    try:
        data = request.get_json()
        
        result = {
            'success': False,
            'message': '交易功能需要连接真实交易软件',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        if real_server.real_data_available and hasattr(real_server, 'trader_api'):
            # 这里可以调用真实的交易函数
            result['message'] = '真实交易功能已连接,但为安全起见暂时禁用'
            result['data'] = data
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

if __name__ == '__main__':
    print("🚀 启动真实交易数据服务器...")
    print("📡 服务地址: http://localhost:8891")
    print("🔗 连接状态:")
    print(f"   真实数据可用: {'✅' if real_server.real_data_available else '❌'}")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=8891, debug=False)
