"""
智能交易Agent - 整合交易日初始化和实时股票数据
"""

from trading_day_init import quick_init, get_account_info
from stock_data_receiver import start_stock_service, get_stock_data
from trader_api_real import api
import time
import json

class SmartTradingAgent:
    def __init__(self):
        self.account_data = {}
        self.stock_data = {}
        self.trading_active = False
        
    def initialize_trading_day(self):
        """交易日初始化"""
        print(" 智能交易Agent - 交易日初始化")
        print("=" * 50)
        
        # 1. 导出持仓数据获取账户信息
        success = quick_init()
        if success:
            self.account_data = get_account_info()
            print(f" 账户信息获取成功")
            print(f"   可用资金: {self.account_data['available_cash']:,.2f}")
            print(f"   持仓股票: {self.account_data['holdings_count']} 只")
            return True
        else:
            print(" 账户信息获取失败")
            return False
    
    def start_stock_data_feed(self, host, port, token):
        """启动股票数据推送"""
        print(f"\n 启动股票数据推送服务...")
        print(f"   服务器: {host}:{port}")
        
        try:
            thread = start_stock_service(host, port, token)
            print(" 股票数据服务启动成功")
            return True
        except Exception as e:
            print(f" 股票数据服务启动失败: {e}")
            return False
    
    def analyze_and_trade(self):
        """分析股票数据并执行交易"""
        print(f"\n 开始智能交易分析...")
        
        while self.trading_active:
            # 获取最新股票数据
            latest_stocks = get_stock_data()
            
            if latest_stocks:
                print(f" 监控 {len(latest_stocks)} 只股票")
                
                # 简单的交易策略示例
                for code, stock_info in latest_stocks.items():
                    self.check_trading_opportunity(code, stock_info)
            
            time.sleep(5)  # 每5秒分析一次
    
    def check_trading_opportunity(self, code, stock_info):
        """检查交易机会"""
        change_pct = stock_info.get('change_pct', 0)
        price = stock_info.get('last_price', 0)
        
        # 示例策略：大跌时买入，大涨时卖出
        if change_pct < -5:  # 跌超5%
            print(f" 发现买入机会: {code} 跌幅 {change_pct:.2f}%")
            self.consider_buy(code, stock_info)
        elif change_pct > 5:  # 涨超5%
            print(f" 发现卖出机会: {code} 涨幅 {change_pct:.2f}%")
            self.consider_sell(code, stock_info)
    
    def consider_buy(self, code, stock_info):
        """考虑买入"""
        available_cash = self.account_data.get('available_cash', 0)
        price = stock_info.get('last_price', 0)
        
        if available_cash > 10000 and price > 0:  # 有足够资金
            quantity = int(10000 / price / 100) * 100  # 买入1万元，整百股
            if quantity >= 100:
                print(f" 准备买入: {code} 数量: {quantity}股 价格: {price:.2f}")
                # 这里可以调用实际买入
                # result = api.buy(code, quantity, price)
                print(f"   (模拟买入，实际交易请取消注释)")
    
    def consider_sell(self, code, stock_info):
        """考虑卖出"""
        # 检查是否持有该股票
        holdings = self.account_data.get('holdings', [])
        for holding in holdings:
            if holding.get('code') == code:
                available_qty = holding.get('available_quantity', 0)
                price = stock_info.get('last_price', 0)
                
                if available_qty >= 100:
                    print(f" 准备卖出: {code} 数量: {available_qty}股 价格: {price:.2f}")
                    # 这里可以调用实际卖出
                    # result = api.sell(code, available_qty, price)
                    print(f"   (模拟卖出，实际交易请取消注释)")
                break
    
    def start_trading(self, host, port, token):
        """启动完整的交易流程"""
        print(" 启动智能交易Agent")
        print("=" * 60)
        
        # 1. 交易日初始化
        if not self.initialize_trading_day():
            return False
        
        # 2. 启动股票数据推送
        if not self.start_stock_data_feed(host, port, token):
            return False
        
        # 3. 等待数据接收
        print("\n 等待股票数据...")
        time.sleep(3)
        
        # 4. 开始交易分析
        self.trading_active = True
        print("\n 开始智能交易...")
        
        try:
            self.analyze_and_trade()
        except KeyboardInterrupt:
            print("\n 用户停止交易")
        finally:
            self.trading_active = False
            print(" 交易Agent已停止")
        
        return True

# 使用示例
def main():
    agent = SmartTradingAgent()
    
    # 配置股票数据服务器信息
    HOST = ''      # 填入实际服务器地址
    PORT = 0       # 填入实际端口
    TOKEN = ''     # 填入实际token
    
    if HOST and PORT and TOKEN:
        agent.start_trading(HOST, PORT, TOKEN)
    else:
        print(" 请先配置股票数据服务器信息")
        print("在代码中填入 HOST, PORT, TOKEN 参数")

if __name__ == "__main__":
    main()
