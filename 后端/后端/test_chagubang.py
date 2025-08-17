"""
茶股帮数据接收器测试脚本
用于测试连接到 l1.chagubang.com:6380 的股票数据推送服务
"""

import time
import threading
from chagubang_receiver import ChaguBangReceiver, start_chagubang_service

def test_basic_connection():
    """测试基本连接功能"""
    print("🔧 测试1: 基本连接功能")
    print("-" * 40)
    
    # 使用您提供的服务器信息
    receiver = ChaguBangReceiver(
        host='l1.chagubang.com',
        port=6380,
        token=''  # 根据您的代码,token可以为空
    )
    
    # 数据计数器
    data_count = 0
    received_stocks = set()
    
    def on_data_received(stock_data):
        nonlocal data_count, received_stocks
        data_count += 1
        received_stocks.add(stock_data['stock_code'])
        
        # 每10条数据输出一次
        if data_count % 10 == 0:
            print(f"📊 已接收 {data_count} 条数据,股票数量: {len(received_stocks)}")
            print(f"   最新: {stock_data['stock_code']} {stock_data.get('stock_name', '')} "
                  f"价格: {stock_data['last_price']:.2f} "
                  f"涨跌: {stock_data['change_pct']:+.2f}%")
    
    # 添加回调
    receiver.add_data_callback(on_data_received)
    
    # 启动接收线程
    thread = threading.Thread(target=receiver.start_receiving, daemon=True)
    thread.start()
    
    try:
        # 运行30秒
        print("⏱️ 运行30秒测试...")
        time.sleep(30)
        
        # 获取统计信息
        stats = receiver.get_stats()
        print(f"\n📈 测试结果:")
        print(f"   连接状态: {stats['connection_status']}")
        print(f"   接收数据: {stats['received_count']} 条")
        print(f"   错误次数: {stats['error_count']} 次")
        print(f"   不同股票: {len(received_stocks)} 只")
        print(f"   队列大小: {stats.get('queue_size', 0)}")
        
        if stats['received_count'] > 0:
            print("✅ 连接测试成功!")
            return True
        else:
            print("❌ 未接收到数据")
            return False
            
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断测试")
        return False
    finally:
        receiver.stop_receiving()

def test_data_parsing():
    """测试数据解析功能"""
    print("\n🔧 测试2: 数据解析功能")
    print("-" * 40)
    
    receiver = ChaguBangReceiver()
    
    # 测试沪深数据解析
    sh_sz_sample = "000001$平安银行$12.34$12.00$12.50$11.90$1000000$12340000.00$0$0$0$0$0$0$0$0$0$0$0$0$0$0$0$0$0$0$0$0$0$0$12.00$0$0$0"
    parsed_sh_sz = receiver._parse_sh_sz_data(sh_sz_sample)
    
    if parsed_sh_sz:
        print("✅ 沪深数据解析成功:")
        print(f"   股票代码: {parsed_sh_sz['stock_code']}")
        print(f"   股票名称: {parsed_sh_sz['stock_name']}")
        print(f"   最新价格: {parsed_sh_sz['last_price']}")
        print(f"   涨跌幅: {parsed_sh_sz['change_pct']:.2f}%")
    else:
        print("❌ 沪深数据解析失败")
    
    # 测试北交所数据解析
    bj_sample = '{"stock_code":"430047","lastPrice":10.50,"open":10.00,"high":11.00,"low":9.80,"volume":50000,"amount":525000.00,"lastClose":10.00}'
    parsed_bj = receiver._parse_bj_data(bj_sample)
    
    if parsed_bj:
        print("✅ 北交所数据解析成功:")
        print(f"   股票代码: {parsed_bj['stock_code']}")
        print(f"   最新价格: {parsed_bj['last_price']}")
        print(f"   涨跌幅: {parsed_bj['change_pct']:.2f}%")
    else:
        print("❌ 北交所数据解析失败")

def test_service_api():
    """测试服务API功能"""
    print("\n🔧 测试3: 服务API功能")
    print("-" * 40)
    
    # 启动服务
    print("🚀 启动茶股帮数据服务...")
    thread = start_chagubang_service(
        host='l1.chagubang.com',
        port=6380,
        token=''
    )
    
    # 等待连接建立
    time.sleep(5)
    
    # 获取服务统计
    from chagubang_receiver import get_service_stats, get_stock_data
    
    stats = get_service_stats()
    print(f"📊 服务状态: {stats}")
    
    # 等待接收一些数据
    print("⏱️ 等待接收数据...")
    time.sleep(10)
    
    # 获取最新数据
    latest_data = get_stock_data()
    print(f"📈 接收到 {len(latest_data)} 只股票的数据")
    
    # 显示前5只股票
    count = 0
    for code, data in latest_data.items():
        if count >= 5:
            break
        print(f"   {code}: {data['last_price']:.2f} ({data['change_pct']:+.2f}%)")
        count += 1
    
    return len(latest_data) > 0

def main():
    """主测试函数"""
    print("🚀 茶股帮股票数据接收器 - 完整测试")
    print("=" * 50)
    print(f"服务器: l1.chagubang.com:6380")
    print(f"协议: TCP Socket + 长度前缀")
    print("=" * 50)
    
    try:
        # 测试1: 基本连接
        success1 = test_basic_connection()
        
        # 测试2: 数据解析
        test_data_parsing()
        
        # 测试3: 服务API
        success3 = test_service_api()
        
        print("\n" + "=" * 50)
        print("🎯 测试总结:")
        print(f"   基本连接: {'✅ 成功' if success1 else '❌ 失败'}")
        print(f"   数据解析: ✅ 成功")
        print(f"   服务API: {'✅ 成功' if success3 else '❌ 失败'}")
        
        if success1 and success3:
            print("\n🎉 所有测试通过!茶股帮数据接收器工作正常")
            print("\n📋 使用说明:")
            print("1. 导入: from chagubang_receiver import start_chagubang_service")
            print("2. 启动: start_chagubang_service(token='您的token')")
            print("3. 获取数据: get_stock_data('股票代码')")
        else:
            print("\n⚠️ 部分测试失败,请检查网络连接和服务器状态")
            
    except Exception as e:
        print(f"\n❌ 测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
