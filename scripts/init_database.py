#!/usr/bin/env python3
"""
数据库初始化脚本
创建必要的表结构和初始数据
"""

import requests
import json
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Supabase配置
SUPABASE_URL = 'https://zzukfxwavknskqcepsjb.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6dWtmeHdhdmtuc2txY2Vwc2piIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyOTg1MDYsImV4cCI6MjA2Njg3NDUwNn0.AMGkJSre3QtRBQK_Lh2Iga4dUzSPvuO1G9s6fF2QPaw'

class DatabaseInitializer:
    def __init__(self):
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'apikey': SUPABASE_KEY
        }
        
    def check_table_exists(self, table_name):
        """检查表是否存在"""
        try:
            response = requests.get(
                f'{SUPABASE_URL}/rest/v1/{table_name}?select=count&limit=1',
                headers=self.headers
            )
            return response.status_code == 200
        except:
            return False
            
    def init_stocks_table(self):
        """初始化stocks表数据"""
        logging.info("初始化stocks表...")
        
        # 检查表是否为空
        try:
            response = requests.get(
                f'{SUPABASE_URL}/rest/v1/stocks?select=count',
                headers=self.headers
            )
            
            if response.status_code == 200:
                existing_count = len(response.json())
                if existing_count > 0:
                    logging.info(f"stocks表已有 {existing_count} 条记录，跳过初始化")
                    return
        except Exception as e:
            logging.error(f"检查stocks表失败: {e}")
            
        # 基础股票数据
        stocks_data = [
            {
                'stock_code': 'sz000001',
                'stock_name': '平安银行',
                'market': 'SZSE',
                'sector': '金融',
                'industry': '银行',
                'is_active': True
            },
            {
                'stock_code': 'sz000002',
                'stock_name': '万科A',
                'market': 'SZSE',
                'sector': '房地产',
                'industry': '房地产开发',
                'is_active': True
            },
            {
                'stock_code': 'sh600000',
                'stock_name': '浦发银行',
                'market': 'SSE',
                'sector': '金融',
                'industry': '银行',
                'is_active': True
            },
            {
                'stock_code': 'sh600036',
                'stock_name': '招商银行',
                'market': 'SSE',
                'sector': '金融',
                'industry': '银行',
                'is_active': True
            },
            {
                'stock_code': 'sh600519',
                'stock_name': '贵州茅台',
                'market': 'SSE',
                'sector': '食品饮料',
                'industry': '白酒',
                'is_active': True
            },
            {
                'stock_code': 'sz002415',
                'stock_name': '海康威视',
                'market': 'SZSE',
                'sector': '科技',
                'industry': '安防设备',
                'is_active': True
            },
            {
                'stock_code': 'sz300750',
                'stock_name': '宁德时代',
                'market': 'SZSE',
                'sector': '新能源',
                'industry': '电池',
                'is_active': True
            },
            {
                'stock_code': 'sh688599',
                'stock_name': '天合光能',
                'market': 'SSE',
                'sector': '新能源',
                'industry': '光伏',
                'is_active': True
            },
            {
                'stock_code': 'sh601318',
                'stock_name': '中国平安',
                'market': 'SSE',
                'sector': '金融',
                'industry': '保险',
                'is_active': True
            },
            {
                'stock_code': 'bj430047',
                'stock_name': '诺思兰德',
                'market': 'BSE',
                'sector': '医药',
                'industry': '生物制药',
                'is_active': True
            }
        ]
        
        try:
            response = requests.post(
                f'{SUPABASE_URL}/rest/v1/stocks',
                headers=self.headers,
                json=stocks_data
            )
            
            if response.status_code in [200, 201]:
                logging.info(f"成功初始化 {len(stocks_data)} 条股票基础数据")
            else:
                logging.error(f"初始化stocks表失败: {response.status_code} - {response.text}")
                
        except Exception as e:
            logging.error(f"初始化stocks表异常: {e}")
            
    def init_system_config(self):
        """初始化系统配置"""
        logging.info("初始化系统配置...")
        
        config_data = [
            {
                'key': 'stock_api_url',
                'value': 'https://realtime-stock-api.pages.dev',
                'description': '股票API地址',
                'category': 'api'
            },
            {
                'key': 'data_sync_interval',
                'value': '300',
                'description': '数据同步间隔(秒)',
                'category': 'sync'
            },
            {
                'key': 'push_data_retention_hours',
                'value': '24',
                'description': '推送数据保留时间(小时)',
                'category': 'cleanup'
            },
            {
                'key': 'api_key_primary',
                'value': 'QT_wat5QfcJ6N9pDZM5',
                'description': '主要API密钥',
                'category': 'api'
            },
            {
                'key': 'data_quality_threshold',
                'value': '85',
                'description': '数据质量阈值',
                'category': 'quality'
            }
        ]
        
        try:
            # 检查是否已有配置
            response = requests.get(
                f'{SUPABASE_URL}/rest/v1/system_config?select=count',
                headers=self.headers
            )
            
            if response.status_code == 200:
                existing_count = len(response.json())
                if existing_count > 0:
                    logging.info(f"system_config表已有 {existing_count} 条记录，跳过初始化")
                    return
                    
            # 插入配置数据
            response = requests.post(
                f'{SUPABASE_URL}/rest/v1/system_config',
                headers=self.headers,
                json=config_data
            )
            
            if response.status_code in [200, 201]:
                logging.info(f"成功初始化 {len(config_data)} 条系统配置")
            else:
                logging.error(f"初始化system_config表失败: {response.status_code} - {response.text}")
                
        except Exception as e:
            logging.error(f"初始化system_config表异常: {e}")
            
    def test_data_sync(self):
        """测试数据同步功能"""
        logging.info("测试数据同步功能...")
        
        try:
            # 调用数据同步API
            response = requests.get('https://realtime-stock-api.pages.dev/api/data-sync?action=sync')
            
            if response.status_code == 200:
                result = response.json()
                logging.info(f"数据同步测试成功: {result.get('message', '')}")
                logging.info(f"处理股票数: {result.get('total_processed', 0)}")
                logging.info(f"成功数: {result.get('successful', 0)}")
                logging.info(f"失败数: {result.get('failed', 0)}")
            else:
                logging.error(f"数据同步测试失败: {response.status_code}")
                
        except Exception as e:
            logging.error(f"数据同步测试异常: {e}")
            
    def test_health_monitor(self):
        """测试健康监控功能"""
        logging.info("测试健康监控功能...")
        
        try:
            response = requests.get('https://realtime-stock-api.pages.dev/api/data-sync?action=monitor')
            
            if response.status_code == 200:
                result = response.json()
                logging.info(f"健康监控测试成功: {result.get('overall_status', '')}")
                
                for check in result.get('health_status', []):
                    logging.info(f"组件 {check['component']}: {check['status']}")
            else:
                logging.error(f"健康监控测试失败: {response.status_code}")
                
        except Exception as e:
            logging.error(f"健康监控测试异常: {e}")
            
    def run_initialization(self):
        """运行完整初始化"""
        logging.info("开始数据库初始化...")
        
        # 初始化基础数据
        self.init_stocks_table()
        self.init_system_config()
        
        # 测试功能
        self.test_data_sync()
        self.test_health_monitor()
        
        logging.info("数据库初始化完成")

def main():
    """主函数"""
    initializer = DatabaseInitializer()
    initializer.run_initialization()

if __name__ == '__main__':
    main()
