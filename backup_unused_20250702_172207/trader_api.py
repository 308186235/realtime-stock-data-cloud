"""
交易程序API接口
为Agent提供简单易用的交易和导出接口
"""

from trader_buy_sell import buy_stock, sell_stock, quick_buy, quick_sell
from trader_export_original import export_holdings, export_transactions, export_orders
from trader_export import export_all_data, get_export_files
from trader_core import cleanup_old_export_files, get_current_focus

class TraderAPI:
    """交易API类"""
    
    def __init__(self):
        """初始化交易API"""
        self.name = "TraderAPI"
        self.version = "1.0"
    
    # ==================== 交易功能 ====================
    
    def buy(self, code, quantity, price="市价"):
        """
        买入股票
        
        Args:
            code (str): 股票代码,如 "000001"
            quantity (str|int): 买入数量,如 "100" 或 100
            price (str): 买入价格,如 "10.50" 或 "市价"
        
        Returns:
            bool: 操作是否成功
        
        Example:
            api.buy("000001", "100", "10.50")  # 以10.50价格买入000001股票100股
            api.buy("600000", 200)  # 市价买入600000股票200股
        """
        return buy_stock(str(code), str(price), str(quantity))
    
    def sell(self, code, quantity, price="市价"):
        """
        卖出股票
        
        Args:
            code (str): 股票代码,如 "000001"
            quantity (str|int): 卖出数量,如 "100" 或 100
            price (str): 卖出价格,如 "10.60" 或 "市价"
        
        Returns:
            bool: 操作是否成功
        
        Example:
            api.sell("000001", "100", "10.60")  # 以10.60价格卖出000001股票100股
            api.sell("600000", 200)  # 市价卖出600000股票200股
        """
        return sell_stock(str(code), str(price), str(quantity))
    
    # ==================== 导出功能 ====================
    
    def export_positions(self):
        """
        导出持仓数据
        
        Returns:
            bool: 操作是否成功
        """
        return export_holdings()
    
    def export_trades(self):
        """
        导出成交数据
        
        Returns:
            bool: 操作是否成功
        """
        return export_transactions()
    
    def export_orders(self):
        """
        导出委托数据
        
        Returns:
            bool: 操作是否成功
        """
        return export_orders()
    
    def export_all(self):
        """
        导出所有数据(持仓,成交,委托)
        
        Returns:
            dict: 各项导出结果
            {
                "holdings": bool,
                "transactions": bool, 
                "orders": bool
            }
        """
        return export_all_data()
    
    # ==================== 文件管理 ====================
    
    def get_files(self):
        """
        获取导出文件列表
        
        Returns:
            dict: 按类型分组的文件列表
            {
                "holdings": [文件列表],
                "transactions": [文件列表],
                "orders": [文件列表]
            }
        """
        return get_export_files()
    
    def cleanup_files(self):
        """
        清理过期文件(15点后过期)
        
        Returns:
            None
        """
        cleanup_old_export_files()
    
    # ==================== 状态查询 ====================
    
    def get_status(self):
        """
        获取当前状态
        
        Returns:
            dict: 状态信息
        """
        hwnd, title = get_current_focus()
        files = self.get_files()
        
        return {
            "current_window": title,
            "trading_software_active": "交易" in title or "股票" in title,
            "export_files": {
                "holdings_count": len(files["holdings"]),
                "transactions_count": len(files["transactions"]),
                "orders_count": len(files["orders"])
            }
        }
    
    # ==================== 批量操作 ====================
    
    def batch_trade(self, trades):
        """
        批量交易
        
        Args:
            trades (list): 交易列表
            [
                {"action": "buy", "code": "000001", "quantity": "100", "price": "10.50"},
                {"action": "sell", "code": "600000", "quantity": "200", "price": "市价"}
            ]
        
        Returns:
            list: 每个交易的结果
        """
        results = []
        
        for trade in trades:
            action = trade.get("action", "").lower()
            code = trade.get("code", "")
            quantity = trade.get("quantity", "")
            price = trade.get("price", "市价")
            
            if action == "buy":
                result = self.buy(code, quantity, price)
            elif action == "sell":
                result = self.sell(code, quantity, price)
            else:
                result = False
                print(f"❌ 未知操作: {action}")
            
            results.append({
                "trade": trade,
                "success": result
            })
        
        return results

# 创建全局API实例
api = TraderAPI()

# 便捷函数(向后兼容)
def trader_buy(code, quantity, price="市价"):
    """便捷买入函数"""
    return api.buy(code, quantity, price)

def trader_sell(code, quantity, price="市价"):
    """便捷卖出函数"""
    return api.sell(code, quantity, price)

def trader_export_all():
    """便捷导出所有数据函数"""
    return api.export_all()

# 测试函数
if __name__ == "__main__":
    print("🧪 测试交易API")
    
    # 测试API实例
    print(f"\nAPI版本: {api.version}")
    
    # 测试状态查询
    print("\n=== 状态查询 ===")
    status = api.get_status()
    print(f"当前窗口: {status['current_window']}")
    print(f"交易软件激活: {status['trading_software_active']}")
    print(f"导出文件数量: {status['export_files']}")
    
    # 测试文件列表
    print("\n=== 文件列表 ===")
    files = api.get_files()
    for file_type, file_list in files.items():
        print(f"{file_type}: {len(file_list)} 个文件")
    
    # 测试批量交易(仅演示,不实际执行)
    print("\n=== 批量交易示例 ===")
    sample_trades = [
        {"action": "buy", "code": "000001", "quantity": "100", "price": "10.50"},
        {"action": "sell", "code": "600000", "quantity": "200", "price": "市价"}
    ]
    print("示例交易列表:")
    for trade in sample_trades:
        print(f"  {trade}")
    
    print("\n✅ API测试完成")
