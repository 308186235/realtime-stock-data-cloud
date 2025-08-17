#!/usr/bin/env python3
"""
MCP全面系统检查
检查DNS,API,数据库,茶股帮连接等所有系统状态
"""

import requests
import time
import json
from datetime import datetime, timedelta

def check_dns_status():
    """检查DNS和域名状态"""
    print("🌐 DNS和域名状态检查")
    print("=" * 50)
    
    domains = {
        "主域名": "https://aigupiao.me",
        "主域名健康": "https://aigupiao.me/health", 
        "API域名": "https://api.aigupiao.me/api/account-balance",
        "Agent域名": "https://agent.aigupiao.me/api/tokens",
        "移动端域名": "https://mobile.aigupiao.me"
    }
    
    results = {}
    
    for name, url in domains.items():
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {name}: 正常 ({response.status_code})")
                results[name] = "OK"
            else:
                print(f"⚠️ {name}: 状态码 {response.status_code}")
                results[name] = f"HTTP_{response.status_code}"
        except requests.exceptions.ConnectionError:
            print(f"❌ {name}: 连接失败")
            results[name] = "CONNECTION_ERROR"
        except Exception as e:
            print(f"❌ {name}: {str(e)[:50]}...")
            results[name] = "ERROR"
    
    return results

def check_api_endpoints():
    """检查关键API端点"""
    print("\n🔌 API端点检查")
    print("=" * 50)
    
    api_endpoints = {
        "账户余额": "https://api.aigupiao.me/api/account-balance",
        "虚拟账户": "https://api.aigupiao.me/api/virtual-account/accounts",
        "茶股帮状态": "https://api.aigupiao.me/api/chagubang/health",
        "Agent分析": "https://api.aigupiao.me/api/agent-analysis",
        "配置管理": "https://api.aigupiao.me/api/config/keys"
    }
    
    results = {}
    
    for name, url in api_endpoints.items():
        try:
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {name}: 正常")
                if 'data' in data:
                    print(f"   数据: {str(data['data'])[:100]}...")
                results[name] = "OK"
            else:
                print(f"⚠️ {name}: 状态码 {response.status_code}")
                results[name] = f"HTTP_{response.status_code}"
        except Exception as e:
            print(f"❌ {name}: {str(e)[:50]}...")
            results[name] = "ERROR"
    
    return results

def check_database_status():
    """检查数据库状态"""
    print("\n🗄️ 数据库状态检查")
    print("=" * 50)
    
    # 通过API检查数据库
    try:
        # 检查今天的数据
        response = requests.get("https://api.aigupiao.me/api/chagubang/stats", timeout=15)
        if response.status_code == 200:
            data = response.json()
            print("✅ 数据库连接正常")
            if 'data' in data:
                stats = data['data']
                print(f"   今日股票数据: {stats.get('stock_data_count', 0)} 条")
                print(f"   今日AI决策: {stats.get('decisions_count', 0)} 条")
                print(f"   最后更新: {stats.get('last_update', 'N/A')}")
            return "OK"
        else:
            print(f"⚠️ 数据库API返回: {response.status_code}")
            return f"HTTP_{response.status_code}"
    except Exception as e:
        print(f"❌ 数据库检查失败: {e}")
        return "ERROR"

def check_chagubang_connection():
    """检查茶股帮连接状态"""
    print("\n📡 茶股帮连接检查")
    print("=" * 50)
    
    try:
        # 检查连接状态
        response = requests.get("https://api.aigupiao.me/api/chagubang/health", timeout=15)
        if response.status_code == 200:
            data = response.json()
            print("✅ 茶股帮API响应正常")
            
            if 'data' in data:
                status = data['data']
                print(f"   连接状态: {status.get('connection_status', 'unknown')}")
                print(f"   活跃Token: {status.get('active_token', 'N/A')}")
                print(f"   今日接收数据: {status.get('data_received_today', 0)} 条")
                print(f"   最后数据时间: {status.get('last_data_time', 'N/A')}")
            
            return "OK"
        else:
            print(f"⚠️ 茶股帮API返回: {response.status_code}")
            return f"HTTP_{response.status_code}"
    except Exception as e:
        print(f"❌ 茶股帮检查失败: {e}")
        return "ERROR"

def check_frontend_config():
    """检查前端配置"""
    print("\n📱 前端配置检查")
    print("=" * 50)
    
    try:
        # 检查前端配置文件是否正确
        config_path = r"E:\正式\移动端\services\config.js"
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'https://aigupiao.me' in content:
            print("✅ 前端API配置正确")
            print("   baseUrl: https://aigupiao.me")
            return "OK"
        else:
            print("❌ 前端API配置错误")
            return "CONFIG_ERROR"
    except Exception as e:
        print(f"❌ 前端配置检查失败: {e}")
        return "ERROR"

def generate_system_report():
    """生成系统状态报告"""
    print("\n" + "=" * 60)
    print("🔍 MCP全面系统检查报告")
    print("=" * 60)
    
    # 执行所有检查
    dns_results = check_dns_status()
    api_results = check_api_endpoints()
    db_status = check_database_status()
    chagubang_status = check_chagubang_connection()
    frontend_status = check_frontend_config()
    
    # 统计结果
    total_checks = len(dns_results) + len(api_results) + 3  # +3 for db, chagubang, frontend
    ok_count = 0
    
    for result in dns_results.values():
        if result == "OK":
            ok_count += 1
    
    for result in api_results.values():
        if result == "OK":
            ok_count += 1
    
    if db_status == "OK":
        ok_count += 1
    if chagubang_status == "OK":
        ok_count += 1
    if frontend_status == "OK":
        ok_count += 1
    
    # 生成总结
    print(f"\n📊 系统健康度: {ok_count}/{total_checks} ({ok_count/total_checks*100:.1f}%)")
    
    if ok_count == total_checks:
        print("🎉 所有系统运行正常!")
        status = "HEALTHY"
    elif ok_count >= total_checks * 0.8:
        print("⚠️ 系统基本正常,有少量问题需要关注")
        status = "MOSTLY_HEALTHY"
    else:
        print("❌ 系统存在严重问题,需要立即处理")
        status = "UNHEALTHY"
    
    # 问题汇总
    print(f"\n🔧 问题汇总:")
    problems = []
    
    for name, result in dns_results.items():
        if result != "OK":
            problems.append(f"DNS: {name} - {result}")
    
    for name, result in api_results.items():
        if result != "OK":
            problems.append(f"API: {name} - {result}")
    
    if db_status != "OK":
        problems.append(f"数据库: {db_status}")
    if chagubang_status != "OK":
        problems.append(f"茶股帮: {chagubang_status}")
    if frontend_status != "OK":
        problems.append(f"前端配置: {frontend_status}")
    
    if problems:
        for i, problem in enumerate(problems, 1):
            print(f"   {i}. {problem}")
    else:
        print("   无问题发现")
    
    print(f"\n⏰ 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🏷️ 系统状态: {status}")
    
    return {
        'status': status,
        'health_score': f"{ok_count}/{total_checks}",
        'problems': problems,
        'timestamp': datetime.now().isoformat()
    }

if __name__ == "__main__":
    report = generate_system_report()
    
    # 保存报告到文件
    with open(r"E:\交易8 - 副本\system_check_report.json", 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
