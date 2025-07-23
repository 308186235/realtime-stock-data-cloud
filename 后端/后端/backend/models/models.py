from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime, JSON, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from datetime import datetime
from .db import Base

# 创建用户与回测多对多关系表
user_backtest = Table(
    "user_backtest",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("backtest_id", Integer, ForeignKey("backtests.id"))
)

class User(Base):
    """用户模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="user")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关系
    backtests = relationship("Backtest", secondary=user_backtest, back_populates="users")
    strategies = relationship("Strategy", back_populates="owner")

class Backtest(Base):
    """回测模型"""
    __tablename__ = "backtests"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    backtest_id = Column(String, default=lambda: str(uuid.uuid4()), unique=True, index=True)
    start_date = Column(String)
    end_date = Column(String)
    initial_capital = Column(Float, default=100000.0)
    commission = Column(Float, default=0.0003)
    status = Column(String, default="completed")  # pending, running, completed, failed
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # 存储回测配置的JSON字段
    config = Column(JSON)
    # 存储回测结果的JSON字段
    results = Column(JSON)

    # 关系
    users = relationship("User", secondary=user_backtest, back_populates="backtests")
    trades = relationship("Trade", back_populates="backtest")

class Strategy(Base):
    """策略模型"""
    __tablename__ = "strategies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    type = Column(String, index=True)  # 策略类型: ma_cross, rsi, bollinger_bands等
    params = Column(JSON)  # 策略参数JSON
    source_code = Column(String, nullable=True)  # 策略源代码(可选)
    owner_id = Column(Integer, ForeignKey("users.id"))
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关系
    owner = relationship("User", back_populates="strategies")

class Trade(Base):
    """交易模型"""
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    backtest_id = Column(Integer, ForeignKey("backtests.id"))
    symbol = Column(String, index=True)
    action = Column(String)  # BUY, SELL
    date = Column(DateTime)
    price = Column(Float)
    shares = Column(Integer)
    cost = Column(Float, nullable=True)  # 买入成本
    revenue = Column(Float, nullable=True)  # 卖出收入
    profit = Column(Float, nullable=True)  # 交易利润
    created_at = Column(DateTime, default=func.now())

    # 关系
    backtest = relationship("Backtest", back_populates="trades")

class TechnicalIndicator(Base):
    """技术指标模型"""
    __tablename__ = "technical_indicators"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    display_name = Column(String)
    description = Column(String, nullable=True)
    parameters = Column(JSON)  # 参数配置JSON
    category = Column(String, nullable=True)  # 指标分类
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class Benchmark(Base):
    """基准指数模型"""
    __tablename__ = "benchmarks"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True)
    name = Column(String)
    market = Column(String)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class VirtualAccount(Base):
    """虚拟账户模型"""
    __tablename__ = "virtual_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    account_name = Column(String, index=True)  # 账户名称，如"东吴秀才"
    broker_type = Column(String)  # 券商类型
    total_assets = Column(Float, default=0.0)  # 总资产
    available_cash = Column(Float, default=0.0)  # 可用资金
    market_value = Column(Float, default=0.0)  # 持仓市值
    frozen_amount = Column(Float, default=0.0)  # 冻结资金
    profit_loss = Column(Float, default=0.0)  # 总盈亏
    profit_loss_ratio = Column(Float, default=0.0)  # 盈亏比例
    last_sync_time = Column(DateTime)  # 最后同步时间
    data_source = Column(String, default="trading_software")  # 数据来源
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关系
    user = relationship("User")
    positions = relationship("VirtualPosition", back_populates="account")

class VirtualPosition(Base):
    """虚拟持仓模型"""
    __tablename__ = "virtual_positions"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("virtual_accounts.id"))
    symbol = Column(String, index=True)  # 证券代码
    name = Column(String)  # 证券名称
    quantity = Column(Integer, default=0)  # 持仓数量
    available_quantity = Column(Integer, default=0)  # 可用数量
    cost_price = Column(Float, default=0.0)  # 成本价
    current_price = Column(Float, default=0.0)  # 当前价
    market_value = Column(Float, default=0.0)  # 市值
    profit_loss = Column(Float, default=0.0)  # 盈亏
    profit_loss_ratio = Column(Float, default=0.0)  # 盈亏比例
    position_date = Column(String)  # 建仓日期
    trade_source = Column(String, default="manual")  # 交易来源：manual, ai, agent
    last_update_time = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关系
    account = relationship("VirtualAccount", back_populates="positions")

class VirtualTrade(Base):
    """虚拟交易记录模型"""
    __tablename__ = "virtual_trades"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("virtual_accounts.id"))
    order_id = Column(String, unique=True, index=True)  # 委托编号
    symbol = Column(String, index=True)  # 证券代码
    name = Column(String)  # 证券名称
    action = Column(String)  # 交易动作：BUY, SELL
    price = Column(Float)  # 成交价格
    quantity = Column(Integer)  # 成交数量
    amount = Column(Float)  # 成交金额
    commission = Column(Float, default=0.0)  # 手续费
    status = Column(String, default="FILLED")  # 状态：PENDING, FILLED, CANCELLED
    trade_source = Column(String, default="manual")  # 交易来源：manual, ai, agent
    trade_time = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())

    # 关系
    account = relationship("VirtualAccount")