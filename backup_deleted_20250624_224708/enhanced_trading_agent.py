"""
增强版智能交易Agent
- 3秒股市数据刷新
- 交易优先，持仓导出次要
- 动态计算盈亏，无需等待持仓导出
- 实时更新虚拟持仓状态
"""

from trading_day_init import quick_init, get_account_info
from stock_data_receiver import start_stock_service, get_stock_data
from trader_api_real import api
import time
import threading
from datetime import datetime

class EnhancedTradingAgent:
    def __init__(self):
        # 基础账户信息
        self.account_data = {}
        
        # 虚拟持仓状态（实时计算）
        self.virtual_holdings = {}  # {股票代码: {quantity, cost_price, market_value, profit_loss}}
        self.virtual_cash = 0.0
        
        # 交易状态
        self.trading_active = False
        self.trade_lock = threading.Lock()  # 交易锁
        
        # 持仓更新
        self.last_holdings_update = None
        self.holdings_update_interval = 30  # 30秒更新一次持仓
        
        # 数据刷新
        self.data_refresh_interval = 3  # 3秒刷新股市数据
        
    def initialize_trading_day(self):
        """交易日初始化"""
        print(" 增强版智能交易Agent - 交易日初始化")
        print("=" * 60)
        
        # 导出持仓数据获取账户信息
        success = quick_init()
        if success:
            self.account_data = get_account_info()
            self.sync_virtual_holdings()
            print(f" 账户信息获取成功")
            print(f"   可用资金: {self.virtual_cash:,.2f}")
            print(f"   持仓股票: {len(self.virtual_holdings)} 只")
            return True
        else:
            print(" 账户信息获取失败")
            return False
    
    def sync_virtual_holdings(self):
        """同步虚拟持仓状态"""
        self.virtual_cash = self.account_data.get('available_cash', 0)
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
                    'last_update': datetime.now().strftime('%H:%M:%S')
                }
        
        self.last_holdings_update = datetime.now()
        print(f" 虚拟持仓已同步: {len(self.virtual_holdings)} 只股票")
    
    def update_virtual_holdings_with_realtime_data(self):
        """用实时数据更新虚拟持仓"""
        latest_stocks = get_stock_data()
        
        for code, holding in self.virtual_holdings.items():
            if code in latest_stocks:
                stock_info = latest_stocks[code]
                current_price = stock_info.get('last_price', 0)
                
                if current_price > 0:
                    # 更新当前价格和市值
                    holding['current_price'] = current_price
                    holding['market_value'] = holding['quantity'] * current_price
                    
                    # 计算盈亏
                    cost_value = holding['quantity'] * holding['cost_price']
                    holding['profit_loss'] = holding['market_value'] - cost_value
                    holding['profit_loss_pct'] = (holding['profit_loss'] / cost_value * 100) if cost_value > 0 else 0
                    
                    holding['last_update'] = datetime.now().strftime('%H:%M:%S')
    
    def execute_trade_with_priority(self, trade_type, code, quantity, price=None):
        """优先执行交易，确保交易成功"""
        with self.trade_lock:
            print(f" 优先执行交易: {trade_type} {code} {quantity}股")
            
            try:
                if trade_type == 'buy':
                    result = api.buy(code, quantity, price or "市价")
                    if result:
                        # 立即更新虚拟持仓
                        self.update_virtual_holding_after_buy(code, quantity, price or 0)
                        print(f" 买入成功: {code} {quantity}股")
                    else:
                        print(f" 买入失败: {code}")
                    return result
                    
                elif trade_type == 'sell':
                    result = api.sell(code, quantity, price or "市价")
                    if result:
                        # 立即更新虚拟持仓
                        self.update_virtual_holding_after_sell(code, quantity)
                        print(f" 卖出成功: {code} {quantity}股")
                    else:
                        print(f" 卖出失败: {code}")
                    return result
                    
            except Exception as e:
                print(f" 交易执行异常: {e}")
                return False
    
    def update_virtual_holding_after_buy(self, code, quantity, price):
        """买入后立即更新虚拟持仓"""
        if code in self.virtual_holdings:
            # 已有持仓，计算平均成本
            old_qty = self.virtual_holdings[code]['quantity']
            old_cost = self.virtual_holdings[code]['cost_price']
            
            new_qty = old_qty + quantity
            new_cost = (old_qty * old_cost + quantity * price) / new_qty if new_qty > 0 else 0
            
            self.virtual_holdings[code]['quantity'] = new_qty
            self.virtual_holdings[code]['available_quantity'] = new_qty
            self.virtual_holdings[code]['cost_price'] = new_cost
        else:
            # 新建持仓
            self.virtual_holdings[code] = {
                'quantity': quantity,
                'available_quantity': quantity,
                'cost_price': price,
                'current_price': price,
                'market_value': quantity * price,
                'profit_loss': 0,
                'last_update': datetime.now().strftime('%H:%M:%S')
            }
        
        # 扣除现金
        self.virtual_cash -= quantity * price
        print(f" 虚拟持仓已更新: {code} 持仓{self.virtual_holdings[code]['quantity']}股")
    
    def update_virtual_holding_after_sell(self, code, quantity):
        """卖出后立即更新虚拟持仓"""
        if code in self.virtual_holdings:
            holding = self.virtual_holdings[code]
            current_price = holding.get('current_price', 0)
            
            # 减少持仓
            holding['quantity'] -= quantity
            holding['available_quantity'] -= quantity
            
            # 增加现金
            self.virtual_cash += quantity * current_price
            
            # 如果持仓为0，删除记录
            if holding['quantity'] <= 0:
                del self.virtual_holdings[code]
                print(f" 已清仓: {code}")
            else:
                print(f" 虚拟持仓已更新: {code} 剩余{holding['quantity']}股")
    
    def analyze_and_trade(self):
        """分析股票数据并执行交易"""
        print(f"\n 开始智能交易分析 (数据刷新间隔: {self.data_refresh_interval}秒)")
        
        while self.trading_active:
            try:
                # 1. 更新虚拟持仓的实时数据
                self.update_virtual_holdings_with_realtime_data()
                
                # 2. 获取最新股票数据
                latest_stocks = get_stock_data()
                
                if latest_stocks:
                    # 3. 分析交易机会
                    for code, stock_info in latest_stocks.items():
                        self.check_trading_opportunity(code, stock_info)
                
                # 4. 显示虚拟持仓状态
                self.display_virtual_holdings()
                
            except Exception as e:
                print(f" 交易分析异常: {e}")
            
            time.sleep(self.data_refresh_interval)
    
    def check_trading_opportunity(self, code, stock_info):
        """检查交易机会"""
        change_pct = stock_info.get('change_pct', 0)
        price = stock_info.get('last_price', 0)
        
        # 基于虚拟持仓和实时数据的交易策略
        if code in self.virtual_holdings:
            # 已持仓股票的卖出策略
            holding = self.virtual_holdings[code]
            profit_pct = holding.get('profit_loss_pct', 0)
            
            if profit_pct > 10:  # 盈利超过10%
                print(f" 盈利卖出机会: {code} 盈利 {profit_pct:.2f}%")
                self.consider_sell(code, stock_info, "盈利了结")
            elif profit_pct < -8:  # 亏损超过8%
                print(f" 止损卖出机会: {code} 亏损 {profit_pct:.2f}%")
                self.consider_sell(code, stock_info, "止损")
        else:
            # 未持仓股票的买入策略
            if change_pct < -5:  # 跌超5%
                print(f" 抄底买入机会: {code} 跌幅 {change_pct:.2f}%")
                self.consider_buy(code, stock_info, "抄底")
    
    def consider_buy(self, code, stock_info, reason):
        """考虑买入"""
        price = stock_info.get('last_price', 0)
        
        if self.virtual_cash > 10000 and price > 0:
            quantity = int(10000 / price / 100) * 100  # 买入1万元，整百股
            if quantity >= 100:
                print(f" 准备买入: {code} {quantity}股 {price:.2f} 原因:{reason}")
                # 执行买入交易
                self.execute_trade_with_priority('buy', code, quantity, price)
    
    def consider_sell(self, code, stock_info, reason):
        """考虑卖出"""
        if code in self.virtual_holdings:
            holding = self.virtual_holdings[code]
            available_qty = holding.get('available_quantity', 0)
            price = stock_info.get('last_price', 0)
            
            if available_qty >= 100:
                print(f" 准备卖出: {code} {available_qty}股 {price:.2f} 原因:{reason}")
                # 执行卖出交易
                self.execute_trade_with_priority('sell', code, available_qty, price)
    
    def display_virtual_holdings(self):
        """显示虚拟持仓状态"""
        if not self.virtual_holdings:
            return
            
        print(f"\n 虚拟持仓状态 (现金: {self.virtual_cash:,.2f})")
        print("-" * 80)
        
        total_market_value = 0
        for code, holding in self.virtual_holdings.items():
            market_value = holding.get('market_value', 0)
            profit_loss = holding.get('profit_loss', 0)
            profit_pct = holding.get('profit_loss_pct', 0)
            update_time = holding.get('last_update', '')
            
            status = "" if profit_loss >= 0 else ""
            print(f"{status} {code} | 持仓:{holding['quantity']}股 | "
                  f"市值:{market_value:,.2f} | 盈亏:{profit_pct:+.2f}% | {update_time}")
            
            total_market_value += market_value
        
        total_assets = self.virtual_cash + total_market_value
        print(f" 总资产: {total_assets:,.2f}")
        print("-" * 80)
    
    def start_trading(self, host, port, token):
        """启动完整的交易流程"""
        print(" 启动增强版智能交易Agent")
        print("=" * 70)
        
        # 1. 交易日初始化
        if not self.initialize_trading_day():
            return False
        
        # 2. 启动股票数据推送
        print(f"\n 启动股票数据推送服务...")
        try:
            start_stock_service(host, port, token)
            print(" 股票数据服务启动成功")
        except Exception as e:
            print(f" 股票数据服务启动失败: {e}")
            return False
        
        # 3. 等待数据接收
        print("\n 等待股票数据...")
        time.sleep(5)
        
        # 4. 开始交易分析
        self.trading_active = True
        print("\n 开始增强版智能交易...")
        
        try:
            self.analyze_and_trade()
        except KeyboardInterrupt:
            print("\n 用户停止交易")
        finally:
            self.trading_active = False
            print(" 增强版交易Agent已停止")
        
        return True

# 使用示例
def main():
    agent = EnhancedTradingAgent()
    
    # 配置股票数据服务器信息
    HOST = ''      # 填入实际服务器地址
    PORT = 0       # 填入实际端口
    TOKEN = ''     # 填入实际token
    
    if HOST and PORT and TOKEN:
        agent.start_trading(HOST, PORT, TOKEN)
    else:
        print(" 请先配置股票数据服务器信息")

if __name__ == "__main__":
    main()
