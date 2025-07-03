#!/usr/bin/env python3
"""
MCP Worker诊断工具
基于MCP分析结果进行深度诊断
"""

import requests
import socket
import subprocess
import time
import json
from datetime import datetime

class MCPWorkerDiagnostic:
    """MCP Worker诊断器"""
    
    def __init__(self):
        self.worker_url = "https://trading-api.308186235.workers.dev"
        self.issues_found = []
        self.solutions = []
        
    def log(self, message, level="INFO"):
        """日志输出"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = {
            "INFO": "\033[36m",     # 青色
            "SUCCESS": "\033[32m",  # 绿色
            "WARNING": "\033[33m",  # 黄色
            "ERROR": "\033[31m",    # 红色
            "RESET": "\033[0m"      # 重置
        }
        
        color = colors.get(level, colors["INFO"])
        reset = colors["RESET"]
        print(f"{color}[{timestamp}] {message}{reset}")
    
    def check_dns_resolution(self):
        """检查DNS解析"""
        self.log("🔍 检查DNS解析...")
        
        try:
            # 解析域名
            domain = self.worker_url.replace("https://", "").replace("http://", "")
            ip = socket.gethostbyname(domain)
            self.log(f"✅ DNS解析成功: {domain} -> {ip}", "SUCCESS")
            return True, ip
        except Exception as e:
            self.log(f"❌ DNS解析失败: {e}", "ERROR")
            self.issues_found.append("DNS解析失败")
            self.solutions.append("检查网络连接和DNS设置")
            return False, None
    
    def check_network_connectivity(self, ip):
        """检查网络连通性"""
        self.log("🌐 检查网络连通性...")
        
        try:
            # Ping测试
            result = subprocess.run(
                ["ping", "-n", "4", ip], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if result.returncode == 0:
                self.log("✅ Ping测试成功", "SUCCESS")
                return True
            else:
                self.log("❌ Ping测试失败", "ERROR")
                self.issues_found.append("网络连通性问题")
                return False
                
        except Exception as e:
            self.log(f"❌ 网络测试异常: {e}", "ERROR")
            return False
    
    def check_http_access(self):
        """检查HTTP访问"""
        self.log("🌍 检查HTTP访问...")
        
        test_urls = [
            self.worker_url,
            f"{self.worker_url}/",
            f"{self.worker_url}/api/agent-analysis",
            "https://httpbin.org/get"  # 对照测试
        ]
        
        for url in test_urls:
            try:
                self.log(f"   测试: {url}")
                
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    self.log(f"   ✅ 成功: {response.status_code}", "SUCCESS")
                    if url == self.worker_url:
                        # 检查响应内容
                        try:
                            data = response.json()
                            if data.get("success"):
                                self.log("   ✅ Worker响应正常", "SUCCESS")
                            else:
                                self.log("   ⚠️ Worker响应异常", "WARNING")
                        except:
                            self.log("   ⚠️ 响应非JSON格式", "WARNING")
                else:
                    self.log(f"   ❌ 失败: {response.status_code}", "ERROR")
                    
            except requests.exceptions.Timeout:
                self.log(f"   ⏰ 超时: {url}", "WARNING")
                if "httpbin.org" not in url:
                    self.issues_found.append(f"Worker访问超时: {url}")
                    
            except requests.exceptions.ConnectionError:
                self.log(f"   🔌 连接错误: {url}", "ERROR")
                if "httpbin.org" not in url:
                    self.issues_found.append(f"Worker连接失败: {url}")
                    
            except Exception as e:
                self.log(f"   ❌ 异常: {e}", "ERROR")
    
    def check_worker_logs(self):
        """检查Worker日志"""
        self.log("📋 检查Worker日志...")
        
        try:
            # 尝试获取Worker日志
            result = subprocess.run(
                ["wrangler", "tail", "--env", "production", "--format", "json"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                self.log("✅ Worker日志访问正常", "SUCCESS")
            else:
                self.log("❌ Worker日志访问失败", "ERROR")
                self.log(f"   错误: {result.stderr}", "ERROR")
                
        except subprocess.TimeoutExpired:
            self.log("⏰ Worker日志获取超时", "WARNING")
        except Exception as e:
            self.log(f"❌ Worker日志检查异常: {e}", "ERROR")
    
    def check_cloudflare_status(self):
        """检查Cloudflare服务状态"""
        self.log("☁️ 检查Cloudflare服务状态...")
        
        try:
            # 检查Cloudflare状态页面
            response = requests.get("https://www.cloudflarestatus.com/api/v2/status.json", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status", {}).get("indicator", "unknown")
                
                if status == "none":
                    self.log("✅ Cloudflare服务正常", "SUCCESS")
                else:
                    self.log(f"⚠️ Cloudflare服务状态: {status}", "WARNING")
                    self.issues_found.append(f"Cloudflare服务异常: {status}")
            else:
                self.log("❌ 无法获取Cloudflare状态", "ERROR")
                
        except Exception as e:
            self.log(f"❌ Cloudflare状态检查失败: {e}", "ERROR")
    
    def analyze_issues(self):
        """分析问题并提供解决方案"""
        self.log("🔍 分析问题...")
        
        if not self.issues_found:
            self.log("✅ 未发现明显问题", "SUCCESS")
            self.solutions.append("Worker可能正在启动中，请稍后重试")
            self.solutions.append("检查本地网络防火墙设置")
            self.solutions.append("尝试使用VPN或其他网络环境")
        else:
            self.log(f"❌ 发现 {len(self.issues_found)} 个问题", "ERROR")
            
            # 基于问题类型提供解决方案
            if any("DNS" in issue for issue in self.issues_found):
                self.solutions.append("更换DNS服务器（如8.8.8.8或1.1.1.1）")
                
            if any("连接" in issue for issue in self.issues_found):
                self.solutions.append("检查防火墙和代理设置")
                self.solutions.append("尝试使用移动网络或VPN")
                
            if any("超时" in issue for issue in self.issues_found):
                self.solutions.append("Worker可能正在冷启动，多次尝试访问")
                self.solutions.append("检查网络延迟和稳定性")
    
    def generate_report(self):
        """生成诊断报告"""
        self.log("📋 生成诊断报告...")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "worker_url": self.worker_url,
            "issues_found": self.issues_found,
            "solutions": self.solutions,
            "next_steps": [
                "1. 尝试在浏览器中直接访问Worker URL",
                "2. 检查本地网络环境和防火墙设置", 
                "3. 使用不同网络环境测试（如移动热点）",
                "4. 联系网络管理员检查企业防火墙",
                "5. 考虑使用备用方案（本地Agent后端）"
            ]
        }
        
        # 保存报告
        with open("worker_diagnostic_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.log("✅ 报告已保存: worker_diagnostic_report.json", "SUCCESS")
        return report
    
    def run_full_diagnostic(self):
        """运行完整诊断"""
        self.log("🚀 开始MCP Worker诊断...")
        self.log(f"🎯 目标Worker: {self.worker_url}")
        self.log("="*60)
        
        # 1. DNS解析检查
        dns_ok, ip = self.check_dns_resolution()
        
        # 2. 网络连通性检查
        if ip:
            self.check_network_connectivity(ip)
        
        # 3. HTTP访问检查
        self.check_http_access()
        
        # 4. Worker日志检查
        self.check_worker_logs()
        
        # 5. Cloudflare状态检查
        self.check_cloudflare_status()
        
        # 6. 问题分析
        self.analyze_issues()
        
        # 7. 生成报告
        report = self.generate_report()
        
        self.log("="*60)
        self.log("🎉 MCP诊断完成！", "SUCCESS")
        
        return report

if __name__ == "__main__":
    diagnostic = MCPWorkerDiagnostic()
    diagnostic.run_full_diagnostic()
