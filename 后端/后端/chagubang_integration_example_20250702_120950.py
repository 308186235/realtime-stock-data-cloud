
# 茶股帮数据源集成示例

from chagubang_receiver import start_chagubang_service, get_stock_data

# 1. 启动数据服务
def start_trading_system():
    """启动交易系统数据服务"""
    # 使用您的有效token
    token = "您的茶股帮Token"
    
    # 启动数据接收服务
    service_thread = start_chagubang_service(token=token)
    print("🚀 股票数据服务已启动")
    
    return service_thread

# 2. 获取实时数据
def get_stock_price(stock_code):
    """获取股票实时价格"""
    data = get_stock_data(stock_code)
    if data:
        return {
            'code': data['stock_code'],
            'price': data['last_price'],
            'change_pct': data['change_pct'],
            'update_time': data['update_time']
        }
    return None

# 3. Agent交易决策
def agent_trading_decision():
    """Agent交易决策示例"""
    # 获取所有股票数据
    all_stocks = get_stock_data()
    
    # 筛选涨幅超过5%的股票
    hot_stocks = []
    for code, data in all_stocks.items():
        if data['change_pct'] > 5.0:
            hot_stocks.append(data)
    
    # 返回交易建议
    return {
        'action': 'buy' if hot_stocks else 'hold',
        'targets': [s['stock_code'] for s in hot_stocks[:3]],  # 前3只
        'reason': f'发现{len(hot_stocks)}只强势股票'
    }

# 4. 使用示例
if __name__ == "__main__":
    # 启动服务
    start_trading_system()
    
    # 等待数据
    import time
    time.sleep(10)
    
    # 获取数据
    price_000001 = get_stock_price("000001")
    if price_000001:
        print(f"平安银行: {price_000001['price']:.2f} ({price_000001['change_pct']:+.2f}%)")
    
    # Agent决策
    decision = agent_trading_decision()
    print(f"交易建议: {decision}")
