# 文件操作最佳实践:
# 1. 始终使用 with 语句打开文件
# 2. 避免在循环中重复打开同一文件
# 3. 大文件处理时考虑分块读取
# 4. 异常情况下确保文件正确关闭

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
frp内网穿透设置工具
"""

import os
import requests
import zipfile
import subprocess
import time
import json

class FrpSetup:
    def __init__(self):
        self.frp_version = "0.52.3"
        self.frp_dir = "frp"
        self.local_port = 8000
        
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
        print(f"{color}{message}{colors['RESET']}")
    
    def download_frp(self):
        """下载frp"""
        self.log("📥 下载frp...")
        
        url = f"https://github.com/fatedier/frp/releases/download/v{self.frp_version}/frp_{self.frp_version}_windows_amd64.zip"
        zip_file = "frp.zip"
        
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(zip_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            self.log("✅ frp下载完成", "SUCCESS")
            return zip_file
        except Exception as e:
            self.log(f"❌ 下载失败: {e}", "ERROR")
            return None
    
    def extract_frp(self, zip_file):
        """解压frp"""
        self.log("📦 解压frp...")
        
        try:
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(".")
            
            # 重命名目录
            extracted_dir = f"frp_{self.frp_version}_windows_amd64"
            if os.path.exists(extracted_dir):
                if os.path.exists(self.frp_dir):
                    import shutil
                    shutil.rmtree(self.frp_dir)
                os.rename(extracted_dir, self.frp_dir)
            
            # 删除zip文件
            os.remove(zip_file)
            
            self.log("✅ frp解压完成", "SUCCESS")
            return True
        except Exception as e:
            self.log(f"❌ 解压失败: {e}", "ERROR")
            return False
    
    def create_frpc_config(self, server_addr, server_port, token=""):
        """创建frpc配置文件"""
        self.log("📝 创建frpc配置...")
        
        config = f"""[common]
server_addr = {server_addr}
server_port = {server_port}
token = {token}

[stock_api]
type = http
local_ip = 127.0.0.1
local_port = {self.local_port}
custom_domains = stock.{server_addr}
"""
        
        config_file = os.path.join(self.frp_dir, "frpc.ini")
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(config)
            
            self.log("✅ 配置文件创建完成", "SUCCESS")
            return config_file
        except Exception as e:
            self.log(f"❌ 配置文件创建失败: {e}", "ERROR")
            return None
    
    def start_frpc(self):
        """启动frpc客户端"""
        self.log("🚀 启动frpc客户端...")
        
        frpc_exe = os.path.join(self.frp_dir, "frpc.exe")
        config_file = os.path.join(self.frp_dir, "frpc.ini")
        
        if not os.path.exists(frpc_exe):
            self.log("❌ frpc.exe不存在", "ERROR")
            return None
        
        if not os.path.exists(config_file):
            self.log("❌ 配置文件不存在", "ERROR")
            return None
        
        try:
            # 启动frpc
            cmd = [frpc_exe, "-c", config_file]
            process = subprocess.Popen(cmd, 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE,
                                     text=True)
            
            self.log("✅ frpc客户端已启动", "SUCCESS")
            return process
        except Exception as e:
            self.log(f"❌ 启动失败: {e}", "ERROR")
            return None
    
    def setup_with_free_server(self):
        """使用免费frp服务器设置"""
        self.log("🌟 使用免费frp服务器设置...")
        
        # 一些免费的frp服务器(仅供测试)
        free_servers = [
            {"addr": "frp.freefrp.net", "port": 7000, "token": "freefrp.net"},
            {"addr": "frp.top", "port": 7000, "token": ""},
            {"addr": "free.frp.icu", "port": 7000, "token": ""}
        ]
        
        self.log("⚠️ 注意:免费服务器仅供测试,稳定性不保证", "WARNING")
        self.log("💡 建议:生产环境请使用自己的服务器", "INFO")
        
        # 选择第一个服务器
        server = free_servers[0]
        self.log(f"📡 使用服务器: {server['addr']}")
        
        # 创建配置
        config_file = self.create_frpc_config(server['addr'], server['port'], server['token'])
        if not config_file:
            return False
        
        # 启动客户端
        process = self.start_frpc()
        if process:
            self.log(f"🌐 访问地址: http://stock.{server['addr']}")
            return True
        
        return False
    
    def setup_manual(self):
        """手动配置frp"""
        self.log("🔧 手动配置frp...")
        
        print("\n请提供frp服务器信息:")
        server_addr = input("服务器地址: ").strip()
        server_port = input("服务器端口 (默认7000): ").strip() or "7000"
        token = input("认证token (可选): ").strip()
        
        if not server_addr:
            self.log("❌ 服务器地址不能为空", "ERROR")
            return False
        
        # 创建配置
        config_file = self.create_frpc_config(server_addr, int(server_port), token)
        if not config_file:
            return False
        
        # 启动客户端
        process = self.start_frpc()
        if process:
            self.log(f"🌐 访问地址: http://stock.{server_addr}")
            return True
        
        return False
    
    def run_setup(self):
        """运行完整设置"""
        self.log("🚀 开始frp设置...")
        
        # 检查是否已存在
        if not os.path.exists(self.frp_dir):
            # 下载frp
            zip_file = self.download_frp()
            if not zip_file:
                return False
            
            # 解压frp
            if not self.extract_frp(zip_file):
                return False
        else:
            self.log("✅ frp已存在,跳过下载", "INFO")
        
        # 选择配置方式
        print("\n选择配置方式:")
        print("1. 使用免费服务器 (快速测试)")
        print("2. 手动配置服务器")
        
        choice = input("请选择 (1/2): ").strip()
        
        if choice == "1":
            return self.setup_with_free_server()
        elif choice == "2":
            return self.setup_manual()
        else:
            self.log("❌ 无效选择", "ERROR")
            return False

if __name__ == "__main__":
    setup = FrpSetup()
    
    if setup.run_setup():
        print("\n🎉 frp设置完成!")
        print("💡 提示:")
        print("  - 确保本地API服务器运行在8000端口")
        print("  - 使用提供的访问地址测试连接")
        print("  - 按Ctrl+C停止frp客户端")
        
        # 等待用户停止
        try:
            input("\n按Enter键停止frp客户端...")
        except KeyboardInterrupt:
            print("\n👋 frp客户端已停止")
    else:
        print("\n❌ frp设置失败")
