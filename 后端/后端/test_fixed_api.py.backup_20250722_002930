#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的Cloudflare Worker API
验证OneDrive支持是否正常工作
"""

import requests
import json

def test_fixed_api():
    print('🔍 测试修复后的Cloudflare Worker API')
    print('='*60)

    # 测试根路径
    try:
        response = requests.get('https://api.aigupiao.me/', timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f'✅ 根路径测试成功')
            version = data.get('data', {}).get('version', '未知')
            message = data.get('data', {}).get('message', '无')
            print(f'   版本: {version}')
            print(f'   消息: {message}')
            if 'FIXED' in str(version):
                print('🎉 检测到修复版本！')
            else:
                print('⚠️ 可能还是旧版本')
        else:
            print(f'❌ 根路径测试失败: {response.status_code}')
    except Exception as e:
        print(f'❌ 根路径测试异常: {e}')

    print()

    # 测试持仓数据
    try:
        response = requests.get('https://api.aigupiao.me/api/local-trading/positions', timeout=10)
        if response.status_code == 200:
            data = response.json()
            api_source = data.get('data', {}).get('api_source', '未知')
            print(f'✅ 持仓数据测试成功')
            print(f'   数据源: {api_source}')
            if 'onedrive' in api_source:
                print('🎉 OneDrive数据源工作正常！')
            else:
                print(f'⚠️ 使用备用数据源: {api_source}')
        else:
            print(f'❌ 持仓数据测试失败: {response.status_code}')
    except Exception as e:
        print(f'❌ 持仓数据测试异常: {e}')

    print()

    # 测试余额数据
    try:
        response = requests.get('https://api.aigupiao.me/api/local-trading/balance', timeout=10)
        if response.status_code == 200:
            data = response.json()
            api_source = data.get('data', {}).get('api_source', '未知')
            print(f'✅ 余额数据测试成功')
            print(f'   数据源: {api_source}')
            if 'onedrive' in api_source:
                print('🎉 OneDrive数据源工作正常！')
            else:
                print(f'⚠️ 使用备用数据源: {api_source}')
        else:
            print(f'❌ 余额数据测试失败: {response.status_code}')
    except Exception as e:
        print(f'❌ 余额数据测试异常: {e}')

    print()

    # 测试Agent完整数据
    try:
        response = requests.get('https://api.aigupiao.me/api/agent/complete-data', timeout=10)
        if response.status_code == 200:
            data = response.json()
            sources = data.get('data', {}).get('data_sources', {})
            print(f'✅ Agent完整数据测试成功')
            print(f'   OneDrive持仓: {sources.get("onedrive_positions", False)}')
            print(f'   OneDrive余额: {sources.get("onedrive_balance", False)}')
            if sources.get('onedrive_positions') and sources.get('onedrive_balance'):
                print('🎉 OneDrive数据完全正常！')
            else:
                print('⚠️ OneDrive数据部分可用')
                
            # 显示分析上下文
            context = data.get('data', {}).get('analysis_context', {})
            if context:
                print(f'   修复状态: {context.get("fix_status", "未知")}')
                print(f'   数据优先级: {context.get("data_priority", "未知")}')
        else:
            print(f'❌ Agent完整数据测试失败: {response.status_code}')
    except Exception as e:
        print(f'❌ Agent完整数据测试异常: {e}')

    print()
    print('🔍 测试完成！')

if __name__ == "__main__":
    test_fixed_api()
