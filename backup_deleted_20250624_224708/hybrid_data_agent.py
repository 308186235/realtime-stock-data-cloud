"""
真正结合Win API和持仓导出的增强Agent
"""

from final_balance_reader import get_balance_winapi
from trading_day_init import quick_init, get_account_info
from auto_cleanup_trading_agent import AutoCleanupTradingAgent
from datetime import datetime

class HybridDataTradingAgent(AutoCleanupTradingAgent):
    def __init__(self):
        super().__init__()
        self.winapi_data = None
        self.export_data = None
        
    def sync_virtual_from_export(self):
        """真正结合Win API和持仓导出的数据同步"""
        print(" 混合数据源同步虚拟持仓...")
        print("=" * 50)
        
        # 1. 获取Win API数据（准确的现金余额）
        print(" 1. 获取Win API现金数据...")
        self.winapi_data = get_balance_winapi()
        
        if self.winapi_data:
            winapi_cash = self.winapi_data.get('available_cash', 0)
            print(f"    Win API现金: {winapi_cash:,.2f}")
        else:
            print("    Win API获取失败")
            winapi_cash = 0
        
        # 2. 获取持仓导出数据（股票信息）
        print("\\n 2. 获取持仓导出股票数据...")
        export_success = quick_init()
        
        if export_success:
            self.export_data = get_account_info()
            export_holdings = self.export_data.get('holdings_count', 0)
            print(f"    持仓导出: {export_holdings} 只股票")
        else:
            print("    持仓导出失败")
            self.export_data = {'holdings': [], 'holdings_count': 0, 'available_cash': 0}
        
        # 3. 结合数据源更新虚拟持仓
        print("\\n 3. 结合数据源更新虚拟持仓...")
        
        # 使用Win API的现金数据（更准确）
        if self.winapi_data and winapi_cash > 0:
            self.virtual_cash = winapi_cash
            cash_source = 'Win API'
            print(f"    现金来源: {cash_source} - {self.virtual_cash:,.2f}")
        else:
            # 备用：使用持仓导出的现金数据
            self.virtual_cash = self.export_data.get('available_cash', 0)
            cash_source = '持仓导出'
            print(f"    现金来源: {cash_source} - {self.virtual_cash:,.2f}")
        
        # 使用持仓导出的股票数据
        self.virtual_holdings = {}
        holdings_source = '持仓导出'
        
        for holding in self.export_data.get('holdings', []):
            code = holding.get('code', '')
            if code:
                self.virtual_holdings[code] = {
                    'quantity': holding.get('quantity', 0),
                    'available_quantity': holding.get('available_quantity', 0),
                    'cost_price': holding.get('cost_price', 0),
                    'current_price': holding.get('current_price', 0),
                    'market_value': holding.get('market_value', 0),
                    'profit_loss': holding.get('profit_loss', 0),
                    'last_sync_time': datetime.now().strftime('%H:%M:%S'),
                    'data_source': f'{cash_source} + {holdings_source}'
                }
        
        print(f"    股票来源: {holdings_source} - {len(self.virtual_holdings)} 只")
        
        # 4. 清理导出文件
        self.cleanup_used_export_files()
        
        # 5. 显示最终结果
        print(f"\\n 混合数据源同步完成:")
        print(f"    虚拟现金: {self.virtual_cash:,.2f} (来源: {cash_source})")
        print(f"    虚拟持仓: {len(self.virtual_holdings)} 只 (来源: {holdings_source})")
        print(f"    数据源: Win API现金 + 持仓导出股票")
        
        self.last_holdings_update = datetime.now()
    
    def get_data_source_info(self):
        """获取数据源信息"""
        info = {
            'cash_source': 'Win API' if self.winapi_data else '持仓导出',
            'holdings_source': '持仓导出',
            'winapi_available': bool(self.winapi_data),
            'export_available': bool(self.export_data),
            'cash_amount': self.virtual_cash,
            'holdings_count': len(self.virtual_holdings)
        }
        return info
    
    def display_virtual_holdings(self):
        """增强版持仓显示 - 显示数据源"""
        data_info = self.get_data_source_info()
        
        print(f"\\n 混合数据源虚拟持仓状态")
        print(f" 现金: {self.virtual_cash:,.2f} (来源: {data_info['cash_source']})")
        print(f" 持仓: {len(self.virtual_holdings)} 只 (来源: {data_info['holdings_source']})")
        print("-" * 70)
        
        if not self.virtual_holdings:
            print(" 当前无持仓股票")
            return
        
        total_market_value = 0
        for code, holding in self.virtual_holdings.items():
            market_value = holding.get('market_value', 0)
            profit_loss = holding.get('profit_loss', 0)
            profit_pct = holding.get('profit_loss_pct', 0)
            sync_time = holding.get('last_sync_time', '')
            
            status = "" if profit_loss >= 0 else ""
            print(f"{status} {code} | 持仓:{holding['quantity']}股 | "
                  f"市值:{market_value:,.2f} | 盈亏:{profit_pct:+.2f}% | {sync_time}")
            
            total_market_value += market_value
        
        total_assets = self.virtual_cash + total_market_value
        print(f" 总资产: {total_assets:,.2f} (混合数据源)")
        print("-" * 70)

# 便捷接口
def create_hybrid_agent():
    """创建混合数据源Agent"""
    return HybridDataTradingAgent()

# 测试函数
if __name__ == "__main__":
    print(" 测试混合数据源交易Agent")
    print("=" * 60)
    
    # 创建混合Agent
    agent = create_hybrid_agent()
    print(" 混合数据源Agent创建成功")
    
    # 测试初始化
    print("\\n 测试交易日初始化...")
    result = agent.initialize_trading_day()
    
    if result:
        print("\\n 混合数据源Agent测试成功!")
        
        # 显示数据源信息
        data_info = agent.get_data_source_info()
        print(f"\\n 数据源详情:")
        print(f"   现金数据源: {data_info['cash_source']}")
        print(f"   持仓数据源: {data_info['holdings_source']}")
        print(f"   Win API可用: {'' if data_info['winapi_available'] else ''}")
        print(f"   持仓导出可用: {'' if data_info['export_available'] else ''}")
        print(f"   现金金额: {data_info['cash_amount']:,.2f}")
        print(f"   持仓数量: {data_info['holdings_count']} 只")
        
        # 显示持仓状态
        agent.display_virtual_holdings()
        
        # 验证数据准确性
        print(f"\\n 数据准确性验证:")
        if data_info['winapi_available'] and data_info['cash_amount'] > 10000:
            print("    Win API现金数据获取成功且合理")
        else:
            print("    Win API现金数据可能有问题")
            
        if data_info['export_available']:
            print("    持仓导出数据获取成功")
        else:
            print("    持仓导出数据获取失败")
    else:
        print("\\n 初始化失败")
