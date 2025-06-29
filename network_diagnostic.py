#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络连接诊断工具
用于排查端口转发、ngrok、API服务器等网络问题
"""

import socket
import subprocess
import requests
import time
import json
from datetime import datetime

class NetworkDiagnostic:
    def __init__(self):
        self.results = {}
        self.local_api_port = 8000
        self.public_ip = None
        self.ngrok_url = None
        
    def log(self, message, level="INFO"):
        """日志输出"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = {
            "INFO": "\033[94m",    # 蓝色
            "SUCCESS": "\033[92m", # 绿色
            "WARNING": "\033[93m", # 黄色
            "ERROR": "\033[91m",   # 红色
            "RESET": "\033[0m"     # 重置
        }
        color = colors.get(level, colors["INFO"])
        print(f"{color}[{timestamp}] {message}{colors['RESET']}")
    
    def check_local_api_server(self):
        """检查本地API服务器状态"""
        self.log("🔍 检查本地API服务器...")
        
        try:
            # 检查端口是否开放
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex(('127.0.0.1', self.local_api_port))
            sock.close()
            
            if result == 0:
                self.log(f"✅ 端口 {self.local_api_port} 开放", "SUCCESS")
                
                # 测试API响应
                try:
                    response = requests.get(f"http://127.0.0.1:{self.local_api_port}/api/auth/test", timeout=5)
                    if response.status_code == 200:
                        self.log("✅ API服务器响应正常", "SUCCESS")
                        self.results['local_api'] = True
                        return True
                    else:
                        self.log(f"❌ API响应异常: {response.status_code}", "ERROR")
                except Exception as e:
                    self.log(f"❌ API请求失败: {e}", "ERROR")
            else:
                self.log(f"❌ 端口 {self.local_api_port} 未开放", "ERROR")
                
        except Exception as e:
            self.log(f"❌ 本地服务器检查失败: {e}", "ERROR")
            
        self.results['local_api'] = False
        return False
    
    def get_public_ip(self):
        """获取公网IP"""
        self.log("🔍 获取公网IP...")
        
        try:
            response = requests.get("https://ipinfo.io/ip", timeout=10)
            if response.status_code == 200:
                self.public_ip = response.text.strip()
                self.log(f"✅ 公网IP: {self.public_ip}", "SUCCESS")
                return self.public_ip
        except Exception as e:
            self.log(f"❌ 获取公网IP失败: {e}", "ERROR")
        
        return None
    
    def check_ngrok_status(self):
        """检查ngrok状态"""
        self.log("🔍 检查ngrok状态...")
        
        try:
            response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=5)
            if response.status_code == 200:
                tunnels = response.json().get('tunnels', [])
                if tunnels:
                    tunnel = tunnels[0]
                    self.ngrok_url = tunnel['public_url']
                    self.log(f"✅ ngrok隧道活跃: {self.ngrok_url}", "SUCCESS")
                    
                    # 测试ngrok连接
                    try:
                        test_response = requests.get(f"{self.ngrok_url}/api/auth/test", timeout=10)
                        if test_response.status_code == 200:
                            self.log("✅ ngrok公网访问正常", "SUCCESS")
                            self.results['ngrok'] = True
                            return True
                        else:
                            self.log(f"❌ ngrok访问异常: {test_response.status_code}", "ERROR")
                    except Exception as e:
                        self.log(f"❌ ngrok访问测试失败: {e}", "ERROR")
                else:
                    self.log("❌ 没有活跃的ngrok隧道", "ERROR")
            else:
                self.log("❌ ngrok API不可访问", "ERROR")
        except Exception as e:
            self.log(f"❌ ngrok检查失败: {e}", "ERROR")
        
        self.results['ngrok'] = False
        return False
    
    def check_port_forwarding(self):
        """检查端口转发"""
        if not self.public_ip:
            self.log("⚠️ 跳过端口转发检查（无公网IP）", "WARNING")
            return False
            
        self.log("🔍 检查端口转发...")
        
        # 测试8888端口（我们配置的端口转发）
        try:
            response = requests.get(f"http://{self.public_ip}:8888/api/auth/test", timeout=10)
            if response.status_code == 200:
                self.log("✅ 端口转发工作正常", "SUCCESS")
                self.results['port_forwarding'] = True
                return True
            else:
                self.log(f"❌ 端口转发响应异常: {response.status_code}", "ERROR")
        except Exception as e:
            self.log(f"❌ 端口转发测试失败: {e}", "ERROR")
        
        self.results['port_forwarding'] = False
        return False
    
    def check_processes(self):
        """检查相关进程"""
        self.log("🔍 检查相关进程...")
        
        processes = ['python.exe', 'ngrok.exe', 'cloudflared.exe']
        running_processes = []
        
        try:
            result = subprocess.run(['tasklist'], capture_output=True, text=True, shell=True)
            output = result.stdout
            
            for process in processes:
                if process in output:
                    running_processes.append(process)
                    self.log(f"✅ {process} 正在运行", "SUCCESS")
                else:
                    self.log(f"❌ {process} 未运行", "WARNING")
            
            self.results['running_processes'] = running_processes
            
        except Exception as e:
            self.log(f"❌ 进程检查失败: {e}", "ERROR")
    
    def generate_report(self):
        """生成诊断报告"""
        self.log("\n" + "="*50)
        self.log("📊 网络诊断报告", "INFO")
        self.log("="*50)
        
        # 基本信息
        if self.public_ip:
            self.log(f"🌐 公网IP: {self.public_ip}")
        if self.ngrok_url:
            self.log(f"🔗 ngrok URL: {self.ngrok_url}")
        
        # 服务状态
        self.log("\n📋 服务状态:")
        self.log(f"  本地API服务器: {'✅ 正常' if self.results.get('local_api') else '❌ 异常'}")
        self.log(f"  ngrok隧道: {'✅ 正常' if self.results.get('ngrok') else '❌ 异常'}")
        self.log(f"  端口转发: {'✅ 正常' if self.results.get('port_forwarding') else '❌ 异常'}")
        
        # 建议
        self.log("\n💡 建议:")
        if self.results.get('local_api'):
            if self.results.get('ngrok'):
                self.log("  ✅ 推荐使用ngrok URL进行外网访问")
                self.log(f"  📱 手机可访问: {self.ngrok_url}/api/auth/test")
            elif self.results.get('port_forwarding'):
                self.log("  ✅ 推荐使用端口转发进行外网访问")
                self.log(f"  📱 手机可访问: http://{self.public_ip}:8888/api/auth/test")
            else:
                self.log("  ⚠️ 建议启用ngrok或配置端口转发")
        else:
            self.log("  ❌ 请先启动本地API服务器")
        
        return self.results
    
    def run_full_diagnostic(self):
        """运行完整诊断"""
        self.log("🚀 开始网络诊断...")
        
        # 1. 检查本地API服务器
        self.check_local_api_server()
        
        # 2. 获取公网IP
        self.get_public_ip()
        
        # 3. 检查ngrok状态
        self.check_ngrok_status()
        
        # 4. 检查端口转发
        self.check_port_forwarding()
        
        # 5. 检查进程
        self.check_processes()
        
        # 6. 生成报告
        return self.generate_report()

if __name__ == "__main__":
    diagnostic = NetworkDiagnostic()
    results = diagnostic.run_full_diagnostic()
    
    # 保存结果到文件
    with open('network_diagnostic_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 诊断结果已保存到: network_diagnostic_results.json")
