#!/usr/bin/env python3
import requests
import time

def test_worker_routes():
    """测试 Worker 路由"""
    routes = [
        "https://api.aigupiao.me/test",
        "https://app.aigupiao.me/test", 
        "https://mobile.aigupiao.me/test",
        "https://admin.aigupiao.me/test",
        "https://aigupiao.me/test"
    ]
    
    print("🧪 测试 Worker 路由...")
    print("="*50)
    
    for url in routes:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {url} - 成功")
            else:
                print(f"❌ {url} - 状态码: {response.status_code}")
        except Exception as e:
            print(f"❌ {url} - 错误: {e}")
        
        time.sleep(1)
    
    print("\n🔍 测试健康检查...")
    try:
        response = requests.get("https://api.aigupiao.me/health", timeout=10)
        if response.status_code == 200:
            print("✅ 健康检查成功")
            print(f"响应: {response.text}")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 健康检查错误: {e}")

if __name__ == "__main__":
    test_worker_routes()
