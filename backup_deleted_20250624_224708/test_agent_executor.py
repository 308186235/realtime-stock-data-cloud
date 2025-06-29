import time
import datetime
from working_trader_FIXED import buy_stock, sell_stock

class SimpleAgent:
    """简化版交易代理 - 用于测试"""
    
    def __init__(self):
        # 模拟市场数据
        self.market_data = {
            '000001': {'price': 10.50, 'change_pct': 12.5},  # 大涨，适合止盈
            '600000': {'price': 15.20, 'change_pct': -4.2},  # 大跌，适合买入
            '000002': {'price': 8.30, 'change_pct': -8.5},   # 大跌，需要止损
        }
        
        # 模拟持仓数据
        self.holdings = [
            {'code': '000001', 'quantity': 100, 'cost_price': 9.00},  # 盈利16.7%
            {'code': '000002', 'quantity': 200, 'cost_price': 9.00},  # 亏损7.8%
        ]
        
        # 模拟账户余额
        self.cash = 20000
    
    def analyze_and_generate_commands(self):
        """分析并生成交易指令"""
        print("🤖 简化版Agent开始分析...")
        print("=" * 40)
        
        # 显示当前市场状况
        print("📊 当前市场数据:")
        for code, data in self.market_data.items():
            print(f"  {code}: {data['price']}元 ({data['change_pct']:+.1f}%)")
        
        # 显示持仓状况
        print(f"\n💰 账户状况:")
        print(f"  现金: {self.cash}元")
        print(f"  持仓:")
        for holding in self.holdings:
            code = holding['code']
            current_price = self.market_data[code]['price']
            profit_pct = (current_price - holding['cost_price']) / holding['cost_price'] * 100
            print(f"    {code}: {holding['quantity']}股, 成本{holding['cost_price']}, 现价{current_price} ({profit_pct:+.1f}%)")
        
        # 生成交易决策
        print(f"\n🧠 交易决策分析:")
        commands = []
        
        # 策略1: 止盈止损
        for holding in self.holdings:
            code = holding['code']
            current_price = self.market_data[code]['price']
            profit_pct = (current_price - holding['cost_price']) / holding['cost_price'] * 100
            
            if profit_pct > 10:  # 盈利超过10%，止盈
                commands.append(f"SELL:{code}:{holding['quantity']}")
                print(f"  ✅ {code} 盈利{profit_pct:.1f}% → 全部卖出{holding['quantity']}股")
                
            elif profit_pct < -5:  # 亏损超过5%，减仓
                sell_qty = holding['quantity'] // 2
                commands.append(f"SELL:{code}:{sell_qty}")
                print(f"  ⚠️ {code} 亏损{profit_pct:.1f}% → 减仓{sell_qty}股")
        
        # 策略2: 低位买入
        for code, data in self.market_data.items():
            if data['change_pct'] < -3:  # 跌幅超过3%
                # 检查是否已持有
                already_hold = any(h['code'] == code for h in self.holdings)
                if not already_hold and self.cash > 10000:
                    buy_qty = 100  # 买入100股
                    commands.append(f"BUY:{code}:{buy_qty}")
                    print(f"  💡 {code} 跌幅{data['change_pct']:.1f}% → 买入{buy_qty}股")
        
        # 生成最终指令字符串
        command_string = '|'.join(commands)
        
        print(f"\n📋 生成交易指令:")
        if commands:
            for i, cmd in enumerate(commands, 1):
                parts = cmd.split(':')
                print(f"  {i}. {parts[0]} {parts[1]} {parts[2]}股")
            print(f"\n🔤 指令字符串: '{command_string}'")
        else:
            print("  无交易建议")
            
        return command_string

