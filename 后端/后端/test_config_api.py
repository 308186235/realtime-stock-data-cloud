#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试配置API功能
"""

import requests
import json

# API基础URL
BASE_URL = "https://app.aigupiao.me/api"

def test_get_config():
    """测试获取配置"""
    try:
        response = requests.get(f"{BASE_URL}/config")
        print("📋 获取配置:")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 成功: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 失败: {response.text}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")

def test_toggle_beijing_exchange(enabled=True):
    """测试切换北交所权限"""
    try:
        response = requests.post(f"{BASE_URL}/config/beijing-exchange", params={"enabled": enabled})
        print(f"\n🔧 {'开启' if enabled else '关闭'}北交所权限:")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 成功: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 失败: {response.text}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")

def test_get_beijing_status():
    """测试获取北交所状态"""
    try:
        response = requests.get(f"{BASE_URL}/config/beijing-exchange")
        print(f"\n📊 北交所权限状态:")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 成功: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 失败: {response.text}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")

def test_update_config():
    """测试更新配置"""
    try:
        config_data = {
            "analysis_interval": 45,
            "reconnect_interval": 25
        }
        response = requests.post(f"{BASE_URL}/config", json=config_data)
        print(f"\n⚙️ 更新配置:")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 成功: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 失败: {response.text}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")

def test_get_system_status():
    """测试获取系统状态"""
    try:
        response = requests.get(f"{BASE_URL}/config/status")
        print(f"\n📈 系统状态:")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 成功: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 失败: {response.text}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")

def main():
    """主测试函数"""
    print("🚀 配置API测试开始")
    print("="*60)
    
    # 1. 获取当前配置
    test_get_config()
    
    # 2. 获取北交所状态
    test_get_beijing_status()
    
    # 3. 开启北交所权限
    test_toggle_beijing_exchange(True)
    
    # 4. 再次获取北交所状态
    test_get_beijing_status()
    
    # 5. 关闭北交所权限
    test_toggle_beijing_exchange(False)
    
    # 6. 更新其他配置
    test_update_config()
    
    # 7. 获取系统状态
    test_get_system_status()
    
    # 8. 最终获取配置
    test_get_config()
    
    print("\n" + "="*60)
    print("✅ 配置API测试完成")

if __name__ == "__main__":
    main()
