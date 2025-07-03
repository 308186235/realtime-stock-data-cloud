#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Agent控制台部署
"""

import requests
import json

def test_deployment():
    print('🧪 测试Agent控制台部署')
    print('='*50)

    # 测试主页
    try:
        response = requests.get('https://6ddf02df.ai-stock-trading-app.pages.dev', timeout=10)
        if response.status_code == 200:
            print('✅ 主页访问正常')
        else:
            print(f'⚠️ 主页HTTP状态: {response.status_code}')
    except Exception as e:
        print(f'❌ 主页访问失败: {e}')

    # 测试Agent控制台
    try:
        response = requests.get('https://6ddf02df.ai-stock-trading-app.pages.dev/agent-console.html', timeout=10)
        if response.status_code == 200:
            print('✅ Agent控制台访问正常')
            print('📄 页面大小:', len(response.text), '字符')
        else:
            print(f'⚠️ Agent控制台HTTP状态: {response.status_code}')
    except Exception as e:
        print(f'❌ Agent控制台访问失败: {e}')

    # 测试API连接
    try:
        response = requests.get('https://api.aigupiao.me/', timeout=10)
        if response.status_code == 200:
            data = response.json()
            print('✅ API连接正常')
            version = data.get('data', {}).get('version', '未知')
            print(f'📊 API版本: {version}')
        else:
            print(f'⚠️ API HTTP状态: {response.status_code}')
    except Exception as e:
        print(f'❌ API连接失败: {e}')

    print('\n🎯 测试完成！')
    print('🌐 请访问: https://6ddf02df.ai-stock-trading-app.pages.dev/agent-console.html')

if __name__ == "__main__":
    test_deployment()
