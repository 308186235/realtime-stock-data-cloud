#!/usr/bin/env python3
"""
重启Cloudflare隧道
"""

from zero_trust_manager import ZeroTrustManager
import time

def main():
    print("🔄 重启Cloudflare隧道...")
    
    manager = ZeroTrustManager()
    
    # 重启隧道
    manager.restart_tunnel()
    
    # 等待隧道启动
    print("⏳ 等待隧道启动...")
    time.sleep(10)
    
    # 检查状态
    status = manager.get_tunnel_status()
    
    if status.get('tunnel_connected', False):
        print("✅ 隧道重启成功!")
        print(f"运行时间: {status.get('uptime', '未知')}")
    else:
        print("❌ 隧道重启失败")
        print(f"状态: {status}")

if __name__ == "__main__":
    main()
