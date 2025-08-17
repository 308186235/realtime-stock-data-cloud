#!/usr/bin/env python3
"""
根本原因分析:为什么交易延迟这么高?
深入分析本地交易软件的真实问题
"""

import requests
import time
import json
import threading
import subprocess
import psutil
from datetime import datetime

class RootCauseAnalyzer:
    def __init__(self):
        self.config = {
            'local_trading': 'http://localhost:8888',
            'local_api': 'http://localhost:8000'
        }
        
        self.analysis_results = {}
    
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
    
    def analyze_system_resources(self):
        """分析系统资源使用情况"""
        self.log("🖥️ 分析系统资源使用情况...")
        
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # 内存使用情况
        memory = psutil.virtual_memory()
        
        # 磁盘IO
        disk_io = psutil.disk_io_counters()
        
        # 网络IO
        network_io = psutil.net_io_counters()
        
        system_info = {
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_available_gb': round(memory.available / (1024**3), 2),
            'disk_read_mb': round(disk_io.read_bytes / (1024**2), 2) if disk_io else 0,
            'disk_write_mb': round(disk_io.write_bytes / (1024**2), 2) if disk_io else 0,
            'network_sent_mb': round(network_io.bytes_sent / (1024**2), 2) if network_io else 0,
            'network_recv_mb': round(network_io.bytes_recv / (1024**2), 2) if network_io else 0
        }
        
        self.log(f"📊 系统资源状态:", "SUCCESS")
        self.log(f"   CPU使用率: {cpu_percent}%")
        self.log(f"   内存使用率: {memory.percent}%")
        self.log(f"   可用内存: {system_info['memory_available_gb']}GB")
        
        self.analysis_results['system_resources'] = system_info
        return system_info
    
    def analyze_process_performance(self):
        """分析相关进程性能"""
        self.log("🔍 分析相关进程性能...")
        
        processes_info = {}
        
        # 查找相关进程
        target_processes = ['python', 'node', 'ngrok', 'cloudflared']
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'create_time']):
            try:
                proc_info = proc.info
                proc_name = proc_info['name'].lower()
                
                for target in target_processes:
                    if target in proc_name:
                        processes_info[f"{proc_info['name']}_{proc_info['pid']}"] = {
                            'pid': proc_info['pid'],
                            'name': proc_info['name'],
                            'cpu_percent': proc_info['cpu_percent'],
                            'memory_percent': proc_info['memory_percent'],
                            'running_time': time.time() - proc_info['create_time']
                        }
                        
                        self.log(f"📋 进程: {proc_info['name']} (PID: {proc_info['pid']})")
                        self.log(f"   CPU: {proc_info['cpu_percent']}%, 内存: {proc_info['memory_percent']:.2f}%")
                        break
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        self.analysis_results['processes'] = processes_info
        return processes_info
    
    def analyze_network_stack(self):
        """分析网络协议栈"""
        self.log("🌐 分析网络协议栈...")
        
        network_tests = [
            {'name': '本地回环', 'host': '127.0.0.1', 'port': 8888},
            {'name': 'localhost', 'host': 'localhost', 'port': 8888},
            {'name': '本机IP', 'host': '0.0.0.0', 'port': 8888}
        ]
        
        network_results = {}
        
        for test in network_tests:
            try:
                import socket
                start_time = time.perf_counter()
                
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex((test['host'], test['port']))
                sock.close()
                
                latency = (time.perf_counter() - start_time) * 1000
                
                network_results[test['name']] = {
                    'success': result == 0,
                    'latency': round(latency, 2),
                    'host': test['host'],
                    'port': test['port']
                }
                
                if result == 0:
                    self.log(f"✅ {test['name']}: {round(latency, 2)}ms", "SUCCESS")
                else:
                    self.log(f"❌ {test['name']}: 连接失败", "ERROR")
                    
            except Exception as e:
                network_results[test['name']] = {
                    'success': False,
                    'error': str(e)
                }
                self.log(f"❌ {test['name']}: {e}", "ERROR")
        
        self.analysis_results['network_stack'] = network_results
        return network_results
    
    def analyze_request_breakdown(self):
        """分解请求处理时间"""
        self.log("⏱️ 分解请求处理时间...")
        
        # 测试不同阶段的延迟
        stages = [
            {'name': 'DNS解析', 'url': 'http://localhost:8888/health'},
            {'name': 'TCP连接', 'url': 'http://127.0.0.1:8888/health'},
            {'name': 'HTTP请求', 'url': 'http://localhost:8888/health'},
            {'name': '简单响应', 'url': 'http://localhost:8888/ping'},
            {'name': '状态查询', 'url': 'http://localhost:8888/status'},
            {'name': '复杂交易', 'url': 'http://localhost:8888/trade'}
        ]
        
        breakdown_results = {}
        
        for stage in stages:
            latencies = []
            
            for i in range(3):  # 测试3次
                try:
                    start_time = time.perf_counter()
                    
                    if stage['name'] == '复杂交易':
                        response = requests.post(
                            stage['url'],
                            json={
                                'action': 'buy',
                                'stock_code': '000001',
                                'quantity': 100,
                                'price': 10.50
                            },
                            timeout=30
                        )
                    else:
                        response = requests.get(stage['url'], timeout=10)
                    
                    latency = (time.perf_counter() - start_time) * 1000
                    latencies.append(latency)
                    
                    self.log(f"   {stage['name']} 第{i+1}次: {round(latency, 2)}ms (状态码: {response.status_code})")
                    
                except Exception as e:
                    latencies.append(9999)
                    self.log(f"   {stage['name']} 第{i+1}次: 失败 - {e}", "ERROR")
                
                time.sleep(0.5)
            
            valid_latencies = [l for l in latencies if l < 9999]
            if valid_latencies:
                avg_latency = sum(valid_latencies) / len(valid_latencies)
                breakdown_results[stage['name']] = {
                    'avg_latency': round(avg_latency, 2),
                    'min_latency': round(min(valid_latencies), 2),
                    'max_latency': round(max(valid_latencies), 2),
                    'success_rate': len(valid_latencies) / len(latencies) * 100
                }
                
                self.log(f"📊 {stage['name']}: 平均{round(avg_latency, 2)}ms", "SUCCESS")
            else:
                breakdown_results[stage['name']] = {
                    'avg_latency': 9999,
                    'success_rate': 0
                }
                self.log(f"❌ {stage['name']}: 全部失败", "ERROR")
        
        self.analysis_results['request_breakdown'] = breakdown_results
        return breakdown_results
    
    def analyze_trading_software_behavior(self):
        """分析交易软件行为"""
        self.log("🔬 分析交易软件行为...")
        
        # 监控交易软件在处理请求时的行为
        behavior_analysis = {}
        
        # 测试不同类型的请求
        request_types = [
            {'name': '健康检查', 'method': 'GET', 'endpoint': '/health', 'expected_fast': True},
            {'name': '状态查询', 'method': 'GET', 'endpoint': '/status', 'expected_fast': True},
            {'name': '余额查询', 'method': 'GET', 'endpoint': '/balance', 'expected_fast': False},
            {'name': '持仓查询', 'method': 'GET', 'endpoint': '/positions', 'expected_fast': False},
            {'name': '模拟交易', 'method': 'POST', 'endpoint': '/trade', 'expected_fast': False, 'data': {
                'action': 'buy', 'stock_code': '000001', 'quantity': 1, 'simulate': True
            }},
            {'name': '真实交易', 'method': 'POST', 'endpoint': '/trade', 'expected_fast': False, 'data': {
                'action': 'buy', 'stock_code': '000001', 'quantity': 100, 'price': 10.50
            }}
        ]
        
        for req_type in request_types:
            self.log(f"🧪 测试: {req_type['name']}")
            
            try:
                start_time = time.perf_counter()
                
                if req_type['method'] == 'POST':
                    response = requests.post(
                        f"{self.config['local_trading']}{req_type['endpoint']}",
                        json=req_type.get('data', {}),
                        timeout=30
                    )
                else:
                    response = requests.get(
                        f"{self.config['local_trading']}{req_type['endpoint']}",
                        timeout=30
                    )
                
                latency = (time.perf_counter() - start_time) * 1000
                
                behavior_analysis[req_type['name']] = {
                    'latency': round(latency, 2),
                    'status_code': response.status_code,
                    'expected_fast': req_type['expected_fast'],
                    'actually_fast': latency < 1000,
                    'response_size': len(response.content),
                    'content_type': response.headers.get('content-type', 'unknown')
                }
                
                # 分析响应内容
                if response.status_code == 200:
                    try:
                        json_response = response.json()
                        behavior_analysis[req_type['name']]['response_type'] = 'json'
                        behavior_analysis[req_type['name']]['response_keys'] = list(json_response.keys()) if isinstance(json_response, dict) else []
                    except:
                        behavior_analysis[req_type['name']]['response_type'] = 'text'
                
                # 判断性能是否符合预期
                if req_type['expected_fast'] and latency > 1000:
                    self.log(f"⚠️ {req_type['name']}: {round(latency, 2)}ms (预期快速但实际很慢)", "WARNING")
                elif not req_type['expected_fast'] and latency > 5000:
                    self.log(f"❌ {req_type['name']}: {round(latency, 2)}ms (即使预期慢也太慢了)", "ERROR")
                else:
                    self.log(f"✅ {req_type['name']}: {round(latency, 2)}ms", "SUCCESS")
                
            except Exception as e:
                behavior_analysis[req_type['name']] = {
                    'error': str(e),
                    'latency': 9999,
                    'expected_fast': req_type['expected_fast']
                }
                self.log(f"❌ {req_type['name']}: 失败 - {e}", "ERROR")
        
        self.analysis_results['trading_software_behavior'] = behavior_analysis
        return behavior_analysis
    
    def identify_bottlenecks(self):
        """识别性能瓶颈"""
        self.log("🎯 识别性能瓶颈...")
        
        bottlenecks = []
        
        # 分析系统资源
        system = self.analysis_results.get('system_resources', {})
        if system.get('cpu_percent', 0) > 80:
            bottlenecks.append({
                'type': 'CPU',
                'severity': 'high',
                'description': f'CPU使用率过高: {system["cpu_percent"]}%',
                'recommendation': '检查CPU密集型进程,考虑优化算法或增加CPU资源'
            })
        
        if system.get('memory_percent', 0) > 90:
            bottlenecks.append({
                'type': 'Memory',
                'severity': 'high',
                'description': f'内存使用率过高: {system["memory_percent"]}%',
                'recommendation': '检查内存泄漏,优化内存使用或增加内存'
            })
        
        # 分析请求处理时间
        breakdown = self.analysis_results.get('request_breakdown', {})
        
        # 找出最慢的操作
        slow_operations = []
        for name, data in breakdown.items():
            if data.get('avg_latency', 0) > 5000:  # 超过5秒
                slow_operations.append((name, data['avg_latency']))
        
        if slow_operations:
            slow_operations.sort(key=lambda x: x[1], reverse=True)
            bottlenecks.append({
                'type': 'Slow Operations',
                'severity': 'critical',
                'description': f'发现{len(slow_operations)}个超慢操作',
                'details': slow_operations,
                'recommendation': '这些操作是主要瓶颈,需要重点优化'
            })
        
        # 分析交易软件行为
        behavior = self.analysis_results.get('trading_software_behavior', {})
        unexpected_slow = []
        
        for name, data in behavior.items():
            if data.get('expected_fast', False) and data.get('latency', 0) > 1000:
                unexpected_slow.append((name, data['latency']))
        
        if unexpected_slow:
            bottlenecks.append({
                'type': 'Unexpected Slow Operations',
                'severity': 'high',
                'description': '预期快速的操作实际很慢',
                'details': unexpected_slow,
                'recommendation': '检查这些操作的实现,可能存在不必要的阻塞'
            })
        
        self.analysis_results['bottlenecks'] = bottlenecks
        return bottlenecks
    
    def generate_optimization_plan(self):
        """生成优化方案"""
        self.log("💡 生成优化方案...")
        
        bottlenecks = self.analysis_results.get('bottlenecks', [])
        
        optimization_plan = {
            'immediate_actions': [],
            'short_term_improvements': [],
            'long_term_solutions': []
        }
        
        # 基于瓶颈分析生成方案
        for bottleneck in bottlenecks:
            if bottleneck['severity'] == 'critical':
                if bottleneck['type'] == 'Slow Operations':
                    optimization_plan['immediate_actions'].extend([
                        '立即检查交易软件配置,禁用不必要的验证步骤',
                        '启用交易软件的快速模式(如果支持)',
                        '检查是否有阻塞的网络调用或文件IO操作'
                    ])
            
            elif bottleneck['severity'] == 'high':
                if bottleneck['type'] == 'CPU':
                    optimization_plan['short_term_improvements'].append('优化CPU密集型操作')
                elif bottleneck['type'] == 'Memory':
                    optimization_plan['short_term_improvements'].append('优化内存使用')
        
        # 通用优化建议
        optimization_plan['immediate_actions'].extend([
            '使用异步处理架构,立即返回确认',
            '实现连接池和会话复用',
            '添加请求缓存机制'
        ])
        
        optimization_plan['short_term_improvements'].extend([
            '优化交易软件配置参数',
            '实现批量交易处理',
            '添加性能监控和告警'
        ])
        
        optimization_plan['long_term_solutions'].extend([
            '考虑更换更快的交易软件',
            '实现分布式交易处理',
            '使用专业的交易API替代现有方案'
        ])
        
        return optimization_plan
    
    def display_comprehensive_analysis(self):
        """显示综合分析结果"""
        self.log("📊 综合分析结果", "SUCCESS")
        self.log("=" * 60, "SUCCESS")
        
        # 显示瓶颈
        bottlenecks = self.analysis_results.get('bottlenecks', [])
        if bottlenecks:
            self.log("🚨 发现的性能瓶颈:", "ERROR")
            for i, bottleneck in enumerate(bottlenecks, 1):
                severity_color = "ERROR" if bottleneck['severity'] == 'critical' else "WARNING"
                self.log(f"{i}. [{bottleneck['severity'].upper()}] {bottleneck['type']}", severity_color)
                self.log(f"   问题: {bottleneck['description']}", "INFO")
                self.log(f"   建议: {bottleneck['recommendation']}", "INFO")
                if 'details' in bottleneck:
                    self.log(f"   详情: {bottleneck['details']}", "INFO")
                print()
        
        # 显示优化方案
        plan = self.generate_optimization_plan()
        
        self.log("💡 优化方案:", "SUCCESS")
        
        if plan['immediate_actions']:
            self.log("🚨 立即行动:", "ERROR")
            for action in plan['immediate_actions']:
                self.log(f"   • {action}", "INFO")
            print()
        
        if plan['short_term_improvements']:
            self.log("⚡ 短期改进:", "WARNING")
            for improvement in plan['short_term_improvements']:
                self.log(f"   • {improvement}", "INFO")
            print()
        
        if plan['long_term_solutions']:
            self.log("🎯 长期方案:", "SUCCESS")
            for solution in plan['long_term_solutions']:
                self.log(f"   • {solution}", "INFO")
        
        # 总结
        print()
        self.log("🎯 根本原因总结:", "SUCCESS")
        
        # 分析最慢的操作
        breakdown = self.analysis_results.get('request_breakdown', {})
        if breakdown:
            slowest_op = max(breakdown.items(), key=lambda x: x[1].get('avg_latency', 0))
            self.log(f"最慢操作: {slowest_op[0]} ({slowest_op[1]['avg_latency']}ms)", "ERROR")
        
        behavior = self.analysis_results.get('trading_software_behavior', {})
        if behavior:
            trade_latency = behavior.get('真实交易', {}).get('latency', 0)
            if trade_latency > 5000:
                self.log(f"核心问题: 交易软件本身处理慢 ({trade_latency}ms)", "ERROR")
                self.log("这不是网络问题,是交易软件的内部处理问题!", "ERROR")
    
    def run_comprehensive_analysis(self):
        """运行综合分析"""
        self.log("🔬 开始根本原因分析", "INFO")
        self.log("=" * 60, "INFO")
        
        # 1. 系统资源分析
        self.analyze_system_resources()
        print()
        
        # 2. 进程性能分析
        self.analyze_process_performance()
        print()
        
        # 3. 网络协议栈分析
        self.analyze_network_stack()
        print()
        
        # 4. 请求处理时间分解
        self.analyze_request_breakdown()
        print()
        
        # 5. 交易软件行为分析
        self.analyze_trading_software_behavior()
        print()
        
        # 6. 识别瓶颈
        self.identify_bottlenecks()
        print()
        
        # 7. 显示综合分析
        self.display_comprehensive_analysis()
        
        self.log("🎉 根本原因分析完成!", "SUCCESS")

if __name__ == "__main__":
    analyzer = RootCauseAnalyzer()
    analyzer.run_comprehensive_analysis()
