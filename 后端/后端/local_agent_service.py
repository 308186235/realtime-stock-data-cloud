#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地交易代理服务
作为Windows服务运行,连接云端API
"""

import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import asyncio
import websockets
import json
import threading
import time
from datetime import datetime
import logging

class LocalTradingService(win32serviceutil.ServiceFramework):
    """本地交易Windows服务"""
    
    _svc_name_ = "LocalTradingAgent"
    _svc_display_name_ = "本地交易代理服务"
    _svc_description_ = "连接云端API,执行本地交易操作"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.running = True
        
        # 配置日志
        logging.basicConfig(
            filename='C:\\TradingAgent\\logs\\service.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # 导入交易模块
        try:
            from trader_buy_sell import buy_stock, sell_stock
            from trader_export import export_holdings, export_trades
            from trader_core import get_account_balance
            
            self.buy_stock = buy_stock
            self.sell_stock = sell_stock
            self.export_holdings = export_holdings
            self.export_trades = export_trades
            self.get_account_balance = get_account_balance
            
            self.logger.info("✅ 交易模块加载成功")
        except Exception as e:
            self.logger.error(f"❌ 交易模块加载失败: {e}")
    
    def SvcStop(self):
        """停止服务"""
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.running = False
        self.logger.info("🛑 服务停止")
    
    def SvcDoRun(self):
        """运行服务"""
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        
        self.logger.info("🚀 本地交易代理服务启动")
        self.main()
    
    def main(self):
        """主运行循环"""
        # 在新线程中运行异步代码
        def run_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.async_main())
        
        thread = threading.Thread(target=run_async)
        thread.daemon = True
        thread.start()
        
        # 等待停止信号
        win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
    
    async def async_main(self):
        """异步主函数"""
        cloud_url = "wss://your-app.railway.app/ws/trading"
        
        while self.running:
            try:
                self.logger.info(f"🔗 连接云端服务: {cloud_url}")
                
                async with websockets.connect(cloud_url) as websocket:
                    # 注册本地代理
                    register_msg = {
                        "type": "register",
                        "agent_type": "local_trading",
                        "capabilities": ["buy", "sell", "export", "balance"],
                        "timestamp": datetime.now().isoformat()
                    }
                    await websocket.send(json.dumps(register_msg))
                    self.logger.info("✅ 已注册到云端服务")
                    
                    # 监听命令
                    async for message in websocket:
                        if not self.running:
                            break
                        
                        try:
                            command = json.loads(message)
                            await self.handle_command(websocket, command)
                        except Exception as e:
                            self.logger.error(f"❌ 处理命令失败: {e}")
            
            except Exception as e:
                self.logger.error(f"❌ 连接失败: {e}")
                if self.running:
                    await asyncio.sleep(5)  # 5秒后重连
    
    async def handle_command(self, websocket, command):
        """处理云端命令"""
        command_type = command.get("type")
        command_id = command.get("id")
        
        self.logger.info(f"📨 收到命令: {command_type}")
        
        try:
            result = None
            
            if command_type == "buy_stock":
                data = command["data"]
                result = self.buy_stock(data["code"], data["price"], data["quantity"])
                
            elif command_type == "sell_stock":
                data = command["data"]
                result = self.sell_stock(data["code"], data["price"], data["quantity"])
                
            elif command_type == "export_holdings":
                result = self.export_holdings()
                
            elif command_type == "get_balance":
                result = self.get_account_balance()
            
            # 发送结果
            response = {
                "type": "command_result",
                "command_id": command_id,
                "success": result is not False,
                "data": result,
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket.send(json.dumps(response))
            self.logger.info(f"✅ 命令执行完成: {command_type}")
            
        except Exception as e:
            error_response = {
                "type": "command_error", 
                "command_id": command_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send(json.dumps(error_response))
            self.logger.error(f"❌ 命令执行失败: {e}")

def install_service():
    """安装服务"""
    try:
        # 创建必要的目录
        import os
        os.makedirs("C:\\TradingAgent\\logs", exist_ok=True)
        
        # 安装服务
        win32serviceutil.InstallService(
            LocalTradingService,
            LocalTradingService._svc_name_,
            LocalTradingService._svc_display_name_,
            description=LocalTradingService._svc_description_
        )
        print("✅ 服务安装成功")
        
        # 启动服务
        win32serviceutil.StartService(LocalTradingService._svc_name_)
        print("✅ 服务启动成功")
        
    except Exception as e:
        print(f"❌ 服务安装失败: {e}")

def uninstall_service():
    """卸载服务"""
    try:
        win32serviceutil.StopService(LocalTradingService._svc_name_)
        win32serviceutil.RemoveService(LocalTradingService._svc_name_)
        print("✅ 服务卸载成功")
    except Exception as e:
        print(f"❌ 服务卸载失败: {e}")

def main():
    """主函数"""
    import sys
    
    if len(sys.argv) == 1:
        # 作为服务运行
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(LocalTradingService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        # 命令行操作
        if sys.argv[1] == 'install':
            install_service()
        elif sys.argv[1] == 'remove':
            uninstall_service()
        elif sys.argv[1] == 'start':
            win32serviceutil.StartService(LocalTradingService._svc_name_)
            print("✅ 服务启动")
        elif sys.argv[1] == 'stop':
            win32serviceutil.StopService(LocalTradingService._svc_name_)
            print("✅ 服务停止")
        else:
            print("用法:")
            print("  python local_agent_service.py install  # 安装服务")
            print("  python local_agent_service.py remove   # 卸载服务")
            print("  python local_agent_service.py start    # 启动服务")
            print("  python local_agent_service.py stop     # 停止服务")

if __name__ == '__main__':
    main()
