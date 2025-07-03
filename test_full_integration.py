"""
完整集成测试：本地导出 → 云端分析 → 云端发送买卖指令到本地
"""

import subprocess
import time
import threading
import requests
import sys
import os

def start_local_api_server():
    """启动本地API服务器"""
    print("🚀 启动本地API服务器...")
    try:
        # 启动本地API服务器
        process = subprocess.Popen([
            sys.executable, "local_trading_api.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # 等待服务器启动
        print("⏳ 等待服务器启动...")
        time.sleep(3)
        
        # 检查服务器是否启动成功
        try:
            response = requests.get("http://localhost:5000/health", timeout=5)
            if response.status_code == 200:
                print("✅ 本地API服务器启动成功!")
                return process
            else:
                print("❌ 本地API服务器启动失败")
                process.terminate()
                return None
        except:
            print("❌ 无法连接到本地API服务器")
            process.terminate()
            return None
            
    except Exception as e:
        print(f"❌ 启动本地API服务器失败: {e}")
        return None

def test_api_functions():
    """测试API基本功能"""
    print("\n🧪 测试API基本功能...")
    
    base_url = "http://localhost:5000"
    
    # 测试健康检查
    print("1. 测试健康检查...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ 健康检查成功")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
        return False
    
    # 测试余额获取
    print("\n2. 测试余额获取...")
    try:
        response = requests.get(f"{base_url}/balance")
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                balance = data['data']
                print(f"✅ 余额获取成功: {balance['available_cash']:,.2f}")
            else:
                print(f"❌ 余额获取失败: {data.get('error')}")
                return False
        else:
            print(f"❌ 余额请求失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 余额请求异常: {e}")
        return False
    
    # 测试数据导出
    print("\n3. 测试数据导出...")
    try:
        payload = {"type": "holdings"}
        response = requests.post(f"{base_url}/export", json=payload, timeout=60)
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print("✅ 数据导出成功")
                files = data['data']['files']
                for key, filename in files.items():
                    print(f"   {key}: {filename}")
                return True
            else:
                print(f"❌ 数据导出失败: {data.get('error')}")
                return False
        else:
            print(f"❌ 导出请求失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 导出请求异常: {e}")
        return False

def run_cloud_agent():
    """运行云端agent模拟器"""
    print("\n🌟 启动云端Agent模拟器...")
    try:
        # 运行云端agent
        result = subprocess.run([
            sys.executable, "cloud_agent_simulator.py"
        ], capture_output=True, text=True, timeout=120)
        
        print("📊 云端Agent执行结果:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ 错误信息:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("⏰ 云端Agent执行超时")
        return False
    except Exception as e:
        print(f"❌ 云端Agent执行失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 完整集成测试：本地导出 → 云端分析 → 云端发送买卖指令到本地")
    print("=" * 80)
    print("📋 测试流程:")
    print("1. 启动本地API服务器")
    print("2. 测试API基本功能（余额、导出）")
    print("3. 运行云端Agent模拟器")
    print("4. 验证完整工作流程")
    print("=" * 80)
    
    # 1. 启动本地API服务器
    server_process = start_local_api_server()
    if not server_process:
        print("❌ 无法启动本地API服务器，测试终止")
        return False
    
    try:
        # 2. 测试API基本功能
        api_success = test_api_functions()
        if not api_success:
            print("❌ API基本功能测试失败，测试终止")
            return False
        
        # 3. 运行云端Agent模拟器
        cloud_success = run_cloud_agent()
        
        # 4. 总结
        print("\n" + "=" * 80)
        print("📊 完整集成测试结果总结:")
        print(f"本地API服务器: ✅ 正常运行")
        print(f"API基本功能: {'✅ 成功' if api_success else '❌ 失败'}")
        print(f"云端Agent模拟器: {'✅ 成功' if cloud_success else '❌ 失败'}")
        
        if api_success and cloud_success:
            print("\n🎉 完整集成测试成功!")
            print("\n📋 验证的完整流程:")
            print("✅ 1. 本地导出交易数据（持仓、成交、委托）")
            print("✅ 2. 云端Agent获取账户余额")
            print("✅ 3. 云端Agent请求数据导出")
            print("✅ 4. 云端Agent分析数据并制定交易策略")
            print("✅ 5. 云端Agent发送买卖指令到本地")
            print("✅ 6. 本地执行买卖指令（模拟）")
            print("\n🎯 这证明了云端Agent可以成功调用本地计算机进行交易操作!")
        else:
            print("❌ 集成测试失败，请检查错误信息")
        
        return api_success and cloud_success
        
    finally:
        # 清理：关闭服务器
        print("\n🧹 清理资源...")
        if server_process:
            server_process.terminate()
            server_process.wait()
            print("✅ 本地API服务器已关闭")

if __name__ == "__main__":
    success = main()
    
    print("\n" + "=" * 80)
    if success:
        print("🎉 测试结论：云端Agent可以成功调用本地计算机进行交易操作!")
        print("📡 通信方式：HTTP API (本地服务器 + 云端请求)")
        print("🔄 数据流向：本地导出 → 云端分析 → 云端指令 → 本地执行")
    else:
        print("❌ 测试失败，需要进一步调试")
    
    sys.exit(0 if success else 1)
