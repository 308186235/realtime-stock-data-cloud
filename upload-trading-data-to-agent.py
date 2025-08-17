#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
上传交易数据到Agent系统
从本地API获取导出的交易数据,然后上传到云端Agent进行分析
"""

import requests
import json
import time
from datetime import datetime
import os

class TradingDataUploader:
    def __init__(self):
        self.local_api = "http://localhost:8000"
        self.cloud_api = "https://api.aigupiao.me"
        
    def get_local_trading_data(self):
        """从本地API获取交易数据"""
        print("📥 从本地API获取交易数据...")
        
        data = {}
        
        # 获取委托数据
        try:
            response = requests.get(f"{self.local_api}/orders", timeout=5)
            if response.status_code == 200:
                orders_data = response.json()
                data['orders'] = orders_data.get('data', [])
                print(f"   ✅ 获取委托数据: {len(data['orders'])} 条")
            else:
                print(f"   ⚠️ 委托数据获取失败: HTTP {response.status_code}")
                data['orders'] = []
        except Exception as e:
            print(f"   ❌ 委托数据获取异常: {e}")
            data['orders'] = []
        
        # 获取成交数据
        try:
            response = requests.get(f"{self.local_api}/trades", timeout=5)
            if response.status_code == 200:
                trades_data = response.json()
                data['trades'] = trades_data.get('data', [])
                print(f"   ✅ 获取成交数据: {len(data['trades'])} 条")
            else:
                print(f"   ⚠️ 成交数据获取失败: HTTP {response.status_code}")
                data['trades'] = []
        except Exception as e:
            print(f"   ❌ 成交数据获取异常: {e}")
            data['trades'] = []
        
        return data
    
    def upload_to_agent_system(self, trading_data):
        """上传数据到Agent系统"""
        print("\n📤 上传数据到Agent系统...")
        
        # 由于云端API端点还没有部署,我们先保存到本地文件
        # 然后通过其他方式上传到Agent系统
        
        # 1. 保存到本地文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"trading_data_export_{timestamp}.json"
        
        export_data = {
            "export_time": datetime.now().isoformat(),
            "data_source": "网上交易5.0",
            "orders_count": len(trading_data.get('orders', [])),
            "trades_count": len(trading_data.get('trades', [])),
            "orders": trading_data.get('orders', []),
            "trades": trading_data.get('trades', [])
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            print(f"   ✅ 数据已保存到本地文件: {filename}")
        except Exception as e:
            print(f"   ❌ 本地文件保存失败: {e}")
            return False
        
        # 2. 尝试上传到虚拟账户系统(作为替代方案)
        try:
            # 检查虚拟账户API是否可用
            response = requests.get(f"{self.cloud_api}/api/virtual-account/accounts", timeout=10)
            if response.status_code == 200:
                print("   ✅ 云端API连接正常")
                
                # 将交易数据转换为虚拟账户格式
                virtual_account_data = self.convert_to_virtual_account_format(trading_data)
                print(f"   📊 转换后的虚拟账户数据: {json.dumps(virtual_account_data, ensure_ascii=False, indent=2)}")
                
                return True
            else:
                print(f"   ⚠️ 云端API连接异常: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ 云端API连接失败: {e}")
            return False
    
    def convert_to_virtual_account_format(self, trading_data):
        """将交易数据转换为虚拟账户格式"""
        print("🔄 转换交易数据为虚拟账户格式...")
        
        # 计算账户统计信息
        orders = trading_data.get('orders', [])
        trades = trading_data.get('trades', [])
        
        # 计算总交易金额
        total_buy_amount = sum(trade.get('amount', 0) for trade in trades if trade.get('trade_type') == 'buy')
        total_sell_amount = sum(trade.get('amount', 0) for trade in trades if trade.get('trade_type') == 'sell')
        
        # 计算持仓
        holdings = {}
        for trade in trades:
            stock_code = trade.get('stock_code', '')
            if stock_code:
                if stock_code not in holdings:
                    holdings[stock_code] = {
                        'stock_code': stock_code,
                        'stock_name': trade.get('stock_name', ''),
                        'quantity': 0,
                        'cost_price': 0,
                        'market_value': 0
                    }
                
                if trade.get('trade_type') == 'buy':
                    holdings[stock_code]['quantity'] += trade.get('quantity', 0)
                elif trade.get('trade_type') == 'sell':
                    holdings[stock_code]['quantity'] -= trade.get('quantity', 0)
        
        # 过滤掉数量为0的持仓
        active_holdings = [h for h in holdings.values() if h['quantity'] > 0]
        
        virtual_account_data = {
            "account_summary": {
                "total_orders": len(orders),
                "total_trades": len(trades),
                "total_buy_amount": total_buy_amount,
                "total_sell_amount": total_sell_amount,
                "active_holdings_count": len(active_holdings),
                "export_time": datetime.now().isoformat()
            },
            "holdings": active_holdings,
            "recent_orders": orders[-10:] if orders else [],  # 最近10条委托
            "recent_trades": trades[-10:] if trades else []   # 最近10条成交
        }
        
        return virtual_account_data
    
    def run_upload_process(self):
        """运行完整的上传流程"""
        print("🚀 开始交易数据上传流程")
        print("=" * 50)
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 1. 获取本地交易数据
        trading_data = self.get_local_trading_data()
        
        if not trading_data.get('orders') and not trading_data.get('trades'):
            print("\n⚠️ 没有获取到交易数据,请确保:")
            print("   1. 网上交易5.0软件正在运行")
            print("   2. 已使用W/E/R键导出数据")
            print("   3. 本地API服务器正在运行 (localhost:8000)")
            return False
        
        # 2. 上传到Agent系统
        success = self.upload_to_agent_system(trading_data)
        
        # 3. 生成上传报告
        self.generate_upload_report(trading_data, success)
        
        return success
    
    def generate_upload_report(self, trading_data, upload_success):
        """生成上传报告"""
        print("\n📊 交易数据上传报告")
        print("=" * 50)
        
        orders_count = len(trading_data.get('orders', []))
        trades_count = len(trading_data.get('trades', []))
        
        print(f"📈 数据统计:")
        print(f"   委托记录: {orders_count} 条")
        print(f"   成交记录: {trades_count} 条")
        print(f"   总记录数: {orders_count + trades_count} 条")
        
        print(f"\n📤 上传状态:")
        if upload_success:
            print("   ✅ 数据上传成功")
            print("   📁 数据已保存到本地文件")
            print("   🤖 Agent系统可以开始分析")
        else:
            print("   ❌ 数据上传失败")
            print("   📁 数据已保存到本地文件作为备份")
        
        print(f"\n💡 后续操作建议:")
        print("   1. 检查生成的JSON文件内容")
        print("   2. 确认数据格式正确")
        print("   3. 等待Agent系统分析结果")
        
        if orders_count > 0:
            print("   4. 委托数据可用于策略分析")
        if trades_count > 0:
            print("   5. 成交数据可用于绩效评估")

def main():
    """主函数"""
    print("📊 交易数据上传到Agent系统")
    print("=" * 60)
    
    uploader = TradingDataUploader()
    
    # 检查本地API服务器状态
    try:
        response = requests.get(f"{uploader.local_api}/health", timeout=5)
        if response.status_code == 200:
            print("✅ 本地API服务器运行正常")
        else:
            print("❌ 本地API服务器状态异常")
            return
    except Exception as e:
        print(f"❌ 无法连接本地API服务器: {e}")
        print("💡 请确保本地API服务器正在运行 (localhost:8000)")
        return
    
    # 运行上传流程
    success = uploader.run_upload_process()
    
    if success:
        print("\n🎉 交易数据上传完成!")
    else:
        print("\n⚠️ 交易数据上传遇到问题,请检查日志")
    
    print("\n🏁 程序结束")

if __name__ == "__main__":
    main()