class SimpleExecutor:
    """简化版交易执行器 - 用于测试"""
    
    def parse_commands(self, command_string):
        """解析交易指令"""
        if not command_string.strip():
            return []
        
        trades = []
        commands = command_string.split('|')
        
        for cmd in commands:
            try:
                parts = cmd.strip().split(':')
                if len(parts) == 3:
                    trades.append({
                        'action': parts[0].upper(),
                        'code': parts[1],
                        'quantity': parts[2]
                    })
                    print(f"  解析: {parts[0]} {parts[1]} {parts[2]}股")
            except Exception as e:
                print(f"  ❌ 解析失败: {cmd} - {e}")
        
        return trades
    
    def execute_commands(self, command_string):
        """执行交易指令"""
        print(f"\n⚡ 执行器开始工作...")
        print("=" * 40)
        
        if not command_string.strip():
            print("❌ 没有交易指令需要执行")
            return
        
        print(f"📥 接收到指令: '{command_string}'")
        
        # 解析指令
        trades = self.parse_commands(command_string)
        
        if not trades:
            print("❌ 没有有效的交易指令")
            return
        
        print(f"\n📋 准备执行 {len(trades)} 个交易:")
        
        # 逐个执行
        for i, trade in enumerate(trades, 1):
            print(f"\n🔄 执行第 {i}/{len(trades)} 个交易")
            print(f"   操作: {trade['action']} {trade['code']} {trade['quantity']}股")
            
            # 询问确认
            confirm = input(f"   是否执行？(y/n/s=跳过): ").strip().lower()
            
            if confirm == 'y':
                try:
                    if trade['action'] == 'BUY':
                        result = buy_stock(trade['code'], "市价", trade['quantity'])
                    elif trade['action'] == 'SELL':
                        result = sell_stock(trade['code'], "市价", trade['quantity'])
                    else:
                        print(f"   ❌ 未知操作: {trade['action']}")
                        continue
                    
                    if result:
                        print("   ✅ 执行成功!")
                    else:
                        print("   ❌ 执行失败!")
                        
                except Exception as e:
                    print(f"   ❌ 执行异常: {e}")
                
                # 交易间隔
                if i < len(trades):
                    print("   ⏳ 等待3秒后执行下一个...")
                    time.sleep(3)
                    
            elif confirm == 's':
                print("   ⏭️ 跳过此交易")
                continue
            else:
                print("   ❌ 取消后续所有交易")
                break
        
        print(f"\n🎯 交易执行完成!")

def test_agent_executor():
    """测试Agent+Executor架构"""
    print("🧪 测试Agent+Executor架构")
    print("=" * 50)
    
    while True:
        print(f"\n请选择测试模式:")
        print("1. 只测试Agent分析 (生成交易指令)")
        print("2. 只测试Executor执行 (手动输入指令)")
        print("3. 测试完整流程 (Agent分析 → Executor执行)")
        print("4. 快速演示 (预设指令)")
        print("5. 退出")
        
        choice = input("选择 (1-5): ").strip()
        
        if choice == "1":
            # 只测试Agent
            print(f"\n🧠 测试Agent分析功能")
            agent = SimpleAgent()
            commands = agent.analyze_and_generate_commands()
            
        elif choice == "2":
            # 只测试Executor
            print(f"\n⚡ 测试Executor执行功能")
            commands = input("请输入交易指令 (例: BUY:000001:100|SELL:600000:200): ").strip()
            executor = SimpleExecutor()
            executor.execute_commands(commands)
            
        elif choice == "3":
            # 测试完整流程
            print(f"\n🔄 测试完整流程")
            
            # Step 1: Agent分析
            agent = SimpleAgent()
            commands = agent.analyze_and_generate_commands()
            
            if commands:
                # Step 2: 用户确认
                proceed = input(f"\n是否继续执行这些交易指令？(y/n): ").strip().lower()
                if proceed == 'y':
                    # Step 3: Executor执行
                    executor = SimpleExecutor()
                    executor.execute_commands(commands)
                else:
                    print("❌ 用户取消执行")
            else:
                print("❌ Agent没有生成交易指令")
                
        elif choice == "4":
            # 快速演示
            print(f"\n🚀 快速演示")
            demo_commands = "BUY:000001:100|SELL:600000:200"
            print(f"演示指令: {demo_commands}")
            
            executor = SimpleExecutor()
            executor.execute_commands(demo_commands)
            
        elif choice == "5":
            print("退出测试")
            break
            
        else:
            print("❌ 无效选择")

if __name__ == "__main__":
    test_agent_executor()
