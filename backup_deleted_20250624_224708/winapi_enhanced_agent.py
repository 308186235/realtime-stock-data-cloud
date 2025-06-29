"""
集成Win API余额获取的增强交易系统
"""

from final_balance_reader import get_balance_winapi
from auto_cleanup_trading_agent import AutoCleanupTradingAgent
from datetime import datetime
import time

class WinAPIEnhancedTradingAgent(AutoCleanupTradingAgent):
    def __init__(self):
        super().__init__()
        self.winapi_balance_enabled = True
        
    def get_account_balance_via_winapi(self):
        """使用Win API获取账户余额"""
        if not self.winapi_balance_enabled:
            return None
            
        try:
            print(" 使用Win API获取账户余额...")
            balance = get_balance_winapi()
            
            if balance and balance.get('available_cash', 0) > 0:
                print(" Win API余额获取成功")
                return balance
            else:
                print(" Win API余额获取失败，使用备用方法")
                return None
                
        except Exception as e:
            print(f" Win API余额获取异常: {e}")
            return None
    
    def sync_virtual_from_export(self):
        """增强版虚拟持仓同步 - 优先使用Win API"""
        print(" 增强版虚拟持仓同步...")
        
        # 1. 首先尝试Win API获取余额
        winapi_balance = self.get_account_balance_via_winapi()
        
        if winapi_balance:
            # 使用Win API数据更新虚拟现金
            self.virtual_cash = winapi_balance.get('available_cash', 0)
            print(f" Win API更新虚拟现金: {self.virtual_cash:,.2f}")
            
            # 仍然需要导出持仓获取股票信息
            print(" 导出持仓获取股票信息...")
            success = quick_init()
            if success:
                self.account_data = get_account_info()
                
                # 更新虚拟持仓（股票部分）
                self.virtual_holdings = {}
                for holding in self.account_data.get('holdings', []):
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
                            'data_source': 'Win API + 持仓导出'
                        }
                
                # 清理导出文件
                self.cleanup_used_export_files()
                
                print(f" 混合模式同步完成: 现金(Win API) + 持仓(导出)")
                print(f" 虚拟现金: {self.virtual_cash:,.2f}")
                print(f" 虚拟持仓: {len(self.virtual_holdings)} 只")
                
            else:
                print(" 持仓导出失败，仅使用Win API现金数据")
        else:
            # Win API失败，使用原始方法
            print(" Win API失败，使用原始持仓导出方法...")
            super().sync_virtual_from_export()
    
    def display_virtual_holdings(self):
        """增强版持仓显示"""
        if not self.virtual_holdings:
            print(f"\\n 账户状态 (现金: {self.virtual_cash:,.2f})")
            print(" 当前无持仓")
            return
            
        print(f"\\n 虚拟持仓状态 (现金: {self.virtual_cash:,.2f})")
        print("-" * 80)
        
        total_market_value = 0
        for code, holding in self.virtual_holdings.items():
            market_value = holding.get('market_value', 0)
            profit_loss = holding.get('profit_loss', 0)
            profit_pct = holding.get('profit_loss_pct', 0)
            sync_time = holding.get('last_sync_time', '')
            data_source = holding.get('data_source', '')
            
            status = "" if profit_loss >= 0 else ""
            print(f"{status} {code} | 持仓:{holding['quantity']}股 | "
                  f"市值:{market_value:,.2f} | 盈亏:{profit_pct:+.2f}% | {sync_time}")
            
            total_market_value += market_value
        
        total_assets = self.virtual_cash + total_market_value
        print(f" 总资产: {total_assets:,.2f} (Win API增强)")
        print("-" * 80)

# 便捷接口
def create_winapi_enhanced_agent():
    """创建Win API增强版交易Agent"""
    return WinAPIEnhancedTradingAgent()

# 测试函数
if __name__ == "__main__":
    print(" 测试Win API增强版交易Agent")
    print("=" * 60)
    
    # 创建增强版Agent
    agent = create_winapi_enhanced_agent()
    print(" Win API增强版Agent创建成功")
    
    # 测试初始化
    print("\\n 测试交易日初始化...")
    result = agent.initialize_trading_day()
    
    if result:
        print("\\n Win API增强版Agent测试成功!")
        print(f" 虚拟现金: {agent.virtual_cash:,.2f}")
        print(f" 虚拟持仓: {len(agent.virtual_holdings)} 只")
        
        # 显示持仓状态
        agent.display_virtual_holdings()
    else:
        print("\\n 初始化失败")
