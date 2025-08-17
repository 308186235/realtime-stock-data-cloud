#!/usr/bin/env python3
"""
连接池交易解决方案
预建立多个连接,保持热连接状态,实现真正的快速交易
"""

import asyncio
import requests
import time
import json
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import queue

class ConnectionPoolTrading:
    def __init__(self):
        self.config = {
            'local_trading': 'http://localhost:8888',
            'pool_size': 5,  # 连接池大小
            'warmup_interval': 30,  # 预热间隔(秒)
            'max_idle_time': 60  # 最大空闲时间(秒)
        }
        
        # 连接池
        self.connection_pool = queue.Queue(maxsize=self.config['pool_size'])
        self.pool_stats = {
            'created': 0,
            'active': 0,
            'idle': 0,
            'total_requests': 0,
            'avg_latency': 0
        }
        
        # 预热线程
        self.warmup_thread = None
        self.is_running = True
        
        # 初始化连接池
        self.initialize_connection_pool()
        self.start_warmup_thread()
    
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
    
    def create_hot_connection(self):
        """创建热连接"""
        session = requests.Session()
        
        # 优化连接参数
        session.headers.update({
            'Connection': 'keep-alive',
            'User-Agent': 'HotConnectionTrading/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache'
        })
        
        # 设置适配器
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=1,
            pool_maxsize=1,
            max_retries=0,  # 不重试,保持快速
            pool_block=False
        )
        
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        
        # 立即预热这个连接
        try:
            start_time = time.perf_counter()
            response = session.get(f"{self.config['local_trading']}/health", timeout=2)
            warmup_time = (time.perf_counter() - start_time) * 1000
            
            if response.status_code == 200:
                connection_info = {
                    'session': session,
                    'created_at': time.time(),
                    'last_used': time.time(),
                    'warmup_time': warmup_time,
                    'request_count': 1,
                    'status': 'hot'
                }
                
                self.pool_stats['created'] += 1
                return connection_info
            else:
                session.close()
                return None
                
        except Exception as e:
            session.close()
            return None
    
    def initialize_connection_pool(self):
        """初始化连接池"""
        self.log(f"🔥 初始化连接池 (大小: {self.config['pool_size']})...")
        
        for i in range(self.config['pool_size']):
            connection = self.create_hot_connection()
            if connection:
                self.connection_pool.put(connection)
                self.log(f"✅ 连接 {i+1} 已预热 ({connection['warmup_time']:.2f}ms)", "SUCCESS")
            else:
                self.log(f"❌ 连接 {i+1} 预热失败", "ERROR")
        
        self.log(f"🎯 连接池初始化完成: {self.connection_pool.qsize()}/{self.config['pool_size']}", "SUCCESS")
    
    def get_hot_connection(self):
        """获取热连接"""
        try:
            # 非阻塞获取连接
            connection = self.connection_pool.get_nowait()
            connection['last_used'] = time.time()
            connection['status'] = 'active'
            self.pool_stats['active'] += 1
            return connection
        except queue.Empty:
            # 连接池空了,创建临时连接
            self.log("⚠️ 连接池空,创建临时连接", "WARNING")
            return self.create_hot_connection()
    
    def return_hot_connection(self, connection):
        """归还热连接"""
        if connection and connection.get('session'):
            connection['last_used'] = time.time()
            connection['status'] = 'idle'
            
            try:
                self.connection_pool.put_nowait(connection)
                self.pool_stats['active'] = max(0, self.pool_stats['active'] - 1)
                self.pool_stats['idle'] += 1
            except queue.Full:
                # 连接池满了,关闭这个连接
                connection['session'].close()
    
    def hot_connection_trade(self, action, stock_code, quantity, price=None):
        """使用热连接进行交易"""
        trade_id = f"hot_trade_{int(time.time() * 1000)}"
        
        # 获取热连接
        connection = self.get_hot_connection()
        if not connection:
            return {
                'trade_id': trade_id,
                'success': False,
                'error': 'no_connection_available',
                'latency': 9999
            }
        
        trade_data = {
            'action': action,
            'stock_code': stock_code,
            'quantity': quantity,
            'price': price,
            'trade_id': trade_id,
            'hot_connection': True,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            start_time = time.perf_counter()
            
            # 使用热连接发送请求
            response = connection['session'].post(
                f"{self.config['local_trading']}/trade",
                json=trade_data,
                timeout=25  # 稍微短一点的超时
            )
            
            latency = (time.perf_counter() - start_time) * 1000
            
            # 更新连接统计
            connection['request_count'] += 1
            self.pool_stats['total_requests'] += 1
            
            result = {
                'trade_id': trade_id,
                'success': response.status_code == 200,
                'latency': round(latency, 2),
                'status_code': response.status_code,
                'connection_reused': True,
                'connection_age': time.time() - connection['created_at'],
                'timestamp': datetime.now().isoformat()
            }
            
            if response.status_code == 200:
                try:
                    result['response'] = response.json()
                except:
                    result['response'] = response.text[:200]
                
                self.log(f"✅ 热连接交易成功: {trade_id} ({round(latency, 2)}ms)", "SUCCESS")
            else:
                result['error'] = f"HTTP {response.status_code}"
                self.log(f"⚠️ 热连接交易异常: {trade_id} (状态码: {response.status_code})", "WARNING")
            
            # 归还连接
            self.return_hot_connection(connection)
            
            return result
            
        except requests.exceptions.Timeout:
            self.log(f"⏰ 热连接交易超时: {trade_id}", "WARNING")
            # 超时的连接可能有问题,不归还到池中
            connection['session'].close()
            
            return {
                'trade_id': trade_id,
                'success': False,
                'error': 'timeout',
                'latency': 25000
            }
            
        except Exception as e:
            self.log(f"❌ 热连接交易失败: {trade_id} - {e}", "ERROR")
            # 出错的连接关闭
            connection['session'].close()
            
            return {
                'trade_id': trade_id,
                'success': False,
                'error': str(e),
                'latency': 9999
            }
    
    def start_warmup_thread(self):
        """启动预热线程"""
        def warmup_worker():
            while self.is_running:
                try:
                    # 检查连接池状态
                    current_size = self.connection_pool.qsize()
                    target_size = self.config['pool_size']
                    
                    if current_size < target_size:
                        # 补充连接
                        needed = target_size - current_size
                        self.log(f"🔄 补充连接池: 需要{needed}个连接", "INFO")
                        
                        for _ in range(needed):
                            connection = self.create_hot_connection()
                            if connection:
                                try:
                                    self.connection_pool.put_nowait(connection)
                                except queue.Full:
                                    connection['session'].close()
                                    break
                    
                    # 预热现有连接
                    self.warmup_existing_connections()
                    
                    time.sleep(self.config['warmup_interval'])
                    
                except Exception as e:
                    self.log(f"❌ 预热线程异常: {e}", "ERROR")
                    time.sleep(5)
        
        self.warmup_thread = threading.Thread(target=warmup_worker, daemon=True)
        self.warmup_thread.start()
        self.log("🔥 预热线程已启动", "SUCCESS")
    
    def warmup_existing_connections(self):
        """预热现有连接"""
        temp_connections = []
        
        # 取出所有连接进行预热
        while not self.connection_pool.empty():
            try:
                connection = self.connection_pool.get_nowait()
                
                # 检查连接是否太老
                age = time.time() - connection['created_at']
                if age > self.config['max_idle_time']:
                    # 关闭老连接
                    connection['session'].close()
                    continue
                
                # 预热连接
                try:
                    start_time = time.perf_counter()
                    response = connection['session'].get(
                        f"{self.config['local_trading']}/health", 
                        timeout=2
                    )
                    warmup_time = (time.perf_counter() - start_time) * 1000
                    
                    if response.status_code == 200:
                        connection['last_warmup'] = time.time()
                        connection['warmup_time'] = warmup_time
                        temp_connections.append(connection)
                    else:
                        connection['session'].close()
                        
                except:
                    connection['session'].close()
                    
            except queue.Empty:
                break
        
        # 将预热好的连接放回池中
        for connection in temp_connections:
            try:
                self.connection_pool.put_nowait(connection)
            except queue.Full:
                connection['session'].close()
    
    def test_hot_connection_performance(self):
        """测试热连接性能"""
        self.log("🔥 测试热连接交易性能...")
        
        # 连续快速交易测试
        test_trades = [
            {'action': 'buy', 'stock_code': '000001', 'quantity': 100},
            {'action': 'sell', 'stock_code': '000002', 'quantity': 200},
            {'action': 'buy', 'stock_code': '000003', 'quantity': 150},
            {'action': 'sell', 'stock_code': '000001', 'quantity': 50},
            {'action': 'buy', 'stock_code': '000004', 'quantity': 300},
            {'action': 'sell', 'stock_code': '000005', 'quantity': 250},
            {'action': 'buy', 'stock_code': '000006', 'quantity': 180},
            {'action': 'sell', 'stock_code': '000007', 'quantity': 120}
        ]
        
        results = []
        total_start_time = time.perf_counter()
        
        for i, trade in enumerate(test_trades, 1):
            self.log(f"🚀 热连接交易 {i}: {trade['action'].upper()} {trade['stock_code']}")
            
            result = self.hot_connection_trade(
                trade['action'],
                trade['stock_code'],
                trade['quantity'],
                10.50 + i * 0.1
            )
            
            results.append(result)
            
            # 极短间隔,测试连接复用效果
            time.sleep(0.05)
        
        total_time = (time.perf_counter() - total_start_time) * 1000
        
        # 分析结果
        successful_trades = [r for r in results if r.get('success', False)]
        latencies = [r['latency'] for r in successful_trades if r['latency'] < 9999]
        
        if latencies:
            avg_latency = sum(latencies) / len(latencies)
            min_latency = min(latencies)
            max_latency = max(latencies)
            
            self.log("📊 热连接性能测试结果:", "SUCCESS")
            self.log(f"   总交易数: {len(test_trades)}")
            self.log(f"   成功交易: {len(successful_trades)}")
            self.log(f"   成功率: {round(len(successful_trades)/len(test_trades)*100, 1)}%")
            self.log(f"   平均延迟: {round(avg_latency, 2)}ms")
            self.log(f"   最小延迟: {round(min_latency, 2)}ms")
            self.log(f"   最大延迟: {round(max_latency, 2)}ms")
            self.log(f"   总耗时: {round(total_time, 2)}ms")
            self.log(f"   吞吐量: {round(len(successful_trades)/(total_time/1000), 2)} 交易/秒")
            
            # 连接复用统计
            reused_connections = len([r for r in successful_trades if r.get('connection_reused')])
            self.log(f"   连接复用率: {round(reused_connections/len(successful_trades)*100, 1)}%")
            
            return {
                'avg_latency': round(avg_latency, 2),
                'min_latency': round(min_latency, 2),
                'max_latency': round(max_latency, 2),
                'success_rate': round(len(successful_trades)/len(test_trades)*100, 1),
                'throughput': round(len(successful_trades)/(total_time/1000), 2),
                'connection_reuse_rate': round(reused_connections/len(successful_trades)*100, 1)
            }
        else:
            self.log("❌ 所有交易都失败了", "ERROR")
            return None
    
    def get_pool_statistics(self):
        """获取连接池统计"""
        return {
            'pool_size': self.connection_pool.qsize(),
            'target_size': self.config['pool_size'],
            'created_connections': self.pool_stats['created'],
            'total_requests': self.pool_stats['total_requests'],
            'active_connections': self.pool_stats['active'],
            'idle_connections': self.pool_stats['idle']
        }
    
    def display_final_summary(self, performance):
        """显示最终总结"""
        self.log("🎯 热连接交易解决方案总结", "SUCCESS")
        self.log("=" * 50, "SUCCESS")
        
        # 连接池状态
        stats = self.get_pool_statistics()
        self.log("🔥 连接池状态:", "SUCCESS")
        self.log(f"   当前连接数: {stats['pool_size']}/{stats['target_size']}")
        self.log(f"   总创建连接: {stats['created_connections']}")
        self.log(f"   总处理请求: {stats['total_requests']}")
        
        # 性能对比
        if performance:
            self.log("⚡ 性能表现:", "SUCCESS")
            self.log(f"   平均延迟: {performance['avg_latency']}ms")
            self.log(f"   最小延迟: {performance['min_latency']}ms")
            self.log(f"   成功率: {performance['success_rate']}%")
            self.log(f"   吞吐量: {performance['throughput']} 交易/秒")
            self.log(f"   连接复用率: {performance['connection_reuse_rate']}%")
            
            # 与原始方案对比
            if performance['avg_latency'] < 7643:
                improvement = round(((7643 - performance['avg_latency']) / 7643) * 100, 1)
                speed_up = round(7643 / performance['avg_latency'], 1)
                self.log(f"   性能提升: {improvement}%", "SUCCESS")
                self.log(f"   速度提升: {speed_up}倍", "SUCCESS")
                self.log(f"   延迟改善: 从7643ms → {performance['avg_latency']}ms", "SUCCESS")
        
        # 优化效果评估
        if performance and performance['avg_latency'] < 1000:
            self.log("🏆 优化效果: 优秀!延迟已降至1秒以下", "SUCCESS")
        elif performance and performance['avg_latency'] < 3000:
            self.log("✅ 优化效果: 良好!延迟显著改善", "SUCCESS")
        else:
            self.log("⚠️ 优化效果: 有限,仍需进一步优化", "WARNING")
    
    def cleanup(self):
        """清理资源"""
        self.is_running = False
        
        # 关闭所有连接
        while not self.connection_pool.empty():
            try:
                connection = self.connection_pool.get_nowait()
                connection['session'].close()
            except:
                break
        
        self.log("🧹 资源清理完成", "SUCCESS")
    
    def run_hot_connection_test(self):
        """运行热连接测试"""
        try:
            self.log("🔥 启动热连接交易测试", "INFO")
            self.log("=" * 60, "INFO")
            
            # 等待连接池完全初始化
            time.sleep(2)
            
            # 运行性能测试
            performance = self.test_hot_connection_performance()
            print()
            
            # 显示总结
            self.display_final_summary(performance)
            
            self.log("🎉 热连接交易测试完成!", "SUCCESS")
            
        finally:
            self.cleanup()

if __name__ == "__main__":
    trading = ConnectionPoolTrading()
    trading.run_hot_connection_test()
