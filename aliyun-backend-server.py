#!/usr/bin/env python3
"""
阿里云服务器后端 - AI股票交易系统
功能:股票数据处理,AI决策,交易执行,数据存储
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import json
import socket
import threading
import time
from datetime import datetime, timedelta
import requests
import logging
from contextlib import contextmanager

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 配置
CONFIG = {
    'database': '/data/stock_trading.db',
    'chagubang': {
        'host': 'l1.chagubang.com',
        'port': 6380,
        'token': 'QT_wat5QfcJ6N9pDZM5'
    },
    'supabase': {
        'url': 'https://zzukfxwavknskqcepsjb.supabase.co',
        'key': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6dWtmeHdhdmtuc2txY2Vwc2piIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTk3NTQ5MDYsImV4cCI6MjAzNTMzMDkwNn0.VQjKQKWgVXKhJhqKvZ8_Zt8wZ8wZ8wZ8wZ8wZ8wZ8wZ'
    }
}

# 全局变量
chagubang_connection = None
stock_data_cache = {}

# 数据库管理
@contextmanager
def get_db():
    conn = sqlite3.connect(CONFIG['database'])
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_database():
    """初始化数据库"""
    with get_db() as conn:
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS stock_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                name TEXT,
                current_price REAL,
                change_amount REAL,
                change_percent REAL,
                volume INTEGER,
                turnover REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                data_source TEXT DEFAULT 'chagubang'
            );
            
            CREATE TABLE IF NOT EXISTS trading_decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                strategy TEXT,
                decision TEXT,
                confidence REAL,
                amount INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                action TEXT NOT NULL,
                amount INTEGER NOT NULL,
                price REAL,
                status TEXT DEFAULT 'PENDING',
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS virtual_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                balance REAL DEFAULT 100000,
                available_balance REAL DEFAULT 100000,
                total_assets REAL DEFAULT 100000,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_stock_symbol ON stock_data(symbol);
            CREATE INDEX IF NOT EXISTS idx_stock_timestamp ON stock_data(timestamp);
        ''')
        conn.commit()

# 茶股帮数据连接
class ChaguBangConnector:
    def __init__(self):
        self.socket = None
        self.connected = False
        self.running = False
    
    def connect(self):
        """连接茶股帮服务器"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((CONFIG['chagubang']['host'], CONFIG['chagubang']['port']))
            
            # 发送认证token
            self.socket.send(CONFIG['chagubang']['token'].encode())
            
            self.connected = True
            logger.info("茶股帮连接成功")
            return True
        except Exception as e:
            logger.error(f"茶股帮连接失败: {e}")
            return False
    
    def start_data_receiver(self):
        """启动数据接收线程"""
        if not self.connected:
            if not self.connect():
                return False
        
        self.running = True
        thread = threading.Thread(target=self._receive_data)
        thread.daemon = True
        thread.start()
        return True
    
    def _receive_data(self):
        """接收股票数据"""
        while self.running and self.connected:
            try:
                data = self.socket.recv(1024).decode('utf-8')
                if data:
                    self._process_stock_data(data)
            except Exception as e:
                logger.error(f"接收数据错误: {e}")
                self.connected = False
                break
    
    def _process_stock_data(self, raw_data):
        """处理股票数据"""
        try:
            fields = raw_data.strip().split('$')
            if len(fields) >= 15:
                stock_data = {
                    'symbol': fields[0],
                    'name': fields[1],
                    'current_price': float(fields[2]) if fields[2] else 0,
                    'change_amount': float(fields[3]) if fields[3] else 0,
                    'change_percent': float(fields[4]) if fields[4] else 0,
                    'volume': int(fields[5]) if fields[5] else 0,
                    'turnover': float(fields[6]) if fields[6] else 0,
                    'timestamp': datetime.now().isoformat()
                }
                
                # 缓存数据
                stock_data_cache[stock_data['symbol']] = stock_data
                
                # 存储到数据库
                self._save_to_database(stock_data)
                
                # 推送到Supabase
                self._push_to_supabase(stock_data)
                
        except Exception as e:
            logger.error(f"处理股票数据失败: {e}")
    
    def _save_to_database(self, data):
        """保存到本地数据库"""
        try:
            with get_db() as conn:
                conn.execute('''
                    INSERT INTO stock_data 
                    (symbol, name, current_price, change_amount, change_percent, volume, turnover)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    data['symbol'], data['name'], data['current_price'],
                    data['change_amount'], data['change_percent'],
                    data['volume'], data['turnover']
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"保存数据库失败: {e}")
    
    def _push_to_supabase(self, data):
        """推送到Supabase"""
        try:
            headers = {
                'apikey': CONFIG['supabase']['key'],
                'Authorization': f"Bearer {CONFIG['supabase']['key']}",
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f"{CONFIG['supabase']['url']}/rest/v1/realtime_stock_data",
                headers=headers,
                json=data,
                timeout=5
            )
            
            if not response.ok:
                logger.warning(f"Supabase推送失败: {response.status_code}")
                
        except Exception as e:
            logger.error(f"推送Supabase失败: {e}")

# 全局连接器实例
chagubang_connector = ChaguBangConnector()

# API路由
@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'database': True,
            'chagubang': chagubang_connector.connected,
            'cache_size': len(stock_data_cache)
        }
    })

@app.route('/api/stock-data', methods=['GET'])
def get_stock_data():
    """获取股票数据"""
    symbol = request.args.get('symbol')
    limit = int(request.args.get('limit', 100))
    
    if not symbol:
        return jsonify({'error': '缺少股票代码参数'}), 400
    
    try:
        # 优先从缓存获取
        if symbol in stock_data_cache:
            cached_data = stock_data_cache[symbol]
            return jsonify({
                'success': True,
                'data': [cached_data],
                'source': 'cache',
                'timestamp': datetime.now().isoformat()
            })
        
        # 从数据库获取
        with get_db() as conn:
            cursor = conn.execute('''
                SELECT * FROM stock_data 
                WHERE symbol = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (symbol, limit))
            
            rows = cursor.fetchall()
            data = [dict(row) for row in rows]
            
            return jsonify({
                'success': True,
                'data': data,
                'source': 'database',
                'timestamp': datetime.now().isoformat()
            })
            
    except Exception as e:
        logger.error(f"获取股票数据失败: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/trading-decision', methods=['POST'])
def make_trading_decision():
    """AI交易决策"""
    try:
        data = request.get_json()
        symbol = data.get('symbol')
        amount = data.get('amount')
        strategy = data.get('strategy', 'momentum')
        
        if not symbol or not amount:
            return jsonify({'error': '缺少必要参数'}), 400
        
        # 获取最新股票数据
        with get_db() as conn:
            cursor = conn.execute('''
                SELECT * FROM stock_data 
                WHERE symbol = ? 
                ORDER BY timestamp DESC 
                LIMIT 20
            ''', (symbol,))
            
            stock_history = [dict(row) for row in cursor.fetchall()]
        
        if len(stock_history) < 2:
            decision = {
                'action': 'HOLD',
                'confidence': 0.1,
                'reason': '数据不足'
            }
        else:
            decision = analyze_stock_data(stock_history, strategy)
        
        # 保存决策记录
        with get_db() as conn:
            conn.execute('''
                INSERT INTO trading_decisions 
                (symbol, strategy, decision, confidence, amount)
                VALUES (?, ?, ?, ?, ?)
            ''', (symbol, strategy, decision['action'], decision['confidence'], amount))
            conn.commit()
        
        return jsonify({
            'success': True,
            'decision': decision,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"交易决策失败: {e}")
        return jsonify({'error': str(e)}), 500

def analyze_stock_data(history, strategy):
    """分析股票数据并生成交易决策"""
    if len(history) < 2:
        return {'action': 'HOLD', 'confidence': 0.1, 'reason': '数据不足'}

    latest = history[0]
    previous = history[1]

    # 计算价格变化
    price_change = (latest['current_price'] - previous['current_price']) / previous['current_price']

    if strategy == 'momentum':
        if price_change > 0.02:
            return {
                'action': 'BUY',
                'confidence': min(price_change * 10, 0.8),
                'reason': f'价格上涨{price_change*100:.2f}%,动量策略建议买入'
            }
        elif price_change < -0.02:
            return {
                'action': 'SELL',
                'confidence': min(abs(price_change) * 10, 0.8),
                'reason': f'价格下跌{abs(price_change)*100:.2f}%,动量策略建议卖出'
            }

    return {
        'action': 'HOLD',
        'confidence': 0.5,
        'reason': '价格波动较小,建议持有'
    }

@app.route('/api/account-info', methods=['GET'])
def get_account_info():
    """获取账户信息"""
    try:
        with get_db() as conn:
            cursor = conn.execute('''
                SELECT * FROM virtual_accounts
                ORDER BY created_at DESC
                LIMIT 1
            ''')

            account = cursor.fetchone()

            if not account:
                # 创建默认账户
                conn.execute('''
                    INSERT INTO virtual_accounts (balance, available_balance, total_assets)
                    VALUES (100000, 100000, 100000)
                ''')
                conn.commit()

                cursor = conn.execute('''
                    SELECT * FROM virtual_accounts
                    ORDER BY created_at DESC
                    LIMIT 1
                ''')
                account = cursor.fetchone()

            return jsonify({
                'success': True,
                'account': dict(account),
                'timestamp': datetime.now().isoformat()
            })

    except Exception as e:
        logger.error(f"获取账户信息失败: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/submit-trade', methods=['POST'])
def submit_trade():
    """提交交易"""
    try:
        data = request.get_json()
        symbol = data.get('symbol')
        action = data.get('action')
        amount = data.get('amount')
        price = data.get('price', 0)

        if not all([symbol, action, amount]):
            return jsonify({'error': '缺少必要的交易参数'}), 400

        # 保存交易记录
        with get_db() as conn:
            cursor = conn.execute('''
                INSERT INTO trades (symbol, action, amount, price, status)
                VALUES (?, ?, ?, ?, 'EXECUTED')
            ''', (symbol, action, amount, price))

            trade_id = cursor.lastrowid
            conn.commit()

        # 这里应该调用实际的交易接口
        # 暂时模拟交易成功

        return jsonify({
            'success': True,
            'trade': {
                'id': trade_id,
                'symbol': symbol,
                'action': action,
                'amount': amount,
                'price': price,
                'status': 'EXECUTED',
                'timestamp': datetime.now().isoformat()
            }
        })

    except Exception as e:
        logger.error(f"提交交易失败: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/realtime-data', methods=['GET'])
def get_realtime_data():
    """获取实时数据"""
    symbols = request.args.get('symbols', '').split(',')
    symbols = [s.strip() for s in symbols if s.strip()]

    if not symbols:
        return jsonify({'error': '缺少股票代码参数'}), 400

    try:
        data = {}
        for symbol in symbols:
            if symbol in stock_data_cache:
                data[symbol] = stock_data_cache[symbol]
            else:
                # 从数据库获取最新数据
                with get_db() as conn:
                    cursor = conn.execute('''
                        SELECT * FROM stock_data
                        WHERE symbol = ?
                        ORDER BY timestamp DESC
                        LIMIT 1
                    ''', (symbol,))

                    row = cursor.fetchone()
                    data[symbol] = dict(row) if row else None

        return jsonify({
            'success': True,
            'data': data,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"获取实时数据失败: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/start-data-push', methods=['POST'])
def start_data_push():
    """启动数据推送"""
    try:
        if chagubang_connector.start_data_receiver():
            return jsonify({
                'success': True,
                'message': '数据推送已启动',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'message': '数据推送启动失败'
            }), 500

    except Exception as e:
        logger.error(f"启动数据推送失败: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/trading-history', methods=['GET'])
def get_trading_history():
    """获取交易历史"""
    try:
        limit = int(request.args.get('limit', 50))

        with get_db() as conn:
            cursor = conn.execute('''
                SELECT * FROM trades
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))

            trades = [dict(row) for row in cursor.fetchall()]

            return jsonify({
                'success': True,
                'trades': trades,
                'timestamp': datetime.now().isoformat()
            })

    except Exception as e:
        logger.error(f"获取交易历史失败: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/system-stats', methods=['GET'])
def get_system_stats():
    """获取系统统计"""
    try:
        with get_db() as conn:
            # 获取各种统计数据
            stats = {}

            # 总交易数
            cursor = conn.execute('SELECT COUNT(*) as count FROM trades')
            stats['total_trades'] = cursor.fetchone()['count']

            # 今日交易数
            today = datetime.now().date()
            cursor = conn.execute('''
                SELECT COUNT(*) as count FROM trades
                WHERE DATE(timestamp) = ?
            ''', (today,))
            stats['today_trades'] = cursor.fetchone()['count']

            # 股票数据点数
            cursor = conn.execute('SELECT COUNT(*) as count FROM stock_data')
            stats['data_points'] = cursor.fetchone()['count']

            # 缓存股票数
            stats['cached_stocks'] = len(stock_data_cache)

            # 连接状态
            stats['chagubang_connected'] = chagubang_connector.connected

            return jsonify({
                'success': True,
                'stats': stats,
                'timestamp': datetime.now().isoformat()
            })

    except Exception as e:
        logger.error(f"获取系统统计失败: {e}")
        return jsonify({'error': str(e)}), 500

# 定时任务:清理旧数据
def cleanup_old_data():
    """清理7天前的股票数据"""
    try:
        cutoff_date = datetime.now() - timedelta(days=7)
        with get_db() as conn:
            cursor = conn.execute('''
                DELETE FROM stock_data
                WHERE timestamp < ?
            ''', (cutoff_date,))

            deleted_count = cursor.rowcount
            conn.commit()

            logger.info(f"清理了 {deleted_count} 条旧数据")

    except Exception as e:
        logger.error(f"清理数据失败: {e}")

# 启动定时任务
def start_background_tasks():
    """启动后台任务"""
    def run_cleanup():
        while True:
            time.sleep(3600)  # 每小时运行一次
            cleanup_old_data()

    cleanup_thread = threading.Thread(target=run_cleanup)
    cleanup_thread.daemon = True
    cleanup_thread.start()

    # 启动茶股帮数据接收
    chagubang_connector.start_data_receiver()

if __name__ == '__main__':
    # 初始化数据库
    init_database()

    # 启动后台任务
    start_background_tasks()

    # 启动Flask应用
    app.run(host='0.0.0.0', port=8000, debug=False)
