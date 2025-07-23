"""
茶股帮使用演示
展示如何使用茶股帮数据接收器
"""

import time
import threading
from datetime import datetime

# 导入茶股帮模块
from chagubang_receiver import ChaguBangReceiver
from chagubang_token_manager import TokenManager

def demo_without_token():
    """演示无Token连接（用于测试连接）"""
    print("🔍 演示1: 无Token连接测试")
    print("-" * 40)
    
    receiver = ChaguBangReceiver(token='')
    
    # 添加连接状态回调
    def on_connection_status():
        stats = receiver.get_stats()
        print(f"连接状态: {stats['connection_status']}")
        if stats['connection_status'] == 'connected':
            print("✅ 连接成功！但需要有效Token才能接收数据")
        return stats['connection_status'] == 'connected'
    
    # 启动连接测试
    thread = threading.Thread(target=receiver.start_receiving, daemon=True)
    thread.start()
    
    # 等待5秒检查连接
    time.sleep(5)
    connected = on_connection_status()
    
    receiver.stop_receiving()
    return connected

def demo_with_token(token: str):
    """演示有Token的完整功能"""
    print(f"\n🚀 演示2: 使用Token接收数据")
    print(f"Token: {token[:15]}...")
    print("-" * 40)
    
    receiver = ChaguBangReceiver(token=token)
    
    # 数据统计
    data_stats = {
        'total_received': 0,
        'unique_stocks': set(),
        'price_changes': [],
        'start_time': time.time()
    }
    
    def on_stock_data(stock_data):
        """股票数据处理"""
        data_stats['total_received'] += 1
        data_stats['unique_stocks'].add(stock_data['stock_code'])
        
        # 记录价格变动
        if abs(stock_data['change_pct']) > 2.0:  # 涨跌幅超过2%
            data_stats['price_changes'].append({
                'code': stock_data['stock_code'],
                'name': stock_data.get('stock_name', ''),
                'price': stock_data['last_price'],
                'change_pct': stock_data['change_pct'],
                'time': datetime.now().strftime('%H:%M:%S')
            })
        
        # 每100条数据输出一次统计
        if data_stats['total_received'] % 100 == 0:
            elapsed = time.time() - data_stats['start_time']
            rate = data_stats['total_received'] / elapsed if elapsed > 0 else 0
            print(f"📊 已接收 {data_stats['total_received']} 条数据, "
                  f"股票数 {len(data_stats['unique_stocks'])}, "
                  f"速率 {rate:.1f}/秒")
    
    # 添加回调
    receiver.add_data_callback(on_stock_data)
    
    # 启动接收
    thread = threading.Thread(target=receiver.start_receiving, daemon=True)
    thread.start()
    
    print("⏱️ 运行30秒数据接收测试...")
    
    # 运行30秒
    for i in range(30):
        time.sleep(1)
        if (i + 1) % 10 == 0:
            stats = receiver.get_stats()
            print(f"运行 {i+1}s - 状态: {stats['connection_status']}, "
                  f"接收: {stats['received_count']}, "
                  f"错误: {stats['error_count']}")
    
    # 停止接收
    receiver.stop_receiving()
    
    # 输出最终统计
    print(f"\n📈 最终统计:")
    print(f"   总接收数据: {data_stats['total_received']} 条")
    print(f"   不同股票: {len(data_stats['unique_stocks'])} 只")
    print(f"   价格异动: {len(data_stats['price_changes'])} 次")
    
    # 显示价格异动
    if data_stats['price_changes']:
        print(f"\n🚨 价格异动记录:")
        for change in data_stats['price_changes'][-5:]:  # 显示最后5次
            print(f"   {change['time']} {change['code']} {change['name']} "
                  f"{change['price']:.2f} ({change['change_pct']:+.2f}%)")
    
    return data_stats['total_received'] > 0

def demo_token_management():
    """演示Token管理"""
    print("\n🔐 演示3: Token管理")
    print("-" * 40)
    
    manager = TokenManager()
    
    # 添加示例token（无效的，仅用于演示）
    demo_tokens = [
        ("demo_token_123", "演示Token 1"),
        ("test_token_456", "演示Token 2"),
        ("sample_token_789", "演示Token 3")
    ]
    
    print("添加演示Token...")
    for token, desc in demo_tokens:
        manager.add_token(token, desc)
    
    # 列出Token
    print("\n📋 Token列表:")
    manager.list_tokens()
    
    # 测试第一个token
    if manager.config['tokens']:
        first_token = manager.config['tokens'][0]['token']
        print(f"\n🔍 测试Token: {first_token[:15]}...")
        result = manager.test_token(first_token)
        print(f"测试结果: {result['status']} - {result['message']}")
    
    return True

def demo_integration_example():
    """演示集成示例"""
    print("\n💻 演示4: 集成示例代码")
    print("-" * 40)
    
    integration_code = '''
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
'''
    
    print(integration_code)
    
    # 保存示例代码
    filename = f"chagubang_integration_example_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(integration_code)
        print(f"\n✅ 集成示例已保存到: {filename}")
    except Exception as e:
        print(f"❌ 保存失败: {e}")
    
    return True

def main():
    """主演示函数"""
    print("🎯 茶股帮股票数据接收器 - 完整演示")
    print("=" * 60)
    print("📊 实时股票数据 | 🔐 Token管理 | 💻 系统集成")
    print("=" * 60)
    
    results = {}
    
    try:
        # 演示1: 无Token连接测试
        results['connection'] = demo_without_token()
        
        # 演示2: Token管理
        results['token_management'] = demo_token_management()
        
        # 演示3: 集成示例
        results['integration'] = demo_integration_example()
        
        # 如果用户提供了token，演示完整功能
        import sys
        if len(sys.argv) > 1:
            token = sys.argv[1]
            print(f"\n🔑 检测到Token参数，演示完整功能...")
            results['data_reception'] = demo_with_token(token)
        else:
            print(f"\n💡 提示: 使用 'python demo_chagubang_usage.py <token>' 演示完整功能")
            results['data_reception'] = False
        
        # 总结
        print(f"\n🎯 演示总结:")
        print(f"   连接测试: {'✅ 成功' if results['connection'] else '❌ 失败'}")
        print(f"   Token管理: {'✅ 成功' if results['token_management'] else '❌ 失败'}")
        print(f"   数据接收: {'✅ 成功' if results['data_reception'] else '⚠️ 需要有效Token'}")
        print(f"   集成示例: {'✅ 成功' if results['integration'] else '❌ 失败'}")
        
        if all(results.values()):
            print(f"\n🎉 所有演示完成！茶股帮数据接收器可以正常使用")
        else:
            print(f"\n📋 使用步骤:")
            print(f"1. 获取茶股帮API Token")
            print(f"2. 运行: python chagubang_token_manager.py add <token>")
            print(f"3. 运行: python demo_chagubang_usage.py <token>")
            print(f"4. 集成到您的交易系统")
        
    except KeyboardInterrupt:
        print(f"\n⏹️ 用户中断演示")
    except Exception as e:
        print(f"\n❌ 演示过程中发生异常: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n✅ 演示完成")


if __name__ == "__main__":
    main()
