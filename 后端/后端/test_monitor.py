#!/usr/bin/env python3
"""
测试监控系统
"""

from system_monitor import SystemMonitor

def main():
    print("🔧 测试监控系统...")
    
    monitor = SystemMonitor()
    status = monitor.run_monitoring_cycle()
    
    print("✅ 监控系统测试完成")
    print(f"告警数量: {len(status['alerts'])}")
    
    local_healthy = len([s for s in status["local_services"].values() if s["status"] == "healthy"])
    local_total = len(status["local_services"])
    print(f"本地服务状态: {local_healthy}/{local_total} 正常")
    
    cloud_healthy = len([s for s in status["cloud_services"].values() if s["status"] == "healthy"])
    cloud_total = len(status["cloud_services"])
    print(f"云端服务状态: {cloud_healthy}/{cloud_total} 正常")
    
    print(f"隧道状态: {status['cloudflare_tunnel']['status']}")
    print(f"交易软件: {status['trading_software']['status']}")

if __name__ == "__main__":
    main()
