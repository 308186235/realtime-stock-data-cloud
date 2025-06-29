import json
import datetime
import pandas as pd
import glob
import os
from working_trader_FIXED import export_holdings, buy_stock, sell_stock

class TradingAgent:
    """交易决策代理 - 负责分析和生成交易指令"""
    
    def __init__(self):
        self.market_data = {}
        self.account_info = {}
    
    def load_market_data(self, data_source=None):
        """加载实时市场数据"""
        print("📊 加载市场数据...")
        
        if data_source:
            # 从您的数据源加载
            self.market_data = data_source
        else:
            # 示例数据
            self.market_data = {
                '000001': {'price': 10.50, 'change_pct': 2.5, 'volume': 1000000},
                '600000': {'price': 15.20, 'change_pct': -3.2, 'volume': 800000},
                '000002': {'price': 8.30, 'change_pct': -5.1, 'volume': 1200000},
                '600036': {'price': 12.80, 'change_pct': 1.8, 'volume': 900000},
            }
        
        print(f"✅ 加载了 {len(self.market_data)} 只股票数据")
        return self.market_data
    
    def analyze_account(self):
        """分析账户持仓"""
        print("💰 分析账户持仓...")
        
        # 导出最新持仓
        export_holdings()
        
        # 解析持仓文件
        try:
            files = glob.glob("持仓数据_*.csv")
            if files:
                latest_file = max(files, key=os.path.getctime)
                df = pd.read_csv(latest_file, encoding='gbk')
                
                # 解析持仓信息（根据实际格式调整）
                self.account_info = {
                    'cash': 50000,  # 可用资金
                    'holdings': [
                        {'code': '000001', 'quantity': 200, 'cost_price': 9.50, 'current_price': 10.50},
                        {'code': '600000', 'quantity': 300, 'cost_price': 16.00, 'current_price': 15.20},
                    ]
                }
            else:
                self.account_info = {'cash': 50000, 'holdings': []}
                
        except Exception as e:
            print(f"持仓分析失败: {e}")
            self.account_info = {'cash': 50000, 'holdings': []}
        
        print(f"✅ 账户分析完成: 现金 {self.account_info['cash']}, 持仓 {len(self.account_info['holdings'])} 只")
        return self.account_info
    
    def generate_trading_signals(self):
        """生成交易信号"""
        print("🧠 生成交易信号...")
        
        signals = []
        
        # 策略1: 持仓止盈止损
        for holding in self.account_info['holdings']:
            code = holding['code']
            cost_price = holding['cost_price']
            current_price = holding['current_price']
            quantity = holding['quantity']
            
            profit_pct = (current_price - cost_price) / cost_price * 100
            
            if profit_pct > 10:  # 止盈
                signals.append({
                    'action': 'sell',
                    'code': code,
                    'quantity': str(quantity),
                    'reason': f'止盈 {profit_pct:.1f}%',
                    'priority': 'high'
                })
            elif profit_pct < -8:  # 止损
                signals.append({
                    'action': 'sell',
                    'code': code,
                    'quantity': str(quantity // 2),  # 减仓一半
                    'reason': f'止损 {profit_pct:.1f}%',
                    'priority': 'high'
                })
        
        # 策略2: 买入机会
        cash = self.account_info['cash']
        if cash > 10000:
            for code, data in self.market_data.items():
                if data['change_pct'] < -3:  # 大跌买入
                    max_buy = min(200, int(cash // data['price'] // 100) * 100)
                    if max_buy > 0:
                        signals.append({
                            'action': 'buy',
                            'code': code,
                            'quantity': str(max_buy),
                            'reason': f'低位买入 {data["change_pct"]:.1f}%',
                            'priority': 'medium'
                        })
                        break  # 只买一只
        
        print(f"✅ 生成 {len(signals)} 个交易信号")
        return signals
    
    def create_trading_plan(self):
        """创建完整的交易计划"""
        print("📋 创建交易计划...")
        
        # 1. 加载数据
        self.load_market_data()
        
        # 2. 分析账户
        self.analyze_account()
        
        # 3. 生成信号
        signals = self.generate_trading_signals()
        
        # 4. 创建交易计划
        trading_plan = {
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'strategy': '智能止盈止损+低位买入',
            'market_summary': {
                'total_stocks': len(self.market_data),
                'account_cash': self.account_info['cash'],
                'holdings_count': len(self.account_info['holdings'])
            },
            'trades': signals
        }
        
        return trading_plan
    
    def format_trading_commands(self, trading_plan):
        """格式化交易指令为字符串"""
        commands = []
        
        for trade in trading_plan['trades']:
            cmd = f"{trade['action'].upper()}:{trade['code']}:{trade['quantity']}"
            commands.append(cmd)
        
        return '|'.join(commands)
    
    def run_analysis(self):
        """运行完整分析流程"""
        print("🤖 启动交易代理分析")
        print("=" * 50)
        
        try:
            # 创建交易计划
            plan = self.create_trading_plan()
            
            # 显示分析结果
            print(f"\n📊 交易分析报告")
            print(f"时间: {plan['timestamp']}")
            print(f"策略: {plan['strategy']}")
            print(f"账户现金: {plan['market_summary']['account_cash']}")
            print(f"持仓数量: {plan['market_summary']['holdings_count']}")
            print(f"交易建议: {len(plan['trades'])}")
            
            if plan['trades']:
                print(f"\n💡 具体建议:")
                for i, trade in enumerate(plan['trades'], 1):
                    print(f"{i}. {trade['action'].upper()} {trade['code']} "
                          f"{trade['quantity']}股 - {trade['reason']}")
            
            # 返回交易指令
            commands = self.format_trading_commands(plan)
            
            print(f"\n🔤 交易指令字符串:")
            print(f"'{commands}'")
            
            # 保存完整计划到文件
            plan_file = f"trading_plan_{datetime.datetime.now().strftime('%m%d_%H%M%S')}.json"
            with open(plan_file, 'w', encoding='utf-8') as f:
                json.dump(plan, f, ensure_ascii=False, indent=2)
            print(f"📄 交易计划已保存: {plan_file}")
            
            return commands, plan
            
        except Exception as e:
            print(f"❌ 分析失败: {e}")
            return "", {}

class TradingExecutor:
    """交易执行器 - 负责解析和执行交易指令"""
    
    def parse_commands(self, command_string):
        """解析交易指令字符串"""
        if not command_string:
            return []
        
        trades = []
        commands = command_string.split('|')
        
        for cmd in commands:
            try:
                parts = cmd.split(':')
                if len(parts) == 3:
                    trades.append({
                        'action': parts[0].lower(),
                        'code': parts[1],
                        'quantity': parts[2]
                    })
            except Exception as e:
                print(f"解析指令失败: {cmd} - {e}")
        
        return trades
    
    def execute_trades(self, command_string, confirm_each=True):
        """执行交易指令"""
        print("⚡ 开始执行交易指令")
        print(f"指令: {command_string}")
        print("-" * 40)
        
        trades = self.parse_commands(command_string)
        
        if not trades:
            print("❌ 没有有效的交易指令")
            return
        
        print(f"📋 解析到 {len(trades)} 个交易指令:")
        for i, trade in enumerate(trades, 1):
            print(f"{i}. {trade['action'].upper()} {trade['code']} {trade['quantity']}股")
        
        if confirm_each:
            confirm = input(f"\n是否执行这些交易？(y/n): ").strip().lower()
            if confirm != 'y':
                print("❌ 用户取消执行")
                return
        
        # 执行交易
        success_count = 0
        for i, trade in enumerate(trades, 1):
            print(f"\n📈 执行交易 {i}/{len(trades)}")
            print(f"操作: {trade['action'].upper()} {trade['code']} {trade['quantity']}股")
            
            try:
                if trade['action'] == 'buy':
                    result = buy_stock(trade['code'], "市价", trade['quantity'])
                elif trade['action'] == 'sell':
                    result = sell_stock(trade['code'], "市价", trade['quantity'])
                else:
                    print(f"❌ 未知操作: {trade['action']}")
                    continue
                
                if result:
                    print("✅ 执行成功")
                    success_count += 1
                else:
                    print("❌ 执行失败")
                    
            except Exception as e:
                print(f"❌ 执行异常: {e}")
            
            # 交易间隔
            if i < len(trades):
                print("⏳ 等待2秒...")
                time.sleep(2)
        
        print(f"\n🎯 执行完成: {success_count}/{len(trades)} 成功")

def main():
    """主程序 - 演示Agent+Executor架构"""
    print("🎯 智能交易系统")
    print("Agent(分析) + Executor(执行) 架构")
    print("=" * 50)
    
    while True:
        print("\n请选择:")
        print("1. Agent分析生成交易指令")
        print("2. 执行交易指令")
        print("3. 一键分析+执行")
        print("4. 退出")
        
        choice = input("选择 (1-4): ").strip()
        
        if choice == "1":
            # 只分析，不执行
            agent = TradingAgent()
            commands, plan = agent.run_analysis()
            
        elif choice == "2":
            # 手动输入指令执行
            commands = input("请输入交易指令 (格式: BUY:000001:100|SELL:600000:200): ").strip()
            executor = TradingExecutor()
            executor.execute_trades(commands)
            
        elif choice == "3":
            # 分析+执行
            agent = TradingAgent()
            commands, plan = agent.run_analysis()
            
            if commands:
                executor = TradingExecutor()
                executor.execute_trades(commands)
            else:
                print("❌ 没有生成交易指令")
                
        elif choice == "4":
            print("退出")
            break
        else:
            print("无效选择")

if __name__ == "__main__":
    main()
