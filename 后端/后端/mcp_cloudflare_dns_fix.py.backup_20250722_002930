#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Cloudflare DNS修复工具
基于MCP检索的最佳实践修复cfargotunnel.com DNS配置问题
"""

import subprocess
import time
import requests
import json
from datetime import datetime

class MCPCloudflareDNSFixer:
    def __init__(self):
        self.tunnel_id = "1b454ed3-f4a8-4db9-bdb1-887f91e9e471"
        self.tunnel_name = "aigupiao"
        self.domain = "aigupiao.me"
        self.local_port = 8000
        self.cfargo_domain = f"{self.tunnel_id}.cfargotunnel.com"
        
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
    
    def run_command(self, command, timeout=30):
        """运行命令并返回结果"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "命令超时"
        except Exception as e:
            return False, "", str(e)
    
    def check_tunnel_status(self):
        """检查隧道状态"""
        self.log("🔍 检查隧道状态...")
        
        success, stdout, stderr = self.run_command(f"cloudflared.exe tunnel info {self.tunnel_name}")
        if success and "CONNECTOR ID" in stdout:
            self.log("✅ 隧道连接正常", "SUCCESS")
            return True
        else:
            self.log("❌ 隧道未连接", "ERROR")
            return False
    
    def restart_tunnel_with_correct_config(self):
        """使用正确配置重启隧道"""
        self.log("🔄 重启隧道...")
        
        # 停止现有隧道
        self.log("停止现有隧道进程...")
        self.run_command("taskkill /f /im cloudflared.exe", timeout=10)
        time.sleep(3)
        
        # 检查配置文件
        self.log("📝 验证配置文件...")
        try:
            with open('config.yml', 'r', encoding='utf-8') as f:
                config_content = f.read()
                self.log(f"当前配置:\n{config_content}")
                
                # 检查配置是否正确
                if f"service: http://127.0.0.1:{self.local_port}" in config_content:
                    self.log("✅ 配置文件端口正确", "SUCCESS")
                else:
                    self.log("❌ 配置文件端口错误", "ERROR")
                    return False
                    
        except Exception as e:
            self.log(f"❌ 读取配置文件失败: {e}", "ERROR")
            return False
        
        # 重新启动隧道
        self.log("🚀 启动隧道...")
        success, stdout, stderr = self.run_command("start \"Cloudflare隧道\" cloudflared.exe tunnel --config config.yml run")
        
        if success:
            self.log("✅ 隧道启动命令执行成功", "SUCCESS")
            time.sleep(8)  # 等待隧道建立连接
            return True
        else:
            self.log(f"❌ 隧道启动失败: {stderr}", "ERROR")
            return False
    
    def fix_dns_routing(self):
        """修复DNS路由配置"""
        self.log("🔧 修复DNS路由配置...")
        
        # 重新配置DNS路由
        commands = [
            f"cloudflared.exe tunnel route dns {self.tunnel_name} {self.domain}",
            f"cloudflared.exe tunnel route dns {self.tunnel_name} www.{self.domain}"
        ]
        
        for cmd in commands:
            self.log(f"执行: {cmd}")
            success, stdout, stderr = self.run_command(cmd)
            
            if success:
                self.log(f"✅ DNS路由配置成功", "SUCCESS")
                if stdout:
                    self.log(f"输出: {stdout.strip()}")
            else:
                self.log(f"⚠️ DNS路由配置: {stderr}", "WARNING")
        
        return True
    
    def test_cfargo_direct_access(self):
        """测试cfargotunnel.com直接访问"""
        self.log("🧪 测试cfargotunnel.com直接访问...")
        
        test_url = f"https://{self.cfargo_domain}/api/auth/test"
        self.log(f"测试URL: {test_url}")
        
        try:
            response = requests.get(test_url, timeout=15)
            if response.status_code == 200:
                self.log("✅ cfargotunnel.com直接访问成功!", "SUCCESS")
                return True
            else:
                self.log(f"❌ cfargotunnel.com访问失败: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ cfargotunnel.com访问异常: {e}", "ERROR")
            return False
    
    def test_domain_access(self):
        """测试域名访问"""
        self.log("🧪 测试域名访问...")
        
        test_urls = [
            f"https://{self.domain}/api/auth/test",
            f"http://{self.domain}/api/auth/test"
        ]
        
        for url in test_urls:
            self.log(f"测试: {url}")
            try:
                response = requests.get(url, timeout=15)
                if response.status_code == 200:
                    self.log(f"✅ 域名访问成功: {url}", "SUCCESS")
                    return True
                else:
                    self.log(f"❌ 域名访问失败: {response.status_code}", "ERROR")
            except Exception as e:
                self.log(f"❌ 域名访问异常: {e}", "ERROR")
        
        return False
    
    def show_manual_dns_fix_instructions(self):
        """显示手动DNS修复说明"""
        self.log("\n" + "="*60, "WARNING")
        self.log("🔧 手动DNS修复说明", "WARNING")
        self.log("="*60, "WARNING")
        self.log("基于MCP检索的最佳实践，请按以下步骤操作:", "INFO")
        self.log("")
        self.log("1. 登录Cloudflare控制台:", "INFO")
        self.log("   https://dash.cloudflare.com", "INFO")
        self.log("")
        self.log("2. 选择域名: aigupiao.me", "INFO")
        self.log("")
        self.log("3. 进入 'DNS' 管理页面", "INFO")
        self.log("")
        self.log("4. 编辑现有的CNAME记录:", "INFO")
        self.log("   类型: CNAME", "INFO")
        self.log("   名称: @ (或 aigupiao.me)", "INFO")
        self.log(f"   内容: {self.cfargo_domain}", "INFO")
        self.log("   代理状态: 已代理 (橙色云朵)", "INFO")
        self.log("   TTL: 自动", "INFO")
        self.log("")
        self.log("5. 保存更改并等待DNS传播 (5-30分钟)", "INFO")
        self.log("")
        self.log("6. 验证配置:", "INFO")
        self.log(f"   访问: https://{self.domain}/api/auth/test", "INFO")
        self.log("")
        self.log("="*60, "WARNING")
    
    def generate_fix_report(self):
        """生成修复报告"""
        self.log("\n" + "="*60)
        self.log("📊 MCP Cloudflare DNS修复报告", "INFO")
        self.log("="*60)
        
        self.log(f"🔧 隧道信息:")
        self.log(f"  隧道ID: {self.tunnel_id}")
        self.log(f"  隧道名称: {self.tunnel_name}")
        self.log(f"  cfargo域名: {self.cfargo_domain}")
        self.log(f"  目标域名: {self.domain}")
        self.log(f"  本地端口: {self.local_port}")
        
        self.log(f"\n💡 关键发现:")
        self.log(f"  DNS记录应该指向: {self.cfargo_domain}")
        self.log(f"  而不是隧道ID本身")
        
        self.log(f"\n🎯 下一步:")
        self.log(f"  1. 手动修复Cloudflare DNS记录")
        self.log(f"  2. 等待DNS传播")
        self.log(f"  3. 测试域名访问")
    
    def run_full_fix(self):
        """运行完整修复流程"""
        self.log("🚀 开始MCP Cloudflare DNS修复...")
        self.log("基于MCP检索的最佳实践进行修复")
        self.log("="*60)
        
        # 1. 检查并重启隧道
        if not self.restart_tunnel_with_correct_config():
            self.log("❌ 隧道重启失败，请检查配置", "ERROR")
            return False
        
        # 2. 等待隧道稳定
        self.log("⏳ 等待隧道稳定...")
        time.sleep(10)
        
        # 3. 检查隧道状态
        if not self.check_tunnel_status():
            self.log("❌ 隧道状态异常", "ERROR")
            return False
        
        # 4. 修复DNS路由
        self.fix_dns_routing()
        
        # 5. 测试cfargotunnel.com直接访问
        cfargo_ok = self.test_cfargo_direct_access()
        
        # 6. 测试域名访问
        domain_ok = self.test_domain_access()
        
        # 7. 生成报告和说明
        self.generate_fix_report()
        
        if not domain_ok:
            self.show_manual_dns_fix_instructions()
        
        if domain_ok:
            self.log("🎉 修复成功！域名访问正常", "SUCCESS")
            return True
        elif cfargo_ok:
            self.log("⚠️ 隧道工作正常，但需要手动修复DNS", "WARNING")
            return False
        else:
            self.log("❌ 隧道配置有问题，需要进一步调试", "ERROR")
            return False

if __name__ == "__main__":
    fixer = MCPCloudflareDNSFixer()
    
    try:
        success = fixer.run_full_fix()
        
        if success:
            print("\n🎉 修复完成！")
        else:
            print("\n⚠️ 需要手动操作完成修复")
            
    except KeyboardInterrupt:
        print("\n👋 修复过程被中断")
    except Exception as e:
        print(f"\n❌ 修复过程出错: {e}")
    
    # 保存修复日志
    print(f"\n📄 修复过程已记录")
