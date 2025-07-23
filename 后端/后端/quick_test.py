#!/usr/bin/env python3
import requests
import time

def quick_test():
    """快速测试 Worker 是否工作"""
    print("🧪 快速测试 Worker 路由...")
    print("="*50)
    
    test_urls = [
        "https://api.aigupiao.me/test",
        "https://app.aigupiao.me/test", 
        "https://aigupiao.me/test"
    ]
    
    for url in test_urls:
        try:
            print(f"测试: {url}")
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ 成功 - 状态码: {response.status_code}")
                if "Worker路由成功" in response.text or "测试成功" in response.text:
                    print("🎉 Worker 正在工作!")
            else:
                print(f"❌ 失败 - 状态码: {response.status_code}")
        except Exception as e:
            print(f"❌ 错误: {e}")
        
        print("-" * 30)
        time.sleep(1)
    
    print("\n🔍 健康检查...")
    try:
        response = requests.get("https://api.aigupiao.me/health", timeout=10)
        if response.status_code == 200:
            print("✅ 健康检查成功")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 健康检查错误: {e}")

if __name__ == "__main__":
    quick_test()
