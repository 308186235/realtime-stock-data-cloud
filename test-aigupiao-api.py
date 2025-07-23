#!/usr/bin/env python3
"""
🧪 AI股票交易系统 - API连接测试脚本
测试aigupiao.me域名的API连接状态
"""

import requests
import time
import json
from datetime import datetime

# 测试端点列表
TEST_ENDPOINTS = [
    'https://aigupiao.me/api/health',
    'https://aigupiao.me/api/virtual-account/accounts',
    'https://aigupiao.me/api/stock-data?code=000001',
    'https://aigupiao.me/api/realtime',
    'https://aigupiao.me/api/agent-analysis'
]

def test_endpoint(url, timeout=10):
    """测试单个API端点"""
    try:
        start_time = time.time()
        response = requests.get(url, timeout=timeout)
        end_time = time.time()
        
        latency = int((end_time - start_time) * 1000)  # 毫秒
        
        return {
            'url': url,
            'status_code': response.status_code,
            'latency_ms': latency,
            'success': response.status_code == 200,
            'response_size': len(response.content),
            'content_type': response.headers.get('content-type', 'unknown')
        }
    except requests.exceptions.Timeout:
        return {
            'url': url,
            'status_code': 'TIMEOUT',
            'latency_ms': timeout * 1000,
            'success': False,
            'error': 'Request timeout'
        }
    except requests.exceptions.RequestException as e:
        return {
            'url': url,
            'status_code': 'ERROR',
            'latency_ms': 0,
            'success': False,
            'error': str(e)
        }

def main():
    print("🚀 AI股票交易系统 - API连接测试")
    print("=" * 50)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试端点数量: {len(TEST_ENDPOINTS)}")
    print()
    
    results = []
    total_latency = 0
    success_count = 0
    
    for i, endpoint in enumerate(TEST_ENDPOINTS, 1):
        print(f"[{i}/{len(TEST_ENDPOINTS)}] 测试: {endpoint}")
        
        result = test_endpoint(endpoint)
        results.append(result)
        
        if result['success']:
            print(f"  ✅ 成功 - {result['latency_ms']}ms")
            success_count += 1
            total_latency += result['latency_ms']
        else:
            print(f"  ❌ 失败 - {result.get('error', f'HTTP {result['status_code']}'}")
        
        time.sleep(0.5)  # 避免请求过快
    
    print()
    print("📊 测试结果汇总")
    print("-" * 30)
    print(f"成功率: {success_count}/{len(TEST_ENDPOINTS)} ({success_count/len(TEST_ENDPOINTS)*100:.1f}%)")
    
    if success_count > 0:
        avg_latency = total_latency / success_count
        print(f"平均延迟: {avg_latency:.0f}ms")
        
        if avg_latency < 1000:
            print("🟢 延迟状态: 优秀")
        elif avg_latency < 3000:
            print("🟡 延迟状态: 良好")
        else:
            print("🔴 延迟状态: 需要优化")
    
    print()
    print("📋 详细结果:")
    for result in results:
        status = "✅" if result['success'] else "❌"
        print(f"  {status} {result['url']}")
        if result['success']:
            print(f"      延迟: {result['latency_ms']}ms | 大小: {result['response_size']}B")
        else:
            print(f"      错误: {result.get('error', 'Unknown error')}")
    
    # 保存结果到文件
    with open('api_test_results.json', 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_endpoints': len(TEST_ENDPOINTS),
                'success_count': success_count,
                'success_rate': success_count/len(TEST_ENDPOINTS)*100,
                'average_latency_ms': total_latency / success_count if success_count > 0 else 0
            },
            'results': results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 测试结果已保存到: api_test_results.json")

if __name__ == "__main__":
    main()
