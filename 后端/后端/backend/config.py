import os
from pydantic import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# 新增加密配置项
from cryptography.fernet import Fernet

# 初始化加密组件
def _decrypt_env(key: str, encrypted: str) -> str:
    fernet = Fernet(key.encode())
    return fernet.decrypt(encrypted.encode()).decode()

class Settings(BaseSettings):
    """Application settings."""
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./stock_trading.db")
    
    # API settings
    API_V1_STR: str = "/api"
    APP_NAME: str = "Stock Trading System"
    
    # Stock API settings
    TUSHARE_TOKEN: str = os.getenv("TUSHARE_TOKEN", "")
    BAOSTOCK_USERNAME: str = os.getenv("BAOSTOCK_USERNAME", "anonymous")
    BAOSTOCK_PASSWORD: str = os.getenv("BAOSTOCK_PASSWORD", "123456")
    
    # Trading settings
    TRADE_TIME_START: str = "09:30:00"
    TRADE_TIME_END: str = "15:00:00"
    TRADING_DAYS: list = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    
    # ThirdParty Integration Settings
    ZHINANZHEN_API_URL: str = os.getenv("ZHINANZHEN_API_URL", "")
    ZHINANZHEN_API_KEY: str = os.getenv("ZHINANZHEN_API_KEY", "")
    
    # 东吴证券设置
    # 同花顺路径
    THS_PATH: str = os.getenv("THS_PATH", "C:/同花顺")
    DONGWU_ACCOUNT_ID: str = os.getenv("DONGWU_ACCOUNT_ID", "")
    DONGWU_ACCOUNT_PWD: str = os.getenv("DONGWU_ACCOUNT_PWD", "")
    DONGWU_VERIFICATION_CODE: str = os.getenv("DONGWU_VERIFICATION_CODE", "")
    DONGWU_DEFAULT_BROKER: str = os.getenv("DONGWU_DEFAULT_BROKER", "THS_DONGWU")
    
    # AI model settings
    MODEL_PATH: str = "ai/models"
    TRAINING_DATA_PATH: str = "data/training"
    
    # WebSocket settings
    WS_HEARTBEAT_INTERVAL: int = 30  # seconds
    
    # Logging settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()
