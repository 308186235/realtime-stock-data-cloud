from port_manager import port_manager\n"""
云端实时股票数据服务主应用
专为云端部署优化,支持Railway,Render等平台
API Key: process.env.STOCK_API_KEY
"""
import os
import sys
import logging
from pathlib import Path

# 添加backend目录到Python路径
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
from datetime import datetime
import time

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="云端实时股票数据服务",
    description="基于process.env.STOCK_API_KEY的实时股票数据推送服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins = [
    "https://aigupiao.me",
    "https://api.aigupiao.me",
    "https://app.aigupiao.me",
    "https://mobile.aigupiao.me",
    "https://admin.aigupiao.me",
    "http://localhost:8080",
    "http://localhost:3000",
    "capacitor://localhost",
    "ionic://localhost"
],  # 云端部署允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 导入云端实时API
try:
    from api.routers.cloud_realtime_api import router as cloud_realtime_router
    app.include_router(cloud_realtime_router, prefix="/api/realtime", tags=["realtime"])
    logger.info("✅ 云端实时API路由已加载")
except Exception as e:
    logger.error(f"❌ 加载云端实时API失败: {str(e)}")

# 静态文件服务
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    logger.info(f"✅ 静态文件服务已挂载: {static_dir}")

@app.get("/", response_class=HTMLResponse)
async def root():
    """根路径 - 显示服务信息"""
    html_content = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>云端实时股票数据服务</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: #333;
                min-height: 100vh;
            }}
            .container {{
                max-width: 800px;
                margin: 0 auto;
                background: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                backdrop-filter: blur(10px);
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 2px solid #eee;
            }}
            .header h1 {{
                color: #2c3e50;
                font-size: 2.5em;
                margin-bottom: 10px;
            }}
            .api-info {{
                color: #7f8c8d;
                font-size: 1.1em;
            }}
            .status-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            .status-card {{
                background: #f8f9fa;
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                border: 2px solid #e9ecef;
            }}
            .status-value {{
                font-size: 2em;
                font-weight: bold;
                margin: 10px 0;
                color: #27ae60;
            }}
            .links {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 15px;
                margin-top: 20px;
            }}
            .link-card {{
                background: #3498db;
                color: white;
                padding: 15px;
                border-radius: 10px;
                text-decoration: none;
                text-align: center;
                transition: all 0.3s ease;
            }}
            .link-card:hover {{
                background: #2980b9;
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            }}
            .deployment-info {{
                background: #e8f5e8;
                border: 1px solid #27ae60;
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 20px;
            }}
            .deployment-info h3 {{
                color: #27ae60;
                margin-top: 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🌐 云端实时股票数据服务</h1>
                <div class="api-info">
                    API Key: process.env.STOCK_API_KEY | 云端部署 | 24/7运行
                </div>
            </div>

            <div class="deployment-info">
                <h3>🚀 服务信息</h3>
                <p><strong>部署时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>服务状态:</strong> <span style="color: #27ae60;">✅ 运行中</span></p>
                <p><strong>推送间隔:</strong> 3秒</p>
                <p><strong>支持股票:</strong> 15只主要A股</p>
            </div>

            <div class="status-grid">
                <div class="status-card">
                    <div>服务状态</div>
                    <div class="status-value">✅ 正常</div>
                </div>
                <div class="status-card">
                    <div>API版本</div>
                    <div class="status-value">v1.0.0</div>
                </div>
                <div class="status-card">
                    <div>WebSocket</div>
                    <div class="status-value">✅ 支持</div>
                </div>
                <div class="status-card">
                    <div>实时推送</div>
                    <div class="status-value">✅ 启用</div>
                </div>
            </div>

            <div class="links">
                <a href="/api/realtime/test" class="link-card">
                    🔍 测试API
                </a>
                <a href="/api/realtime/health" class="link-card">
                    💓 健康检查
                </a>
                <a href="/api/realtime/stats" class="link-card">
                    📊 服务统计
                </a>
                <a href="/docs" class="link-card">
                    📚 API文档
                </a>
                <a href="/static/cloud_test.html" class="link-card">
                    🌐 监控面板
                </a>
            </div>

            <div style="margin-top: 30px; text-align: center; color: #7f8c8d;">
                <p>🔗 WebSocket连接: <code>wss://{{当前域名}}/api/realtime/ws</code></p>
                <p>📈 支持股票: 000001, 600000, 600519, 000858, 002415 等</p>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/api/health")
async def health_check():
    """全局健康检查"""
    return {
        "status": "healthy",
        "service": "cloud-realtime-stock-service",
        "version": "1.0.0",
        "api_key": "process.env.STOCK_API_KEY",
        "timestamp": time.time(),
        "uptime": time.time() - start_time,
        "environment": os.getenv("ENVIRONMENT", "production"),
        "platform": detect_platform()
    }

@app.get("/api/info")
async def service_info():
    """服务信息"""
    return {
        "service": "云端实时股票数据服务",
        "description": "基于process.env.STOCK_API_KEY的实时股票数据推送服务",
        "version": "1.0.0",
        "api_key": "process.env.STOCK_API_KEY",
        "features": [
            "实时股票数据推送",
            "WebSocket连接支持", 
            "多股票订阅",
            "云端部署优化",
            "24/7运行"
        ],
        "endpoints": {
            "websocket": "/api/realtime/ws",
            "test": "/api/realtime/test",
            "health": "/api/realtime/health",
            "stats": "/api/realtime/stats",
            "stocks": "/api/realtime/stocks"
        },
        "supported_stocks": [
            "000001", "600000", "600519", "000858", "002415",
            "600036", "300059", "002594", "300750", "000002"
        ],
        "timestamp": time.time()
    }

def detect_platform():
    """检测部署平台"""
    if os.getenv("RAILWAY_ENVIRONMENT"):
        return "Railway"
    elif os.getenv("RENDER"):
        return "Render"
    elif os.getenv("VERCEL"):
        return "Vercel"
    elif os.getenv("NETLIFY"):
        return "Netlify"
    elif os.getenv("HEROKU"):
        return "Heroku"
    else:
        return "Unknown"

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """请求日志中间件"""
    start_time_req = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time_req
    
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )
    
    return response

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理"""
    logger.error(f"全局异常: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "内部服务器错误",
            "message": str(exc),
            "timestamp": time.time()
        }
    )

# 记录启动时间
start_time = time.time()

if __name__ == "__main__":
    # 获取端口配置
    port = int(os.getenv("PORT", 8001))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"🚀 启动云端实时股票数据服务")
    logger.info(f"📡 API Key: process.env.STOCK_API_KEY")
    logger.info(f"🌐 服务地址: http://{host}:{port}")
    logger.info(f"🔧 部署平台: {detect_platform()}")
    logger.info(f"🌍 环境: {os.getenv('ENVIRONMENT', 'production')}")
    
    # 启动服务
    uvicorn.run(
        "cloud_app:app",
        host=host,
        port=port,
        reload=False,  # 生产环境不启用热重载
        access_log=True,
        log_level="info"
    )
