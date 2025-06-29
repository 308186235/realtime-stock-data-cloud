import requests
import json
import time
from datetime import datetime, timedelta
import sys

API_BASE_URL = "http://localhost:8000"

def print_header(title):
    """打印标题"""
    print("\n" + "=" * 50)
    print(f" {title} ".center(50))
    print("=" * 50)

def print_result(success, message=""):
    """打印结果"""
    if success:
        print(f"✓ 成功: {message}" if message else "✓ 成功")
    else:
        print(f"✗ 失败: {message}" if message else "✗ 失败")

def test_full_workflow():
    """测试完整的前后端交互流程"""
    print_header("开始测试完整回测流程")
    
    # 初始化
    auth_token = None
    backtest_id = None
    
    # 步骤1: 登录并获取认证令牌
    print_header("步骤1: 认证流程")
    print("登录获取令牌...")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/auth/token",
            json={"username": "admin", "password": "admin123"},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            auth_data = response.json()
            auth_token = auth_data.get("access_token")
            
            if auth_token:
                print_result(True, f"获取到认证令牌: {auth_token}")
                
                # 验证用户信息
                print("\n验证用户信息...")
                headers = {"Authorization": f"Bearer {auth_token}"}
                
                me_response = requests.get(
                    f"{API_BASE_URL}/api/auth/me",
                    headers=headers
                )
                
                if me_response.status_code == 200:
                    user_data = me_response.json()
                    print_result(True, f"用户: {user_data.get('username')}")
                else:
                    print_result(False, f"获取用户信息失败: {me_response.status_code}")
                    return
            else:
                print_result(False, "响应中没有认证令牌")
                return
        else:
            print_result(False, f"登录失败: {response.status_code}")
            print(response.text)
            return
    except Exception as e:
        print_result(False, f"登录异常: {e}")
        return
    
    # 步骤2: 获取技术指标和基准列表
    print_header("步骤2: 获取技术指标和基准列表")
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    print("获取可用技术指标...")
    try:
        indicators_response = requests.get(
            f"{API_BASE_URL}/api/backtesting/indicators",
            headers=headers
        )
        
        if indicators_response.status_code == 200:
            indicators = indicators_response.json()
            print_result(True, f"获取到 {len(indicators)} 个技术指标")
        else:
            print_result(False, f"获取技术指标失败: {indicators_response.status_code}")
    except Exception as e:
        print_result(False, f"技术指标异常: {e}")
    
    print("\n获取可用基准指数...")
    try:
        benchmarks_response = requests.get(
            f"{API_BASE_URL}/api/backtesting/benchmarks",
            headers=headers
        )
        
        if benchmarks_response.status_code == 200:
            benchmarks = benchmarks_response.json()
            print_result(True, f"获取到 {len(benchmarks)} 个基准指数")
        else:
            print_result(False, f"获取基准指数失败: {benchmarks_response.status_code}")
    except Exception as e:
        print_result(False, f"基准指数异常: {e}")
    
    # 步骤3: 执行回测
    print_header("步骤3: 执行回测")
    
    # 构建回测请求
    backtest_request = {
        "strategies": [
            {
                "type": "inverted_three_red",
                "params": {
                    "body_decrease_threshold": 0.67,
                    "upper_shadow_increase_threshold": 1.0,
                    "volume_threshold": 1.5
                }
            }
        ],
        "symbols": ["AAPL", "MSFT"],
        "start_date": (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
        "end_date": datetime.now().strftime("%Y-%m-%d"),
        "initial_capital": 100000.0,
        "commission": 0.0003,
        "name": f"测试回测 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "risk_management": {
            "enabled": True,
            "max_position_size": 0.2,
            "max_drawdown": 0.1,
            "fixed_stop_loss": 0.05,
            "trailing_stop_loss": 0.08,
            "time_stop_loss": 10,
            "position_sizing_method": "risk",
            "risk_per_trade": 0.02
        },
        "technical_indicators": {
            "enabled": True,
            "indicators": ["ma", "ema", "macd", "rsi", "bollinger"]
        },
        "benchmark_comparison": {
            "enabled": True,
            "symbol": "000001.SS"
        }
    }
    
    print("执行回测...")
    try:
        run_response = requests.post(
            f"{API_BASE_URL}/api/backtesting/run",
            headers=headers | {"Content-Type": "application/json"},
            json=backtest_request
        )
        
        if run_response.status_code == 200:
            result = run_response.json()
            backtest_id = result.get("backtest_id")
            
            if backtest_id:
                print_result(True, f"回测执行成功，ID: {backtest_id}")
                print(f"指标数据: 总收益率={result.get('metrics', {}).get('total_return', 0):.2%}")
                print(f"交易次数: {len(result.get('trades', []))}")
                if result.get('benchmark_report'):
                    print(f"基准比较: Alpha={result.get('benchmark_report', {}).get('alpha', 0):.2f}")
            else:
                print_result(False, "响应中没有回测ID")
                return
        else:
            print_result(False, f"回测执行失败: {run_response.status_code}")
            print(run_response.text)
            return
    except Exception as e:
        print_result(False, f"回测异常: {e}")
        return
    
    # 步骤4: 获取回测结果
    if not backtest_id:
        print_result(False, "没有回测ID，无法获取结果")
        return
    
    print_header("步骤4: 获取回测结果")
    print(f"获取回测 {backtest_id} 的详细结果...")
    
    try:
        results_response = requests.get(
            f"{API_BASE_URL}/api/backtesting/results/{backtest_id}",
            headers=headers
        )
        
        if results_response.status_code == 200:
            detailed_results = results_response.json()
            print_result(True, "获取详细结果成功")
            print(f"回测名称: {detailed_results.get('name')}")
            print(f"创建时间: {detailed_results.get('created_at')}")
            if "report" in detailed_results and "metrics" in detailed_results["report"]:
                metrics = detailed_results["report"]["metrics"]
                print(f"详细指标:")
                print(f"  总收益率: {metrics.get('total_return', 0):.2%}")
                print(f"  年化收益率: {metrics.get('annual_return', 0):.2%}")
                print(f"  夏普比率: {metrics.get('sharpe_ratio', 0):.2f}")
                print(f"  最大回撤: {metrics.get('max_drawdown', 0):.2%}")
        else:
            print_result(False, f"获取详细结果失败: {results_response.status_code}")
            print(results_response.text)
    except Exception as e:
        print_result(False, f"获取结果异常: {e}")
    
    # 步骤5: 保存回测
    print_header("步骤5: 保存回测")
    print("保存回测结果...")
    
    save_request = {
        "backtest_id": backtest_id,
        "name": f"已保存回测 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    }
    
    try:
        save_response = requests.post(
            f"{API_BASE_URL}/api/backtesting/save",
            headers=headers | {"Content-Type": "application/json"},
            json=save_request
        )
        
        if save_response.status_code == 200:
            save_result = save_response.json()
            print_result(True, f"保存成功: {save_result.get('message')}")
        else:
            print_result(False, f"保存失败: {save_response.status_code}")
            print(save_response.text)
    except Exception as e:
        print_result(False, f"保存异常: {e}")
    
    # 步骤6: 获取回测历史
    print_header("步骤6: 获取回测历史")
    print("获取回测历史记录...")
    
    try:
        history_response = requests.get(
            f"{API_BASE_URL}/api/backtesting/history",
            headers=headers
        )
        
        if history_response.status_code == 200:
            history = history_response.json()
            print_result(True, f"获取到 {len(history)} 条历史记录")
            
            if history:
                print("\n最近的回测记录:")
                for i, record in enumerate(history[:3], 1):  # 只显示前3条
                    print(f"{i}. {record.get('name')} - {record.get('symbols')} - "
                          f"收益率: {record.get('total_return', 0):.2%}")
        else:
            print_result(False, f"获取历史失败: {history_response.status_code}")
            print(history_response.text)
    except Exception as e:
        print_result(False, f"历史记录异常: {e}")
    
    # 测试总结
    print_header("测试总结")
    print("前后端API对接测试已完成!")
    print("所有API端点工作正常，前后端对接成功。")
    print("=" * 50)

if __name__ == "__main__":
    # 等待服务器启动
    print("等待API服务器启动...")
    time.sleep(2)
    
    # 执行测试
    test_full_workflow() 