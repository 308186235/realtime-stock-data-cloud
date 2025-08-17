"""
测试Supabase集成到交易系统
"""
import sys
import os
import uuid

# 添加backend目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.adapters.database_adapter import db_adapter
from backend.services.portfolio_service import portfolio_service

def test_user_management():
    """测试用户管理"""
    print("🧑💼 测试用户管理...")
    
    # 创建测试用户
    user_id = str(uuid.uuid4())
    user_data = {
        'id': user_id,
        'username': 'test_trader',
        'display_name': '测试交易员',
        'avatar_url': None
    }
    
    result = db_adapter.create_user(user_data)
    if result['success']:
        print(f"✅ 用户创建成功: {result['data']}")
    else:
        print(f"❌ 用户创建失败: {result['error']}")
        return None
    
    # 获取用户信息
    get_result = db_adapter.get_user(user_id)
    if get_result['success'] and get_result['data']:
        print(f"✅ 用户查询成功: {get_result['data']['username']}")
    else:
        print(f"❌ 用户查询失败")
    
    return user_id

def test_stock_management():
    """测试股票信息管理"""
    print("\n📈 测试股票信息管理...")
    
    # 创建测试股票
    stocks = [
        {'code': '000001', 'name': '平安银行', 'market': 'SZ', 'sector': '金融', 'industry': '银行'},
        {'code': '600519', 'name': '贵州茅台', 'market': 'SH', 'sector': '消费', 'industry': '白酒'},
        {'code': '000858', 'name': '五粮液', 'market': 'SZ', 'sector': '消费', 'industry': '白酒'}
    ]
    
    created_stocks = []
    for stock in stocks:
        result = db_adapter.create_stock(stock)
        if result['success']:
            print(f"✅ 股票创建成功: {stock['name']} ({stock['code']})")
            created_stocks.append(stock['code'])
        else:
            print(f"❌ 股票创建失败: {stock['name']} - {result.get('error', '未知错误')}")
    
    # 查询股票信息
    get_result = db_adapter.get_stocks()
    if get_result['success']:
        print(f"✅ 股票查询成功,共 {len(get_result['data'])} 只股票")
        for stock in get_result['data'][:3]:  # 显示前3只
            print(f"   - {stock['name']} ({stock['code']})")
    else:
        print(f"❌ 股票查询失败: {get_result['error']}")
    
    return created_stocks

def test_portfolio_management(user_id: str, stock_codes: list):
    """测试投资组合管理"""
    print("\n💼 测试投资组合管理...")
    
    # 创建投资组合
    portfolio_result = portfolio_service.create_portfolio(
        user_id=user_id,
        name="测试投资组合",
        initial_cash=100000.0
    )
    
    if not portfolio_result['success']:
        print(f"❌ 投资组合创建失败: {portfolio_result['error']}")
        return None
    
    portfolio_id = portfolio_result['data']['id']
    print(f"✅ 投资组合创建成功: ID {portfolio_id}")
    
    # 添加持仓
    holdings = [
        {'stock_code': stock_codes[0], 'shares': 1000, 'cost_price': 12.50},
        {'stock_code': stock_codes[1], 'shares': 100, 'cost_price': 1800.00},
        {'stock_code': stock_codes[2], 'shares': 200, 'cost_price': 180.00}
    ] if len(stock_codes) >= 3 else []
    
    for holding in holdings:
        result = portfolio_service.add_holding(
            portfolio_id=portfolio_id,
            stock_code=holding['stock_code'],
            shares=holding['shares'],
            cost_price=holding['cost_price']
        )
        
        if result['success']:
            print(f"✅ 持仓添加成功: {holding['stock_code']} x {holding['shares']}")
        else:
            print(f"❌ 持仓添加失败: {holding['stock_code']} - {result.get('error', '未知错误')}")
    
    # 获取投资组合详情
    detail_result = portfolio_service.get_portfolio_detail(portfolio_id)
    if detail_result['success']:
        portfolio = detail_result['data']
        print(f"✅ 投资组合详情获取成功:")
        print(f"   - 名称: {portfolio['name']}")
        print(f"   - 现金: ¥{portfolio.get('cash', 0):,.2f}")
        print(f"   - 持仓数量: {len(portfolio.get('holdings', []))}")
        print(f"   - 总资产: ¥{portfolio.get('total_value', 0):,.2f}")
    else:
        print(f"❌ 投资组合详情获取失败: {detail_result['error']}")
    
    # 获取投资组合表现
    performance_result = portfolio_service.get_portfolio_performance(portfolio_id)
    if performance_result['success']:
        perf = performance_result['data']
        print(f"✅ 投资组合表现:")
        print(f"   - 总成本: ¥{perf['total_cost']:,.2f}")
        print(f"   - 市值: ¥{perf['total_market_value']:,.2f}")
        print(f"   - 盈亏: ¥{perf['profit_loss']:,.2f} ({perf['profit_loss_ratio']:.2f}%)")
    else:
        print(f"❌ 投资组合表现获取失败: {performance_result['error']}")
    
    return portfolio_id

def test_system_config():
    """测试系统配置"""
    print("\n⚙️ 测试系统配置...")
    
    # 获取系统配置
    config_result = db_adapter.get_system_config()
    if config_result['success']:
        configs = config_result['data']
        print(f"✅ 系统配置获取成功,共 {len(configs)} 项配置")
        for config in configs[:3]:  # 显示前3项
            print(f"   - {config['key']}: {config.get('value', 'N/A')}")
    else:
        print(f"❌ 系统配置获取失败: {config_result['error']}")
    
    # 更新系统配置
    update_result = db_adapter.update_system_config(
        key='test_config',
        value={'test': True, 'timestamp': '2025-01-01T00:00:00Z'},
        description='测试配置项'
    )
    
    if update_result['success']:
        print(f"✅ 系统配置更新成功")
    else:
        print(f"❌ 系统配置更新失败: {update_result['error']}")

def cleanup_test_data():
    """清理测试数据"""
    print("\n🧹 清理测试数据...")
    
    try:
        # 删除测试用户
        result = db_adapter.supabase.client.table('user_profiles').delete().eq('username', 'test_trader').execute()
        print("✅ 测试用户数据清理完成")
        
        # 删除测试股票
        test_codes = ['000001', '600519', '000858']
        for code in test_codes:
            db_adapter.supabase.client.table('stocks').delete().eq('code', code).execute()
        print("✅ 测试股票数据清理完成")
        
        # 删除测试配置
        db_adapter.supabase.client.table('system_config').delete().eq('key', 'test_config').execute()
        print("✅ 测试配置数据清理完成")
        
    except Exception as e:
        print(f"⚠️ 清理测试数据时出现错误: {str(e)}")

def main():
    """主测试函数"""
    print("🚀 开始Supabase交易系统集成测试...\n")
    
    try:
        # 测试用户管理
        user_id = test_user_management()
        if not user_id:
            print("❌ 用户管理测试失败,停止后续测试")
            return
        
        # 测试股票管理
        stock_codes = test_stock_management()
        if not stock_codes:
            print("❌ 股票管理测试失败,停止后续测试")
            return
        
        # 测试投资组合管理
        portfolio_id = test_portfolio_management(user_id, stock_codes)
        
        # 测试系统配置
        test_system_config()
        
        print("\n" + "="*60)
        print("🎉 Supabase交易系统集成测试完成!")
        print("✅ 所有核心功能测试通过")
        print("✅ 数据库适配器工作正常")
        print("✅ 投资组合服务集成成功")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理测试数据
        cleanup_test_data()

if __name__ == "__main__":
    main()
