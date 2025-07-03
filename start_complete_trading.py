#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整交易系统启动器
一键启动云端Agent调用本地电脑交易的完整系统
"""

import subprocess
import time
import sys
import os
import requests
from datetime import datetime

def print_banner():
    """打印启动横幅"""
    print("=" * 80)
    print("🎯 完整云端Agent调用本地电脑交易系统")
    print("=" * 80)
    print(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("系统组件:")
    print("  ✅ 本地交易API服务器")
    print("  ✅ 云端Agent决策系统")
    print("  ✅ WebSocket实时通信")
    print("  ✅ 完整演示和测试")
    print("=" * 80)

def check_dependencies():
    """检查依赖"""
    print("\n🔍 检查系统依赖...")
    
    required_files = [
        "complete_cloud_local_trading_system.py",
        "complete_trading_demo.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ 缺少必要文件:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ 所有依赖文件存在")
    return True

def start_local_system():
    """启动本地交易系统"""
    print("\n🚀 启动本地交易系统...")
    
    try:
        process = subprocess.Popen(
            [sys.executable, "complete_cloud_local_trading_system.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("✅ 本地交易系统启动中...")
        print("📍 服务地址: http://localhost:8888")
        print("📖 API文档: http://localhost:8888/docs")
        
        return process
        
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return None

def wait_for_system_ready():
    """等待系统准备就绪"""
    print("\n⏳ 等待系统准备就绪...")
    
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            response = requests.get("http://localhost:8888/health", timeout=2)
            if response.status_code == 200:
                print("✅ 系统已就绪")
                return True
        except:
            pass
        
        print(f"   等待中... ({attempt + 1}/{max_attempts})")
        time.sleep(2)
    
    print("❌ 系统启动超时")
    return False

def test_system():
    """测试系统功能"""
    print("\n🧪 测试系统功能...")
    
    tests = [
        ("状态检查", "GET", "/status"),
        ("系统信息", "GET", "/"),
        ("健康检查", "GET", "/health")
    ]
    
    all_passed = True
    
    for test_name, method, endpoint in tests:
        try:
            if method == "GET":
                response = requests.get(f"http://localhost:8888{endpoint}", timeout=5)
            
            if response.status_code == 200:
                print(f"✅ {test_name}: 通过")
            else:
                print(f"❌ {test_name}: 失败 (HTTP {response.status_code})")
                all_passed = False
                
        except Exception as e:
            print(f"❌ {test_name}: 异常 ({e})")
            all_passed = False
    
    return all_passed

def run_demo():
    """运行演示"""
    print("\n🎬 运行完整演示...")
    
    try:
        result = subprocess.run(
            [sys.executable, "complete_trading_demo.py"],
            timeout=120,  # 2分钟超时
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ 演示运行成功")
            print("\n📋 演示输出:")
            print(result.stdout)
        else:
            print("❌ 演示运行失败")
            print(f"错误输出: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("⏰ 演示运行超时")
    except Exception as e:
        print(f"❌ 演示运行异常: {e}")

def show_usage_guide():
    """显示使用指南"""
    print("\n📋 使用指南")
    print("-" * 40)
    print("1. 基础API调用:")
    print("   curl http://localhost:8888/status")
    print("   curl http://localhost:8888/health")
    
    print("\n2. 执行交易:")
    print('   curl -X POST http://localhost:8888/trade \\')
    print('        -H "Content-Type: application/json" \\')
    print('        -d \'{"action":"buy","stock_code":"000001","quantity":100,"price":12.5}\'')
    
    print("\n3. Agent决策:")
    print('   curl -X POST http://localhost:8888/agent-decision \\')
    print('        -H "Content-Type: application/json" \\')
    print('        -d \'{"action":"buy","stock_code":"000001","stock_name":"平安银行","quantity":100,"price":12.5,"confidence":0.8,"reason":"技术分析看涨","timestamp":"2024-01-15T10:30:00"}\'')
    
    print("\n4. 查看历史:")
    print("   curl http://localhost:8888/history")
    print("   curl http://localhost:8888/decisions")
    
    print("\n5. WebSocket连接:")
    print("   ws://localhost:8888/ws")

def interactive_menu():
    """交互式菜单"""
    while True:
        print("\n" + "=" * 50)
        print("🎯 完整交易系统控制台")
        print("=" * 50)
        print("1. 查看系统状态")
        print("2. 执行测试交易")
        print("3. 启动云端Agent")
        print("4. 查看交易历史")
        print("5. 查看决策历史")
        print("6. 运行完整演示")
        print("7. 显示使用指南")
        print("0. 退出")
        print("-" * 50)
        
        choice = input("请选择操作 (0-7): ").strip()
        
        if choice == "0":
            print("👋 再见！")
            break
        elif choice == "1":
            check_system_status()
        elif choice == "2":
            execute_test_trade()
        elif choice == "3":
            start_cloud_agent()
        elif choice == "4":
            show_trade_history()
        elif choice == "5":
            show_decision_history()
        elif choice == "6":
            run_demo()
        elif choice == "7":
            show_usage_guide()
        else:
            print("❌ 无效选择，请重试")

def check_system_status():
    """检查系统状态"""
    try:
        response = requests.get("http://localhost:8888/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("\n📊 系统状态:")
            print(f"   - 服务运行: {data.get('service_running')}")
            print(f"   - 交易API: {data.get('trader_api_available')}")
            print(f"   - WebSocket: {data.get('websocket_connected')}")
            print(f"   - 云端连接: {data.get('cloud_connected')}")
            print(f"   - 运行模式: {data.get('mode')}")
        else:
            print(f"❌ 获取状态失败: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ 连接失败: {e}")

def execute_test_trade():
    """执行测试交易"""
    print("\n💰 执行测试交易...")
    
    trade_data = {
        "action": "buy",
        "stock_code": "000001",
        "quantity": 100,
        "price": 12.5
    }
    
    try:
        response = requests.post("http://localhost:8888/trade", json=trade_data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print("✅ 交易执行成功:")
            print(f"   - 消息: {result['message']}")
            print(f"   - 交易ID: {result['trade_id']}")
        else:
            print(f"❌ 交易失败: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ 交易异常: {e}")

def start_cloud_agent():
    """启动云端Agent"""
    print("\n🤖 启动云端Agent...")
    
    try:
        process = subprocess.Popen(
            [sys.executable, "complete_cloud_local_trading_system.py", "agent"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("✅ 云端Agent已启动")
        print("⏳ Agent将运行10秒后自动停止...")
        
        time.sleep(10)
        process.terminate()
        
        print("🛑 云端Agent已停止")
        
    except Exception as e:
        print(f"❌ 启动Agent失败: {e}")

def show_trade_history():
    """显示交易历史"""
    try:
        response = requests.get("http://localhost:8888/history", timeout=5)
        if response.status_code == 200:
            result = response.json()
            trades = result.get('trades', [])
            
            print(f"\n📈 交易历史 (共{len(trades)}笔):")
            for trade in trades[-10:]:  # 显示最近10笔
                print(f"   - {trade.get('action', '').upper()} {trade.get('stock_code')} {trade.get('quantity')}股 @¥{trade.get('price')} [{trade.get('timestamp', '')[:19]}]")
        else:
            print(f"❌ 获取交易历史失败: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ 获取交易历史异常: {e}")

def show_decision_history():
    """显示决策历史"""
    try:
        response = requests.get("http://localhost:8888/decisions", timeout=5)
        if response.status_code == 200:
            result = response.json()
            decisions = result.get('decisions', [])
            
            print(f"\n🤖 决策历史 (共{len(decisions)}个):")
            for decision in decisions[-10:]:  # 显示最近10个
                auto = "🚀" if decision.get('auto_executed') else "⏸️"
                print(f"   {auto} {decision.get('action', '').upper()} {decision.get('stock_code')} (置信度: {decision.get('confidence')}) - {decision.get('reason', '')}")
        else:
            print(f"❌ 获取决策历史失败: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ 获取决策历史异常: {e}")

def main():
    """主函数"""
    print_banner()
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 启动本地系统
    local_process = start_local_system()
    if not local_process:
        return
    
    try:
        # 等待系统就绪
        if not wait_for_system_ready():
            return
        
        # 测试系统
        if not test_system():
            print("⚠️ 部分测试失败，但系统可能仍可使用")
        
        print("\n🎉 系统启动成功！")
        
        # 进入交互式菜单
        interactive_menu()
        
    except KeyboardInterrupt:
        print("\n👋 用户中断，正在停止系统...")
    finally:
        # 清理
        if local_process:
            local_process.terminate()
            print("✅ 本地交易系统已停止")

if __name__ == "__main__":
    main()
