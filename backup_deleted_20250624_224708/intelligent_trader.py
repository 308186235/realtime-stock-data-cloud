import pandas as pd
import glob
import os
import time
import datetime
from working_trader_FIXED import export_holdings, buy_stock, sell_stock

class IntelligentTradingAgent:
    """智能交易代理"""
    
    def __init__(self):
        self.market_data = {}
        self.account_info = {}
        self.trading_log = []
    
    def get_real_time_data(self):
        """获取实时股票数据 - 接入您的数据源"""
        print("📊 获取实时市场数据...")
        
        # TODO: 这里接入您提供的实时数据源
        # 示例数据格式
        self.market_data = {
            '000001': {'price': 10.50, 'change': 0.05, 'change_pct': 0.48, 'volume': 1000000},
            '600000': {'price': 15.20, 'change': -0.10, 'change_pct': -0.65, 'volume': 800000},
            '000002': {'price': 8.30, 'change': -0.20, 'change_pct': -2.35, 'volume': 1200000},
            '600036': {'price': 12.80, 'change': 0.15, 'change_pct': 1.19, 'volume': 900000},
        }
        
        print(f"✅ 获取到 {len(self.market_data)} 只股票的实时数据")
        return self.market_data
    
    def analyze_account_balance(self):
        """分析账户余额和持仓"""
        print("💰 分析账户状态...")
        
        # 1. 导出最新持仓数据
        print("导出持仓数据...")
        export_holdings()
        time.sleep(2)  # 等待导出完成
        
        # 2. 解析持仓文件
        try:
            files = glob.glob("持仓数据_*.csv")
            if not files:
                print("❌ 没有找到持仓数据文件")
                return None
            
            latest_file = max(files, key=os.path.getctime)
            print(f"📄 解析文件: {latest_file}")
            
            # 读取CSV文件
            df = pd.read_csv(latest_file, encoding='gbk')
            
            # 解析账户信息
            self.account_info = {
                'cash_balance': 50000,  # 示例：可用资金
                'total_assets': 100000,  # 示例：总资产
                'holdings': []
            }
            
            # 解析持仓（根据实际CSV格式调整）
            if not df.empty:
                for _, row in df.iterrows():
                    holding = {
                        'code': row.get('股票代码', ''),
                        'name': row.get('股票名称', ''),
                        'quantity': row.get('持仓数量', 0),
                        'cost_price': row.get('成本价', 0),
                        'current_price': row.get('现价', 0),
                        'market_value': row.get('市值', 0),
                        'profit_loss': row.get('盈亏', 0)
                    }
                    if holding['code']:  # 只添加有效的持仓
                        self.account_info['holdings'].append(holding)
            
            print(f"✅ 账户分析完成: 现金 {self.account_info['cash_balance']}, 持仓 {len(self.account_info['holdings'])} 只")
            return self.account_info
            
        except Exception as e:
            print(f"❌ 解析持仓文件失败: {e}")
            return None
    
    def analyze_trading_opportunities(self):
        """分析交易机会"""
        print("🧠 执行交易策略分析...")
        decisions = []
        
        if not self.market_data or not self.account_info:
            print("❌ 缺少市场数据或账户信息")
            return decisions
        
        # 策略1: 持仓止盈止损分析
        print("📈 分析持仓止盈止损...")
        for holding in self.account_info['holdings']:
            code = holding['code']
            cost_price = holding['cost_price']
            quantity = holding['quantity']
            
            if code in self.market_data:
                current_price = self.market_data[code]['price']
                profit_pct = (current_price - cost_price) / cost_price * 100
                
                if profit_pct > 10:  # 盈利超过10%，止盈
                    decisions.append({
                        'action': 'sell',
                        'code': code,
                        'quantity': quantity,
                        'reason': f'止盈 (盈利{profit_pct:.1f}%)',
                        'priority': 'high'
                    })
                elif profit_pct < -8:  # 亏损超过8%，止损
                    decisions.append({
                        'action': 'sell',
                        'code': code,
                        'quantity': quantity // 2,  # 减仓一半
                        'reason': f'止损 (亏损{profit_pct:.1f}%)',
                        'priority': 'high'
                    })
        
        # 策略2: 买入机会分析
        print("💡 分析买入机会...")
        cash = self.account_info['cash_balance']
        if cash > 10000:  # 有足够现金
            buy_candidates = []
            
            for code, data in self.market_data.items():
                # 寻找大跌的股票作为买入候选
                if data['change_pct'] < -3:  # 跌幅超过3%
                    buy_candidates.append({
                        'code': code,
                        'change_pct': data['change_pct'],
                        'price': data['price']
                    })
            
            # 按跌幅排序，选择跌幅最大的
            buy_candidates.sort(key=lambda x: x['change_pct'])
            
            if buy_candidates:
                candidate = buy_candidates[0]
                max_quantity = min(100, int(cash // candidate['price'] // 100) * 100)  # 按手买入
                
                if max_quantity > 0:
                    decisions.append({
                        'action': 'buy',
                        'code': candidate['code'],
                        'quantity': max_quantity,
                        'reason': f'低位买入 (跌幅{candidate["change_pct"]:.1f}%)',
                        'priority': 'medium'
                    })
        
        print(f"✅ 策略分析完成，生成 {len(decisions)} 个交易决策")
        return decisions
    
    def execute_trading_decisions(self, decisions):
        """执行交易决策"""
        if not decisions:
            print("📝 没有交易决策需要执行")
            return
        
        print(f"⚡ 准备执行 {len(decisions)} 个交易决策...")
        
        # 按优先级排序
        decisions.sort(key=lambda x: {'high': 1, 'medium': 2, 'low': 3}.get(x['priority'], 3))
        
        for i, decision in enumerate(decisions, 1):
            print(f"\n📋 执行决策 {i}/{len(decisions)}")
            print(f"操作: {decision['action']}")
            print(f"股票: {decision['code']}")
            print(f"数量: {decision['quantity']}")
            print(f"原因: {decision['reason']}")
            
            # 询问用户确认
            confirm = input("是否执行此交易？(y/n/s=跳过): ").strip().lower()
            
            if confirm == 'y':
                try:
                    if decision['action'] == 'buy':
                        result = buy_stock(decision['code'], "市价", str(decision['quantity']))
                    elif decision['action'] == 'sell':
                        result = sell_stock(decision['code'], "市价", str(decision['quantity']))
                    
                    if result:
                        print("✅ 交易执行成功")
                        self.trading_log.append({
                            'time': datetime.datetime.now(),
                            'action': decision['action'],
                            'code': decision['code'],
                            'quantity': decision['quantity'],
                            'reason': decision['reason'],
                            'status': 'success'
                        })
                    else:
                        print("❌ 交易执行失败")
                        
                except Exception as e:
                    print(f"❌ 交易执行异常: {e}")
                    
                time.sleep(2)  # 交易间隔
                
            elif confirm == 's':
                print("⏭️ 跳过此交易")
                continue
            else:
                print("❌ 取消交易")
                break
    
    def run_intelligent_trading(self):
        """运行智能交易主流程"""
        print("🤖 启动智能交易代理")
        print("=" * 50)
        
        try:
            # 1. 获取实时数据
            self.get_real_time_data()
            
            # 2. 分析账户状态
            account_info = self.analyze_account_balance()
            if not account_info:
                print("❌ 无法获取账户信息，退出")
                return
            
            # 3. 分析交易机会
            decisions = self.analyze_trading_opportunities()
            
            # 4. 显示分析结果
            print("\n📊 交易分析报告")
            print("-" * 30)
            print(f"账户现金: {self.account_info['cash_balance']}")
            print(f"持仓数量: {len(self.account_info['holdings'])}")
            print(f"交易建议: {len(decisions)}")
            
            if decisions:
                print("\n💡 交易建议:")
                for i, decision in enumerate(decisions, 1):
                    print(f"{i}. {decision['action'].upper()} {decision['code']} "
                          f"{decision['quantity']}股 - {decision['reason']}")
            
            # 5. 执行交易
            if decisions:
                execute = input("\n是否执行交易建议？(y/n): ").strip().lower()
                if execute == 'y':
                    self.execute_trading_decisions(decisions)
                else:
                    print("📝 交易建议已保存，未执行")
            
            print("\n✅ 智能交易流程完成")
            
        except Exception as e:
            print(f"❌ 智能交易流程异常: {e}")

def main():
    """主程序"""
    agent = IntelligentTradingAgent()
    agent.run_intelligent_trading()

if __name__ == "__main__":
    main()
