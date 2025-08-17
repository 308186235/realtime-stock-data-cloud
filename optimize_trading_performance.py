#!/usr/bin/env python3
"""
优化本地交易软件性能
"""

import requests
import time
import json
import asyncio
import concurrent.futures
from datetime import datetime

class TradingPerformanceOptimizer:
    def __init__(self):
        self.config = {
            'local_trading': 'http://localhost:8888',
            'ngrok_http': 'https://2346443b1406.ngrok-free.app'
        }
    
    def log(self, message, level="INFO"):
        """记录日志"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        colors = {
            "INFO": "\033[36m",
            "SUCCESS": "\033[32m",
            "WARNING": "\033[33m",
            "ERROR": "\033[31m",
            "RESET": "\033[0m"
        }
        color = colors.get(level, colors["INFO"])
        print(f"{color}[{timestamp}] [{level}] {message}{colors['RESET']}")
    
    def test_fast_trading_endpoints(self):
        """测试快速交易端点"""
        self.log("⚡ 寻找快速交易端点...")
        
        # 测试不同的交易端点和参数
        fast_endpoints = [
            {
                'name': '快速买入(异步)',
                'url': f"{self.config['local_trading']}/trade/async",
                'data': {'action': 'buy', 'stock_code': '000001', 'quantity': 100}
            },
            {
                'name': '快速买入(简化)',
                'url': f"{self.config['local_trading']}/trade/fast",
                'data': {'action': 'buy', 'stock_code': '000001', 'quantity': 100}
            },
            {
                'name': '交易预检查',
                'url': f"{self.config['local_trading']}/trade/validate",
                'data': {'action': 'buy', 'stock_code': '000001', 'quantity': 100}
            },
            {
                'name': '模拟交易',
                'url': f"{self.config['local_trading']}/trade/simulate",
                'data': {'action': 'buy', 'stock_code': '000001', 'quantity': 100}
            },
            {
                'name': '最小化交易',
                'url': f"{self.config['local_trading']}/trade",
                'data': {'action': 'buy', 'stock_code': '000001', 'quantity': 1, 'fast': True}
            }
        ]
        
        results = {}
        
        for endpoint in fast_endpoints:
            try:
                self.log(f"🧪 测试: {endpoint['name']}")
                
                start_time = time.perf_counter()
                response = requests.post(
                    endpoint['url'], 
                    json=endpoint['data'], 
                    timeout=5  # 短超时
                )
                latency = (time.perf_counter() - start_time) * 1000
                
                results[endpoint['name']] = {
                    'latency': round(latency),
                    'status_code': response.status_code,
                    'success': response.status_code in [200, 201, 202]
                }
                
                if response.status_code in [200, 201, 202]:
                    self.log(f"✅ {endpoint['name']}: {round(latency)}ms", "SUCCESS")
                else:
                    self.log(f"⚠️ {endpoint['name']}: {round(latency)}ms (状态码: {response.status_code})", "WARNING")
                
            except requests.exceptions.Timeout:
                results[endpoint['name']] = {'latency': 5000, 'status_code': 0, 'timeout': True}
                self.log(f"⏰ {endpoint['name']}: 超时 (>5s)", "WARNING")
            except Exception as e:
                results[endpoint['name']] = {'latency': 9999, 'error': str(e)}
                self.log(f"❌ {endpoint['name']}: 失败 - {e}", "ERROR")
        
        return results
    
    def test_optimized_trading_params(self):
        """测试优化的交易参数"""
        self.log("🔧 测试优化的交易参数...")
        
        # 不同的参数组合
        param_tests = [
            {
                'name': '最小参数',
                'data': {
                    'action': 'buy',
                    'stock_code': '000001',
                    'quantity': 100
                }
            },
            {
                'name': '快速模式',
                'data': {
                    'action': 'buy',
                    'stock_code': '000001',
                    'quantity': 100,
                    'fast_mode': True,
                    'skip_validation': True
                }
            },
            {
                'name': '异步模式',
                'data': {
                    'action': 'buy',
                    'stock_code': '000001',
                    'quantity': 100,
                    'async': True,
                    'callback': False
                }
            },
            {
                'name': '批量模式',
                'data': {
                    'trades': [
                        {'action': 'buy', 'stock_code': '000001', 'quantity': 100}
                    ],
                    'batch': True
                }
            }
        ]
        
        results = {}
        
        for test in param_tests:
            try:
                self.log(f"🧪 测试: {test['name']}")
                
                start_time = time.perf_counter()
                response = requests.post(
                    f"{self.config['local_trading']}/trade",
                    json=test['data'],
                    timeout=10
                )
                latency = (time.perf_counter() - start_time) * 1000
                
                results[test['name']] = {
                    'latency': round(latency),
                    'status_code': response.status_code,
                    'response': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text[:100]
                }
                
                self.log(f"📊 {test['name']}: {round(latency)}ms (状态码: {response.status_code})")
                
            except Exception as e:
                results[test['name']] = {'error': str(e)}
                self.log(f"❌ {test['name']}: 失败 - {e}", "ERROR")
        
        return results
    
    def test_connection_optimization(self):
        """测试连接优化"""
        self.log("🔗 测试连接优化...")
        
        # 使用会话复用
        session = requests.Session()
        session.headers.update({
            'Connection': 'keep-alive',
            'User-Agent': 'FastTradingClient/1.0'
        })
        
        # 预热连接
        try:
            session.get(f"{self.config['local_trading']}/health", timeout=5)
            self.log("🔥 连接预热完成", "SUCCESS")
        except:
            self.log("⚠️ 连接预热失败", "WARNING")
        
        # 测试复用连接的性能
        latencies = []
        
        for i in range(5):
            try:
                start_time = time.perf_counter()
                response = session.post(
                    f"{self.config['local_trading']}/trade",
                    json={
                        'action': 'buy',
                        'stock_code': '000001',
                        'quantity': 100,
                        'fast_mode': True
                    },
                    timeout=10
                )
                latency = (time.perf_counter() - start_time) * 1000
                latencies.append(latency)
                
                self.log(f"📊 第{i+1}次复用连接: {round(latency)}ms")
                
            except Exception as e:
                self.log(f"❌ 第{i+1}次失败: {e}", "ERROR")
        
        if latencies:
            avg_latency = sum(latencies) / len(latencies)
            self.log(f"✅ 连接复用平均延迟: {round(avg_latency)}ms", "SUCCESS")
            return round(avg_latency)
        
        return 9999
    
    async def test_async_trading(self):
        """测试异步交易"""
        self.log("🚀 测试异步交易...")
        
        import aiohttp
        
        async def make_async_trade():
            try:
                async with aiohttp.ClientSession() as session:
                    start_time = time.perf_counter()
                    async with session.post(
                        f"{self.config['local_trading']}/trade",
                        json={
                            'action': 'buy',
                            'stock_code': '000001',
                            'quantity': 100,
                            'async': True
                        },
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        latency = (time.perf_counter() - start_time) * 1000
                        return latency, response.status
            except Exception as e:
                return 9999, 0
        
        # 测试异步性能
        try:
            latency, status = await make_async_trade()
            self.log(f"📊 异步交易: {round(latency)}ms (状态码: {status})")
            return latency
        except Exception as e:
            self.log(f"❌ 异步交易失败: {e}", "ERROR")
            return 9999
    
    def create_optimized_trading_client(self):
        """创建优化的交易客户端"""
        self.log("⚡ 创建优化的交易客户端...")
        
        optimized_client_code = '''#!/usr/bin/env python3
"""
优化的交易客户端
专门用于云端Agent到本地交易的高性能连接
"""

import requests
import time
import json
from datetime import datetime

class OptimizedTradingClient:
    def __init__(self, base_url="http://localhost:8888"):
        self.base_url = base_url
        self.session = requests.Session()
        
        # 优化连接设置
        self.session.headers.update({
            'Connection': 'keep-alive',
            'User-Agent': 'OptimizedTradingClient/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        # 预热连接
        self._warmup_connection()
    
    def _warmup_connection(self):
        """预热连接"""
        try:
            self.session.get(f"{self.base_url}/health", timeout=5)
            print("✅ 连接预热完成")
        except:
            print("⚠️ 连接预热失败")
    
    def fast_trade(self, action, stock_code, quantity, price=None):
        """快速交易"""
        trade_data = {
            'action': action,
            'stock_code': stock_code,
            'quantity': quantity,
            'fast_mode': True,
            'skip_validation': True
        }
        
        if price:
            trade_data['price'] = price
        
        try:
            start_time = time.perf_counter()
            response = self.session.post(
                f"{self.base_url}/trade",
                json=trade_data,
                timeout=5  # 短超时强制快速响应
            )
            latency = (time.perf_counter() - start_time) * 1000
            
            return {
                'success': response.status_code == 200,
                'latency': round(latency),
                'response': response.json() if response.status_code == 200 else None,
                'status_code': response.status_code
            }
            
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'latency': 5000,
                'error': 'timeout',
                'message': '交易超时,可能仍在处理中'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def batch_trade(self, trades):
        """批量交易"""
        try:
            start_time = time.perf_counter()
            response = self.session.post(
                f"{self.base_url}/trade/batch",
                json={'trades': trades, 'fast_mode': True},
                timeout=10
            )
            latency = (time.perf_counter() - start_time) * 1000
            
            return {
                'success': response.status_code == 200,
                'latency': round(latency),
                'response': response.json() if response.status_code == 200 else None
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def validate_trade(self, action, stock_code, quantity):
        """快速验证交易(不执行)"""
        try:
            start_time = time.perf_counter()
            response = self.session.post(
                f"{self.base_url}/trade/validate",
                json={
                    'action': action,
                    'stock_code': stock_code,
                    'quantity': quantity
                },
                timeout=2  # 极短超时
            )
            latency = (time.perf_counter() - start_time) * 1000
            
            return {
                'valid': response.status_code == 200,
                'latency': round(latency),
                'response': response.json() if response.status_code == 200 else None
            }
        except Exception as e:
            return {'valid': False, 'error': str(e)}

# 使用示例
if __name__ == "__main__":
    client = OptimizedTradingClient()
    
    # 快速交易测试
    result = client.fast_trade('buy', '000001', 100, 10.50)
    print(f"交易结果: {result}")
    
    # 验证测试
    validation = client.validate_trade('buy', '000001', 100)
    print(f"验证结果: {validation}")
'''
        
        with open('optimized_trading_client.py', 'w', encoding='utf-8') as f:
            f.write(optimized_client_code)
        
        self.log("📄 优化客户端已创建: optimized_trading_client.py", "SUCCESS")
    
    def generate_performance_recommendations(self):
        """生成性能优化建议"""
        self.log("💡 生成性能优化建议...")
        
        recommendations = [
            {
                'priority': 'HIGH',
                'category': '本地交易软件',
                'issue': '交易处理时间过长 (7.6秒)',
                'solutions': [
                    '检查本地交易软件是否有阻塞操作',
                    '优化交易软件配置,减少确认步骤',
                    '使用异步交易模式',
                    '启用快速交易模式(如果支持)'
                ]
            },
            {
                'priority': 'MEDIUM',
                'category': '网络连接',
                'issue': 'ngrok隧道延迟 (571ms)',
                'solutions': [
                    '使用更快的隧道服务(如frp,natapp)',
                    '考虑使用VPN直连',
                    '优化网络连接质量',
                    '使用连接池和会话复用'
                ]
            },
            {
                'priority': 'LOW',
                'category': '客户端优化',
                'issue': '请求参数和超时设置',
                'solutions': [
                    '使用优化的交易客户端',
                    '设置合适的超时时间',
                    '启用连接复用',
                    '使用批量交易减少请求次数'
                ]
            }
        ]
        
        self.log("📋 性能优化建议:", "SUCCESS")
        for i, rec in enumerate(recommendations, 1):
            priority_color = "ERROR" if rec['priority'] == 'HIGH' else "WARNING" if rec['priority'] == 'MEDIUM' else "INFO"
            self.log(f"{i}. [{rec['priority']}] {rec['category']}: {rec['issue']}", priority_color)
            for j, solution in enumerate(rec['solutions'], 1):
                self.log(f"   {j}) {solution}", "INFO")
            print()
        
        return recommendations
    
    def run_optimization_test(self):
        """运行优化测试"""
        self.log("🚀 开始交易性能优化测试", "INFO")
        self.log("=" * 60, "INFO")
        
        # 1. 测试快速端点
        fast_results = self.test_fast_trading_endpoints()
        print()
        
        # 2. 测试优化参数
        param_results = self.test_optimized_trading_params()
        print()
        
        # 3. 测试连接优化
        connection_latency = self.test_connection_optimization()
        print()
        
        # 4. 创建优化客户端
        self.create_optimized_trading_client()
        print()
        
        # 5. 生成建议
        recommendations = self.generate_performance_recommendations()
        
        # 6. 总结
        self.log("🎯 优化测试总结:", "SUCCESS")
        
        # 找出最快的方法
        best_method = None
        best_latency = 9999
        
        for name, result in fast_results.items():
            if result.get('success') and result.get('latency', 9999) < best_latency:
                best_latency = result['latency']
                best_method = name
        
        if best_method:
            self.log(f"✅ 最快方法: {best_method} ({best_latency}ms)", "SUCCESS")
        else:
            self.log("⚠️ 未找到明显更快的方法", "WARNING")
        
        if connection_latency < 1000:
            self.log(f"✅ 连接复用优化: {connection_latency}ms", "SUCCESS")
        
        self.log("📄 请使用 optimized_trading_client.py 获得最佳性能", "SUCCESS")
        
        self.log("🎉 优化测试完成!", "SUCCESS")

if __name__ == "__main__":
    optimizer = TradingPerformanceOptimizer()
    optimizer.run_optimization_test()
