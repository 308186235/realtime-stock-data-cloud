#!/usr/bin/env python3
'''
ngrok + Cloudflare混合方案测试脚本
生成时间: 2025-07-21 21:31:23
'''

import requests
import time
from datetime import datetime

def test_hybrid_solution():
    print("🚀 测试ngrok + Cloudflare混合方案")
    print("=" * 60)
    
    # 测试目标
    test_urls = [
        {"name": "ngrok直连", "url": "https://2346443b1406.ngrok-free.app/health"},
        {"name": "Cloudflare代理", "url": "https://api.aigupiao.me/health"},
        {"name": "本地服务", "url": "http://localhost:8000/api/health"}
    ]
    
    results = {}
    
    for test in test_urls:
        try:
            print(f"\n🧪 测试: {test['name']}")
            start_time = time.time()
            
            response = requests.get(test['url'], timeout=15)
            latency = round((time.time() - start_time) * 1000)
            
            results[test['name']] = {
                'latency': latency,
                'success': response.status_code == 200,
                'status_code': response.status_code
            }
            
            if response.status_code == 200:
                print(f"✅ {test['name']}: {latency}ms")
            else:
                print(f"⚠️ {test['name']}: {latency}ms (状态码: {response.status_code})")
                
        except Exception as e:
            results[test['name']] = {
                'latency': 9999,
                'success': False,
                'error': str(e)
            }
            print(f"❌ {test['name']}: 失败 - {e}")
        
        time.sleep(1)
    
    # 分析结果
    print("\n📊 性能对比:")
    print("-" * 40)
    
    for name, result in results.items():
        if result['success']:
            print(f"{name.ljust(15)}: {result['latency']}ms")
        else:
            print(f"{name.ljust(15)}: 失败")
    
    # 计算改善
    if results.get('ngrok直连', {}).get('success') and results.get('Cloudflare代理', {}).get('success'):
        ngrok_latency = results['ngrok直连']['latency']
        cf_latency = results['Cloudflare代理']['latency']
        
        if ngrok_latency < cf_latency:
            improvement = round(((cf_latency - ngrok_latency) / cf_latency) * 100)
            print(f"\n🚀 ngrok比Cloudflare快 {improvement}%")
        else:
            print(f"\n⚠️ Cloudflare仍然更快")
    
    print(f"\n🎯 测试完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    test_hybrid_solution()
