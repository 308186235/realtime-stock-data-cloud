#!/usr/bin/env python3
"""
测试当前API的详细响应
"""

import json
import requests

def test_api_endpoints():
    """测试API端点"""
    api_base = "https://api.aigupiao.me"
    
    endpoints = [
        ("根路径", "/"),
        ("健康检查", "/health"),
        ("持仓数据", "/api/local-trading/positions"),
        ("余额数据", "/api/local-trading/balance"),
        ("Agent完整数据", "/api/agent/complete-data")
    ]
    
    print("🔍 测试当前API详细响应")
    print("=" * 60)
    
    for name, path in endpoints:
        url = f"{api_base}{path}"
        print(f"\n🔥 测试: {name}")
        print(f"   URL: {url}")
        
        try:
            response = requests.get(url, timeout=10)
            
            print(f"   状态码: {response.status_code}")
            print(f"   响应时间: {response.elapsed.total_seconds():.2f}秒")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   响应格式: JSON")
                    print(f"   响应大小: {len(json.dumps(data))} 字符")
                    
                    # 显示关键信息
                    if isinstance(data, dict):
                        for key in ['message', 'version', 'data_sources', 'api_source', 'source', 'timestamp']:
                            if key in data:
                                print(f"   {key}: {data[key]}")
                            elif 'data' in data and key in data['data']:
                                print(f"   {key}: {data['data'][key]}")
                    
                    # 显示完整响应（截断）
                    response_str = json.dumps(data, ensure_ascii=False, indent=2)
                    if len(response_str) > 500:
                        print(f"   完整响应: {response_str[:500]}...")
                    else:
                        print(f"   完整响应: {response_str}")
                        
                except json.JSONDecodeError:
                    print(f"   响应格式: 非JSON")
                    print(f"   响应内容: {response.text[:200]}...")
            else:
                print(f"   错误响应: {response.text[:200]}...")
                
        except Exception as e:
            print(f"   异常: {e}")

if __name__ == "__main__":
    test_api_endpoints()
    input("\n按回车键退出...")
