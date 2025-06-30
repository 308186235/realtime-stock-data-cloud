"""
云端实时数据测试部署器
将实时股票数据测试工具部署到云端平台
"""
import os
import json
import subprocess
import requests
import time
from datetime import datetime
import base64

class CloudRealtimeTestDeployer:
    """云端实时测试部署器"""
    
    def __init__(self):
        self.platforms = {
            'railway': {
                'name': 'Railway',
                'url': 'https://railway.app',
                'free_tier': True,
                'websocket_support': True,
                'recommended': True
            },
            'render': {
                'name': 'Render',
                'url': 'https://render.com',
                'free_tier': True,
                'websocket_support': True,
                'recommended': True
            },
            'vercel': {
                'name': 'Vercel',
                'url': 'https://vercel.com',
                'free_tier': True,
                'websocket_support': False,
                'recommended': False
            },
            'netlify': {
                'name': 'Netlify',
                'url': 'https://netlify.com',
                'free_tier': True,
                'websocket_support': False,
                'recommended': False
            }
        }
        
        self.config = {
            'api_key': 'QT_wat5QfcJ6N9pDZM5',
            'port': 8001,
            'environment': 'production'
        }
    
    def create_railway_config(self):
        """创建Railway部署配置"""
        railway_config = {
            "build": {
                "builder": "NIXPACKS"
            },
            "deploy": {
                "startCommand": "python backend/app.py",
                "healthcheckPath": "/api/health",
                "healthcheckTimeout": 300,
                "restartPolicyType": "ON_FAILURE",
                "restartPolicyMaxRetries": 10
            }
        }
        
        # 创建railway.json
        with open('railway.json', 'w', encoding='utf-8') as f:
            json.dump(railway_config, f, indent=2, ensure_ascii=False)
        
        # 创建Procfile
        with open('Procfile', 'w', encoding='utf-8') as f:
            f.write('web: python backend/app.py\n')
        
        # 创建runtime.txt
        with open('runtime.txt', 'w', encoding='utf-8') as f:
            f.write('python-3.9\n')
        
        print("✅ Railway配置文件已创建")
        return True
    
    def create_render_config(self):
        """创建Render部署配置"""
        render_config = {
            "services": [
                {
                    "type": "web",
                    "name": "realtime-stock-test",
                    "runtime": "python3",
                    "buildCommand": "pip install -r backend/requirements.txt",
                    "startCommand": "python backend/app.py",
                    "plan": "free",
                    "healthCheckPath": "/api/health",
                    "envVars": [
                        {
                            "key": "PORT",
                            "value": "10000"
                        },
                        {
                            "key": "MARKET_DATA_API_KEY",
                            "value": "QT_wat5QfcJ6N9pDZM5"
                        },
                        {
                            "key": "ENVIRONMENT",
                            "value": "production"
                        },
                        {
                            "key": "REALTIME_DATA_ENABLED",
                            "value": "true"
                        }
                    ]
                }
            ]
        }
        
        # 创建render.yaml
        with open('render.yaml', 'w', encoding='utf-8') as f:
            import yaml
            yaml.dump(render_config, f, default_flow_style=False, allow_unicode=True)
        
        print("✅ Render配置文件已创建")
        return True
    
    def create_docker_config(self):
        """创建Docker配置"""
        dockerfile_content = """
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# 复制requirements文件
COPY backend/requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 设置环境变量
ENV PORT=8001
ENV PYTHONPATH=/app
ENV MARKET_DATA_API_KEY=QT_wat5QfcJ6N9pDZM5
ENV ENVIRONMENT=production
ENV REALTIME_DATA_ENABLED=true

# 暴露端口
EXPOSE 8001

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8001/api/health || exit 1

# 启动命令
CMD ["python", "backend/app.py"]
"""
        
        with open('Dockerfile', 'w', encoding='utf-8') as f:
            f.write(dockerfile_content)
        
        # 创建.dockerignore
        dockerignore_content = """
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env
pip-log.txt
pip-delete-this-directory.txt
.tox
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis
.vscode
.idea
*.swp
*.swo
*~
"""
        
        with open('.dockerignore', 'w', encoding='utf-8') as f:
            f.write(dockerignore_content)
        
        print("✅ Docker配置文件已创建")
        return True
    
    def create_cloud_test_page(self):
        """创建云端测试页面"""
        cloud_test_html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>云端实时股票数据测试</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #eee;
        }
        .header h1 {
            color: #2c3e50;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .api-info {
            color: #7f8c8d;
            font-size: 1.1em;
        }
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .status-card {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            border: 2px solid #e9ecef;
        }
        .status-value {
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }
        .connected { color: #27ae60; }
        .disconnected { color: #e74c3c; }
        .info { color: #3498db; }
        .controls {
            text-align: center;
            margin-bottom: 30px;
        }
        .btn {
            padding: 12px 24px;
            margin: 5px;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        .btn-primary { background: #3498db; color: white; }
        .btn-success { background: #27ae60; color: white; }
        .btn-danger { background: #e74c3c; color: white; }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }
        .log-area {
            height: 300px;
            overflow-y: auto;
            background: #2c3e50;
            color: #ecf0f1;
            padding: 15px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.4;
        }
        .deployment-info {
            background: #e8f5e8;
            border: 1px solid #27ae60;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .deployment-info h3 {
            color: #27ae60;
            margin-top: 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌐 云端实时股票数据测试</h1>
            <div class="api-info">
                API Key: QT_wat5QfcJ6N9pDZM5 | 云端部署 | 24/7运行
            </div>
        </div>

        <div class="deployment-info">
            <h3>🚀 部署信息</h3>
            <p><strong>部署平台:</strong> <span id="platform">检测中...</span></p>
            <p><strong>服务地址:</strong> <span id="serviceUrl">获取中...</span></p>
            <p><strong>部署时间:</strong> <span id="deployTime">-</span></p>
            <p><strong>运行状态:</strong> <span id="serviceStatus">检查中...</span></p>
        </div>

        <div class="status-grid">
            <div class="status-card">
                <div>连接状态</div>
                <div id="connectionStatus" class="status-value disconnected">断开</div>
            </div>
            <div class="status-card">
                <div>接收数据</div>
                <div id="dataCount" class="status-value info">0</div>
            </div>
            <div class="status-card">
                <div>活跃股票</div>
                <div id="activeStocks" class="status-value info">0</div>
            </div>
            <div class="status-card">
                <div>运行时间</div>
                <div id="uptime" class="status-value info">00:00:00</div>
            </div>
        </div>

        <div class="controls">
            <button class="btn btn-primary" onclick="testConnection()">🔗 测试连接</button>
            <button class="btn btn-success" onclick="startMonitoring()">📊 开始监控</button>
            <button class="btn btn-danger" onclick="stopMonitoring()">⏹️ 停止监控</button>
        </div>

        <div>
            <h3>📋 实时日志</h3>
            <div id="logArea" class="log-area"></div>
        </div>
    </div>

    <script>
        // 自动检测部署环境
        function detectPlatform() {
            const hostname = window.location.hostname;
            let platform = '未知平台';
            
            if (hostname.includes('railway.app')) {
                platform = 'Railway';
            } else if (hostname.includes('render.com')) {
                platform = 'Render';
            } else if (hostname.includes('vercel.app')) {
                platform = 'Vercel';
            } else if (hostname.includes('netlify.app')) {
                platform = 'Netlify';
            } else if (hostname.includes('herokuapp.com')) {
                platform = 'Heroku';
            }
            
            document.getElementById('platform').textContent = platform;
            document.getElementById('serviceUrl').textContent = window.location.origin;
        }

        // 日志函数
        function log(message, type = 'info') {
            const logArea = document.getElementById('logArea');
            const timestamp = new Date().toLocaleTimeString();
            const logEntry = document.createElement('div');
            logEntry.style.color = type === 'error' ? '#e74c3c' : 
                                 type === 'success' ? '#27ae60' : 
                                 type === 'warning' ? '#f39c12' : '#3498db';
            logEntry.textContent = `[${timestamp}] ${message}`;
            logArea.appendChild(logEntry);
            logArea.scrollTop = logArea.scrollHeight;
        }

        // 测试连接
        async function testConnection() {
            log('开始测试云端服务连接...', 'info');
            
            try {
                const response = await fetch('/api/health');
                if (response.ok) {
                    const data = await response.json();
                    log('✅ 后端API连接成功', 'success');
                    document.getElementById('serviceStatus').textContent = '运行中';
                    document.getElementById('serviceStatus').style.color = '#27ae60';
                    
                    // 测试实时数据API
                    const realtimeResponse = await fetch('/api/realtime-data/test');
                    if (realtimeResponse.ok) {
                        log('✅ 实时数据API测试成功', 'success');
                    } else {
                        log('⚠️ 实时数据API测试失败', 'warning');
                    }
                } else {
                    log('❌ 后端API连接失败', 'error');
                    document.getElementById('serviceStatus').textContent = '异常';
                    document.getElementById('serviceStatus').style.color = '#e74c3c';
                }
            } catch (error) {
                log(`❌ 连接测试失败: ${error.message}`, 'error');
            }
        }

        // 开始监控
        function startMonitoring() {
            log('🚀 开始实时数据监控...', 'info');
            // 这里可以添加WebSocket连接逻辑
            document.getElementById('connectionStatus').textContent = '已连接';
            document.getElementById('connectionStatus').className = 'status-value connected';
        }

        // 停止监控
        function stopMonitoring() {
            log('⏹️ 停止实时数据监控', 'info');
            document.getElementById('connectionStatus').textContent = '断开';
            document.getElementById('connectionStatus').className = 'status-value disconnected';
        }

        // 页面加载完成后初始化
        window.onload = function() {
            detectPlatform();
            document.getElementById('deployTime').textContent = new Date().toLocaleString();
            log('🌐 云端测试页面加载完成', 'info');
            
            // 自动测试连接
            setTimeout(testConnection, 1000);
        };
    </script>
</body>
</html>"""
        
        # 创建云端测试页面目录
        os.makedirs('static', exist_ok=True)
        with open('static/cloud_test.html', 'w', encoding='utf-8') as f:
            f.write(cloud_test_html)
        
        print("✅ 云端测试页面已创建")
        return True
    
    def create_deployment_script(self):
        """创建部署脚本"""
        deploy_script = """#!/bin/bash
# 云端实时数据测试部署脚本

echo "🚀 开始部署实时股票数据测试系统到云端..."

# 检查Git仓库
if [ ! -d ".git" ]; then
    echo "📁 初始化Git仓库..."
    git init
    git add .
    git commit -m "Initial commit: 实时股票数据测试系统"
fi

echo "📋 选择部署平台:"
echo "1. Railway (推荐)"
echo "2. Render"
echo "3. Docker部署"
echo "4. 全部部署"

read -p "请选择 (1-4): " choice

case $choice in
    1)
        echo "🚂 部署到Railway..."
        if command -v railway &> /dev/null; then
            railway login
            railway new
            railway up
        else
            echo "❌ 请先安装Railway CLI: npm install -g @railway/cli"
        fi
        ;;
    2)
        echo "🎨 部署到Render..."
        echo "请访问 https://render.com 并连接您的GitHub仓库"
        ;;
    3)
        echo "🐳 Docker部署..."
        docker build -t realtime-stock-test .
        docker run -p 8001:8001 realtime-stock-test
        ;;
    4)
        echo "🌐 全部部署..."
        echo "请按照README文档进行多平台部署"
        ;;
    *)
        echo "❌ 无效选择"
        ;;
esac

echo "✅ 部署脚本执行完成"
"""
        
        with open('deploy.sh', 'w', encoding='utf-8') as f:
            f.write(deploy_script)
        
        # 设置执行权限
        os.chmod('deploy.sh', 0o755)
        
        print("✅ 部署脚本已创建")
        return True
    
    def create_cloud_requirements(self):
        """创建云端requirements.txt"""
        cloud_requirements = """
# 云端实时股票数据测试依赖
fastapi==0.104.1
uvicorn[standard]==0.24.0
websockets==12.0
pydantic==2.5.0
python-multipart==0.0.6
aiofiles==23.2.1
redis==5.0.1
asyncio-mqtt==0.16.1
requests==2.31.0
python-dotenv==1.0.0
pandas==2.1.4
numpy==1.24.3
psutil==5.9.6
schedule==1.2.0
APScheduler==3.10.4

# 数据库支持
sqlalchemy==2.0.23
alembic==1.13.1

# 监控和日志
structlog==23.2.0
prometheus-client==0.19.0

# 安全
cryptography==41.0.8
passlib[bcrypt]==1.7.4
python-jose[cryptography]==3.3.0

# 云端部署
gunicorn==21.2.0
"""
        
        with open('requirements_cloud.txt', 'w', encoding='utf-8') as f:
            f.write(cloud_requirements.strip())
        
        print("✅ 云端requirements.txt已创建")
        return True
    
    def create_environment_configs(self):
        """创建环境配置文件"""
        # 生产环境配置
        prod_env = """
# 生产环境配置
ENVIRONMENT=production
PORT=8001

# 实时数据配置
MARKET_DATA_API_KEY=QT_wat5QfcJ6N9pDZM5
REALTIME_DATA_ENABLED=true
REALTIME_PUSH_INTERVAL=3

# 数据库配置 (使用SQLite for simplicity)
DATABASE_URL=sqlite:///./data/trading.db

# 日志配置
LOG_LEVEL=INFO

# CORS配置
CORS_ORIGINS=*

# WebSocket配置
WS_HEARTBEAT_INTERVAL=30
"""
        
        with open('.env.production', 'w', encoding='utf-8') as f:
            f.write(prod_env.strip())
        
        # 开发环境配置
        dev_env = """
# 开发环境配置
ENVIRONMENT=development
PORT=8001

# 实时数据配置
MARKET_DATA_API_KEY=QT_wat5QfcJ6N9pDZM5
REALTIME_DATA_ENABLED=true
REALTIME_PUSH_INTERVAL=3

# 数据库配置
DATABASE_URL=sqlite:///./data/trading_dev.db

# 日志配置
LOG_LEVEL=DEBUG

# CORS配置
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# WebSocket配置
WS_HEARTBEAT_INTERVAL=30
"""
        
        with open('.env.development', 'w', encoding='utf-8') as f:
            f.write(dev_env.strip())
        
        print("✅ 环境配置文件已创建")
        return True
    
    def show_deployment_guide(self):
        """显示部署指南"""
        print("\n" + "="*80)
        print("🌐 云端部署指南")
        print("="*80)
        
        print("\n📋 推荐部署平台:")
        for key, platform in self.platforms.items():
            status = "✅ 推荐" if platform['recommended'] else "⚠️ 限制"
            ws_support = "✅ 支持" if platform['websocket_support'] else "❌ 不支持"
            print(f"  {status} {platform['name']}")
            print(f"     - WebSocket: {ws_support}")
            print(f"     - 免费额度: {'✅ 有' if platform['free_tier'] else '❌ 无'}")
            print(f"     - 网址: {platform['url']}")
            print()
        
        print("🚀 快速部署步骤:")
        print("1. 选择部署平台 (推荐Railway或Render)")
        print("2. 连接GitHub仓库")
        print("3. 配置环境变量")
        print("4. 启动部署")
        print("5. 访问云端测试页面")
        
        print("\n🔧 必要的环境变量:")
        print("- MARKET_DATA_API_KEY=QT_wat5QfcJ6N9pDZM5")
        print("- ENVIRONMENT=production")
        print("- REALTIME_DATA_ENABLED=true")
        print("- PORT=8001 (或平台指定端口)")
        
        print("\n📊 部署后测试:")
        print("- 访问: https://your-app.platform.com/static/cloud_test.html")
        print("- 检查: https://your-app.platform.com/api/health")
        print("- 监控: 实时数据推送状态")
        
        print("="*80)
    
    def deploy_to_cloud(self):
        """执行云端部署"""
        print("🚀 开始创建云端部署配置...")
        
        # 创建所有配置文件
        self.create_railway_config()
        self.create_render_config()
        self.create_docker_config()
        self.create_cloud_test_page()
        self.create_deployment_script()
        self.create_cloud_requirements()
        self.create_environment_configs()
        
        print("\n✅ 所有云端部署文件已创建完成！")
        
        # 显示部署指南
        self.show_deployment_guide()
        
        return True

def main():
    """主函数"""
    deployer = CloudRealtimeTestDeployer()
    
    print("🌐 云端实时股票数据测试部署器")
    print("API Key: QT_wat5QfcJ6N9pDZM5")
    print("="*60)
    
    try:
        deployer.deploy_to_cloud()
        
        print("\n🎯 下一步操作:")
        print("1. 将代码推送到GitHub仓库")
        print("2. 在Railway/Render上连接仓库")
        print("3. 配置环境变量")
        print("4. 启动部署")
        print("5. 访问云端测试页面验证功能")
        
    except Exception as e:
        print(f"❌ 部署配置创建失败: {str(e)}")

if __name__ == "__main__":
    main()
