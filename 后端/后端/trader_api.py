from validation_utils import ValidationError, validate_trade_data, InputValidator
"""
交易API统一接口
为Agent提供简单易用的交易和导出接口
"""

import time
from datetime import datetime
from trader_buy_sell import buy_stock, sell_stock, quick_buy, quick_sell
from trader_export import export_holdings, export_transactions, export_orders, export_all_data
from trader_core import cleanup_old_export_files, get_current_focus

class TraderAPI:
    """交易API统一接口类"""
    
    def __init__(self):
        self.version = "1.0.0"
        self.last_operation = None
        self.operation_count = 0
        
    def get_status(self):
        """获取交易系统状态"""
        hwnd, current_title = get_current_focus()
        trading_software_active = "交易" in current_title or "股票" in current_title
        
        return {
            "version": self.version,
            "current_window": current_title,
            "window_handle": hwnd,
            "trading_software_active": trading_software_active,
            "last_operation": self.last_operation,
            "operation_count": self.operation_count,
            "timestamp": datetime.now().isoformat()
        }
    
    def buy(self, code, quantity, price=None):
        """买入股票
        
        Args:
            code: 股票代码
            quantity: 数量
            price: 价格(可选,不提供则市价买入)
        
        Returns:
            bool: 操作是否成功
        """
        try:
            # 输入验证
            trade_data = {'code': code, 'quantity': quantity}
            if price is not None:
                trade_data['price'] = price
            
            validated_data = validate_trade_data(trade_data)
            
            # 使用验证后的数据
            validated_code = validated_data['code']
            validated_quantity = validated_data['quantity']
            validated_price = validated_data.get('price')
            
            if validated_price is None:
                result = quick_buy(validated_code, validated_quantity)
            else:
                result = buy_stock(validated_code, float(validated_price), validated_quantity)
            
            self.last_operation = f"买入 {validated_code} {validated_quantity}股"
            if result:
                self.operation_count += 1
            
            return result
        except ValidationError as e:
            print(f"❌ 买入参数验证失败: {e}")
            return False
        except Exception as e:
            print(f"❌ 买入操作失败: {e}")
            return False
    
    def sell(self, code, quantity, price=None):
        """卖出股票
        
        Args:
            code: 股票代码
            quantity: 数量
            price: 价格(可选,不提供则市价卖出)
        
        Returns:
            bool: 操作是否成功
        """
        try:
            if price is None:
                result = quick_sell(code, quantity)
            else:
                result = sell_stock(code, price, quantity)
            
            self.last_operation = f"卖出 {code} {quantity}股"
            if result:
                self.operation_count += 1
            
            return result
        except Exception as e:
            print(f"❌ 卖出操作失败: {e}")
            return False
    
    def export_data(self, data_type="all"):
        """导出数据

        Args:
            data_type: 数据类型 ("holdings", "transactions", "orders", "all")

        Returns:
            dict: 导出结果
        """
        try:
            if data_type == "holdings":
                result = {"holdings": export_holdings()}
            elif data_type == "transactions":
                result = {"transactions": export_transactions()}
            elif data_type == "orders":
                result = {"orders": export_orders()}
            elif data_type == "all":
                result = export_all_data()
            else:
                print(f"❌ 不支持的数据类型: {data_type}")
                return {"error": f"不支持的数据类型: {data_type}"}

            self.last_operation = f"导出数据 {data_type}"
            self.operation_count += 1

            return result
        except Exception as e:
            print(f"❌ 导出数据失败: {e}")
            return {"error": f"导出数据失败: {e}"}

    def export_all(self, data_type="all"):
        """导出所有数据 - 兼容性方法"""
        return self.export_data(data_type)
    
    def cleanup_files(self):
        """清理过期文件"""
        try:
            cleanup_old_export_files()
            self.last_operation = "清理过期文件"
            return True
        except Exception as e:
            print(f"❌ 清理文件失败: {e}")
            return False
    
    def get_portfolio(self):
        """获取投资组合(通过导出持仓数据)"""
        try:
            result = export_holdings()
            if result:
                self.last_operation = "获取投资组合"
                return {
                    "success": True,
                    "message": "投资组合数据已导出",
                    "export_result": result
                }
            else:
                return {
                    "success": False,
                    "message": "投资组合数据导出失败"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"获取投资组合失败: {e}"
            }
    
    def get_balance(self):
        """获取账户余额(需要切换到资金页面)"""
        try:
            # 这里可以添加获取余额的逻辑
            # 目前返回模拟数据
            return {
                "success": True,
                "balance": {
                    "total_assets": 100000.00,
                    "available_cash": 50000.00,
                    "market_value": 50000.00,
                    "frozen_cash": 0.00
                },
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"获取余额失败: {e}"
            }

# 创建全局API实例
api = TraderAPI()

# 便捷函数
def get_trader_api():
    """获取交易API实例"""
    return api

def test_trader_api():
    """测试交易API"""
    print("🧪 交易API测试")
    print("=" * 50)
    
    # 测试状态获取
    status = api.get_status()
    print(f"✅ 状态获取: {status}")
    
    # 测试余额获取
    balance = api.get_balance()
    print(f"✅ 余额获取: {balance}")
    
    print("✅ 交易API测试完成")

if __name__ == "__main__":
    test_trader_api()
