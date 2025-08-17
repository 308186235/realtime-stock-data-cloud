#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
前后端连接测试工具
"""

import requests
import json
import time
from datetime import datetime

def test_backend_apis():
    """测试后端API"""
    print("🔍 测试后端API连接...")
    
    base_url = "http://localhost:8002"
    
    # 测试的API端点
    endpoints = [
        {"path": "/", "name": "首页"},
        {"path": "/api/health", "name": "健康检查"},
        {"path": "/test", "name": "测试端点"},
        {"path": "/api/stats", "name": "请求统计"},
        {"path": "/api/test/ping", "name": "Ping测试"},
        {"path": "/api/test/echo?message=前端测试", "name": "Echo测试"},
        {"path": "/api/stock/quote?code=000001", "name": "股票报价"},
        {"path": "/api/t-trading/summary", "name": "T+0交易摘要"},
    ]
    
    results = []
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint['path']}"
        try:
            start_time = time.time()
            response = requests.get(url, timeout=10)
            end_time = time.time()
            
            response_time = round((end_time - start_time) * 1000, 2)
            
            if response.status_code == 200:
                print(f"✅ {endpoint['name']}: {response.status_code} ({response_time}ms)")
                results.append({
                    "endpoint": endpoint['name'],
                    "url": url,
                    "status": "success",
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "content_type": response.headers.get('content-type', 'unknown')
                })
            else:
                print(f"⚠️ {endpoint['name']}: {response.status_code}")
                results.append({
                    "endpoint": endpoint['name'],
                    "url": url,
                    "status": "warning",
                    "status_code": response.status_code,
                    "response_time": response_time
                })
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint['name']}: {e}")
            results.append({
                "endpoint": endpoint['name'],
                "url": url,
                "status": "error",
                "error": str(e)
            })
    
    return results

def test_cors_headers():
    """测试CORS头"""
    print("\n🔍 测试CORS配置...")
    
    url = "http://localhost:8002/api/health"
    
    try:
        # 模拟前端请求
        headers = {
            'Origin': 'http://localhost:8080',  # 前端开发服务器
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        
        # 发送OPTIONS预检请求
        response = requests.options(url, headers=headers, timeout=5)
        
        print(f"OPTIONS请求状态: {response.status_code}")
        
        # 检查CORS头
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
            'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials')
        }
        
        print("CORS头信息:")
        for header, value in cors_headers.items():
            if value:
                print(f"  ✅ {header}: {value}")
            else:
                print(f"  ❌ {header}: 未设置")
        
        return cors_headers
        
    except Exception as e:
        print(f"❌ CORS测试失败: {e}")
        return None

def test_post_request():
    """测试POST请求"""
    print("\n🔍 测试POST请求...")
    
    url = "http://localhost:8002/api/test/echo"
    data = {
        "message": "前端POST测试",
        "timestamp": datetime.now().isoformat(),
        "source": "frontend_test"
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ POST请求成功: {response.status_code}")
            try:
                result = response.json()
                print(f"✅ 响应数据: {json.dumps(result, ensure_ascii=False, indent=2)}")
                return True
            except json.JSONDecodeError:
                print(f"⚠️ 响应不是JSON格式: {response.text[:100]}...")
                return False
        else:
            print(f"⚠️ POST请求失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ POST请求错误: {e}")
        return False

def generate_frontend_test_code():
    """生成前端测试代码"""
    print("\n📝 生成前端测试代码...")
    
    test_code = """
// 前端连接测试代码 (JavaScript)
const API_BASE_URL = 'http://localhost:8002';

// 测试GET请求
async function testGetRequest() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/health`);
        const data = await response.json();
        console.log('✅ GET请求成功:', data);
        return true;
    } catch (error) {
        console.error('❌ GET请求失败:', error);
        return false;
    }
}

// 测试POST请求
async function testPostRequest() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/test/echo`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: '前端测试消息',
                timestamp: new Date().toISOString()
            })
        });
        const data = await response.json();
        console.log('✅ POST请求成功:', data);
        return true;
    } catch (error) {
        console.error('❌ POST请求失败:', error);
        return false;
    }
}

// 运行所有测试
async function runAllTests() {
    console.log('🚀 开始前端连接测试...');
    
    const getResult = await testGetRequest();
    const postResult = await testPostRequest();
    
    if (getResult && postResult) {
        console.log('🎉 前后端连接测试全部通过!');
    } else {
        console.log('⚠️ 部分测试失败,请检查配置');
    }
}

// 执行测试
runAllTests();
"""
    
    # 保存测试代码到文件
    with open('frontend_connection_test.js', 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    print("✅ 前端测试代码已保存到: frontend_connection_test.js")

def main():
    """主函数"""
    print("=" * 60)
    print("🔗 前后端连接测试工具")
    print("=" * 60)
    
    # 1. 测试后端API
    api_results = test_backend_apis()
    
    # 2. 测试CORS配置
    cors_results = test_cors_headers()
    
    # 3. 测试POST请求
    post_result = test_post_request()
    
    # 4. 生成前端测试代码
    generate_frontend_test_code()
    
    # 5. 生成测试报告
    print("\n" + "=" * 60)
    print("📋 连接测试报告")
    print("=" * 60)
    
    # API测试结果
    success_count = len([r for r in api_results if r.get('status') == 'success'])
    total_count = len(api_results)
    
    print(f"\n🔗 API连接测试: {success_count}/{total_count} 成功")
    
    if success_count == total_count:
        print("✅ 所有API端点都可正常访问")
    else:
        print("⚠️ 部分API端点有问题")
    
    # CORS测试结果
    print(f"\n🌐 CORS配置: {'✅ 正常' if cors_results else '❌ 有问题'}")
    
    # POST测试结果
    print(f"📤 POST请求: {'✅ 正常' if post_result else '❌ 有问题'}")
    
    # 总结
    if success_count == total_count and cors_results and post_result:
        print(f"\n🎉 前后端连接完全正常!")
        print(f"🌐 后端服务器: http://localhost:8002")
        print(f"📱 前端可以正常连接后端API")
    else:
        print(f"\n⚠️ 连接存在问题,需要进一步检查")
    
    # 保存详细报告
    report = {
        "timestamp": datetime.now().isoformat(),
        "backend_url": "http://localhost:8002",
        "api_tests": api_results,
        "cors_test": cors_results,
        "post_test": post_result,
        "summary": {
            "api_success_rate": f"{success_count}/{total_count}",
            "cors_ok": bool(cors_results),
            "post_ok": post_result,
            "overall_status": "success" if (success_count == total_count and cors_results and post_result) else "partial"
        }
    }
    
    with open('frontend_backend_connection_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 详细报告已保存到: frontend_backend_connection_report.json")

if __name__ == "__main__":
    main()
