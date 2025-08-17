#!/usr/bin/env python3
"""
云端Agent到本地交易的WebSocket服务
自动启动脚本
"""

import asyncio
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fix_cloud_agent_websocket_connection import CloudAgentWebSocketFixer

async def main():
    print("🚀 启动云端Agent WebSocket连接服务")
    print("=" * 50)
    
    fixer = CloudAgentWebSocketFixer()
    
    # 首先测试WebSocket端点
    print("\n🔍 测试WebSocket端点...")
    endpoints_result = await fixer.test_websocket_endpoints()
    
    # 启动WebSocket客户端
    print("\n🤖 启动Agent WebSocket客户端...")
    await fixer.run_websocket_client_with_reconnect()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 服务已停止")
    except Exception as e:
        print(f"\n❌ 服务异常: {e}")
