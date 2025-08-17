#!/usr/bin/env python3
"""
详细测试茶股帮连接和数据获取
"""

import socket
import time
import threading
from datetime import datetime
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

class ChaguBangTester:
    """茶股帮详细测试器"""
    
    def __init__(self):
        self.token = os.getenv("CHAGUBANG_TOKEN", "QT_wat5QfcJ6N9pDZM5")
        self.host = os.getenv("CHAGUBANG_HOST", "l1.chagubang.com")
        self.port = int(os.getenv("CHAGUBANG_PORT", "6380"))
        self.socket = None
        self.connected = False
        self.data_received = []
        
    def test_network_connectivity(self):
        """测试网络连通性"""
        print("🌐 测试网络连通性...")
        
        import subprocess
        import platform
        
        # 根据操作系统选择ping命令
        if platform.system().lower() == "windows":
            cmd = ["ping", "-n", "3", self.host]
        else:
            cmd = ["ping", "-c", "3", self.host]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✅ 网络连通性正常 - {self.host}")
                return True
            else:
                print(f"❌ 网络连通性失败 - {self.host}")
                print(f"   错误信息: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ 网络测试失败: {e}")
            return False
    
    def test_port_connectivity(self):
        """测试端口连通性"""
        print(f"🔌 测试端口连通性 {self.host}:{self.port}...")
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((self.host, self.port))
            sock.close()
            
            if result == 0:
                print(f"✅ 端口 {self.port} 可访问")
                return True
            else:
                print(f"❌ 端口 {self.port} 不可访问 (错误代码: {result})")
                return False
        except Exception as e:
            print(f"❌ 端口测试失败: {e}")
            return False
    
    def test_different_times(self):
        """测试不同时间段的连接"""
        print("⏰ 检查当前时间和交易时段...")
        
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        weekday = now.weekday()  # 0=Monday, 6=Sunday
        
        print(f"   当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   星期: {['一', '二', '三', '四', '五', '六', '日'][weekday]}")
        
        # 检查是否在交易时间
        is_trading_day = weekday < 5  # 周一到周五
        is_morning_session = "09:10" <= current_time <= "11:30"
        is_afternoon_session = "13:00" <= current_time <= "15:00"
        is_trading_time = is_trading_day and (is_morning_session or is_afternoon_session)
        
        if is_trading_time:
            print("✅ 当前在交易时间内")
        else:
            print("⚠️ 当前不在交易时间内")
            if not is_trading_day:
                print("   原因: 非交易日 (周末)")
            else:
                print("   原因: 非交易时段")
                print("   交易时段: 09:10-11:30, 13:00-15:00")
        
        return is_trading_time
    
    def connect_with_retry(self, max_retries=3):
        """带重试的连接"""
        print(f"🔄 尝试连接茶股帮服务器 (最多重试{max_retries}次)...")
        
        for attempt in range(max_retries):
            print(f"\n📡 第 {attempt + 1} 次连接尝试...")
            
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.settimeout(10)
                
                print(f"   连接到 {self.host}:{self.port}...")
                self.socket.connect((self.host, self.port))
                print("   ✅ TCP连接成功")
                
                # 发送Token
                print(f"   🔐 发送Token: {self.token}")
                self.socket.send(self.token.encode('utf-8'))
                
                # 等待认证响应
                print("   ⏳ 等待认证响应...")
                self.socket.settimeout(5)
                response = self.socket.recv(1024)
                
                if response:
                    response_text = response.decode('utf-8', errors='ignore')
                    print(f"   📨 认证响应: {repr(response_text)}")
                    
                    # 分析响应
                    if len(response_text.strip()) > 0:
                        print("   ✅ 服务器有响应，认证可能成功")
                        self.connected = True
                        return True
                    else:
                        print("   ⚠️ 服务器响应为空")
                else:
                    print("   ⚠️ 服务器无响应")
                
            except socket.timeout:
                print(f"   ❌ 第{attempt + 1}次连接超时")
            except socket.error as e:
                print(f"   ❌ 第{attempt + 1}次连接错误: {e}")
            except Exception as e:
                print(f"   ❌ 第{attempt + 1}次未知错误: {e}")
            
            # 清理连接
            if self.socket:
                try:
                    self.socket.close()
                except:
                    pass
                self.socket = None
            
            if attempt < max_retries - 1:
                print(f"   ⏳ 等待3秒后重试...")
                time.sleep(3)
        
        print("❌ 所有连接尝试都失败了")
        return False
    
    def listen_for_data(self, duration=10):
        """监听数据"""
        if not self.connected or not self.socket:
            print("❌ 未连接到服务器")
            return False
        
        print(f"👂 监听股票数据 ({duration}秒)...")
        
        try:
            self.socket.settimeout(1)  # 1秒超时，用于循环检查
            start_time = time.time()
            
            while time.time() - start_time < duration:
                try:
                    data = self.socket.recv(4096)
                    if data:
                        data_text = data.decode('utf-8', errors='ignore')
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        print(f"   📊 [{timestamp}] 收到数据: {data_text[:100]}...")
                        self.data_received.append((timestamp, data_text))
                        
                        # 分析数据格式
                        if '$' in data_text:
                            print(f"   ✅ 检测到茶股帮格式数据 (包含$分隔符)")
                        
                except socket.timeout:
                    continue  # 继续监听
                except Exception as e:
                    print(f"   ❌ 数据接收错误: {e}")
                    break
            
            if self.data_received:
                print(f"✅ 成功接收到 {len(self.data_received)} 条数据")
                return True
            else:
                print("⚠️ 未接收到任何数据")
                return False
                
        except Exception as e:
            print(f"❌ 监听过程出错: {e}")
            return False
    
    def run_comprehensive_test(self):
        """运行综合测试"""
        print("🚀 茶股帮API密钥综合测试")
        print("=" * 60)
        print(f"🔑 Token: {self.token}")
        print(f"🌐 服务器: {self.host}:{self.port}")
        print()
        
        results = {}
        
        # 测试1: 网络连通性
        results['network'] = self.test_network_connectivity()
        print()
        
        # 测试2: 端口连通性
        results['port'] = self.test_port_connectivity()
        print()
        
        # 测试3: 交易时间检查
        results['trading_time'] = self.test_different_times()
        print()
        
        # 测试4: 连接和认证
        results['connection'] = self.connect_with_retry()
        
        # 测试5: 数据监听 (如果连接成功)
        if results['connection']:
            print()
            results['data'] = self.listen_for_data(10)
        else:
            results['data'] = False
        
        # 清理连接
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        
        # 结果汇总
        print("\n" + "=" * 60)
        print("📊 测试结果汇总:")
        print(f"  网络连通性: {'✅ 正常' if results['network'] else '❌ 异常'}")
        print(f"  端口连通性: {'✅ 正常' if results['port'] else '❌ 异常'}")
        print(f"  交易时间: {'✅ 是' if results['trading_time'] else '⚠️ 否'}")
        print(f"  服务器连接: {'✅ 成功' if results['connection'] else '❌ 失败'}")
        print(f"  数据接收: {'✅ 成功' if results['data'] else '❌ 失败'}")
        
        # 诊断建议
        print("\n💡 诊断建议:")
        if not results['network']:
            print("  1. 检查网络连接和DNS解析")
        elif not results['port']:
            print("  1. 检查防火墙设置")
            print("  2. 确认服务器端口是否正确")
        elif not results['trading_time']:
            print("  1. 茶股帮可能只在交易时间提供服务")
            print("  2. 建议在交易时间 (09:10-11:30, 13:00-15:00) 重新测试")
        elif not results['connection']:
            print("  1. Token可能已过期或无效")
            print("  2. 服务器可能暂时不可用")
        elif not results['data']:
            print("  1. 连接成功但无数据，可能需要特定的请求格式")
            print("  2. 或者当前时间段没有股票数据推送")
        else:
            print("  🎉 所有测试通过！API密钥可以正常使用")
        
        return results

if __name__ == "__main__":
    tester = ChaguBangTester()
    results = tester.run_comprehensive_test()
