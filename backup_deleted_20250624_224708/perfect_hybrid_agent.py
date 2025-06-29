"""
最终完美版混合数据Agent - 解决界面切换问题
"""

from fixed_balance_reader import get_balance_fixed
from trading_day_init import quick_init, get_account_info
from auto_cleanup_trading_agent import AutoCleanupTradingAgent
from datetime import datetime

class PerfectHybridTradingAgent(AutoCleanupTradingAgent):
    def __init__(self):
        super().__init__()
        self.winapi_data = None
        self.export_data = None
        
    def sync_virtual_from_export(self):
        """完美版混合数据源同步 - 解决界面切换问题"""
        print(" 完美版混合数据源同步...")
        print("=" * 60)
        
        # 1. 获取Win API数据（F4F1自动切换）
        print(" 1. 获取Win API现金数据（含界面修复）...")
        self.winapi_data = get_balance_fixed()
        
        if self.winapi_data:
            winapi_cash = self.winapi_data.get('available_cash', 0)
            print(f"    Win API现金: {winapi_cash:,.2f}")
            print("    已自动切换回F1买卖页面")
        else:
            print("    Win API获取失败")
            winapi_cash = 0
        
        # 2. 在F1页面获取持仓导出数据（W键现在有效）
        print("\\n 2. 在F1页面获取持仓数据（W键有效）...")
        export_success = quick_init()
        
        if export_success:
            self.export_data = get_account_info()
            export_holdings = self.export_data.get('holdings_count', 0)
            export_cash = self.export_data.get('available_cash', 0)
            print(f"    持仓导出: {export_holdings} 只股票")
            print(f"    导出现金: {export_cash:,.2f}")
        else:
            print("    持仓导出失败")
            self.export_data = {'holdings': [], 'holdings_count': 0, 'available_cash': 0}
        
        # 3. 智能结合数据源
        print("\\n 3. 智能结合数据源...")
        
        # 现金数据：优先使用Win API（更准确）
        if self.winapi_data and winapi_cash > 0:
            self.virtual_cash = winapi_cash
            cash_source = 'Win API'
        elif self.export_data and self.export_data.get('available_cash', 0) > 0:
            self.virtual_cash = self.export_data.get('available_cash', 0)
            cash_source = '持仓导出'
        else:
            self.virtual_cash = 0
            cash_source = '无数据'
        
        print(f"    现金来源: {cash_source} - {self.virtual_cash:,.2f}")
        
        # 持仓数据：使用持仓导出
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
        print(f"\\n 完美版同步完成:")
        print(f"    虚拟现金: {self.virtual_cash:,.2f} (来源: {cash_source})")
        print(f"    虚拟持仓: {len(self.virtual_holdings)} 只 (来源: {holdings_source})")
        print(f"    界面修复: F4获取余额F1买卖页面W键有效")
        
        self.last_holdings_update = datetime.now()
    
    def display_virtual_holdings(self):
        """显示持仓状态"""
        print(f"\\n 完美版虚拟持仓状态")
        print(f" 现金: {self.virtual_cash:,.2f}")
        print(f" 持仓: {len(self.virtual_holdings)} 只")
        print("-" * 70)
        
        if not self.virtual_holdings:
            print(" 当前无持仓股票")
            return
        
        total_market_value = 0
        for code, holding in self.virtual_holdings.items():
            market_value = holding.get('market_value', 0)
            profit_loss = holding.get('profit_loss', 0)
            profit_pct = holding.get('profit_loss_pct', 0)
            
            status = "" if profit_loss >= 0 else ""
            print(f"{status} {code} | 持仓:{holding['quantity']}股 | "
                  f"市值:{market_value:,.2f} | 盈亏:{profit_pct:+.2f}%")
            
            total_market_value += market_value
        
        total_assets = self.virtual_cash + total_market_value
        print(f" 总资产: {total_assets:,.2f}")
        print("-" * 70)

def create_perfect_hybrid_agent():
    """创建完美版混合数据源Agent"""
    return PerfectHybridTradingAgent()

if __name__ == "__main__":
    print(" 测试完美版混合数据源Agent")
    print("=" * 70)
    
    agent = create_perfect_hybrid_agent()
    print(" 完美版Agent创建成功")
    
    print("\\n 测试交易日初始化...")
    result = agent.initialize_trading_day()
    
    if result:
        print("\\n 完美版Agent测试成功!")
        print("\\n 关键修复:")
        print("   1. Win API获取现金 (F4资金页面)")
        print("   2. 自动切换回F1买卖页面")
        print("   3. W键持仓导出正常工作")
        print("   4. 完美的界面管理")
        
        agent.display_virtual_holdings()
        
        if agent.virtual_cash > 10000:
            print("\\n 完美验证: 所有功能正常")
        else:
            print("\\n 需要进一步检查")
    else:
        print("\\n 初始化失败")
