# 文件操作最佳实践:
# 1. 始终使用 with 语句打开文件
# 2. 避免在循环中重复打开同一文件
# 3. 大文件处理时考虑分块读取
# 4. 异常情况下确保文件正确关闭

#!/usr/bin/env python3
"""
测试阿里云Ubuntu服务器连接和服务状态
"""

import requests
import subprocess
import json
from datetime import datetime

def test_server_connectivity():
    """测试服务器连通性"""
    print("🔍 测试服务器连通性:")
    
    # 测试主域名连接
    endpoints = [
        "https://api.aigupiao.me/health",
        "https://aigupiao.me/health"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=15)
            if response.status_code == 200:
                print(f"  ✅ {endpoint}: 连接成功")
                try:
                    data = response.json()
                    print(f"     版本: {data.get('data', {}).get('version', 'N/A')}")
                    print(f"     状态: {data.get('data', {}).get('status', 'N/A')}")
                except:
                    print(f"     响应: {response.text[:100]}...")
            else:
                print(f"  ⚠️ {endpoint}: 状态码 {response.status_code}")
        except Exception as e:
            print(f"  ❌ {endpoint}: 连接失败 - {e}")

def test_ubuntu_services():
    """测试Ubuntu服务状态"""
    print("\n🐧 测试Ubuntu服务状态:")
    
    # 通过API检查服务状态
    try:
        response = requests.get("https://api.aigupiao.me/api/system/status", timeout=15)
        if response.status_code == 200:
            data = response.json()
            print("  ✅ 系统状态API可用")
            
            if 'data' in data:
                system_info = data['data']
                print(f"     CPU使用率: {system_info.get('cpu_percent', 'N/A')}%")
                print(f"     内存使用率: {system_info.get('memory_percent', 'N/A')}%")
                print(f"     磁盘使用率: {system_info.get('disk_percent', 'N/A')}%")
        else:
            print(f"  ❌ 系统状态API: 状态码 {response.status_code}")
    except Exception as e:
        print(f"  ❌ 系统状态API: 连接失败 - {e}")

def test_trading_api():
    """测试交易API"""
    print("\n📈 测试交易API:")
    
    endpoints = [
        ("股票报价", "https://api.aigupiao.me/api/stock/quote?symbol=000001"),
        ("市场数据", "https://api.aigupiao.me/api/market/summary"),
        ("Agent状态", "https://api.aigupiao.me/api/agent/status")
    ]
    
    for name, endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=15)
            if response.status_code == 200:
                print(f"  ✅ {name}: 可用")
                try:
                    data = response.json()
                    if 'data' in data:
                        print(f"     数据: {str(data['data'])[:100]}...")
                except:
                    pass
            else:
                print(f"  ❌ {name}: 状态码 {response.status_code}")
        except Exception as e:
            print(f"  ❌ {name}: 连接失败 - {e}")

def test_database_connection():
    """测试数据库连接"""
    print("\n🗄️ 测试数据库连接:")
    
    try:
        response = requests.get("https://api.aigupiao.me/api/database/health", timeout=15)
        if response.status_code == 200:
            data = response.json()
            print("  ✅ 数据库连接正常")
            if 'data' in data:
                db_info = data['data']
                print(f"     数据库类型: {db_info.get('type', 'N/A')}")
                print(f"     连接状态: {db_info.get('status', 'N/A')}")
        else:
            print(f"  ❌ 数据库健康检查: 状态码 {response.status_code}")
    except Exception as e:
        print(f"  ❌ 数据库健康检查: 连接失败 - {e}")

def test_nginx_status():
    """测试Nginx状态"""
    print("\n🌐 测试Nginx状态:")
    
    try:
        # 测试Nginx状态页面
        response = requests.get("https://api.aigupiao.me/nginx_status", timeout=15)
        if response.status_code == 200:
            print("  ✅ Nginx状态页面可用")
            print(f"     响应: {response.text[:200]}...")
        else:
            print(f"  ⚠️ Nginx状态页面: 状态码 {response.status_code}")
    except Exception as e:
        print(f"  ❌ Nginx状态页面: 连接失败 - {e}")

def test_websocket_connection():
    """测试WebSocket连接"""
    print("\n🔌 测试WebSocket连接:")
    
    try:
        # 简单的WebSocket连接测试
        import websocket
        
        def on_message(ws, message):
            print(f"  ✅ WebSocket消息接收: {message[:100]}...")
            ws.close()
        
        def on_error(ws, error):
            print(f"  ❌ WebSocket错误: {error}")
        
        def on_open(ws):
            print("  ✅ WebSocket连接已建立")
            ws.send('{"type": "ping"}')
        
        ws = websocket.WebSocketApp("wss://api.aigupiao.me/ws",
                                  on_message=on_message,
                                  on_error=on_error,
                                  on_open=on_open)
        ws.run_forever(timeout=10)
        
    except ImportError:
        print("  ⚠️ WebSocket库未安装,跳过测试")
    except Exception as e:
        print(f"  ❌ WebSocket连接失败: {e}")

if __name__ == "__main__":
    print(f"🔧 Ubuntu服务器连接测试 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    test_server_connectivity()
    test_ubuntu_services()
    test_trading_api()
    test_database_connection()
    test_nginx_status()
    test_websocket_connection()
    
    print("\n" + "=" * 60)
    print("✅ 测试完成")
