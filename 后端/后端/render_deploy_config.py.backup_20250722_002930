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
        def disabled_mock_function():
        raise ValueError("❌ 模拟功能已禁用，请使用真实交易接口")