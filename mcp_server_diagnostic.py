#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP驱动的服务器诊断和修复工具
"""

import os
import sys
import time
import json
import socket
import requests
import subprocess
from datetime import datetime
from urllib.parse import urlparse

class MCPServerDiagnostic:
    """MCP驱动的服务器诊断工具"""
    
    def __init__(self):
        self.server_url = "http://localhost:8001"
        self.issues = []
        self.fixes = []
        
    def log_issue(self, issue_type, description, severity="medium"):
        """记录问题"""
        self.issues.append({
            "type": issue_type,
            "description": description,
            "severity": severity,
            "timestamp": datetime.now().isoformat()
        })
        
    def log_fix(self, fix_type, description, success=True):
        """记录修复"""
        self.fixes.append({
            "type": fix_type,
            "description": description,
            "success": success,
            "timestamp": datetime.now().isoformat()
        })
    
    def check_port_availability(self, port=8001):
        """检查端口可用性"""
        print(f"🔍 检查端口 {port} 可用性...")
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                result = s.connect_ex(('localhost', port))
                if result == 0:
                    print(f"✅ 端口 {port} 正在使用中")
                    return True
                else:
                    print(f"❌ 端口 {port} 未被使用")
                    self.log_issue("port", f"端口 {port} 未被使用", "high")
                    return False
        except Exception as e:
            print(f"❌ 端口检查失败: {e}")
            self.log_issue("port", f"端口检查失败: {e}", "high")
            return False
    
    def check_server_response(self):
        """检查服务器响应"""
        print("🔍 检查服务器响应...")
        
        endpoints = [
            "/",
            "/api/health",
            "/api/test/ping"
        ]
        
        for endpoint in endpoints:
            url = f"{self.server_url}{endpoint}"
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"✅ {endpoint}: {response.status_code}")
                else:
                    print(f"⚠️ {endpoint}: {response.status_code}")
                    self.log_issue("response", f"{endpoint} 返回 {response.status_code}", "medium")
            except requests.exceptions.RequestException as e:
                print(f"❌ {endpoint}: {e}")
                self.log_issue("connection", f"{endpoint} 连接失败: {e}", "high")
    
    def check_spam_requests(self):
        """检查垃圾请求"""
        print("🔍 检查垃圾请求...")
        
        # 检查是否有进程在发送大量请求
        try:
            result = subprocess.run(['netstat', '-an'], capture_output=True, text=True, timeout=10)
            connections = result.stdout.count(':8001')
            
            if connections > 10:
                print(f"⚠️ 发现 {connections} 个到端口8001的连接")
                self.log_issue("spam", f"过多连接到端口8001: {connections}", "medium")
            else:
                print(f"✅ 连接数正常: {connections}")
                
        except Exception as e:
            print(f"⚠️ 无法检查连接: {e}")
    
    def fix_spam_requests(self):
        """修复垃圾请求问题"""
        print("🔧 修复垃圾请求问题...")
        
        # 添加 /test 路由到服务器
        server_file = "backend/simple_server.py"
        
        try:
            with open(server_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否已经有 /test 路由
            if 'elif path == \'/test\':' not in content:
                # 在路由分发中添加 /test 路由
                old_route = "        elif path == '/api/t-trading/summary':\n            self._handle_trading_summary()"
                new_route = """        elif path == '/test':
            self._handle_test()
        elif path == '/api/t-trading/summary':
            self._handle_trading_summary()"""
                
                content = content.replace(old_route, new_route)
                
                # 添加处理函数
                old_handler = "    def _handle_trading_summary(self):"
                new_handler = """    def _handle_test(self):
        \"\"\"处理测试请求\"\"\"
        self._set_headers()
        response = {
            "status": "ok",
            "message": "测试端点正常",
            "timestamp": datetime.now().isoformat()
        }
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
    
    def _handle_trading_summary(self):"""
                
                content = content.replace(old_handler, new_handler)
                
                # 保存文件
                with open(server_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print("✅ 已添加 /test 路由")
                self.log_fix("route", "添加 /test 路由", True)
                return True
            else:
                print("✅ /test 路由已存在")
                return True
                
        except Exception as e:
            print(f"❌ 修复失败: {e}")
            self.log_fix("route", f"添加 /test 路由失败: {e}", False)
            return False
    
    def restart_server(self):
        """重启服务器"""
        print("🔄 重启服务器...")
        
        try:
            # 查找并终止现有服务器进程
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                                  capture_output=True, text=True)
            
            # 这里简化处理，实际应该更精确地识别服务器进程
            print("⚠️ 请手动重启服务器: python backend/simple_server.py")
            self.log_fix("restart", "建议手动重启服务器", True)
            
        except Exception as e:
            print(f"❌ 重启失败: {e}")
            self.log_fix("restart", f"重启失败: {e}", False)
    
    def generate_report(self):
        """生成诊断报告"""
        print("\n" + "="*60)
        print("📋 MCP服务器诊断报告")
        print("="*60)
        
        print(f"\n🔍 发现的问题 ({len(self.issues)}):")
        for issue in self.issues:
            severity_icon = {"low": "💡", "medium": "⚠️", "high": "❌"}
            icon = severity_icon.get(issue['severity'], "❓")
            print(f"  {icon} [{issue['type']}] {issue['description']}")
        
        print(f"\n🔧 执行的修复 ({len(self.fixes)}):")
        for fix in self.fixes:
            icon = "✅" if fix['success'] else "❌"
            print(f"  {icon} [{fix['type']}] {fix['description']}")
        
        # 保存报告到文件
        report = {
            "timestamp": datetime.now().isoformat(),
            "issues": self.issues,
            "fixes": self.fixes,
            "summary": {
                "total_issues": len(self.issues),
                "total_fixes": len(self.fixes),
                "successful_fixes": len([f for f in self.fixes if f['success']])
            }
        }
        
        with open('mcp_diagnostic_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 详细报告已保存到: mcp_diagnostic_report.json")
    
    def run_full_diagnostic(self):
        """运行完整诊断"""
        print("🚀 开始MCP驱动的服务器诊断...")
        print("="*60)
        
        # 1. 检查端口
        port_ok = self.check_port_availability()
        
        # 2. 检查服务器响应
        if port_ok:
            self.check_server_response()
        
        # 3. 检查垃圾请求
        self.check_spam_requests()
        
        # 4. 修复问题
        if any(issue['type'] == 'spam' for issue in self.issues):
            if self.fix_spam_requests():
                self.restart_server()
        
        # 5. 生成报告
        self.generate_report()
        
        print("\n🎉 诊断完成！")

def main():
    """主函数"""
    diagnostic = MCPServerDiagnostic()
    diagnostic.run_full_diagnostic()

if __name__ == "__main__":
    main()
