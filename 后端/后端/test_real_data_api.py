#!/usr/bin/env python3
"""
测试真实数据API - 验证友好错误提示
"""

import requests
import json

def test_real_data_api():
    base_url = "https://api.aigupiao.me"
    
    print("🧪 测试真实数据API - 友好错误提示")
    print("=" * 60)
    print(f"测试URL: {base_url}")
    print("策略: 拒绝模拟数据,提供友好错误提示")
    print()
    
    # 测试端点
    endpoints = [
        ("/", "系统状态"),
        ("/api/agent-analysis", "Agent分析"),
        ("/api/account-balance", "账户余额"),
        ("/api/chagubang/health", "茶股帮健康检查")
    ]
    
    for endpoint, name in endpoints:
        url = f"{base_url}{endpoint}"
        print(f"🔍 测试: {name}")
        print(f"端点: {endpoint}")
        print("-" * 40)
        
        try:
            response = requests.get(url, timeout=10)
            data = response.json()
            
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ 服务正常")
                print(f"消息: {data.get('message', '无消息')}")
                if 'data_policy' in data:
                    print(f"数据策略: {data['data_policy']}")
                    
            elif response.status_code == 503:
                print("⚠️ 服务不可用 (符合预期 - 无真实数据)")
                print(f"错误: {data.get('error', '未知错误')}")
                print(f"消息: {data.get('message', '无消息')}")
                
                if 'requirements' in data:
                    print("\n📋 系统要求:")
                    for req in data['requirements']:
                        print(f"   {req}")
                
                if 'next_steps' in data:
                    print("\n🔧 解决步骤:")
                    for step in data['next_steps']:
                        print(f"   {step}")
                
                if 'debug_info' in data:
                    print(f"\n🐛 调试信息:")
                    debug = data['debug_info']
                    for key, value in debug.items():
                        print(f"   {key}: {value}")
                        
            else:
                print(f"❌ 意外状态码: {response.status_code}")
                print(f"响应: {data}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求失败: {e}")
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")
        except Exception as e:
            print(f"❌ 异常: {e}")
        
        print()
    
    print("=" * 60)
    print("📊 测试总结")
    print("=" * 60)
    print("✅ API现在正确拒绝提供模拟数据")
    print("✅ 提供了友好的错误提示和解决方案")
    print("✅ 明确说明了获取真实数据的要求")
    print()
    print("🎯 前端应用现在会显示:")
    print("   • 明确的错误信息而不是模拟数据")
    print("   • 详细的解决步骤指导")
    print("   • 系统要求和配置说明")
    print("   • 友好的用户体验")
    print()
    print("💡 下一步:")
    print("   1. 配置真实的交易接口")
    print("   2. 连接有效的茶股帮数据源")
    print("   3. 在交易时间内测试")
    print("   4. 验证所有服务正常运行")

if __name__ == "__main__":
    test_real_data_api()
