#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
处理现有的交易数据文件并上传到Agent系统
读取已导出的持仓,委托,成交数据文件,转换格式后上传给Agent分析
"""

import os
import json
import glob
import pandas as pd
import requests
from datetime import datetime

class TradingFileProcessor:
    def __init__(self):
        self.cloud_api = "https://api.aigupiao.me"
        self.processed_data = {}
        
    def find_trading_files(self):
        """查找交易数据文件"""
        print("🔍 查找交易数据文件...")
        print("=" * 50)
        
        # 查找各类文件
        file_patterns = {
            'holdings': '*持仓数据*.xls*',
            'orders': '*委托数据*.xls*', 
            'transactions': '*成交数据*.xls*'
        }
        
        found_files = {}
        
        for data_type, pattern in file_patterns.items():
            files = glob.glob(pattern)
            if files:
                # 按修改时间排序,获取最新的文件
                latest_file = max(files, key=os.path.getmtime)
                found_files[data_type] = {
                    'latest': latest_file,
                    'all_files': files,
                    'count': len(files)
                }
                
                file_time = datetime.fromtimestamp(os.path.getmtime(latest_file))
                print(f"✅ {data_type}: 找到 {len(files)} 个文件")
                print(f"   最新文件: {latest_file}")
                print(f"   修改时间: {file_time.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                print(f"❌ {data_type}: 未找到文件")
                found_files[data_type] = None
        
        return found_files
    
    def process_holdings_file(self, file_path):
        """处理持仓数据文件"""
        print(f"\n📊 处理持仓数据: {file_path}")
        
        try:
            # 读取Excel文件
            df = pd.read_excel(file_path)
            
            print(f"   📋 原始数据: {len(df)} 行 x {len(df.columns)} 列")
            print(f"   📋 列名: {list(df.columns)}")
            
            # 转换为标准格式
            holdings_data = []
            for _, row in df.iterrows():
                holding = {
                    'stock_code': str(row.get('证券代码', '')),
                    'stock_name': str(row.get('证券名称', '')),
                    'quantity': float(row.get('股票余额', 0)) if pd.notna(row.get('股票余额')) else 0,
                    'available_quantity': float(row.get('可用余额', 0)) if pd.notna(row.get('可用余额')) else 0,
                    'cost_price': float(row.get('成本价', 0)) if pd.notna(row.get('成本价')) else 0,
                    'current_price': float(row.get('最新价', 0)) if pd.notna(row.get('最新价')) else 0,
                    'market_value': float(row.get('最新市值', 0)) if pd.notna(row.get('最新市值')) else 0,
                    'profit_loss': float(row.get('浮动盈亏', 0)) if pd.notna(row.get('浮动盈亏')) else 0,
                    'profit_loss_ratio': float(row.get('盈亏比例', 0)) if pd.notna(row.get('盈亏比例')) else 0
                }
                
                # 只添加有效的持仓记录
                if holding['stock_code'] and holding['quantity'] > 0:
                    holdings_data.append(holding)
            
            print(f"   ✅ 处理完成: {len(holdings_data)} 条有效持仓记录")
            return holdings_data
            
        except Exception as e:
            print(f"   ❌ 处理失败: {e}")
            return []
    
    def process_orders_file(self, file_path):
        """处理委托数据文件"""
        print(f"\n📊 处理委托数据: {file_path}")
        
        try:
            df = pd.read_excel(file_path)
            
            print(f"   📋 原始数据: {len(df)} 行 x {len(df.columns)} 列")
            print(f"   📋 列名: {list(df.columns)}")
            
            orders_data = []
            for _, row in df.iterrows():
                order = {
                    'order_id': str(row.get('委托编号', '')),
                    'stock_code': str(row.get('证券代码', '')),
                    'stock_name': str(row.get('证券名称', '')),
                    'order_type': str(row.get('买卖方向', '')),
                    'order_price': float(row.get('委托价格', 0)) if pd.notna(row.get('委托价格')) else 0,
                    'order_quantity': int(row.get('委托数量', 0)) if pd.notna(row.get('委托数量')) else 0,
                    'filled_quantity': int(row.get('成交数量', 0)) if pd.notna(row.get('成交数量')) else 0,
                    'order_status': str(row.get('委托状态', '')),
                    'order_time': str(row.get('委托时间', '')),
                    'order_date': str(row.get('委托日期', ''))
                }
                
                if order['order_id'] and order['stock_code']:
                    orders_data.append(order)
            
            print(f"   ✅ 处理完成: {len(orders_data)} 条委托记录")
            return orders_data
            
        except Exception as e:
            print(f"   ❌ 处理失败: {e}")
            return []
    
    def process_transactions_file(self, file_path):
        """处理成交数据文件"""
        print(f"\n📊 处理成交数据: {file_path}")
        
        try:
            df = pd.read_excel(file_path)
            
            print(f"   📋 原始数据: {len(df)} 行 x {len(df.columns)} 列")
            print(f"   📋 列名: {list(df.columns)}")
            
            transactions_data = []
            for _, row in df.iterrows():
                transaction = {
                    'trade_id': str(row.get('成交编号', '')),
                    'stock_code': str(row.get('证券代码', '')),
                    'stock_name': str(row.get('证券名称', '')),
                    'trade_type': str(row.get('买卖方向', '')),
                    'trade_price': float(row.get('成交价格', 0)) if pd.notna(row.get('成交价格')) else 0,
                    'trade_quantity': int(row.get('成交数量', 0)) if pd.notna(row.get('成交数量')) else 0,
                    'trade_amount': float(row.get('成交金额', 0)) if pd.notna(row.get('成交金额')) else 0,
                    'commission': float(row.get('手续费', 0)) if pd.notna(row.get('手续费')) else 0,
                    'stamp_duty': float(row.get('印花税', 0)) if pd.notna(row.get('印花税')) else 0,
                    'trade_time': str(row.get('成交时间', '')),
                    'trade_date': str(row.get('成交日期', ''))
                }
                
                if transaction['trade_id'] and transaction['stock_code']:
                    transactions_data.append(transaction)
            
            print(f"   ✅ 处理完成: {len(transactions_data)} 条成交记录")
            return transactions_data
            
        except Exception as e:
            print(f"   ❌ 处理失败: {e}")
            return []
    
    def process_all_files(self, found_files):
        """处理所有找到的文件"""
        print("\n🔄 处理所有交易数据文件...")
        print("=" * 50)
        
        processed_data = {
            'holdings': [],
            'orders': [],
            'transactions': []
        }
        
        # 处理持仓文件
        if found_files.get('holdings'):
            file_path = found_files['holdings']['latest']
            processed_data['holdings'] = self.process_holdings_file(file_path)
        
        # 处理委托文件
        if found_files.get('orders'):
            file_path = found_files['orders']['latest']
            processed_data['orders'] = self.process_orders_file(file_path)
        
        # 处理成交文件
        if found_files.get('transactions'):
            file_path = found_files['transactions']['latest']
            processed_data['transactions'] = self.process_transactions_file(file_path)
        
        return processed_data
    
    def create_agent_analysis_data(self, processed_data):
        """创建Agent分析数据"""
        print("\n🤖 创建Agent分析数据...")
        print("=" * 50)
        
        holdings = processed_data.get('holdings', [])
        orders = processed_data.get('orders', [])
        transactions = processed_data.get('transactions', [])
        
        # 计算统计信息
        total_market_value = sum(h.get('market_value', 0) for h in holdings)
        total_profit_loss = sum(h.get('profit_loss', 0) for h in holdings)
        
        # 分析交易模式
        buy_orders = [o for o in orders if '买' in o.get('order_type', '')]
        sell_orders = [o for o in orders if '卖' in o.get('order_type', '')]
        
        agent_data = {
            "data_source": "网上交易5.0实盘数据",
            "analysis_time": datetime.now().isoformat(),
            "portfolio_summary": {
                "total_holdings": len(holdings),
                "total_market_value": total_market_value,
                "total_profit_loss": total_profit_loss,
                "profit_loss_ratio": (total_profit_loss / total_market_value * 100) if total_market_value > 0 else 0
            },
            "trading_activity": {
                "total_orders": len(orders),
                "buy_orders": len(buy_orders),
                "sell_orders": len(sell_orders),
                "total_transactions": len(transactions)
            },
            "holdings_detail": holdings,
            "recent_orders": orders[-10:] if orders else [],
            "recent_transactions": transactions[-10:] if transactions else []
        }
        
        print(f"   📊 持仓总数: {len(holdings)}")
        print(f"   💰 总市值: ¥{total_market_value:,.2f}")
        print(f"   📈 总盈亏: ¥{total_profit_loss:,.2f}")
        print(f"   📋 委托总数: {len(orders)}")
        print(f"   🔄 成交总数: {len(transactions)}")
        
        return agent_data
    
    def save_and_upload_data(self, agent_data):
        """保存并上传数据"""
        print("\n💾 保存并上传数据...")
        print("=" * 50)
        
        # 保存到本地文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"agent_analysis_data_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(agent_data, f, ensure_ascii=False, indent=2)
            print(f"✅ 数据已保存到: {filename}")
        except Exception as e:
            print(f"❌ 本地保存失败: {e}")
            return False
        
        # 尝试连接云端API
        try:
            response = requests.get(f"{self.cloud_api}/api/health", timeout=10)
            if response.status_code == 200:
                print("✅ 云端API连接正常")
                print("📤 数据已准备好供Agent系统分析")
                return True
            else:
                print(f"⚠️ 云端API状态异常: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 云端API连接失败: {e}")
            print("💡 数据已保存到本地,可稍后上传")
            return False
    
    def run_processing(self):
        """运行完整的处理流程"""
        print("🎯 处理现有交易数据文件")
        print("=" * 60)
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 1. 查找文件
        found_files = self.find_trading_files()
        
        # 检查是否找到文件
        has_files = any(found_files.values())
        if not has_files:
            print("\n❌ 未找到任何交易数据文件")
            print("💡 请确保在包含导出文件的目录中运行此脚本")
            return False
        
        # 2. 处理文件
        processed_data = self.process_all_files(found_files)
        
        # 3. 创建Agent分析数据
        agent_data = self.create_agent_analysis_data(processed_data)
        
        # 4. 保存并上传
        success = self.save_and_upload_data(agent_data)
        
        # 5. 生成报告
        self.generate_final_report(found_files, processed_data, success)
        
        return success
    
    def generate_final_report(self, found_files, processed_data, success):
        """生成最终报告"""
        print("\n📊 处理报告")
        print("=" * 50)
        
        print("📁 文件处理结果:")
        for data_type, file_info in found_files.items():
            if file_info:
                count = len(processed_data.get(data_type, []))
                print(f"   ✅ {data_type}: {file_info['count']} 个文件 → {count} 条记录")
            else:
                print(f"   ❌ {data_type}: 未找到文件")
        
        if success:
            print("\n🎉 数据处理完成!")
            print("✅ 真实交易数据已准备好供Agent分析")
            print("\n🤖 Agent可以分析:")
            print("   📈 持仓结构和风险分布")
            print("   💰 盈亏状况和绩效表现") 
            print("   🔄 交易行为和模式识别")
            print("   🎯 投资策略优化建议")
        else:
            print("\n⚠️ 数据处理遇到问题")
            print("💡 数据已保存到本地JSON文件")
        
        print(f"\n🕒 完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """主函数"""
    processor = TradingFileProcessor()
    processor.run_processing()

if __name__ == "__main__":
    main()
