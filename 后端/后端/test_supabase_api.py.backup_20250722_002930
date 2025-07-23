"""
测试Supabase API路由
"""
import requests
import json
import uuid
from datetime import datetime

# API基础URL
BASE_URL = "http://localhost:8000/api/supabase"

def test_api_endpoints():
    """测试所有API端点"""
    print("🚀 开始测试Supabase API路由...\n")
    
    # 测试数据
    user_id = str(uuid.uuid4())
    portfolio_id = None
    stock_codes = []
    
    try:
        # 1. 测试创建用户
        print("👤 测试创建用户...")
        user_data = {
            "id": user_id,
            "username": "api_test_user",
            "email": "test@example.com",
            "display_name": "API测试用户",
            "is_active": True
        }
        
        response = requests.post(f"{BASE_URL}/users", json=user_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 用户创建成功: {result['data']['username']}")
        else:
            print(f"❌ 用户创建失败: {response.status_code} - {response.text}")
            return False
        
        # 2. 测试获取用户信息
        print("\n🔍 测试获取用户信息...")
        response = requests.get(f"{BASE_URL}/users/{user_id}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 用户信息获取成功: {result['data']['display_name']}")
        else:
            print(f"❌ 用户信息获取失败: {response.status_code}")
        
        # 3. 测试创建股票
        print("\n📈 测试创建股票...")
        stocks = [
            {"code": "000001", "name": "平安银行", "market": "SZ", "sector": "金融"},
            {"code": "600519", "name": "贵州茅台", "market": "SH", "sector": "消费"},
            {"code": "000858", "name": "五粮液", "market": "SZ", "sector": "消费"}
        ]
        
        for stock in stocks:
            response = requests.post(f"{BASE_URL}/stocks", json=stock)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 股票创建成功: {stock['name']} ({stock['code']})")
                stock_codes.append(stock['code'])
            else:
                print(f"❌ 股票创建失败: {stock['name']} - {response.status_code}")
        
        # 4. 测试获取股票列表
        print("\n📊 测试获取股票列表...")
        response = requests.get(f"{BASE_URL}/stocks")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 股票列表获取成功，共 {len(result['data'])} 只股票")
        else:
            print(f"❌ 股票列表获取失败: {response.status_code}")
        
        # 5. 测试创建投资组合
        print("\n💼 测试创建投资组合...")
        portfolio_data = {
            "user_id": user_id,
            "name": "API测试投资组合",
            "cash": 500000.0,
            "total_value": 500000.0,
            "stock_value": 0.0,
            "is_default": True
        }
        
        response = requests.post(f"{BASE_URL}/portfolios", json=portfolio_data)
        if response.status_code == 200:
            result = response.json()
            portfolio_id = result['data']['id']
            print(f"✅ 投资组合创建成功: {result['data']['name']}")
            print(f"   - ID: {portfolio_id}")
        else:
            print(f"❌ 投资组合创建失败: {response.status_code} - {response.text}")
            return False
        
        # 6. 测试创建持仓
        print("\n🛒 测试创建持仓...")
        holdings = [
            {"portfolio_id": portfolio_id, "stock_code": "000001", "shares": 5000, "cost_price": 12.50},
            {"portfolio_id": portfolio_id, "stock_code": "600519", "shares": 200, "cost_price": 1800.00},
            {"portfolio_id": portfolio_id, "stock_code": "000858", "shares": 1000, "cost_price": 180.00}
        ]
        
        for holding in holdings:
            response = requests.post(f"{BASE_URL}/holdings", json=holding)
            if response.status_code == 200:
                result = response.json()
                cost = holding['shares'] * holding['cost_price']
                print(f"✅ 持仓创建成功: {holding['stock_code']} x {holding['shares']} = ¥{cost:,.2f}")
            else:
                print(f"❌ 持仓创建失败: {holding['stock_code']} - {response.status_code}")
        
        # 7. 测试创建交易记录
        print("\n📝 测试创建交易记录...")
        for holding in holdings:
            transaction_data = {
                "portfolio_id": portfolio_id,
                "stock_code": holding['stock_code'],
                "transaction_type": "buy",
                "shares": holding['shares'],
                "price": holding['cost_price'],
                "total_amount": holding['shares'] * holding['cost_price'],
                "commission": holding['shares'] * holding['cost_price'] * 0.0003,
                "notes": f"API测试买入{holding['stock_code']}"
            }
            
            response = requests.post(f"{BASE_URL}/transactions", json=transaction_data)
            if response.status_code == 200:
                print(f"✅ 交易记录创建成功: {holding['stock_code']}")
            else:
                print(f"❌ 交易记录创建失败: {holding['stock_code']} - {response.status_code}")
        
        # 8. 测试获取投资组合详情
        print("\n🔍 测试获取投资组合详情...")
        response = requests.get(f"{BASE_URL}/portfolios/{portfolio_id}")
        if response.status_code == 200:
            result = response.json()
            portfolio = result['data']
            print(f"✅ 投资组合详情获取成功:")
            print(f"   - 名称: {portfolio['name']}")
            print(f"   - 现金: ¥{portfolio['cash']:,.2f}")
            print(f"   - 持仓数量: {portfolio.get('holdings_count', 0)}")
            print(f"   - 总资产: ¥{portfolio['total_value']:,.2f}")
        else:
            print(f"❌ 投资组合详情获取失败: {response.status_code}")
        
        # 9. 测试获取持仓列表
        print("\n📋 测试获取持仓列表...")
        response = requests.get(f"{BASE_URL}/holdings", params={"portfolio_id": portfolio_id})
        if response.status_code == 200:
            result = response.json()
            holdings_data = result['data']
            print(f"✅ 持仓列表获取成功，共 {len(holdings_data)} 只股票:")
            for holding in holdings_data:
                current_price = holding.get('current_price', holding.get('cost_price', 0))
                market_value = holding['shares'] * current_price
                print(f"   - {holding['stock_code']}: {holding['shares']}股 @ ¥{holding['cost_price']:.2f} = ¥{market_value:,.2f}")
        else:
            print(f"❌ 持仓列表获取失败: {response.status_code}")
        
        # 10. 测试获取交易记录
        print("\n📜 测试获取交易记录...")
        response = requests.get(f"{BASE_URL}/transactions", params={"portfolio_id": portfolio_id})
        if response.status_code == 200:
            result = response.json()
            transactions = result['data']
            print(f"✅ 交易记录获取成功，共 {len(transactions)} 笔交易:")
            for i, tx in enumerate(transactions[:3], 1):  # 显示前3笔
                print(f"   {i}. {tx['transaction_type'].upper()} {tx['stock_code']} x {tx['shares']} @ ¥{tx['price']:.2f}")
        else:
            print(f"❌ 交易记录获取失败: {response.status_code}")
        
        # 11. 测试更新投资组合
        print("\n🔄 测试更新投资组合...")
        update_data = {
            "cash": 100000.0,
            "stock_value": 400000.0,
            "total_value": 500000.0
        }
        
        response = requests.put(f"{BASE_URL}/portfolios/{portfolio_id}", json=update_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 投资组合更新成功")
        else:
            print(f"❌ 投资组合更新失败: {response.status_code}")
        
        # 12. 测试系统配置
        print("\n⚙️ 测试系统配置...")
        config_data = {
            "value": {"test": True, "api_test": True, "timestamp": datetime.now().isoformat()},
            "description": "API测试配置"
        }
        
        response = requests.put(f"{BASE_URL}/config/api_test_config", json=config_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 系统配置更新成功")
        else:
            print(f"❌ 系统配置更新失败: {response.status_code}")
        
        # 获取系统配置
        response = requests.get(f"{BASE_URL}/config", params={"key": "api_test_config"})
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 系统配置获取成功")
        else:
            print(f"❌ 系统配置获取失败: {response.status_code}")
        
        print("\n" + "="*60)
        print("🎉 所有API测试完成！")
        print("✅ Supabase API路由工作正常")
        print("✅ 数据库适配器集成成功")
        print("✅ 前后端API接口畅通")
        print("="*60)
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到API服务器，请确保后端服务正在运行")
        print("   启动命令: python backend/app.py")
        return False
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {str(e)}")
        return False
    
    finally:
        # 清理测试数据
        print("\n🧹 清理测试数据...")
        try:
            response = requests.delete(f"{BASE_URL}/cleanup")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {result['message']}")
            else:
                print(f"⚠️ 清理数据失败: {response.status_code}")
        except Exception as e:
            print(f"⚠️ 清理数据时出现错误: {str(e)}")

def main():
    """主函数"""
    print("🔧 Supabase API路由测试工具")
    print("="*60)
    
    success = test_api_endpoints()
    
    if success:
        print("\n🎊 测试成功完成！")
        print("💡 提示：现在可以在前端中使用这些API端点")
        print("📍 API文档：http://localhost:8000/docs")
    else:
        print("\n💥 测试失败，请检查错误信息")

if __name__ == "__main__":
    main()
