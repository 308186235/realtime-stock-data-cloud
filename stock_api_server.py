#!/usr/bin/env python3
"""
股票数据API服务器
提供RESTful API接口，整合混合数据源
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import asyncio
import uvicorn
import os
from datetime import datetime
import logging
from hybrid_stock_data_manager import HybridStockDataManager, StockData, TradingTimeChecker, DataSource

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="智能股票数据API",
    description="混合数据源股票API服务 (茶股帮TCP + 腾讯API)",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局数据管理器
data_manager: Optional[HybridStockDataManager] = None
realtime_data: Dict[str, StockData] = {}

# 响应模型
class StockResponse(BaseModel):
    code: str
    name: str
    current_price: float
    change: float
    change_percent: float
    volume: int
    high: float = 0.0
    low: float = 0.0
    open_price: float = 0.0
    close_price: float = 0.0
    timestamp: str
    source: str

class MarketStatusResponse(BaseModel):
    is_trading: bool
    current_time: str
    weekday: str
    next_trading_session: str
    data_source: str
    connected_sources: List[str]

class SystemStatusResponse(BaseModel):
    status: str
    uptime: str
    data_sources: Dict[str, str]
    cached_stocks: int
    last_update: str

# 启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动时初始化"""
    global data_manager
    
    logger.info("🚀 启动股票数据API服务器...")
    
    # 初始化数据管理器
    data_manager = HybridStockDataManager()
    
    # 添加实时数据回调
    async def on_realtime_data(stock_data: StockData):
        realtime_data[stock_data.code] = stock_data
        logger.info(f"📊 实时数据更新: {stock_data.name} ¥{stock_data.current_price:.2f}")
    
    data_manager.add_data_callback(on_realtime_data)
    
    # 如果在交易时间，启动实时监听
    if TradingTimeChecker.is_trading_time():
        logger.info("交易时间内，启动后台实时数据监听...")
        asyncio.create_task(data_manager.start())
    
    logger.info("✅ 股票数据API服务器启动完成")

# 关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时清理"""
    global data_manager
    
    logger.info("🛑 关闭股票数据API服务器...")
    
    if data_manager:
        data_manager.stop()
    
    logger.info("✅ 股票数据API服务器已关闭")

# API路由
@app.get("/", summary="API根路径")
async def root():
    """API根路径"""
    return {
        "message": "智能股票数据API",
        "version": "1.0.0",
        "description": "混合数据源股票API服务 (茶股帮TCP + 腾讯API)",
        "endpoints": {
            "market_status": "/market/status",
            "single_stock": "/stock/{stock_code}",
            "multiple_stocks": "/stocks",
            "popular_stocks": "/stocks/popular",
            "system_status": "/system/status"
        }
    }

@app.get("/market/status", response_model=MarketStatusResponse, summary="市场状态")
async def get_market_status():
    """获取市场交易状态"""
    trading_status = TradingTimeChecker.get_trading_status()
    
    # 确定当前数据源
    data_source = "茶股帮TCP" if (trading_status['is_trading'] and 
                                data_manager and 
                                data_manager.chagubang.connected) else "腾讯API"
    
    # 连接的数据源列表
    connected_sources = []
    if data_manager:
        if data_manager.chagubang.connected:
            connected_sources.append("茶股帮TCP")
        connected_sources.append("腾讯API")  # 腾讯API总是可用
    
    return MarketStatusResponse(
        is_trading=trading_status['is_trading'],
        current_time=trading_status['current_time'],
        weekday=trading_status['weekday'],
        next_trading_session=trading_status['next_trading_session'],
        data_source=data_source,
        connected_sources=connected_sources
    )

@app.get("/stock/{stock_code}", response_model=StockResponse, summary="获取单个股票数据")
async def get_single_stock(stock_code: str):
    """获取单个股票数据"""
    if not data_manager:
        raise HTTPException(status_code=500, detail="数据管理器未初始化")
    
    try:
        stock_data = await data_manager.get_single_stock(stock_code)
        
        if not stock_data:
            raise HTTPException(status_code=404, detail=f"未找到股票 {stock_code}")
        
        return StockResponse(
            code=stock_data.code,
            name=stock_data.name,
            current_price=stock_data.current_price,
            change=stock_data.change,
            change_percent=stock_data.change_percent,
            volume=stock_data.volume,
            high=stock_data.high,
            low=stock_data.low,
            open_price=stock_data.open_price,
            close_price=stock_data.close_price,
            timestamp=stock_data.timestamp,
            source=stock_data.source.value
        )
        
    except Exception as e:
        logger.error(f"获取股票 {stock_code} 失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stocks", response_model=List[StockResponse], summary="获取多个股票数据")
async def get_multiple_stocks(stock_codes: List[str]):
    """获取多个股票数据"""
    if not data_manager:
        raise HTTPException(status_code=500, detail="数据管理器未初始化")
    
    if len(stock_codes) > 50:
        raise HTTPException(status_code=400, detail="一次最多查询50只股票")
    
    try:
        stocks_data = await data_manager.get_stock_data(stock_codes)
        
        results = []
        for code in stock_codes:
            if code in stocks_data:
                stock_data = stocks_data[code]
                results.append(StockResponse(
                    code=stock_data.code,
                    name=stock_data.name,
                    current_price=stock_data.current_price,
                    change=stock_data.change,
                    change_percent=stock_data.change_percent,
                    volume=stock_data.volume,
                    high=stock_data.high,
                    low=stock_data.low,
                    open_price=stock_data.open_price,
                    close_price=stock_data.close_price,
                    timestamp=stock_data.timestamp,
                    source=stock_data.source.value
                ))
        
        return results
        
    except Exception as e:
        logger.error(f"获取多个股票失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stocks/popular", response_model=List[StockResponse], summary="获取热门股票")
