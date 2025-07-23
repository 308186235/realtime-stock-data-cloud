#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP修复Cloudflare DNS IPv4地址配置
解决子域名DNS记录需要正确IPv4地址的问题
"""

import requests
import socket
import subprocess
import json
import time
from datetime import datetime

class CloudflareDNSFixer:
    def __init__(self):
        self.domain = "aigupiao.me"
        self.subdomains = ["app", "api", "mobile", "admin", "ws", "docs"]
        self.cloudflare_ips = []
        
    def log(self, message, level="INFO"):
        """日志输出"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = {
            "INFO": "\033[36m",      # 青色
            "SUCCESS": "\033[32m",   # 绿色
            "WARNING": "\033[33m",   # 黄色
            "ERROR": "\033[31m",     # 红色
            "RESET": "\033[0m"       # 重置
        }
        color = colors.get(level, colors["INFO"])
        print(f"{color}[{timestamp}] {message}{colors['RESET']}")
        
    def get_cloudflare_pages_ips(self):
        """获取Cloudflare Pages的IPv4地址"""
        self.log("🔍 获取Cloudflare Pages IPv4地址...")
        
        # Cloudflare Pages常用的IPv4地址
        known_cf_ips = [
            "104.21.0.0",
            "172.67.0.0", 
            "104.26.0.0",
            "108.162.192.0"
        ]
        
        # 尝试解析一些知名的Cloudflare Pages站点
        test_domains = [
            "pages.dev",
            "cloudflare.com",
            "workers.dev"
        ]
        
        found_ips = set()
        
        for domain in test_domains:
            try:
                result = socket.getaddrinfo(domain, None, socket.AF_INET)
                for item in result:
                    ip = item[4][0]
                    if ip.startswith(('104.', '172.', '108.')):
                        found_ips.add(ip)
                        self.log(f"发现Cloudflare IP: {ip}")
            except Exception as e:
                self.log(f"解析 {domain} 失败: {e}", "WARNING")
                
        # 如果没找到,使用已知的IP段
        if not found_ips:
            self.log("使用已知的Cloudflare IP地址", "INFO")
            found_ips = {"104.21.0.1", "172.67.0.1"}
            
        self.cloudflare_ips = list(found_ips)
        return self.cloudflare_ips
        
    def get_recommended_ip(self):
        """获取推荐的IP地址"""
        if not self.cloudflare_ips:
            self.get_cloudflare_pages_ips()
            
        # 优先使用104.21.x.x段的IP
        for ip in self.cloudflare_ips:
            if ip.startswith('104.21.'):
                return ip
                
        # 其次使用172.67.x.x段的IP  
        for ip in self.cloudflare_ips:
            if ip.startswith('172.67.'):
                return ip
                
        # 默认返回第一个
        return self.cloudflare_ips[0] if self.cloudflare_ips else "104.21.0.1"
        
    def test_ip_connectivity(self, ip):
        """测试IP地址连通性"""
        try:
            # 尝试连接到80端口
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((ip, 80))
            sock.close()
            
            if result == 0:
                self.log(f"✅ IP {ip} 连通性测试通过", "SUCCESS")
                return True
            else:
                self.log(f"❌ IP {ip} 连通性测试失败", "WARNING")
                return False
        except Exception as e:
            self.log(f"❌ IP {ip} 测试异常: {e}", "ERROR")
            return False
            
    def generate_dns_config(self):
        """生成DNS配置建议"""
        recommended_ip = self.get_recommended_ip()
        
        self.log("📋 生成DNS配置建议...")
        
        config = {
            "domain": self.domain,
            "recommended_ip": recommended_ip,
            "dns_records": []
        }
        
        # 为每个子域名生成A记录
        for subdomain in self.subdomains:
            record = {
                "type": "A",
                "name": subdomain,
                "content": recommended_ip,
                "proxy": True,
                "ttl": "Auto"
            }
            config["dns_records"].append(record)
            
        return config
        
    def print_dns_instructions(self, config):
        """打印DNS配置说明"""
        self.log("=" * 60)
        self.log("🎯 Cloudflare DNS配置说明", "SUCCESS")
        self.log("=" * 60)
        
        print(f"\n📍 推荐使用的IPv4地址: {config['recommended_ip']}")
        print(f"🌐 域名: {config['domain']}")
        
        print("\n📋 需要添加的DNS记录:")
        print("-" * 50)
        print("类型    名称      内容                    代理状态    TTL")
        print("-" * 50)
        
        for record in config["dns_records"]:
            proxy_status = "已代理" if record["proxy"] else "仅DNS"
            print(f"A       {record['name']:<8} {record['content']:<20} {proxy_status:<8} {record['ttl']}")
            
        print("-" * 50)
        
        print("\n🔧 配置步骤:")
        print("1. 登录 Cloudflare Dashboard: https://dash.cloudflare.com")
        print(f"2. 选择域名: {config['domain']}")
        print("3. 进入 DNS 设置")
        print("4. 点击 '添加记录'")
        print("5. 按照上表添加每个A记录")
        print("6. 确保代理状态为 '已代理' (橙色云朵)")
        print("7. TTL设置为 '自动'")
        
        print("\n⚠️  重要提示:")
        print("- 必须启用代理状态 (橙色云朵)")
        print("- 不要使用 '仅DNS' 模式")
        print("- 等待5-10分钟DNS传播")
        
    def verify_current_dns(self):
        """验证当前DNS配置"""
        self.log("🔍 验证当前DNS配置...")
        
        for subdomain in self.subdomains:
            full_domain = f"{subdomain}.{self.domain}"
            try:
                result = socket.getaddrinfo(full_domain, None, socket.AF_INET)
                if result:
                    ip = result[0][4][0]
                    self.log(f"{full_domain} -> {ip}")
                else:
                    self.log(f"{full_domain} -> 无记录", "WARNING")
            except Exception as e:
                self.log(f"{full_domain} -> 解析失败: {e}", "ERROR")
                
    def run_fix(self):
        """运行修复流程"""
        self.log("🚀 开始修复Cloudflare DNS IPv4配置...", "SUCCESS")
        
        # 1. 获取Cloudflare IP地址
        self.get_cloudflare_pages_ips()
        
        # 2. 测试IP连通性
        recommended_ip = self.get_recommended_ip()
        self.test_ip_connectivity(recommended_ip)
        
        # 3. 生成配置
        config = self.generate_dns_config()
        
        # 4. 打印配置说明
        self.print_dns_instructions(config)
        
        # 5. 验证当前DNS
        self.verify_current_dns()
        
        # 6. 保存配置到文件
        with open("cloudflare_dns_config.json", "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
            
        self.log("✅ 配置已保存到 cloudflare_dns_config.json", "SUCCESS")
        
        print("\n" + "=" * 60)
        print("🎉 修复完成!请按照上述说明配置Cloudflare DNS")
        print("=" * 60)

if __name__ == "__main__":
    fixer = CloudflareDNSFixer()
    fixer.run_fix()
