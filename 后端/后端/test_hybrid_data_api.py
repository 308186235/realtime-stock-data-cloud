#!/usr/bin/env python3
"""
测试混合数据源API
验证股票实时数据 + 本地交易数据的整合
"""

import json
import requests
from datetime import datetime
from pathlib import Path

class HybridDataAPITester:
    """混合数据源API测试器"""
    
    def __init__(self):
        # 测试API地址 (部署后需要更新)
        self.api_base = "https://api.aigupiao.me"  # 或者Worker的默认URL
        
        # 测试端点
        self.endpoints = {
            "root": "/",
            "health": "/health",
            "agent_complete": "/api/agent/complete-data",
            "stock_realtime": "/api/stock/realtime",
            "local_positions": "/api/local-trading/positions",
            "local_balance": "/api/local-trading/balance",
            "data_status": "/api/data-sources/status"
        }
    
    def test_endpoint(self, name, path, params=None):
        """测试单个端点"""
        url = f"{self.api_base}{path}"
        
        try:
            print(f"\n🔍 测试: {name}")
            print(f"   URL: {url}")
            
            if params:
                print(f"   参数: {params}")
                url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])
            
            response = requests.get(url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ 响应成功: {response.status_code}")
                print(f"   响应时间: {response.elapsed.total_seconds():.2f}秒")
                
                # 分析响应数据
                if 'success' in data:
                    print(f"   API状态: {'成功' if data['success'] else '失败'}")
                
                if 'data' in data:
                    response_data = data['data']
                    
                    # 显示关键信息
                    if 'message' in response_data:
                        print(f"   消息: {response_data['message']}")
                    
                    if 'timestamp' in response_data:
                        print(f"   时间戳: {response_data['timestamp']}")
                    
                    if 'data_sources' in response_data:
                        print(f"   数据源状态: {response_data['data_sources']}")
                    
                    if 'source' in response_data:
                        print(f"   数据来源: {response_data['source']}")
                    
                    if 'api_source' in response_data:
                        print(f"   API来源: {response_data['api_source']}")
                    
                    # 特定端点的详细信息
                    if name == "Agent完整数据":
                        self.analyze_agent_data(response_data)
                    elif name == "股票实时数据":
                        self.analyze_stock_data(response_data)
                    elif name == "本地持仓数据":
                        self.analyze_positions_data(response_data)
                    elif name == "本地余额数据":
                        self.analyze_balance_data(response_data)
                    elif name == "数据源状态":
                        self.analyze_data_sources_status(response_data)
                
                return True, data
                
            else:
                print(f"❌ 响应失败: {response.status_code}")
                print(f"   错误信息: {response.text[:200]}...")
                return False, None
                
        except requests.exceptions.Timeout:
            print("⏰ 请求超时")
            return False, None
        except requests.exceptions.ConnectionError:
            print("🔌 连接失败")
            return False, None
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            return False, None
    
    def analyze_agent_data(self, data):
        """分析Agent完整数据"""
        print("   📊 Agent数据分析:")
        
        if 'stock_data' in data:
            stock_count = len(data['stock_data'].get('stocks', []))
            print(f"     股票数据: {stock_count} 只股票")
        
        if 'trading_data' in data:
            trading_data = data['trading_data']
            
            if 'positions' in trading_data:
                positions = trading_data['positions'].get('positions', [])
                print(f"     持仓数据: {len(positions)} 只持仓")
            
            if 'balance' in trading_data:
                balance = trading_data['balance'].get('balance', {})
                total_assets = balance.get('total_assets', 0)
                print(f"     余额数据: 总资产 ¥{total_assets:,.2f}")
        
        if 'analysis_context' in data:
            context = data['analysis_context']
            market_status = context.get('market_status', '未知')
            print(f"     市场状态: {market_status}")
    
    def analyze_stock_data(self, data):
        """分析股票数据"""
        if 'stocks' in data:
            stocks = data['stocks']
            print(f"   📈 股票数据: {len(stocks)} 只股票")
            
            for stock in stocks[:3]:  # 显示前3只
                code = stock.get('code', '未知')
                name = stock.get('name', '未知')
                price = stock.get('current_price', 0)
                print(f"     {code} {name}: ¥{price}")
    
    def analyze_positions_data(self, data):
        """分析持仓数据"""
        if 'positions' in data:
            positions = data['positions']
            print(f"   📊 持仓数据: {len(positions)} 只持仓")
            
            total_value = 0
            for pos in positions:
                code = pos.get('stock_code', '未知')
                name = pos.get('stock_name', '未知')
                value = pos.get('market_value', 0)
                total_value += value
                print(f"     {code} {name}: ¥{value:,.2f}")
            
            print(f"   💰 总市值: ¥{total_value:,.2f}")
    
    def analyze_balance_data(self, data):
        """分析余额数据"""
        if 'balance' in data:
            balance = data['balance']
            cash = balance.get('available_cash', 0)
            assets = balance.get('total_assets', 0)
            profit = balance.get('total_profit_loss', 0)
            
            print(f"   💰 余额分析:")
            print(f"     可用资金: ¥{cash:,.2f}")
            print(f"     总资产: ¥{assets:,.2f}")
            print(f"     总盈亏: ¥{profit:,.2f}")
    
    def analyze_data_sources_status(self, data):
        """分析数据源状态"""
        if 'data_sources' in data:
            sources = data['data_sources']
            print(f"   🔍 数据源状态:")
            
            for source_name, source_info in sources.items():
                status = source_info.get('status', '未知')
                status_icon = "✅" if status == 'connected' else "❌"
                print(f"     {status_icon} {source_name}: {status}")
                
                if 'description' in source_info:
                    print(f"       描述: {source_info['description']}")
                
                if 'last_update' in source_info and source_info['last_update']:
                    print(f"       最后更新: {source_info['last_update']}")
    
    def run_comprehensive_test(self):
        """运行综合测试"""
        print("🚀 混合数据源API综合测试")
        print("=" * 60)
        
        test_results = {}
        
        # 1. 基础端点测试
        print("\n📋 第一阶段: 基础端点测试")
        
        basic_tests = [
            ("根路径", "root"),
            ("健康检查", "health"),
            ("数据源状态", "data_status")
        ]
        
        for name, endpoint_key in basic_tests:
            success, data = self.test_endpoint(name, self.endpoints[endpoint_key])
            test_results[endpoint_key] = {"success": success, "data": data}
        
        # 2. 数据端点测试
        print("\n📋 第二阶段: 数据端点测试")
        
        data_tests = [
            ("股票实时数据", "stock_realtime", {"codes": "000001,600036,000002"}),
            ("本地持仓数据", "local_positions"),
            ("本地余额数据", "local_balance")
        ]
        
        for test_info in data_tests:
            if len(test_info) == 3:
                name, endpoint_key, params = test_info
                success, data = self.test_endpoint(name, self.endpoints[endpoint_key], params)
            else:
                name, endpoint_key = test_info
                success, data = self.test_endpoint(name, self.endpoints[endpoint_key])
            
            test_results[endpoint_key] = {"success": success, "data": data}
        
        # 3. Agent完整数据测试
        print("\n📋 第三阶段: Agent完整数据测试")
        
        success, data = self.test_endpoint(
            "Agent完整数据", 
            self.endpoints["agent_complete"],
            {"stocks": "000001,600036,000002"}
        )
        test_results["agent_complete"] = {"success": success, "data": data}
        
        # 4. 生成测试报告
        self.generate_test_report(test_results)
        
        return test_results
    
    def generate_test_report(self, test_results):
        """生成测试报告"""
        print("\n" + "=" * 60)
        print("📊 混合数据源API测试报告")
        print("=" * 60)
        print(f"⏰ 测试时间: {datetime.now().isoformat()}")
        
        # 统计测试结果
        total_tests = len(test_results)
        successful_tests = sum(1 for result in test_results.values() if result["success"])
        success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"\n📈 测试统计:")
        print(f"   总测试数: {total_tests}")
        print(f"   成功数: {successful_tests}")
        print(f"   成功率: {success_rate:.1f}%")
        
        # 详细结果
        print(f"\n📋 详细结果:")
        for endpoint, result in test_results.items():
            status_icon = "✅" if result["success"] else "❌"
            print(f"   {status_icon} {endpoint}: {'成功' if result['success'] else '失败'}")
        
        # 数据源分析
        if "data_status" in test_results and test_results["data_status"]["success"]:
            status_data = test_results["data_status"]["data"]
            if status_data and "data" in status_data:
                sources = status_data["data"].get("data_sources", {})
                
                print(f"\n🔍 数据源状态:")
                for source_name, source_info in sources.items():
                    status = source_info.get("status", "未知")
                    status_icon = "✅" if status == "connected" else "❌"
                    print(f"   {status_icon} {source_name}: {status}")
        
        # 建议和结论
        print(f"\n💡 测试结论:")
        if success_rate >= 80:
            print("🎉 混合数据源API工作正常!")
            print("✅ 股票实时数据和本地交易数据都能正常获取")
            print("✅ Agent可以获得完整的数据分析基础")
        elif success_rate >= 50:
            print("⚠️ 混合数据源API部分正常")
            print("📝 部分数据源可能需要配置或修复")
        else:
            print("❌ 混合数据源API存在问题")
            print("🔧 需要检查API部署和数据源配置")
        
        print("=" * 60)

def main():
    """主函数"""
    print("🔍 注意: 请确保API已正确部署到Cloudflare")
    print("如果使用Worker默认URL,请更新脚本中的api_base地址")
    print()
    
    tester = HybridDataAPITester()
    test_results = tester.run_comprehensive_test()
    
    # 检查是否有成功的测试
    has_success = any(result["success"] for result in test_results.values())
    
    if has_success:
        print("\n🎯 测试完成,部分或全部功能正常!")
    else:
        print("\n💥 测试完成,但所有端点都失败了!")
        print("🔧 请检查:")
        print("1. API是否已正确部署")
        print("2. 域名配置是否正确")
        print("3. 网络连接是否正常")
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    main()
