#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查后端和前端系统状态及配置
"""

import subprocess
import requests
import json
import os
from datetime import datetime

class SystemStatusChecker:
    def __init__(self):
        self.backend_port = 8000
        self.results = {}
        
    def log(self, message, level="INFO"):
        """日志输出"""
        colors = {
            "INFO": "\033[94m",
            "SUCCESS": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m",
            "RESET": "\033[0m"
        }
        color = colors.get(level, colors["INFO"])
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{color}[{timestamp}] {message}{colors['RESET']}")
    
    def check_backend_process(self):
        """检查后端进程"""
        self.log("🔍 检查后端进程...")
        
        try:
            result = subprocess.run(['tasklist'], capture_output=True, text=True, shell=True)
            output = result.stdout
            
            python_processes = []
            for line in output.split('\n'):
                if 'python.exe' in line.lower():
                    python_processes.append(line.strip())
            
            if python_processes:
                self.log(f"✅ 发现 {len(python_processes)} 个Python进程", "SUCCESS")
                for i, process in enumerate(python_processes[:3]):  # 只显示前3个
                    self.log(f"  {i+1}. {process}", "INFO")
                self.results['backend_process'] = True
                return True
            else:
                self.log("❌ 未发现Python进程", "ERROR")
                self.results['backend_process'] = False
                return False
                
        except Exception as e:
            self.log(f"❌ 检查进程失败: {e}", "ERROR")
            self.results['backend_process'] = False
            return False
    
    def check_backend_api(self):
        """检查后端API"""
        self.log("🔍 检查后端API...")
        
        test_endpoints = [
            f"http://127.0.0.1:{self.backend_port}/api/auth/test",
            f"http://127.0.0.1:{self.backend_port}/api/health",
            f"http://127.0.0.1:{self.backend_port}/"
        ]
        
        for endpoint in test_endpoints:
            try:
                self.log(f"测试: {endpoint}")
                response = requests.get(endpoint, timeout=5)
                
                if response.status_code == 200:
                    self.log(f"✅ {endpoint} 响应正常", "SUCCESS")
                    try:
                        data = response.json()
                        self.log(f"  响应数据: {json.dumps(data, ensure_ascii=False)[:100]}...", "INFO")
                    except:
                        self.log(f"  响应内容: {response.text[:100]}...", "INFO")
                    
                    self.results['backend_api'] = True
                    return True
                else:
                    self.log(f"⚠️ {endpoint} 响应异常: {response.status_code}", "WARNING")
                    
            except Exception as e:
                self.log(f"❌ {endpoint} 连接失败: {e}", "ERROR")
        
        self.results['backend_api'] = False
        return False
    
    def check_port_usage(self):
        """检查端口使用情况"""
        self.log("🔍 检查端口使用情况...")
        
        ports_to_check = [8000, 8080, 8888, 3000, 5173, 8081]
        
        try:
            result = subprocess.run(['netstat', '-an'], capture_output=True, text=True, shell=True)
            output = result.stdout
            
            used_ports = []
            for port in ports_to_check:
                if f":{port}" in output:
                    used_ports.append(port)
                    self.log(f"✅ 端口 {port} 正在使用", "SUCCESS")
                else:
                    self.log(f"❌ 端口 {port} 未使用", "WARNING")
            
            self.results['used_ports'] = used_ports
            return len(used_ports) > 0
            
        except Exception as e:
            self.log(f"❌ 检查端口失败: {e}", "ERROR")
            return False
    
    def check_frontend_config(self):
        """检查前端配置"""
        self.log("🔍 检查前端配置...")
        
        config_files = [
            '炒股养家/env.js',
            'frontend/stock5/env.js',
            'frontend/gupiao1/env.js'
        ]
        
        configs_found = []
        
        for config_file in config_files:
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    self.log(f"✅ 找到配置文件: {config_file}", "SUCCESS")
                    
                    # 检查API URL配置
                    if 'ngrok' in content:
                        self.log("  📡 配置使用ngrok", "INFO")
                    elif 'aigupiao.me' in content:
                        self.log("  🌐 配置使用域名", "INFO")
                    elif 'localhost' in content:
                        self.log("  💻 配置使用本地", "INFO")
                    
                    configs_found.append(config_file)
                    
                except Exception as e:
                    self.log(f"❌ 读取配置文件失败: {config_file} - {e}", "ERROR")
            else:
                self.log(f"❌ 配置文件不存在: {config_file}", "WARNING")
        
        self.results['frontend_configs'] = configs_found
        return len(configs_found) > 0
    
    def check_tunnel_status(self):
        """检查隧道状态"""
        self.log("🔍 检查隧道状态...")
        
        # 检查ngrok
        try:
            response = requests.get("http://localhost:4040/api/tunnels", timeout=3)
            if response.status_code == 200:
                tunnels = response.json().get('tunnels', [])
                if tunnels:
                    tunnel = tunnels[0]
                    url = tunnel['public_url']
                    self.log(f"✅ ngrok隧道运行: {url}", "SUCCESS")
                    self.results['ngrok_tunnel'] = url
                else:
                    self.log("❌ ngrok无活跃隧道", "WARNING")
            else:
                self.log("❌ ngrok API不可访问", "WARNING")
        except:
            self.log("❌ ngrok未运行", "WARNING")
        
        # 检查Cloudflare隧道
        try:
            result = subprocess.run(['cloudflared.exe', 'tunnel', 'info', 'aigupiao'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and "CONNECTOR ID" in result.stdout:
                self.log("✅ Cloudflare隧道连接正常", "SUCCESS")
                self.results['cloudflare_tunnel'] = True
            else:
                self.log("❌ Cloudflare隧道未连接", "WARNING")
                self.results['cloudflare_tunnel'] = False
        except:
            self.log("❌ Cloudflare隧道检查失败", "WARNING")
            self.results['cloudflare_tunnel'] = False
    
    def check_frontend_process(self):
        """检查前端进程"""
        self.log("🔍 检查前端进程...")
        
        try:
            result = subprocess.run(['tasklist'], capture_output=True, text=True, shell=True)
            output = result.stdout
            
            frontend_processes = []
            keywords = ['node.exe', 'npm.exe', 'vite', 'webpack', 'serve']
            
            for line in output.split('\n'):
                for keyword in keywords:
                    if keyword in line.lower():
                        frontend_processes.append(line.strip())
                        break
            
            if frontend_processes:
                self.log(f"✅ 发现 {len(frontend_processes)} 个前端相关进程", "SUCCESS")
                for process in frontend_processes[:3]:
                    self.log(f"  {process}", "INFO")
                self.results['frontend_process'] = True
                return True
            else:
                self.log("❌ 未发现前端进程", "WARNING")
                self.results['frontend_process'] = False
                return False
                
        except Exception as e:
            self.log(f"❌ 检查前端进程失败: {e}", "ERROR")
            return False
    
    def generate_status_report(self):
        """生成状态报告"""
        self.log("\n" + "="*60)
        self.log("📊 系统状态报告", "INFO")
        self.log("="*60)
        
        # 后端状态
        self.log("\n🔧 后端状态:")
        self.log(f"  进程运行: {'✅' if self.results.get('backend_process') else '❌'}")
        self.log(f"  API响应: {'✅' if self.results.get('backend_api') else '❌'}")
        
        # 前端状态
        self.log("\n🎨 前端状态:")
        self.log(f"  进程运行: {'✅' if self.results.get('frontend_process') else '❌'}")
        self.log(f"  配置文件: {'✅' if self.results.get('frontend_configs') else '❌'}")
        
        # 隧道状态
        self.log("\n🌐 隧道状态:")
        if self.results.get('ngrok_tunnel'):
            self.log(f"  ngrok: ✅ {self.results['ngrok_tunnel']}")
        else:
            self.log("  ngrok: ❌")
        
        self.log(f"  Cloudflare: {'✅' if self.results.get('cloudflare_tunnel') else '❌'}")
        
        # 端口使用
        if self.results.get('used_ports'):
            self.log(f"\n🔌 使用中的端口: {', '.join(map(str, self.results['used_ports']))}")
        
        # 建议
        self.log("\n💡 建议:")
        
        if not self.results.get('backend_api'):
            self.log("  ❌ 需要启动后端API服务器", "ERROR")
            self.log("    运行: python simple_api_server.py", "INFO")
        
        if not self.results.get('frontend_process'):
            self.log("  ⚠️ 前端进程未运行", "WARNING")
            self.log("    可能需要启动前端开发服务器", "INFO")
        
        if self.results.get('ngrok_tunnel'):
            self.log("  ✅ 推荐使用ngrok进行测试", "SUCCESS")
        elif self.results.get('cloudflare_tunnel'):
            self.log("  ✅ 可以使用Cloudflare隧道", "SUCCESS")
        else:
            self.log("  ⚠️ 建议启动隧道服务", "WARNING")
    
    def run_full_check(self):
        """运行完整检查"""
        self.log("🚀 开始系统状态检查...")
        
        # 检查后端
        self.check_backend_process()
        self.check_backend_api()
        
        # 检查前端
        self.check_frontend_process()
        self.check_frontend_config()
        
        # 检查网络
        self.check_port_usage()
        self.check_tunnel_status()
        
        # 生成报告
        self.generate_status_report()
        
        return self.results

if __name__ == "__main__":
    checker = SystemStatusChecker()
    results = checker.run_full_check()
    
    # 保存结果
    with open('system_status_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 检查结果已保存到: system_status_results.json")
