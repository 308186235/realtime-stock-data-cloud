#!/usr/bin/env python3
"""
测试本地导出API
"""

import requests
import json

def test_local_export():
    """测试本地导出API"""
    print("🔧 测试本地导出API")
    print("=" * 40)
    
    # 测试不同的导出类型
    export_tests = [
        {"data_type": "holdings"},
        {"data_type": "balance"},
        {"data_type": "all"},
        {"data_type": "status"}
    ]
    
    for test_data in export_tests:
        print(f"\n🔥 测试导出: {test_data['data_type']}")
        
        try:
            response = requests.post(
                "http://localhost:8888/export",
                json=test_data,
                timeout=10
            )
            
            print(f"   状态码: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print("   ✅ 成功")
                    print(f"   📊 响应: {json.dumps(data, indent=2, ensure_ascii=False)[:200]}...")
                except:
                    print("   ✅ 成功 (非JSON响应)")
                    print(f"   📄 内容: {response.text[:200]}...")
            else:
                print(f"   ❌ 失败")
                print(f"   📄 错误: {response.text[:200]}...")
                
        except Exception as e:
            print(f"   ❌ 异常: {e}")
    
    # 测试其他端点
    print(f"\n🔥 测试其他端点")
    
    other_tests = [
        {"url": "http://localhost:8888/", "name": "根路径"},
        {"url": "http://localhost:8888/health", "name": "健康检查"}
    ]
    
    for test in other_tests:
        print(f"\n🔥 测试: {test['name']}")
        print(f"   URL: {test['url']}")
        
        try:
            response = requests.get(test['url'], timeout=10)
            print(f"   状态码: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print("   ✅ 成功")
                    print(f"   📊 响应: {json.dumps(data, indent=2, ensure_ascii=False)[:200]}...")
                except:
                    print("   ✅ 成功 (非JSON响应)")
                    print(f"   📄 内容: {response.text[:200]}...")
            else:
                print(f"   ❌ 失败: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 异常: {e}")

if __name__ == "__main__":
    test_local_export()
