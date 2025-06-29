#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Render部署配置 - 混合架构方案
"""

import os
import json
import yaml
from pathlib import Path

class RenderDeployConfig:
    """Render部署配置生成器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.backend_path = self.project_root / "backend"
    
    def create_render_yaml(self):
        """创建render.yaml配置文件"""
        
        render_config = {
            "services": [
                {
                    "type": "web",
                    "name": "trading-backend-api",
                    "runtime": "python3",
                    "buildCommand": "pip install -r backend/requirements.txt",
                    "startCommand": "python backend/app.py",
                    "plan": "free",
                    "envVars": [
                        {
                            "key": "PYTHONPATH",
                            "value": "/opt/render/project/src"
                        },
                        {
                            "key": "PORT", 
                            "value": "10000"
                        },
                        {
                            "key": "ENVIRONMENT",
                            "value": "production"
                        },
                        {
                            "key": "DATABASE_URL",
                            "value": "sqlite:///./data/trading.db"
                        },
                        {
                            "key": "CORS_ORIGINS",
                            "value": "*"
                        }
                    ],
                    "healthCheckPath": "/api/health",
                    "autoDeploy": True,
                    "disk": {
                        "name": "trading-data",
                        "mountPath": "/opt/render/project/src/data",
                        "sizeGB": 1
                    }
                }
            ]
        }
        
        with open("render.yaml", "w", encoding="utf-8") as f:
            yaml.dump(render_config, f, default_flow_style=False, allow_unicode=True)
        
        print("✅ render.yaml 配置文件已创建")
        return True
    
    def create_requirements_txt(self):
        """创建/更新requirements.txt"""
        
        requirements = [
            "fastapi==0.104.1",
            "uvicorn[standard]==0.24.0", 
            "sqlalchemy==2.0.23",
            "pandas==2.1.3",
            "numpy==1.24.3",
            "requests==2.31.0",
            "websockets==12.0",
            "python-multipart==0.0.6",
            "python-jose[cryptography]==3.3.0",
            "passlib[bcrypt]==1.7.4",
            "python-dotenv==1.0.0",
            "redis==5.0.1",
            "apscheduler==3.10.4",
            "pydantic==2.5.0",
            "httpx==0.25.2",
            "aiofiles==23.2.1",
            "python-cors==4.3.1",
            "asyncio-mqtt==0.16.1"
        ]
        
        requirements_path = self.backend_path / "requirements.txt"
        
        with open(requirements_path, "w", encoding="utf-8") as f:
            f.write("\n".join(requirements))
        
        print(f"✅ requirements.txt 已创建: {requirements_path}")
        return True
    
    def create_render_start_script(self):
        """创建Render启动脚本"""
        
        start_script = """#!/bin/bash
# Render启动脚本

echo "🚀 启动交易系统后端服务..."

# 设置环境变量
export PYTHONPATH="/opt/render/project/src"
export PORT="${PORT:-10000}"

# 创建必要目录
mkdir -p data logs

# 启动服务
echo "📡 启动API服务在端口 $PORT"
python backend/app.py
"""
        
        with open("start.sh", "w", encoding="utf-8") as f:
            f.write(start_script)
        
        os.chmod("start.sh", 0o755)
        print("✅ start.sh 启动脚本已创建")
        return True
    
    def update_backend_for_render(self):
        """更新后端代码以适配Render"""
        
        # 检查backend/app.py是否存在
        app_py_path = self.backend_path / "app.py"
        
        if not app_py_path.exists():
            print("❌ backend/app.py 不存在，请检查项目结构")
            return False
        
        # 读取现有内容
        with open(app_py_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 添加Render适配代码
        render_adaptation = '''
# Render平台适配
import os
PORT = int(os.getenv("PORT", 8000))

# 在文件末尾的if __name__ == "__main__":部分修改
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app", 
        host="0.0.0.0", 
        port=PORT,
        log_level="info",
        access_log=True
    )
'''
        
        # 如果还没有适配代码，则添加
        if "PORT = int(os.getenv" not in content:
            # 找到最后的if __name__ == "__main__":并替换
            lines = content.split('\n')
            new_lines = []
            in_main_block = False
            
            for line in lines:
                if 'if __name__ == "__main__":' in line:
                    in_main_block = True
                    new_lines.append(line)
                    new_lines.append('    import uvicorn')
                    new_lines.append('    import os')
                    new_lines.append('    PORT = int(os.getenv("PORT", 8000))')
                    new_lines.append('    uvicorn.run(')
                    new_lines.append('        "app:app",')
                    new_lines.append('        host="0.0.0.0",')
                    new_lines.append('        port=PORT,')
                    new_lines.append('        log_level="info",')
                    new_lines.append('        access_log=True')
                    new_lines.append('    )')
                elif in_main_block and line.strip().startswith('uvicorn.run'):
                    # 跳过原有的uvicorn.run调用
                    continue
                elif in_main_block and (line.strip().startswith('host=') or 
                                      line.strip().startswith('port=') or
                                      line.strip().startswith('reload=')):
                    # 跳过原有的参数
                    continue
                else:
                    if not (in_main_block and line.strip() == ')'):
                        new_lines.append(line)
                    if line.strip() == ')' and in_main_block:
                        in_main_block = False
            
            # 写回文件
            with open(app_py_path, "w", encoding="utf-8") as f:
                f.write('\n'.join(new_lines))
            
            print("✅ backend/app.py 已更新以适配Render")
        else:
            print("✅ backend/app.py 已经适配Render")
        
        return True
    
    def create_local_hybrid_client(self):
        """创建本地混合架构客户端"""
        
        hybrid_client = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地混合架构客户端
连接Render云端API，执行本地交易操作
"""

import asyncio
import websockets
import json
import requests
import time
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('local_agent.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LocalTradingClient:
    """本地交易客户端"""
    
    def __init__(self, render_url):
        self.render_url = render_url
        self.api_url = render_url
        self.ws_url = render_url.replace('https://', 'wss://') + '/ws'
        self.running = False
        
        # 导入本地交易模块
        try:
            from trader_buy_sell import buy_stock, sell_stock
            from trader_export import export_holdings, export_trades  
            from trader_core import get_account_balance
            
            self.buy_stock = buy_stock
            self.sell_stock = sell_stock
            self.export_holdings = export_holdings
            self.export_trades = export_trades
            self.get_account_balance = get_account_balance
            
            logger.info("✅ 本地交易模块加载成功")
        except Exception as e:
            logger.error(f"❌ 本地交易模块加载失败: {e}")
            logger.info("💡 将使用模拟交易模式")
            self._setup_mock_functions()
    
    def _setup_mock_functions(self):
        """设置模拟交易函数"""
        def mock_buy_stock(code, price, quantity):
            logger.info(f"🔄 模拟买入: {code} 价格:{price} 数量:{quantity}")
            return {"success": True, "message": "模拟买入成功"}
        
        def mock_sell_stock(code, price, quantity):
            logger.info(f"🔄 模拟卖出: {code} 价格:{price} 数量:{quantity}")
            return {"success": True, "message": "模拟卖出成功"}
        
        def mock_export_holdings():
            logger.info("🔄 模拟导出持仓")
            return {"success": True, "data": "模拟持仓数据"}
        
        def mock_get_balance():
            logger.info("🔄 模拟获取余额")
            return {"balance": 100000, "available": 80000}
        
        self.buy_stock = mock_buy_stock
        self.sell_stock = mock_sell_stock
        self.export_holdings = mock_export_holdings
        self.get_account_balance = mock_get_balance
    
    async def connect_and_run(self):
        """连接并运行客户端"""
        self.running = True
        
        while self.running:
            try:
                logger.info(f"🔗 连接到Render服务: {self.ws_url}")
                
                # 检查服务是否可用
                if not await self._check_service_health():
                    logger.warning("⚠️ 服务健康检查失败，等待重试...")
                    await asyncio.sleep(30)
                    continue
                
                async with websockets.connect(
                    self.ws_url,
                    ping_interval=30,
                    ping_timeout=10
                ) as websocket:
                    
                    # 注册客户端
                    await self._register_client(websocket)
                    
                    # 开始心跳任务
                    heartbeat_task = asyncio.create_task(
                        self._send_heartbeat(websocket)
                    )
                    
                    # 监听消息
                    try:
                        async for message in websocket:
                            await self._handle_message(websocket, message)
                    finally:
                        heartbeat_task.cancel()
                        
            except websockets.exceptions.ConnectionClosed:
                logger.warning("⚠️ 连接断开，准备重连...")
            except Exception as e:
                logger.error(f"❌ 连接异常: {e}")
            
            if self.running:
                logger.info("⏳ 10秒后重新连接...")
                await asyncio.sleep(10)
    
    async def _check_service_health(self):
        """检查服务健康状态"""
        try:
            response = requests.get(f"{self.api_url}/api/health", timeout=10)
            return response.status_code == 200
        except:
            return False
    
    async def _register_client(self, websocket):
        """注册客户端"""
        register_msg = {
            "type": "register",
            "client_type": "local_trading_agent",
            "capabilities": ["buy", "sell", "export", "balance"],
            "timestamp": datetime.now().isoformat()
        }
        
        await websocket.send(json.dumps(register_msg))
        logger.info("✅ 已注册到云端服务")
    
    async def _send_heartbeat(self, websocket):
        """发送心跳"""
        while True:
            try:
                heartbeat = {
                    "type": "heartbeat",
                    "timestamp": datetime.now().isoformat(),
                    "status": "running"
                }
                await websocket.send(json.dumps(heartbeat))
                await asyncio.sleep(30)
            except:
                break
    
    async def _handle_message(self, websocket, message):
        """处理消息"""
        try:
            data = json.loads(message)
            command_type = data.get("type")
            command_id = data.get("id")
            
            logger.info(f"📨 收到命令: {command_type}")
            
            result = None
            
            if command_type == "buy_stock":
                params = data["data"]
                result = self.buy_stock(
                    params["code"], 
                    params["price"], 
                    params["quantity"]
                )
            elif command_type == "sell_stock":
                params = data["data"]
                result = self.sell_stock(
                    params["code"],
                    params["price"], 
                    params["quantity"]
                )
            elif command_type == "export_holdings":
                result = self.export_holdings()
            elif command_type == "get_balance":
                result = self.get_account_balance()
            
            # 发送结果
            response = {
                "type": "command_result",
                "command_id": command_id,
                "success": True,
                "data": result,
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket.send(json.dumps(response))
            logger.info(f"✅ 命令执行完成: {command_type}")
            
        except Exception as e:
            logger.error(f"❌ 处理消息失败: {e}")
            
            if "command_id" in locals():
                error_response = {
                    "type": "command_error",
                    "command_id": command_id,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                await websocket.send(json.dumps(error_response))

def main():
    """主函数"""
    # Render服务URL - 部署后需要更新
    RENDER_URL = "https://your-app-name.onrender.com"
    
    print("🌐 本地交易代理客户端")
    print("=" * 50)
    print(f"🔗 连接地址: {RENDER_URL}")
    print("📱 移动应用API: 使用相同地址")
    print("🖥️ 本地交易: 通过此客户端执行")
    print("=" * 50)
    
    # 创建客户端
    client = LocalTradingClient(RENDER_URL)
    
    try:
        # 运行客户端
        asyncio.run(client.connect_and_run())
    except KeyboardInterrupt:
        print("\\n👋 用户中断，退出程序")
        client.running = False

if __name__ == "__main__":
    main()
'''
        
        with open("local_hybrid_client.py", "w", encoding="utf-8") as f:
            f.write(hybrid_client)
        
        print("✅ local_hybrid_client.py 本地客户端已创建")
        return True

def main():
    """主函数"""
    print("🎨 Render部署配置生成器")
    print("=" * 50)
    
    config = RenderDeployConfig()
    
    print("📝 生成Render部署配置...")
    
    # 1. 创建render.yaml
    config.create_render_yaml()
    
    # 2. 创建/更新requirements.txt
    config.create_requirements_txt()
    
    # 3. 创建启动脚本
    config.create_render_start_script()
    
    # 4. 更新后端代码
    config.update_backend_for_render()
    
    # 5. 创建本地客户端
    config.create_local_hybrid_client()
    
    print("\n✅ Render部署配置完成！")
    print("\n📋 接下来的步骤:")
    print("1. 访问 https://render.com")
    print("2. 连接您的GitHub仓库")
    print("3. 选择 'Web Service'")
    print("4. 使用 render.yaml 配置")
    print("5. 等待部署完成")
    print("6. 获取部署URL")
    print("7. 更新 local_hybrid_client.py 中的URL")
    print("8. 运行本地客户端: python local_hybrid_client.py")
    
    print("\n💡 优势:")
    print("- 🆓 免费750小时/月")
    print("- 🔄 自动部署")
    print("- 🌐 HTTPS支持")
    print("- 📱 移动应用直连云端API")
    print("- 🖥️ 本地交易软件正常工作")

if __name__ == "__main__":
    main()