async def get_popular_stocks():
    """获取热门股票数据"""
    popular_codes = [
        "sh000001",  # 上证指数
        "sz399001",  # 深证成指
        "sz399006",  # 创业板指
        "sh600519",  # 贵州茅台
        "sz000001",  # 平安银行
        "sh600036",  # 招商银行
        "sh601318",  # 中国平安
        "sh600276",  # 恒瑞医药
        "sz300015",  # 爱尔眼科
        "sh688981",  # 中芯国际
    ]
    
    return await get_multiple_stocks(popular_codes)

@app.get("/system/status", response_model=SystemStatusResponse, summary="系统状态")
async def get_system_status():
    """获取系统状态"""
    # 计算运行时间 (简化版)
    uptime = "运行中"
    
    # 数据源状态
    data_sources = {
        "腾讯API": "可用",
        "茶股帮TCP": "可用" if (data_manager and data_manager.chagubang.connected) else "未连接"
    }
    
    return SystemStatusResponse(
        status="运行中",
        uptime=uptime,
        data_sources=data_sources,
        cached_stocks=len(realtime_data),
        last_update=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )

@app.get("/stocks/realtime", summary="获取实时数据缓存")
async def get_realtime_cache():
    """获取当前实时数据缓存"""
    if not realtime_data:
        return {"message": "暂无实时数据", "count": 0}
    
    results = []
    for code, stock_data in realtime_data.items():
        results.append({
            "code": stock_data.code,
            "name": stock_data.name,
            "current_price": stock_data.current_price,
            "change_percent": stock_data.change_percent,
            "timestamp": stock_data.timestamp,
            "source": stock_data.source.value
        })
    
    return {
        "message": f"实时数据缓存",
        "count": len(results),
        "data": results
    }

# 健康检查
@app.get("/health", summary="健康检查")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "data_manager": "initialized" if data_manager else "not_initialized"
    }

# Token管理相关端点
@app.post("/token/update", summary="更新茶股帮Token")
async def update_chagubang_token(request: dict):
    """更新茶股帮Token"""
    try:
        new_token = request.get("token")
        if not new_token:
            raise HTTPException(status_code=400, detail="Token不能为空")

        if not new_token.startswith("QT_"):
            raise HTTPException(status_code=400, detail="Token格式错误，应该以QT_开头")

        # 更新环境变量中的Token
        os.environ["CHAGUBANG_TOKEN"] = new_token
        os.environ["STOCK_API_KEY"] = new_token

        # 如果数据管理器存在，更新其Token
        if data_manager:
            data_manager.chagubang.token = new_token

            # 如果当前已连接，断开并重新连接
            if data_manager.chagubang.connected:
                data_manager.chagubang.disconnect()
                # 如果在交易时间，尝试重新连接
                if TradingTimeChecker.is_trading_time():
                    asyncio.create_task(data_manager.chagubang.connect())

        logger.info(f"Token已更新: {new_token[:15]}...")

        return {
            "success": True,
            "message": "Token更新成功",
            "token_preview": new_token[:15] + "...",
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    except Exception as e:
        logger.error(f"更新Token失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/token/current", summary="获取当前Token信息")
async def get_current_token():
    """获取当前Token信息"""
    try:
        current_token = os.getenv("CHAGUBANG_TOKEN", "")

        return {
            "success": True,
            "current_token": current_token[:15] + "..." if current_token else "未设置",
            "full_token": current_token,  # 仅用于内部，实际部署时应移除
            "connected": data_manager.chagubang.connected if data_manager else False,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    except Exception as e:
        logger.error(f"获取Token信息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/token/test", summary="测试Token连接")
async def test_token_connection(request: dict):
    """测试Token连接"""
    try:
        test_token = request.get("token")
        if not test_token:
            raise HTTPException(status_code=400, detail="Token不能为空")

        # 检查是否在交易时间
        trading_status = TradingTimeChecker.get_trading_status()

        if not trading_status['is_trading']:
            return {
                "success": False,
                "message": "当前不在交易时间，无法测试Token连接",
                "trading_status": trading_status,
                "suggestion": "请在交易时间 (09:10-11:30, 13:00-15:00) 重新测试"
            }

        # 创建临时连接器测试Token
        from hybrid_stock_data_manager import ChaguBangConnector
        test_connector = ChaguBangConnector(test_token)

        # 尝试连接
        connection_result = await test_connector.connect()

        # 清理连接
        test_connector.disconnect()

        return {
            "success": connection_result,
            "message": "Token连接成功" if connection_result else "Token连接失败",
            "token_preview": test_token[:15] + "...",
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    except Exception as e:
        logger.error(f"测试Token失败: {e}")
        return {
            "success": False,
            "message": f"测试失败: {str(e)}",
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

# 启动服务器
if __name__ == "__main__":
    print("🚀 启动智能股票数据API服务器...")
    print("📊 支持数据源: 茶股帮TCP + 腾讯API")
    print("🌐 API文档: http://localhost:8000/docs")
    print("⚡ 健康检查: http://localhost:8000/health")
    
    uvicorn.run(
        "stock_api_server:app",
        host="0.0.0.0",
        port=8001,
        reload=False,
        log_level="info"
    )
