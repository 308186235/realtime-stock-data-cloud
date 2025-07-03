"""
茶股帮数据API路由
提供茶股帮实时股票数据的API接口
"""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from backend.services.chagubang_integration import (
    get_realtime_stock_data,
    get_market_overview_data,
    get_hot_stocks_data,
    get_chagubang_stats,
    initialize_chagubang_service
)

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/health")
async def health_check():
    """茶股帮服务健康检查"""
    try:
        stats = await get_chagubang_stats()
        
        return {
            "status": "healthy" if stats.get('connection_status') == 'connected' else "unhealthy",
            "service": "chagubang",
            "connection_status": stats.get('connection_status', 'unknown'),
            "total_received": stats.get('total_received', 0),
            "unique_stocks": stats.get('unique_stocks', 0),
            "last_update": stats.get('last_update'),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"茶股帮健康检查失败: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.get("/stocks/{stock_code}")
async def get_stock_realtime_data(stock_code: str):
    """获取单只股票实时数据"""
    try:
        stock_data = await get_realtime_stock_data(stock_code.upper())
        
        if not stock_data:
            raise HTTPException(status_code=404, detail=f"Stock {stock_code} not found")
        
        return {
            "success": True,
            "data": stock_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取股票数据失败 {stock_code}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stock data: {str(e)}")

@router.get("/stocks")
async def get_all_stocks_data(
    limit: Optional[int] = Query(None, description="限制返回数量"),
    sort_by: Optional[str] = Query("change_pct", description="排序字段"),
    order: Optional[str] = Query("desc", description="排序方向 (asc/desc)")
):
    """获取所有股票实时数据"""
    try:
        all_data = await get_realtime_stock_data()
        
        if not all_data:
            return {
                "success": True,
                "data": [],
                "total": 0,
                "message": "No stock data available",
                "timestamp": datetime.now().isoformat()
            }
        
        # 转换为列表
        stocks_list = list(all_data.values())
        
        # 排序
        if sort_by in ['last_price', 'change_pct', 'volume', 'amount']:
            reverse = (order.lower() == 'desc')
            stocks_list.sort(key=lambda x: x.get(sort_by, 0), reverse=reverse)
        
        # 限制数量
        if limit:
            stocks_list = stocks_list[:limit]
        
        return {
            "success": True,
            "data": stocks_list,
            "total": len(all_data),
            "returned": len(stocks_list),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"获取所有股票数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stocks data: {str(e)}")

@router.get("/market/overview")
async def get_market_overview():
    """获取市场概览"""
    try:
        overview = await get_market_overview_data()
        
        return {
            "success": True,
            "data": overview,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"获取市场概览失败: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get market overview: {str(e)}")

@router.get("/market/hot")
async def get_hot_stocks(
    limit: int = Query(10, description="返回数量", ge=1, le=100),
    type: str = Query("change", description="热门类型: change(涨跌幅), volume(成交量)")
):
    """获取热门股票"""
    try:
        hot_stocks = await get_hot_stocks_data(limit)
        
        # 根据类型重新排序
        if type == "volume":
            hot_stocks.sort(key=lambda x: x.get('volume', 0), reverse=True)
        elif type == "amount":
            hot_stocks.sort(key=lambda x: x.get('amount', 0), reverse=True)
        # 默认按涨跌幅排序（已在服务中实现）
        
        return {
            "success": True,
            "data": hot_stocks[:limit],
            "type": type,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"获取热门股票失败: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get hot stocks: {str(e)}")

@router.get("/stats")
async def get_service_statistics():
    """获取茶股帮服务统计信息"""
    try:
        stats = await get_chagubang_stats()
        
        return {
            "success": True,
            "data": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"获取服务统计失败: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get service stats: {str(e)}")

@router.post("/initialize")
async def initialize_service(background_tasks: BackgroundTasks):
    """初始化茶股帮服务"""
    try:
        # 在后台任务中初始化服务
        background_tasks.add_task(initialize_chagubang_service)
        
        return {
            "success": True,
            "message": "茶股帮服务初始化已启动",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"初始化茶股帮服务失败: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to initialize service: {str(e)}")

@router.get("/search")
async def search_stocks(
    q: str = Query(..., description="搜索关键词"),
    limit: int = Query(10, description="返回数量", ge=1, le=50)
):
    """搜索股票"""
    try:
        all_data = await get_realtime_stock_data()
        
        if not all_data:
            return {
                "success": True,
                "data": [],
                "query": q,
                "total": 0,
                "timestamp": datetime.now().isoformat()
            }
        
        # 搜索匹配的股票
        query = q.upper()
        matched_stocks = []
        
        for stock_data in all_data.values():
            stock_code = stock_data.get('stock_code', '').upper()
            stock_name = stock_data.get('stock_name', '').upper()
            
            if query in stock_code or query in stock_name:
                matched_stocks.append(stock_data)
        
        # 限制返回数量
        matched_stocks = matched_stocks[:limit]
        
        return {
            "success": True,
            "data": matched_stocks,
            "query": q,
            "total": len(matched_stocks),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"搜索股票失败: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search stocks: {str(e)}")

@router.get("/market/sectors")
async def get_market_sectors():
    """获取市场板块数据"""
    try:
        all_data = await get_realtime_stock_data()
        
        if not all_data:
            return {
                "success": True,
                "data": [],
                "timestamp": datetime.now().isoformat()
            }
        
        # 简单的板块分类（基于股票代码）
        sectors = {
            "沪市主板": [],  # 600xxx
            "深市主板": [],  # 000xxx
            "中小板": [],    # 002xxx
            "创业板": [],    # 300xxx
            "科创板": [],    # 688xxx
            "北交所": [],    # 8xxxxx
            "其他": []
        }
        
        for stock_data in all_data.values():
            code = stock_data.get('stock_code', '')
            
            if code.startswith('600') or code.startswith('601') or code.startswith('603'):
                sectors["沪市主板"].append(stock_data)
            elif code.startswith('000'):
                sectors["深市主板"].append(stock_data)
            elif code.startswith('002'):
                sectors["中小板"].append(stock_data)
            elif code.startswith('300'):
                sectors["创业板"].append(stock_data)
            elif code.startswith('688'):
                sectors["科创板"].append(stock_data)
            elif code.startswith('8') and len(code) == 6:
                sectors["北交所"].append(stock_data)
            else:
                sectors["其他"].append(stock_data)
        
        # 计算板块统计
        sector_stats = {}
        for sector_name, stocks in sectors.items():
            if stocks:
                changes = [s.get('change_pct', 0) for s in stocks]
                sector_stats[sector_name] = {
                    "count": len(stocks),
                    "avg_change": sum(changes) / len(changes) if changes else 0,
                    "rising": len([c for c in changes if c > 0]),
                    "falling": len([c for c in changes if c < 0])
                }
        
        return {
            "success": True,
            "data": sector_stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"获取板块数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get sector data: {str(e)}")

# WebSocket支持（如果需要）
@router.websocket("/ws")
async def websocket_endpoint(websocket):
    """WebSocket实时数据推送"""
    await websocket.accept()
    
    try:
        # 这里可以实现WebSocket实时推送逻辑
        # 订阅茶股帮数据更新并推送给客户端
        while True:
            # 获取最新数据
            overview = await get_market_overview_data()
            
            # 发送给客户端
            await websocket.send_json({
                "type": "market_overview",
                "data": overview,
                "timestamp": datetime.now().isoformat()
            })
            
            # 等待一段时间
            import asyncio
            await asyncio.sleep(5)
            
    except Exception as e:
        logger.error(f"WebSocket连接异常: {e}")
    finally:
        await websocket.close()
