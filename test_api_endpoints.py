"""
测试API端点
验证新创建的API端点是否正常工作
"""

import requests
import json
from datetime import datetime

class APITester:
    """API测试器"""
    
    def __init__(self, base_url="https://api.aigupiao.me"):
        self.base_url = base_url
        self.test_results = {}
    
    def test_endpoint(self, endpoint, method="GET", data=None):
        """测试单个端点"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=10)
            else:
                return {"success": False, "error": f"不支持的方法: {method}"}
            
            result = {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
                "content_type": response.headers.get("content-type", ""),
                "response_size": len(response.content)
            }
            
            if response.status_code == 200:
                try:
                    result["data"] = response.json()
                except:
                    result["data"] = response.text[:200]
            else:
                result["error"] = response.text[:200]
            
            return result
            
        except requests.exceptions.Timeout:
            return {"success": False, "error": "请求超时"}
        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "连接失败"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🧪 API端点测试开始")
        print("=" * 60)
        print(f"测试目标: {self.base_url}")
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # 定义要测试的端点
        endpoints = [
            # Agent分析API
            ("Agent分析", "/api/agent-analysis", "GET"),
            ("Agent状态", "/api/agent-analysis/status", "GET"),
            ("Agent指标", "/api/agent-analysis/metrics", "GET"),
            ("Agent配置", "/api/agent-analysis/config", "GET"),
            ("Agent日志", "/api/agent-analysis/logs", "GET"),
            
            # 账户余额API
            ("账户余额", "/api/account-balance", "GET"),
            ("余额摘要", "/api/account-balance/summary", "GET"),
            ("持仓信息", "/api/account-balance/positions", "GET"),
            ("绩效指标", "/api/account-balance/performance", "GET"),
            
            # 茶股帮API
            ("茶股帮健康检查", "/api/chagubang/health", "GET"),
            ("茶股帮统计", "/api/chagubang/stats", "GET"),
            ("茶股帮股票数据", "/api/chagubang/stocks?limit=5", "GET"),
            ("茶股帮市场概览", "/api/chagubang/market/overview", "GET"),
            
            # 其他现有API
            ("实时数据", "/api/realtime-data/stocks", "GET"),
            ("技术指标", "/api/technical/indicators", "GET"),
        ]
        
        # 执行测试
        for test_name, endpoint, method in endpoints:
            print(f"\n🔍 测试: {test_name}")
            print(f"端点: {method} {endpoint}")
            print("-" * 40)
            
            result = self.test_endpoint(endpoint, method)
            self.test_results[test_name] = result
            
            if result["success"]:
                print(f"✅ 成功 ({result['status_code']}) - {result['response_time']:.3f}s")
                if "data" in result and isinstance(result["data"], dict):
                    if result["data"].get("success"):
                        print(f"   数据: {result['data'].get('message', '正常响应')}")
                    else:
                        print(f"   错误: {result['data'].get('error', '未知错误')}")
            else:
                print(f"❌ 失败: {result.get('error', '未知错误')}")
                if "status_code" in result:
                    print(f"   状态码: {result['status_code']}")
        
        # 生成测试报告
        self.generate_report()
    
    def generate_report(self):
        """生成测试报告"""
        print("\n" + "=" * 60)
        print("📊 测试报告")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results.values() if r["success"])
        
        print(f"总测试数: {total_tests}")
        print(f"成功数: {successful_tests}")
        print(f"失败数: {total_tests - successful_tests}")
        print(f"成功率: {successful_tests/total_tests*100:.1f}%")
        
        print("\n📋 详细结果:")
        for test_name, result in self.test_results.items():
            status = "✅" if result["success"] else "❌"
            print(f"{status} {test_name}")
            if not result["success"]:
                print(f"    错误: {result.get('error', '未知错误')}")
        
        print("\n💡 建议:")
        if successful_tests == total_tests:
            print("🎉 所有API端点都正常工作！")
        else:
            failed_tests = [name for name, result in self.test_results.items() if not result["success"]]
            print("需要修复的端点:")
            for test_name in failed_tests:
                print(f"  • {test_name}")
            
            print("\n可能的解决方案:")
            print("1. 检查后端服务是否正在运行")
            print("2. 确认API路由配置正确")
            print("3. 检查Cloudflare部署状态")
            print("4. 验证域名DNS解析")
        
        print(f"\n测试完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def main():
    """主函数"""
    print("🚀 API端点测试工具")
    print("用于验证前端调用的API端点是否正常工作")
    print()
    
    # 创建测试器
    tester = APITester()
    
    # 运行测试
    try:
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断测试")
    except Exception as e:
        print(f"\n❌ 测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
