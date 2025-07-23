# 文件操作最佳实践:
# 1. 始终使用 with 语句打开文件
# 2. 避免在循环中重复打开同一文件
# 3. 大文件处理时考虑分块读取
# 4. 异常情况下确保文件正确关闭

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bore内网穿透设置工具 - 比frp更简单
"""

import subprocess
import time
import requests

def setup_bore():
    """设置bore内网穿透"""
    print("🚀 设置bore内网穿透...")
    
    # 方法1:使用cargo安装bore
    print("📦 尝试安装bore...")
    try:
        # 检查是否已安装cargo
        result = subprocess.run(['cargo', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ 检测到cargo,正在安装bore...")
            install_result = subprocess.run(['cargo', 'install', 'bore-cli'], 
                                          capture_output=True, text=True)
            if install_result.returncode == 0:
                print("✅ bore安装成功")
                return start_bore_tunnel()
            else:
                print("❌ bore安装失败")
        else:
            print("⚠️ 未检测到cargo")
    except FileNotFoundError:
        print("⚠️ 未检测到cargo")
    
    # 方法2:使用在线服务
    print("\n🌐 使用在线bore服务...")
    return use_online_bore()

def start_bore_tunnel():
    """启动bore隧道"""
    try:
        print("🚀 启动bore隧道...")
        # bore local 8000 --to bore.pub
        process = subprocess.Popen(['bore', 'local', '8000', '--to', 'bore.pub'],
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True)
        
        # 等待启动
        time.sleep(3)
        
        if process.poll() is None:  # 进程还在运行
            print("✅ bore隧道启动成功")
            print("🌐 访问地址将在bore.pub上显示")
            return True
        else:
            print("❌ bore隧道启动失败")
            return False
    except FileNotFoundError:
        print("❌ bore命令未找到")
        return False

def use_online_bore():
    """使用在线bore服务"""
    print("💡 bore是一个轻量级的内网穿透工具")
    print("📝 手动设置步骤:")
    print("1. 访问 https://bore.pub")
    print("2. 按照说明下载bore客户端")
    print("3. 运行命令: bore local 8000 --to bore.pub")
    print("4. 获得公网访问地址")
    return False

if __name__ == "__main__":
    setup_bore()
