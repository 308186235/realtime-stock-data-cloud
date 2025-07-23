"""
数据库设置和初始化脚本
"""
import sqlite3
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path="data/trading_system.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """初始化数据库表"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建用户表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建投资组合表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS portfolios (
                    id TEXT PRIMARY KEY,
                    user_id INTEGER,
                    name TEXT NOT NULL,
                    total_value REAL DEFAULT 0,
                    cash REAL DEFAULT 0,
                    stock_value REAL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # 创建持仓表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS holdings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    portfolio_id TEXT,
                    stock_code TEXT NOT NULL,
                    stock_name TEXT NOT NULL,
                    shares INTEGER NOT NULL,
                    cost_price REAL NOT NULL,
                    current_price REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (portfolio_id) REFERENCES portfolios (id)
                )
            ''')
            
            # 创建交易记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    portfolio_id TEXT,
                    stock_code TEXT NOT NULL,
                    stock_name TEXT NOT NULL,
                    transaction_type TEXT NOT NULL, -- 'buy' or 'sell'
                    shares INTEGER NOT NULL,
                    price REAL NOT NULL,
                    total_amount REAL NOT NULL,
                    commission REAL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (portfolio_id) REFERENCES portfolios (id)
                )
            ''')
            
            # 创建策略表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS strategies (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'inactive',
                    profit_pct REAL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建市场数据表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS market_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stock_code TEXT NOT NULL,
                    stock_name TEXT NOT NULL,
                    price REAL NOT NULL,
                    change_amount REAL,
                    change_pct REAL,
                    volume INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info(f"数据库初始化完成: {self.db_path}")
            
        except Exception as e:
            logger.error(f"数据库初始化失败: {str(e)}")
            raise
    
    def insert_sample_data(self):
        """插入示例数据"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 插入示例投资组合
            cursor.execute('''
                INSERT OR REPLACE INTO portfolios 
                (id, user_id, name, total_value, cash, stock_value) 
                VALUES (?, ?, ?, ?, ?, ?)
            ''', ('portfolio-001', 1, '默认组合', 152340.56, 25600.38, 126740.18))
            
            # 插入示例持仓
            holdings_data = [
                ('portfolio-001', '600000', '浦发银行', 1000, 10.56, 11.23),
                ('portfolio-001', '000001', '平安银行', 500, 15.20, 16.45),
                ('portfolio-001', '000002', '万科A', 300, 25.67, 25.34)
            ]
            
            cursor.executemany('''
                INSERT OR REPLACE INTO holdings 
                (portfolio_id, stock_code, stock_name, shares, cost_price, current_price) 
                VALUES (?, ?, ?, ?, ?, ?)
            ''', holdings_data)
            
            # 插入示例策略
            strategies_data = [
                ('strategy-001', '均线策略', '基于移动平均线的交易策略', 'active', 12.5),
                ('strategy-002', '动量策略', '基于价格动量的交易策略', 'inactive', 8.3),
                ('strategy-003', 'RSI策略', '基于相对强弱指数的交易策略', 'active', 15.2)
            ]
            
            cursor.executemany('''
                INSERT OR REPLACE INTO strategies 
                (id, name, description, status, profit_pct) 
                VALUES (?, ?, ?, ?, ?)
            ''', strategies_data)
            
            # 插入示例市场数据
            market_data = [
                ('600000', '浦发银行', 11.23, 0.67, 6.34, 1500000),
                ('000001', '平安银行', 16.45, 1.25, 8.22, 2300000),
                ('000002', '万科A', 25.34, -0.33, -1.28, 1800000),
                ('600036', '招商银行', 42.56, 2.15, 5.32, 3200000),
                ('000858', '五粮液', 168.90, -3.45, -2.00, 890000)
            ]
            
            cursor.executemany('''
                INSERT OR REPLACE INTO market_data 
                (stock_code, stock_name, price, change_amount, change_pct, volume) 
                VALUES (?, ?, ?, ?, ?, ?)
            ''', market_data)
            
            conn.commit()
            conn.close()
            
            logger.info("示例数据插入完成")
            
        except Exception as e:
            logger.error(f"插入示例数据失败: {str(e)}")
            raise
    
    def get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)

def setup_database():
    """设置数据库"""
    print("🗄️ 正在设置数据库...")
    
    db_manager = DatabaseManager()
    db_manager.insert_sample_data()
    
    print("✅ 数据库设置完成!")
    print(f"📍 数据库位置: {db_manager.db_path}")
    
    return db_manager

if __name__ == "__main__":
    setup_database()
