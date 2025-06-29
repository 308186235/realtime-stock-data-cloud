#!/usr/bin/env python
import requests
import json
import time
import sys
import os

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# API基础URL - 修复路径
BASE_URL = "http://localhost:8000"

def test_auth_api():
    """测试认证API"""
    print("\n===== 测试认证API =====")
    
    # 登录获取令牌
    login_url = f"{BASE_URL}/api/auth/token"  # 完整路径
    
    # 使用表单数据发送认证请求
    form_data = {
        "username": "admin",
        "password": "admin123",
        "grant_type": "password"  # OAuth2 要求
    }
    
    print(f"尝试登录: {login_url}")
    try:
        response = requests.post(
            login_url, 
            data=form_data
        )
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            try:
                token_data = response.json()
                print(f"解析的JSON数据: {token_data}")
                if isinstance(token_data, dict):
                    token = token_data.get("access_token")
                    print("登录成功,获取到认证令牌")
                    
                    # 测试获取用户信息
                    me_url = f"{BASE_URL}/api/auth/me"  # 完整路径
                    headers = {"Authorization": f"Bearer {token}"}
                    
                    print(f"获取用户信息: {me_url}")
                    me_response = requests.get(me_url, headers=headers)
                    
                    if me_response.status_code == 200:
                        user_data = me_response.json()
                        print(f"获取用户信息成功: {user_data}")
                        return token
                    else:
                        print(f"获取用户信息失败: {me_response.status_code} - {me_response.text}")
                        return None
                else:
                    print(f"错误: 响应不是字典格式: {type(token_data)}")
                    return None
            except json.JSONDecodeError as e:
                print(f"解析响应数据失败: {e}")
                print(f"响应内容: {response.text}")
                return None
        else:
            print(f"登录失败: {response.status_code} - {response.text}")
            return None
    except requests.RequestException as e:
        print(f"请求异常: {e}")
        print("确保服务器已启动并在 http://localhost:8000 上运行")
        return None

def test_backtest_api(token):
    """测试回测API"""
    print("\n===== 测试回测API =====")
    
    if not token:
        print("缺少认证令牌,无法测试回测API")
        return
    
    # 准备请求头
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 请求参数
    backtest_data = {
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
        "start_date": "2021-01-01",
        "end_date": "2021-12-31",
        "initial_capital": 100000,
        "commission": 0.0003,
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
    
    # 执行回测
    run_url = f"{BASE_URL}/api/backtesting/run"  # 完整路径
    print(f"执行回测: {run_url}")
    
    try:
        response = requests.post(run_url, headers=headers, json=backtest_data)
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text[:200]}..." if len(response.text) > 200 else f"响应内容: {response.text}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                backtest_id = result.get("backtest_id")
                print(f"回测执行成功,ID: {backtest_id}")
                
                # 获取回测结果
                time.sleep(1)  # 等待一秒确保结果已保存
                get_result_url = f"{BASE_URL}/api/backtesting/results/{backtest_id}"  # 完整路径
                print(f"获取回测结果: {get_result_url}")
                
                result_response = requests.get(get_result_url, headers=headers)
                
                if result_response.status_code == 200:
                    backtest_result = result_response.json()
                    print("回测结果获取成功")
                    print(f"回测名称: {backtest_result.get('name')}")
                    if 'report' in backtest_result and 'metrics' in backtest_result['report']:
                        metrics = backtest_result['report']['metrics']
                        print(f"总收益率: {metrics.get('total_return', 0):.2%}")
                        print(f"夏普比率: {metrics.get('sharpe_ratio', 0):.2f}")
                        print(f"最大回撤: {metrics.get('max_drawdown', 0):.2%}")
                    
                    # 获取回测历史
                    history_url = f"{BASE_URL}/api/backtesting/history"  # 完整路径
                    print(f"获取回测历史: {history_url}")
                    
                    history_response = requests.get(history_url, headers=headers)
                    
                    if history_response.status_code == 200:
                        history = history_response.json()
                        print(f"回测历史获取成功,共 {len(history)} 条记录")
                    else:
                        print(f"回测历史获取失败: {history_response.status_code} - {history_response.text}")
                else:
                    print(f"回测结果获取失败: {result_response.status_code} - {result_response.text}")
            except json.JSONDecodeError as e:
                print(f"解析响应数据失败: {e}")
                print(f"响应内容: {response.text}")
        else:
            print(f"回测执行失败: {response.status_code} - {response.text}")
    except requests.RequestException as e:
        print(f"请求异常: {e}")

def main():
    """主函数"""
    print("开始API集成测试...")
    
    # 测试认证API
    token = test_auth_api()
    
    # 测试回测API
    test_backtest_api(token)
    
    print("\n===== API集成测试完成 =====")

if __name__ == "__main__":
    main() 
