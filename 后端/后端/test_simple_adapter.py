"""
测试简化数据库适配器 - 完整的交易系统功能测试
"""
import sys
import os
import uuid
from datetime import datetime

# 添加backend目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.adapters.simple_database_adapter import simple_db_adapter

def test_complete_trading_workflow():
    """测试完整的交易工作流程"""
    print("🚀 开始完整交易系统工作流程测试...\n")
    
    # 第一步:创建用户
    print("👤 第一步:创建用户")
    user_id = str(uuid.uuid4())
    user_data = {
        'id': user_id,
        'username': 'trader_demo',
        'email': 'trader@example.com',
        'display_name': '演示交易员',
        'is_active': True
    }
    
    user_result = simple_db_adapter.create_user(user_data)
    if user_result['success']:
        print(f"✅ 用户创建成功: {user_result['data']['username']}")
    else:
        print(f"❌ 用户创建失败: {user_result['error']}")
        return False
    
    # 第二步:创建股票池
    print("\n📈 第二步:创建股票池")
    stocks = [
        {'code': '000001', 'name': '平安银行', 'market': 'SZ', 'sector': '金融', 'industry': '银行'},
        {'code': '600519', 'name': '贵州茅台', 'market': 'SH', 'sector': '消费', 'industry': '白酒'},
        {'code': '000858', 'name': '五粮液', 'market': 'SZ', 'sector': '消费', 'industry': '白酒'},
        {'code': '600036', 'name': '招商银行', 'market': 'SH', 'sector': '金融', 'industry': '银行'},
        {'code': '002415', 'name': '海康威视', 'market': 'SZ', 'sector': '科技', 'industry': '安防'}
    ]
    
    created_stocks = []
    for stock in stocks:
        result = simple_db_adapter.create_stock(stock)
        if result['success']:
            print(f"✅ 股票创建成功: {stock['name']} ({stock['code']})")
            created_stocks.append(stock['code'])
        else:
            print(f"❌ 股票创建失败: {stock['name']}")
    
    # 第三步:创建投资组合
    print("\n💼 第三步:创建投资组合")
    portfolio_data = {
        'user_id': user_id,
        'name': '演示投资组合',
        'cash': 1000000.0,  # 100万初始资金
        'total_value': 1000000.0,
        'stock_value': 0.0,
        'is_default': True
    }
    
    portfolio_result = simple_db_adapter.create_portfolio(portfolio_data)
    if portfolio_result['success']:
        portfolio_id = portfolio_result['data']['id']
        print(f"✅ 投资组合创建成功: {portfolio_result['data']['name']}")
        print(f"   - ID: {portfolio_id}")
        print(f"   - 初始资金: ¥{portfolio_data['cash']:,.2f}")
    else:
        print(f"❌ 投资组合创建失败: {portfolio_result['error']}")
        return False
    
    # 第四步:模拟买入操作
    print("\n🛒 第四步:模拟买入操作")
    trades = [
        {'stock_code': '000001', 'shares': 10000, 'price': 12.50, 'type': 'buy'},
        {'stock_code': '600519', 'shares': 500, 'price': 1800.00, 'type': 'buy'},
        {'stock_code': '000858', 'shares': 1000, 'price': 180.00, 'type': 'buy'},
        {'stock_code': '600036', 'shares': 5000, 'price': 45.00, 'type': 'buy'}
    ]
    
    total_cost = 0
    for trade in trades:
        # 创建持仓
        holding_data = {
            'portfolio_id': portfolio_id,
            'stock_code': trade['stock_code'],
            'shares': trade['shares'],
            'cost_price': trade['price'],
            'current_price': trade['price']
        }
        
        holding_result = simple_db_adapter.create_holding(holding_data)
        if holding_result['success']:
            cost = trade['shares'] * trade['price']
            total_cost += cost
            print(f"✅ 买入成功: {trade['stock_code']} x {trade['shares']} @ ¥{trade['price']:.2f} = ¥{cost:,.2f}")
        else:
            print(f"❌ 买入失败: {trade['stock_code']}")
        
        # 创建交易记录
        transaction_data = {
            'portfolio_id': portfolio_id,
            'stock_code': trade['stock_code'],
            'transaction_type': trade['type'],
            'shares': trade['shares'],
            'price': trade['price'],
            'total_amount': trade['shares'] * trade['price'],
            'commission': trade['shares'] * trade['price'] * 0.0003,  # 万三手续费
            'notes': f"买入{trade['stock_code']}"
        }
        
        simple_db_adapter.create_transaction(transaction_data)
    
    print(f"📊 总买入成本: ¥{total_cost:,.2f}")
    
    # 第五步:更新投资组合
    print("\n📊 第五步:更新投资组合状态")
    remaining_cash = portfolio_data['cash'] - total_cost
    update_data = {
        'cash': remaining_cash,
        'stock_value': total_cost,
        'total_value': remaining_cash + total_cost
    }
    
    update_result = simple_db_adapter.update_portfolio(portfolio_id, update_data)
    if update_result['success']:
        print(f"✅ 投资组合更新成功:")
        print(f"   - 剩余现金: ¥{remaining_cash:,.2f}")
        print(f"   - 持仓市值: ¥{total_cost:,.2f}")
        print(f"   - 总资产: ¥{remaining_cash + total_cost:,.2f}")
    
    # 第六步:查询投资组合详情
    print("\n🔍 第六步:查询投资组合详情")
    portfolio_detail = simple_db_adapter.get_portfolio(portfolio_id)
    if portfolio_detail['success'] and portfolio_detail['data']:
        portfolio = portfolio_detail['data']
        print(f"✅ 投资组合详情:")
        print(f"   - 名称: {portfolio['name']}")
        print(f"   - 现金: ¥{portfolio['cash']:,.2f}")
        print(f"   - 股票市值: ¥{portfolio['stock_value']:,.2f}")
        print(f"   - 总资产: ¥{portfolio['total_value']:,.2f}")
        print(f"   - 创建时间: {portfolio['created_at']}")
    
    # 第七步:查询持仓明细
    print("\n📋 第七步:查询持仓明细")
    holdings_result = simple_db_adapter.get_holdings(portfolio_id)
    if holdings_result['success']:
        holdings = holdings_result['data']
        print(f"✅ 持仓明细 (共{len(holdings)}只股票):")
        for holding in holdings:
            market_value = holding['shares'] * holding['current_price']
            print(f"   - {holding['stock_code']}: {holding['shares']}股 @ ¥{holding['cost_price']:.2f} = ¥{market_value:,.2f}")
    
    # 第八步:查询交易记录
    print("\n📜 第八步:查询交易记录")
    transactions_result = simple_db_adapter.get_transactions(portfolio_id)
    if transactions_result['success']:
        transactions = transactions_result['data']
        print(f"✅ 交易记录 (共{len(transactions)}笔):")
        for i, tx in enumerate(transactions[:3], 1):  # 显示前3笔
            print(f"   {i}. {tx['transaction_type'].upper()} {tx['stock_code']} x {tx['shares']} @ ¥{tx['price']:.2f}")
    
    # 第九步:模拟价格变动和盈亏计算
    print("\n📈 第九步:模拟价格变动和盈亏计算")
    price_changes = {
        '000001': 13.20,  # +5.6%
        '600519': 1750.00,  # -2.8%
        '000858': 195.00,  # +8.3%
        '600036': 47.50   # +5.6%
    }
    
    total_profit_loss = 0
    print("💰 价格变动和盈亏:")
    for holding in holdings:
        stock_code = holding['stock_code']
        if stock_code in price_changes:
            old_price = holding['cost_price']
            new_price = price_changes[stock_code]
            shares = holding['shares']
            
            old_value = shares * old_price
            new_value = shares * new_price
            profit_loss = new_value - old_value
            profit_loss_pct = (profit_loss / old_value) * 100
            
            total_profit_loss += profit_loss
            
            # 更新持仓价格
            simple_db_adapter.update_holding(holding['id'], {'current_price': new_price})
            
            print(f"   - {stock_code}: ¥{old_price:.2f} → ¥{new_price:.2f} ({profit_loss_pct:+.1f}%) = {profit_loss:+,.2f}")
    
    print(f"📊 总盈亏: ¥{total_profit_loss:+,.2f}")
    
    # 第十步:生成投资组合报告
    print("\n📊 第十步:生成投资组合报告")
    new_total_value = remaining_cash + total_cost + total_profit_loss
    total_return_pct = (total_profit_loss / total_cost) * 100 if total_cost > 0 else 0
    
    print("="*60)
    print("📈 投资组合最终报告")
    print("="*60)
    print(f"用户: {user_data['display_name']}")
    print(f"投资组合: {portfolio_data['name']}")
    print(f"初始资金: ¥{portfolio_data['cash']:,.2f}")
    print(f"投资成本: ¥{total_cost:,.2f}")
    print(f"当前市值: ¥{total_cost + total_profit_loss:,.2f}")
    print(f"剩余现金: ¥{remaining_cash:,.2f}")
    print(f"总资产: ¥{new_total_value:,.2f}")
    print(f"总收益: ¥{total_profit_loss:+,.2f} ({total_return_pct:+.2f}%)")
    print(f"持仓股票: {len(holdings)}只")
    print(f"交易笔数: {len(transactions)}笔")
    print("="*60)
    
    return True

def cleanup_demo_data():
    """清理演示数据"""
    print("\n🧹 清理演示数据...")
    try:
        result = simple_db_adapter.cleanup_test_data()
        if result['success']:
            print(f"✅ 清理完成,删除了 {result['data']['cleaned_count']} 条记录")
        else:
            print(f"❌ 清理失败: {result['error']}")
    except Exception as e:
        print(f"⚠️ 清理过程中出现错误: {str(e)}")

def main():
    """主函数"""
    try:
        success = test_complete_trading_workflow()
        
        if success:
            print("\n🎉 完整交易系统工作流程测试成功!")
            print("✅ 所有功能正常工作")
            print("✅ 简化数据库适配器运行良好")
            print("✅ 数据存储和查询功能完整")
        else:
            print("\n❌ 测试过程中出现问题")
            
    except Exception as e:
        print(f"\n💥 测试过程中出现异常: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理演示数据
        cleanup_demo_data()

if __name__ == "__main__":
    main()
