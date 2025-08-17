import requests
import time
import sys

# API基础URL
BASE_URL = "http://localhost:8000"

def test_auth_test_endpoint():
    """测试认证API测试端点"""
    print("\n测试认证API测试端点...")
    
    # 测试端点
    test_url = f"{BASE_URL}/api/auth/test"
    
    try:
        response = requests.get(test_url)
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            print("✓ 认证API测试端点可访问")
            return True
        else:
            print("✗ 认证API测试端点不可访问")
            return False
    except requests.RequestException as e:
        print(f"✗ 请求异常: {e}")
        return False

def test_backtesting_test_endpoint():
    """测试回测API测试端点"""
    print("\n测试回测API测试端点...")
    
    # 测试端点
    test_url = f"{BASE_URL}/api/backtesting/test"
    
    try:
        response = requests.get(test_url)
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            print("✓ 回测API测试端点可访问")
            return True
        else:
            print("✗ 回测API测试端点不可访问")
            return False
    except requests.RequestException as e:
        print(f"✗ 请求异常: {e}")
        return False

def test_docs_endpoint():
    """测试API文档端点"""
    print("\n测试API文档端点...")
    
    # 测试端点
    test_url = f"{BASE_URL}/api/docs"
    
    try:
        response = requests.get(test_url)
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容长度: {len(response.text)} 字符")
        
        if response.status_code == 200 and len(response.text) > 100:  # 简单验证是否为正常的文档页面
            print("✓ API文档端点可访问")
            return True
        else:
            print("✗ API文档端点不可访问")
            return False
    except requests.RequestException as e:
        print(f"✗ 请求异常: {e}")
        return False

def main():
    """主函数"""
    print("开始简单API端点测试...")
    
    # 等待服务器启动
    print("等待服务器启动...")
    time.sleep(2)
    
    # 测试各端点
    auth_test_ok = test_auth_test_endpoint()
    backtesting_test_ok = test_backtesting_test_endpoint()
    docs_ok = test_docs_endpoint()
    
    # 总结
    print("\n测试结果总结:")
    print(f"认证API测试端点: {'✓' if auth_test_ok else '✗'}")
    print(f"回测API测试端点: {'✓' if backtesting_test_ok else '✗'}")
    print(f"API文档端点: {'✓' if docs_ok else '✗'}")
    
    all_ok = auth_test_ok and backtesting_test_ok and docs_ok
    
    print(f"\n总体结果: {'✓ 所有测试通过' if all_ok else '✗ 部分测试失败'}")
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main()) 
