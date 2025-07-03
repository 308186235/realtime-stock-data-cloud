"""
应用配置设置
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./trading.db")

# JWT配置
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY environment variable is required")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# API配置
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))

# 东吴证券配置
DONGWU_DEFAULT_BROKER = "dongwu_xiucai"

# 日志配置
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# CORS配置
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8080",
    "https://aigupiao.me",
    "https://trading-system-api.netlify.app"
]

# Supabase配置
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://zzukfxwavknskqcepsjb.supabase.co")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6dWtmeHdhdmtuc2txY2Vwc2piIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyOTg1MDYsImV4cCI6MjA2Njg3NDUwNn0.AMGkJSre3QtRBQK_Lh2Iga4dUzSPvuO1G9s6fF2QPaw")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6dWtmeHdhdmtuc2txY2Vwc2piIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTI5ODUwNiwiZXhwIjoyMDY2ODc0NTA2fQ.Ksy_A6qfaUn9qBethAw4o8Xpn0iSxluaBTCxbnd3u5g")

# 市场数据配置
MARKET_DATA_API_KEY = os.getenv("MARKET_DATA_API_KEY", "QT_wat5QfcJ6N9pDZM5")
MARKET_DATA_HOST = os.getenv("MARKET_DATA_HOST", "")  # 实时数据服务器地址
MARKET_DATA_PORT = int(os.getenv("MARKET_DATA_PORT", "0"))  # 实时数据服务器端口
MARKET_DATA_TOKEN = os.getenv("MARKET_DATA_TOKEN", "")  # 实时数据认证token

# Redis配置
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")

# 实时数据推送配置
REALTIME_DATA_ENABLED = os.getenv("REALTIME_DATA_ENABLED", "true").lower() == "true"
REALTIME_PUSH_INTERVAL = int(os.getenv("REALTIME_PUSH_INTERVAL", "3"))  # 推送间隔(秒)

# 交易配置
TRADING_ENABLED = os.getenv("TRADING_ENABLED", "false").lower() == "true"
MOCK_TRADING = os.getenv("MOCK_TRADING", "true").lower() == "true"

# Redis配置
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
REDIS_ENABLED = os.getenv("REDIS_ENABLED", "false").lower() == "true"

# 文件存储配置
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 10 * 1024 * 1024))  # 10MB

# 调试配置
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
TESTING = os.getenv("TESTING", "false").lower() == "true"

# 应用信息
APP_NAME = "AI股票交易系统"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "基于AI的股票交易和投资组合管理系统"
