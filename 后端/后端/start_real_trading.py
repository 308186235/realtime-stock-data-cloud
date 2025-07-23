# 文件操作最佳实践:
# 1. 始终使用 with 语句打开文件
# 2. 避免在循环中重复打开同一文件
# 3. 大文件处理时考虑分块读取
# 4. 异常情况下确保文件正确关闭

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真实交易系统启动器
启动云端Agent调用本地电脑真实交易系统
"""

import subprocess
import time
import sys
import os
import requests
from datetime import datetime

def print_warning_banner():
    """打印警告横幅"""
    print("=" * 80)
    print("⚠️ 真实交易系统 - 重要警告")
    print("=" * 80)
    print("这是真实交易模式,所有操作都会影响您的实际账户!")
    print("")
    print("使用前请确保:")
    print("1. 🕐 现在是收盘时间(避免意外成交)")
    print("2. 💻 东吴证券软件已启动并登录")
    print("3. 🔒 您了解交易风险和责任")
    print("4. 📋 已备份重要数据")
    print("5. 🧪 仅用于测试和演示")
    print("")
    print("系统功能:")
    print("✅ 真实买入/卖出交易")
    print("✅ 真实持仓数据导出")
    print("✅ 真实成交记录查询")
    print("✅ 云端Agent智能决策")
    print("=" * 80)

def check_trading_software():
    """检查交易软件状态"""
    print("\n🔍 检查交易软件状态...")
    
    try:
        # 尝试导入交易模块
        from trader_api import TraderAPI
        api = TraderAPI()
        
        # 检查状态
        status = api.get_status()
        
        print("✅ 交易模块加载成功")
        print(f"   - 当前窗口: {status.get('current_window', '未知')}")
        print(f"   - 交易软件激活: {status.get('trading_software_active', False)}")
        
        if status.get('trading_software_active'):
            print("✅ 交易软件状态正常")
            return True
        else:
            print("⚠️ 交易软件未激活")
            print("请启动东吴证券软件并登录后重试")
            return False
            
    except ImportError as e:
        print(f"❌ 交易模块导入失败: {e}")
        print("请确保trader_api.py等文件在当前目录")
        return False
    except Exception as e:
        print(f"❌ 检查交易软件失败: {e}")
        return False

def start_real_trading_system():
    """启动真实交易系统"""
    print("\n🚀 启动真实交易系统...")
    
    try:
        process = subprocess.Popen(
            [sys.executable, "real_cloud_local_trading_system.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            input="YES\n"  # 自动确认启动
        )
        
        print("✅ 真实交易系统启动中...")
        print("📍 服务地址: http://localhost:8889")
        print("📖 API文档: http://localhost:8889/docs")
        
        return process
        
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return None

def wait_for_real_system_ready():
    """等待真实系统准备就绪"""
    print("\n⏳ 等待真实交易系统准备就绪...")
    
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            response = requests.get("http://localhost:8889/health", timeout=2)
            if response.status_code == 200:
                print("✅ 真实交易系统已就绪")
                return True
        except:
            pass
        
        print(f"   等待中... ({attempt + 1}/{max_attempts})")
        time.sleep(2)
    
    print("❌ 系统启动超时")
    return False

def test_real_system():
    """测试真实系统功能"""
    print("\n🧪 测试真实系统功能...")
    
    tests = [
        ("系统信息", "GET", "/"),
        ("状态检查", "GET", "/status"),
        ("健康检查", "GET", "/health")
    ]
    
    all_passed = True
    
    for test_name, method, endpoint in tests:
        try:
            if method == "GET":
                response = requests.get(f"http://localhost:8889{endpoint}", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {test_name}: 通过")
                
                if endpoint == "/status":
                    trading_active = data.get('trading_software_active', False)
                    print(f"   - 交易软件: {'✅ 激活' if trading_active else '❌ 未激活'}")
                    if not trading_active:
                        all_passed = False
                elif endpoint == "/":
                    print(f"   - 模式: {data.get('mode', '未知')}")
                    
            else:
                print(f"❌ {test_name}: 失败 (HTTP {response.status_code})")
                all_passed = False
                
        except Exception as e:
            print(f"❌ {test_name}: 异常 ({e})")
            all_passed = False
    
    return all_passed

def run_real_demo():
    """运行真实演示"""
    print("\n🎬 运行真实交易演示...")
    print("⚠️ 注意: 这将执行真实的交易指令!")
    
    confirm = input("确认运行真实交易演示? (输入 'YES' 继续): ")
    if confirm != "YES":
        print("已取消演示")
        return
    
    try:
        result = subprocess.run(
            [sys.executable, "real_cloud_agent_demo.py"],
            timeout=180,  # 3分钟超时
            input="YES\n",  # 自动确认演示
            text=True,
            capture_output=True
        )
        
        if result.returncode == 0:
            print("✅ 真实交易演示运行成功")
            print("\n📋 演示输出:")
            print(result.stdout)
        else:
            print("❌ 真实交易演示运行失败")
            print(f"错误输出: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("⏰ 演示运行超时")
    except Exception as e:
        print(f"❌ 演示运行异常: {e}")

def interactive_real_menu():
    """交互式真实交易菜单"""
    while True:
        print("\n" + "=" * 50)
        print("🎯 真实交易系统控制台")
        print("=" * 50)
        print("1. 查看系统状态")
        print("2. 执行真实交易测试")
        print("3. 导出真实持仓数据")
        print("4. 导出真实成交记录")
        print("5. 查看交易历史")
        print("6. 运行真实交易演示")
        print("7. 显示API使用指南")
        print("0. 退出")
        print("-" * 50)
        
        choice = input("请选择操作 (0-7): ").strip()
        
        if choice == "0":
            print("👋 再见!")
            break
        elif choice == "1":
            check_real_system_status()
        elif choice == "2":
            execute_real_test_trade()
        elif choice == "3":
            export_real_holdings()
        elif choice == "4":
            export_real_transactions()
        elif choice == "5":
            show_real_trade_history()
        elif choice == "6":
            run_real_demo()
        elif choice == "7":
            show_real_api_guide()
        else:
            print("❌ 无效选择,请重试")

def check_real_system_status():
    """检查真实系统状态"""
    try:
        response = requests.get("http://localhost:8889/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("\n📊 真实系统状态:")
            print(f"   - 服务运行: {data.get('service_running')}")
            print(f"   - 交易API: {data.get('trader_api_available')}")
            print(f"   - 交易软件: {data.get('trading_software_active')}")
            print(f"   - 运行模式: {data.get('mode')}")
            
            stats = data.get('stats', {})
            print(f"   - 已执行交易: {stats.get('trades_executed', 0)}")
            print(f"   - 已导出数据: {stats.get('exports_completed', 0)}")
            print(f"   - 错误次数: {stats.get('errors_count', 0)}")
        else:
            print(f"❌ 获取状态失败: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ 连接失败: {e}")

def execute_real_test_trade():
    """执行真实测试交易"""
    print("\n💰 执行真实测试交易...")
    print("⚠️ 警告: 这是真实交易,会影响实际账户!")
    
    confirm = input("确认执行真实交易? (输入 'YES' 继续): ")
    if confirm != "YES":
        print("已取消交易")
        return
    
    # 获取用户输入
    stock_code = input("请输入股票代码 (如 000001): ").strip()
    action = input("请输入操作类型 (buy/sell): ").strip().lower()
    quantity = input("请输入数量: ").strip()
    price = input("请输入价格 (回车使用市价): ").strip() or "市价"
    
    if not all([stock_code, action, quantity]):
        print("❌ 输入不完整")
        return
    
    if action not in ['buy', 'sell']:
        print("❌ 操作类型必须是 buy 或 sell")
        return
    
    try:
        quantity = int(quantity)
    except ValueError:
        print("❌ 数量必须是数字")
        return
    
    trade_data = {
        "action": action,
        "stock_code": stock_code,
        "quantity": quantity,
        "price": price
    }
    
    try:
        response = requests.post("http://localhost:8889/trade", json=trade_data, timeout=60)
        if response.status_code == 200:
            result = response.json()
            print("✅ 真实交易执行完成:")
            print(f"   - 结果: {result['message']}")
            print(f"   - 交易ID: {result['trade_id']}")
        else:
            print(f"❌ 交易失败: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ 交易异常: {e}")

def export_real_holdings():
    """导出真实持仓数据"""
    print("\n📊 导出真实持仓数据...")
    
    try:
        response = requests.post("http://localhost:8889/export", json={"data_type": "holdings"}, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print("✅ 持仓数据导出成功")
            
            data = result.get('data', [])
            if data:
                print(f"   - 持仓股票: {len(data)}只")
            else:
                print("   - 暂无持仓数据")
        else:
            print(f"❌ 导出失败: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ 导出异常: {e}")

def export_real_transactions():
    """导出真实成交记录"""
    print("\n📋 导出真实成交记录...")
    
    try:
        response = requests.post("http://localhost:8889/export", json={"data_type": "transactions"}, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print("✅ 成交记录导出成功")
            
            data = result.get('data', [])
            if data:
                print(f"   - 成交记录: {len(data)}笔")
            else:
                print("   - 暂无成交记录")
        else:
            print(f"❌ 导出失败: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ 导出异常: {e}")

def show_real_trade_history():
    """显示真实交易历史"""
    try:
        response = requests.get("http://localhost:8889/history", timeout=5)
        if response.status_code == 200:
            result = response.json()
            trades = result.get('trades', [])
            
            print(f"\n📈 真实交易历史 (共{len(trades)}笔):")
            for trade in trades[-10:]:  # 显示最近10笔
                success = "✅" if trade.get('success') else "❌"
                print(f"   {success} {trade.get('action', '').upper()} {trade.get('stock_code')} {trade.get('quantity')}股 @{trade.get('price')} [{trade.get('timestamp', '')[:19]}]")
        else:
            print(f"❌ 获取交易历史失败: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ 获取交易历史异常: {e}")

def show_real_api_guide():
    """显示真实API使用指南"""
    print("\n📋 真实交易API使用指南")
    print("-" * 40)
    print("1. 执行真实交易:")
    print('   curl -X POST http://localhost:8889/trade \\')
    print('        -H "Content-Type: application/json" \\')
    print('        -d \'{"action":"buy","stock_code":"000001","quantity":100,"price":"10.50"}\'')
    
    print("\n2. 导出真实持仓:")
    print('   curl -X POST http://localhost:8889/export \\')
    print('        -H "Content-Type: application/json" \\')
    print('        -d \'{"data_type":"holdings"}\'')
    
    print("\n3. 查看系统状态:")
    print("   curl http://localhost:8889/status")
    
    print("\n4. 查看交易历史:")
    print("   curl http://localhost:8889/history")
    
    print("\n⚠️ 注意事项:")
    print("- 所有操作都是真实的,会影响实际账户")
    print("- 建议在收盘时间进行测试")
    print("- 确保东吴证券软件已启动并登录")

def main():
    """主函数"""
    print_warning_banner()
    
    # 用户确认
    confirm = input("\n确认启动真实交易系统? (输入 'YES' 继续): ")
    if confirm != "YES":
        print("已取消启动")
        return
    
    # 检查交易软件
    if not check_trading_software():
        print("\n❌ 交易软件检查失败,请解决问题后重试")
        return
    
    # 启动真实交易系统
    real_process = start_real_trading_system()
    if not real_process:
        return
    
    try:
        # 等待系统就绪
        if not wait_for_real_system_ready():
            return
        
        # 测试系统
        if not test_real_system():
            print("⚠️ 部分测试失败,但系统可能仍可使用")
        
        print("\n🎉 真实交易系统启动成功!")
        
        # 进入交互式菜单
        interactive_real_menu()
        
    except KeyboardInterrupt:
        print("\n👋 用户中断,正在停止系统...")
    finally:
        # 清理
        if real_process:
            real_process.terminate()
            print("✅ 真实交易系统已停止")

if __name__ == "__main__":
    main()
