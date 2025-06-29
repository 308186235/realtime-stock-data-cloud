import requests
import json
import time

API_BASE_URL = "http://localhost:8000"

def test_endpoints():
    """测试主要API端点"""
    endpoints = [
        {"url": "/api/auth/test", "method": "GET", "name": "认证测试端点"},
        {"url": "/api/backtesting/test", "method": "GET", "name": "回测测试端点"},
        {"url": "/api/docs", "method": "GET", "name": "API文档"},
        {"url": "/api/auth/token", "method": "POST", "name": "登录API"},
        {"url": "/api/auth/me", "method": "GET", "name": "用户信息API", "auth": True},
        {"url": "/api/backtesting/run", "method": "POST", "name": "回测执行API", "auth": True}
    ]
    
    print("开始测试API连接...\n")
    time.sleep(1)  # 等待服务器完全启动
    
    # 跟踪认证令牌
    auth_token = None
    
    for endpoint in endpoints:
        url = API_BASE_URL + endpoint["url"]
        method = endpoint["method"]
        name = endpoint["name"]
        needs_auth = endpoint.get("auth", False)
        
        print(f"测试 {name} - {url} [{method}]")
        
        try:
            headers = {}
            if needs_auth and auth_token:
                headers["Authorization"] = f"Bearer {auth_token}"
                
            if method == "GET":
                response = requests.get(url, headers=headers)
            elif method == "POST":
                response = requests.post(url, headers=headers)
            else:
                print(f"不支持的方法: {method}")
                continue
                
            print(f"  状态码: {response.status_code}")
            
            if response.status_code == 200:
                if url.endswith("/docs"):
                    print(f"  内容长度: {len(response.text)} 字符")
                    print(f"  结果: {'✓ 成功' if len(response.text) > 100 else '✗ 失败'}")
                else:
                    try:
                        result = response.json()
                        print(f"  响应JSON: {json.dumps(result, ensure_ascii=False, indent=2)[:200]}...")
                        print("  结果: ✓ 成功")
                        
                        # 如果是登录API，保存令牌用于后续请求
                        if url.endswith("/token"):
                            auth_token = result.get("access_token")
                            print(f"  获取到认证令牌: {auth_token}")
                    except ValueError:
                        print(f"  响应内容: {response.text[:100]}...")
                        print("  结果: ✗ 无法解析JSON")
            else:
                print(f"  响应内容: {response.text}")
                print("  结果: ✗ 请求失败")
        except requests.RequestException as e:
            print(f"  请求异常: {e}")
            print("  结果: ✗ 连接失败")
            
        print()  # 空行分隔

if __name__ == "__main__":
    test_endpoints() 