#!/usr/bin/env python3
"""
分析和优化云端Agent到本地交易的延迟
"""

import asyncio
import requests
import time
import json
from datetime import datetime
import concurrent.futures
import threading

class LatencyAnalyzer:
    def __init__(self):
        self.config = {
            'ngrok_http': 'https://2346443b1406.ngrok-free.app',
            'local_api': 'http://localhost:8000',
            'local_trading': 'http://localhost:8888',
            'test_iterations': 10
        }
        
        self.results = {}
    
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
    
    def test_network_latency(self):
        """测试网络延迟"""
        self.log("🌐 测试网络基础延迟...")
        
        endpoints = [
            {'name': '本地API', 'url': f"{self.config['local_api']}/api/health"},
            {'name': '本地交易', 'url': f"{self.config['local_trading']}/health"},
            {'name': 'ngrok隧道', 'url': f"{self.config['ngrok_http']}/api/health"}
        ]
        
        network_results = {}
        
        for endpoint in endpoints:
            latencies = []
            
            for i in range(5):  # 快速测试5次
                try:
                    start_time = time.perf_counter()
                    response = requests.get(endpoint['url'], timeout=10)
                    latency = (time.perf_counter() - start_time) * 1000
                    latencies.append(latency)
                    
                except Exception as e:
                    latencies.append(9999)
            
            avg_latency = round(sum(latencies) / len(latencies))
            min_latency = round(min(latencies))
            max_latency = round(max(latencies))
            
            network_results[endpoint['name']] = {
                'avg': avg_latency,
                'min': min_latency,
                'max': max_latency,
                'all': latencies
            }
            
            self.log(f"📊 {endpoint['name']}: 平均{avg_latency}ms (最小{min_latency}ms, 最大{max_latency}ms)")
        
        self.results['network_latency'] = network_results
        return network_results
    
    def test_trading_operation_breakdown(self):
        """分解交易操作延迟"""
        self.log("💰 分解交易操作延迟...")
        
        # 测试不同的交易操作
        operations = [
            {
                'name': '简单健康检查',
                'url': f"{self.config['local_trading']}/health",
                'method': 'GET'
            },
            {
                'name': '交易状态查询',
                'url': f"{self.config['local_trading']}/status",
                'method': 'GET'
            },
            {
                'name': '模拟交易(最小数据)',
                'url': f"{self.config['local_trading']}/trade",
                'method': 'POST',
                'data': {
                    'action': 'buy',
                    'stock_code': '000001',
                    'quantity': 1,  # 最小数量
                    'price': 1.0    # 简单价格
                }
            },
            {
                'name': '复杂交易(完整数据)',
                'url': f"{self.config['local_trading']}/trade",
                'method': 'POST',
                'data': {
                    'action': 'buy',
                    'stock_code': '000001',
                    'quantity': 100,
                    'price': 10.50,
                    'order_type': 'limit',
                    'time_in_force': 'day'
                }
            }
        ]
        
        operation_results = {}
        
        for op in operations:
            self.log(f"🧪 测试: {op['name']}")
            
            latencies = []
            
            for i in range(3):  # 测试3次
                try:
                    start_time = time.perf_counter()
                    
                    if op['method'] == 'POST':
                        response = requests.post(op['url'], json=op.get('data'), timeout=30)
                    else:
                        response = requests.get(op['url'], timeout=30)
                    
                    latency = (time.perf_counter() - start_time) * 1000
                    latencies.append(latency)
                    
                    self.log(f"   第{i+1}次: {round(latency)}ms (状态码: {response.status_code})")
                    
                except Exception as e:
                    latencies.append(9999)
                    self.log(f"   第{i+1}次: 失败 - {e}", "ERROR")
                
                time.sleep(1)  # 间隔1秒
            
            avg_latency = round(sum(latencies) / len(latencies))
            operation_results[op['name']] = {
                'avg': avg_latency,
                'all': latencies
            }
            
            self.log(f"📊 {op['name']}: 平均{avg_latency}ms")
        
        self.results['operation_breakdown'] = operation_results
        return operation_results
    
    def test_concurrent_requests(self):
        """测试并发请求性能"""
        self.log("🚀 测试并发请求性能...")
        
        def make_request():
            try:
                start_time = time.perf_counter()
                response = requests.get(f"{self.config['local_trading']}/health", timeout=10)
                latency = (time.perf_counter() - start_time) * 1000
                return latency, response.status_code
            except Exception as e:
                return 9999, 0
        
        # 测试不同并发数
        concurrent_levels = [1, 2, 5, 10]
        concurrent_results = {}
        
        for level in concurrent_levels:
            self.log(f"🔄 测试{level}个并发请求...")
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=level) as executor:
                start_time = time.perf_counter()
                futures = [executor.submit(make_request) for _ in range(level)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
                total_time = (time.perf_counter() - start_time) * 1000
            
            latencies = [r[0] for r in results]
            success_count = len([r for r in results if r[1] == 200])
            
            concurrent_results[f'{level}并发'] = {
                'total_time': round(total_time),
                'avg_latency': round(sum(latencies) / len(latencies)),
                'success_rate': round((success_count / level) * 100),
                'throughput': round(level / (total_time / 1000), 2)  # 请求/秒
            }
            
            self.log(f"📊 {level}并发: 总时间{round(total_time)}ms, 平均延迟{round(sum(latencies) / len(latencies))}ms, 成功率{round((success_count / level) * 100)}%")
        
        self.results['concurrent_performance'] = concurrent_results
        return concurrent_results
    
    def test_optimized_requests(self):
        """测试优化后的请求"""
        self.log("⚡ 测试优化后的请求...")
        
        # 使用会话复用连接
        session = requests.Session()
        session.headers.update({
            'Connection': 'keep-alive',
            'User-Agent': 'OptimizedTradingClient/1.0'
        })
        
        # 测试优化方案
        optimizations = [
            {
                'name': '会话复用',
                'session': session,
                'timeout': 10
            },
            {
                'name': '短超时',
                'session': requests,
                'timeout': 5
            },
            {
                'name': '极短超时',
                'session': requests,
                'timeout': 2
            }
        ]
        
        optimization_results = {}
        
        for opt in optimizations:
            self.log(f"🧪 测试: {opt['name']}")
            
            latencies = []
            success_count = 0
            
            for i in range(5):
                try:
                    start_time = time.perf_counter()
                    
                    if hasattr(opt['session'], 'get'):
                        response = opt['session'].get(
                            f"{self.config['local_trading']}/health", 
                            timeout=opt['timeout']
                        )
                    else:
                        response = opt['session'].get(
                            f"{self.config['local_trading']}/health", 
                            timeout=opt['timeout']
                        )
                    
                    latency = (time.perf_counter() - start_time) * 1000
                    latencies.append(latency)
                    
                    if response.status_code == 200:
                        success_count += 1
                    
                    self.log(f"   第{i+1}次: {round(latency)}ms")
                    
                except Exception as e:
                    latencies.append(9999)
                    self.log(f"   第{i+1}次: 失败 - {e}", "ERROR")
            
            avg_latency = round(sum([l for l in latencies if l < 9999]) / max(1, len([l for l in latencies if l < 9999])))
            
            optimization_results[opt['name']] = {
                'avg_latency': avg_latency,
                'success_rate': round((success_count / 5) * 100),
                'timeout': opt['timeout']
            }
            
            self.log(f"📊 {opt['name']}: 平均{avg_latency}ms, 成功率{round((success_count / 5) * 100)}%")
        
        self.results['optimized_requests'] = optimization_results
        return optimization_results
    
    def analyze_latency_sources(self):
        """分析延迟来源"""
        self.log("🔍 分析延迟来源...")
        
        network = self.results.get('network_latency', {})
        operations = self.results.get('operation_breakdown', {})
        
        # 分析网络延迟
        local_api_latency = network.get('本地API', {}).get('avg', 0)
        local_trading_latency = network.get('本地交易', {}).get('avg', 0)
        ngrok_latency = network.get('ngrok隧道', {}).get('avg', 0)
        
        # 分析操作延迟
        health_check_latency = operations.get('简单健康检查', {}).get('avg', 0)
        simple_trade_latency = operations.get('模拟交易(最小数据)', {}).get('avg', 0)
        complex_trade_latency = operations.get('复杂交易(完整数据)', {}).get('avg', 0)
        
        analysis = {
            'network_overhead': {
                'local_api': local_api_latency,
                'local_trading': local_trading_latency,
                'ngrok_tunnel': ngrok_latency,
                'tunnel_overhead': ngrok_latency - local_api_latency if ngrok_latency > 0 and local_api_latency > 0 else 0
            },
            'operation_overhead': {
                'health_check': health_check_latency,
                'simple_trade': simple_trade_latency,
                'complex_trade': complex_trade_latency,
                'trade_processing_time': complex_trade_latency - health_check_latency if complex_trade_latency > 0 and health_check_latency > 0 else 0
            }
        }
        
        self.results['latency_analysis'] = analysis
        return analysis
    
    def generate_optimization_recommendations(self):
        """生成优化建议"""
        self.log("💡 生成优化建议...")
        
        analysis = self.results.get('latency_analysis', {})
        network = analysis.get('network_overhead', {})
        operations = analysis.get('operation_overhead', {})
        
        recommendations = []
        
        # 网络优化建议
        tunnel_overhead = network.get('tunnel_overhead', 0)
        if tunnel_overhead > 500:
            recommendations.append({
                'type': 'network',
                'priority': 'high',
                'issue': f'ngrok隧道开销过大: {tunnel_overhead}ms',
                'solution': '考虑使用更快的隧道服务或直接VPN连接'
            })
        
        # 操作优化建议
        trade_processing = operations.get('trade_processing_time', 0)
        if trade_processing > 5000:
            recommendations.append({
                'type': 'processing',
                'priority': 'high',
                'issue': f'交易处理时间过长: {trade_processing}ms',
                'solution': '优化本地交易软件响应速度,检查是否有阻塞操作'
            })
        
        # 并发优化建议
        concurrent = self.results.get('concurrent_performance', {})
        if concurrent:
            best_throughput = max([v.get('throughput', 0) for v in concurrent.values()])
            if best_throughput < 5:
                recommendations.append({
                    'type': 'concurrency',
                    'priority': 'medium',
                    'issue': f'并发性能较低: {best_throughput} 请求/秒',
                    'solution': '使用连接池和会话复用提高并发性能'
                })
        
        # 超时优化建议
        optimized = self.results.get('optimized_requests', {})
        if optimized:
            best_optimization = min(optimized.values(), key=lambda x: x.get('avg_latency', 9999))
            if best_optimization.get('avg_latency', 9999) < 100:
                recommendations.append({
                    'type': 'timeout',
                    'priority': 'low',
                    'issue': '可以进一步优化超时设置',
                    'solution': f'使用{best_optimization.get("timeout", 5)}秒超时可获得最佳性能'
                })
        
        self.results['recommendations'] = recommendations
        return recommendations
    
    def display_results(self):
        """显示结果"""
        self.log("📊 延迟分析结果", "SUCCESS")
        self.log("=" * 60, "SUCCESS")
        
        # 显示网络延迟
        network = self.results.get('network_latency', {})
        if network:
            self.log("🌐 网络基础延迟:", "SUCCESS")
            for name, data in network.items():
                self.log(f"   {name}: {data['avg']}ms (范围: {data['min']}-{data['max']}ms)")
        
        print()
        
        # 显示操作延迟
        operations = self.results.get('operation_breakdown', {})
        if operations:
            self.log("💰 交易操作延迟:", "SUCCESS")
            for name, data in operations.items():
                self.log(f"   {name}: {data['avg']}ms")
        
        print()
        
        # 显示延迟分析
        analysis = self.results.get('latency_analysis', {})
        if analysis:
            self.log("🔍 延迟来源分析:", "SUCCESS")
            network_overhead = analysis.get('network_overhead', {})
            operation_overhead = analysis.get('operation_overhead', {})
            
            self.log(f"   网络隧道开销: {network_overhead.get('tunnel_overhead', 0)}ms")
            self.log(f"   交易处理时间: {operation_overhead.get('trade_processing_time', 0)}ms")
        
        print()
        
        # 显示优化建议
        recommendations = self.results.get('recommendations', [])
        if recommendations:
            self.log("💡 优化建议:", "SUCCESS")
            for i, rec in enumerate(recommendations, 1):
                priority_color = "ERROR" if rec['priority'] == 'high' else "WARNING" if rec['priority'] == 'medium' else "INFO"
                self.log(f"   {i}. [{rec['priority'].upper()}] {rec['issue']}", priority_color)
                self.log(f"      解决方案: {rec['solution']}", "INFO")
        
        print()
        
        # 总结
        self.log("🎯 优化总结:", "SUCCESS")
        
        # 找出最大的延迟来源
        max_latency_source = "未知"
        max_latency_value = 0
        
        if analysis:
            tunnel_overhead = analysis.get('network_overhead', {}).get('tunnel_overhead', 0)
            trade_processing = analysis.get('operation_overhead', {}).get('trade_processing_time', 0)
            
            if tunnel_overhead > max_latency_value:
                max_latency_value = tunnel_overhead
                max_latency_source = "网络隧道"
            
            if trade_processing > max_latency_value:
                max_latency_value = trade_processing
                max_latency_source = "交易处理"
        
        if max_latency_value > 0:
            self.log(f"   主要延迟来源: {max_latency_source} ({max_latency_value}ms)")
            
            if max_latency_value > 5000:
                self.log("   🚨 延迟过高,需要立即优化!", "ERROR")
            elif max_latency_value > 1000:
                self.log("   ⚠️ 延迟较高,建议优化", "WARNING")
            else:
                self.log("   ✅ 延迟在可接受范围内", "SUCCESS")
    
    def save_analysis_report(self):
        """保存分析报告"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'analysis_type': 'Latency Analysis and Optimization',
            'results': self.results
        }
        
        filename = f"latency_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        self.log(f"📄 延迟分析报告已保存: {filename}", "SUCCESS")
    
    def run_full_analysis(self):
        """运行完整分析"""
        self.log("🚀 开始延迟分析和优化", "INFO")
        self.log("=" * 60, "INFO")
        
        # 1. 测试网络延迟
        self.test_network_latency()
        print()
        
        # 2. 分解交易操作延迟
        self.test_trading_operation_breakdown()
        print()
        
        # 3. 测试并发性能
        self.test_concurrent_requests()
        print()
        
        # 4. 测试优化方案
        self.test_optimized_requests()
        print()
        
        # 5. 分析延迟来源
        self.analyze_latency_sources()
        
        # 6. 生成优化建议
        self.generate_optimization_recommendations()
        
        # 7. 显示结果
        self.display_results()
        
        # 8. 保存报告
        self.save_analysis_report()
        
        self.log("🎉 延迟分析完成!", "SUCCESS")

if __name__ == "__main__":
    analyzer = LatencyAnalyzer()
    analyzer.run_full_analysis()
