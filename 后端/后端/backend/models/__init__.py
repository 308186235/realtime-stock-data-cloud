from .db import Base, engine, SessionLocal, get_db
from .models import (
    User,
    Backtest,
    Strategy,
    Trade,
    TechnicalIndicator,
    Benchmark,
    VirtualAccount,
    VirtualPosition,
    VirtualTrade
)

# 导出模型和数据库工具
__all__ = [
    'Base',
    'engine',
    'SessionLocal',
    'get_db',
    'User',
    'Backtest',
    'Strategy',
    'Trade',
    'TechnicalIndicator',
    'Benchmark',
    'VirtualAccount',
    'VirtualPosition',
    'VirtualTrade'
]

# 创建数据库表
def init_db():
    Base.metadata.create_all(bind=engine) 