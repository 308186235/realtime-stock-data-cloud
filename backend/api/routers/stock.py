from fastapi import APIRouter, HTTPException, Depends, Query, Body
from typing import Optional, List, Dict, Any
import logging
import sys
import os

# 添加路径以导入适配器
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from adapters.simple_database_adapter import simple_db_adapter
from services.market_data_service import MarketDataService

# 初始化日志
logger = logging.getLogger(__name__)

router = APIRouter()

# 初始化服务
market_data_service = MarketDataService()

@router.get("/")
async def get_stocks(
    market: Optional[str] = Query(None, description="市场,如SH,SZ等"),
    industry: Optional[str] = Query(None, description="行业分类"),
    limit: int = Query(20, description="返回数量限制", ge=1, le=100)
):
    """获取股票列表"""
    try:
        # 构建过滤条件
        filters = {}
        if market:
            filters['market'] = market
        if industry:
            filters['industry'] = industry

        # 从数据库获取股票列表
        stocks = simple_db_adapter.get_stocks(filters, limit)

        # 如果数据库中没有数据，返回示例数据
        if not stocks:
            stocks = [
                {"code": "600000", "name": "浦发银行", "market": "SH", "industry": "银行", "is_active": True},
                {"code": "600036", "name": "招商银行", "market": "SH", "industry": "银行", "is_active": True},
                {"code": "000001", "name": "平安银行", "market": "SZ", "industry": "银行", "is_active": True},
                {"code": "002415", "name": "海康威视", "market": "SZ", "industry": "电子", "is_active": True}
            ]

        return {
            "success": True,
            "data": stocks,
            "total": len(stocks)
        }
    except Exception as e:
        logger.error(f"获取股票列表出错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_stock(stock_data: Dict[str, Any] = Body(...)):
    """创建股票信息"""
    try:
        result = simple_db_adapter.create_stock(stock_data)
        if result['success']:
            return {
                "success": True,
                "data": result['data'],
                "message": "股票信息创建成功"
            }
        else:
            raise HTTPException(status_code=400, detail=result.get('error', '创建股票信息失败'))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建股票信息出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建股票信息失败: {str(e)}")

@router.get("/{stock_code}")
async def get_stock_info(stock_code: str):
    """获取指定股票的基本信息"""
    try:
        # 从数据库获取股票基本信息
        result = simple_db_adapter.get_stock(stock_code)
        if result['success']:
            stock_info = result['data']

            # 尝试获取实时价格数据
            try:
                price_data = market_data_service.get_real_time_data(stock_code)
                if price_data:
                    stock_info.update(price_data)
            except Exception as e:
                logger.warning(f"获取实时价格失败: {str(e)}")
                # 使用默认价格数据
                stock_info.update({
                    "price": 15.67,
                    "change": 0.45,
                    "change_pct": 2.96,
                    "open": 15.32,
                    "high": 15.89,
                    "low": 15.28,
                    "volume": 12568900,
                    "amount": 196358620,
                    "market_cap": 15672000000,
                    "pe_ratio": 12.5,
                    "pb_ratio": 1.35,
                    "dividend_yield": 2.3
                })

            return {
                "success": True,
                "data": stock_info
            }
        else:
            raise HTTPException(status_code=404, detail="股票不存在")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取股票信息出错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{stock_code}/kdata")
async def get_stock_kdata(
    stock_code: str,
    period: str = Query("daily", description="K线周期,如daily,weekly,monthly"),
    start_date: Optional[str] = Query(None, description="开始日期,格式YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期,格式YYYY-MM-DD"),
    limit: int = Query(30, description="返回条数", ge=1, le=500)
):
    """获取股票K线数据"""
    try:
        # 实际应用中这里应该从数据源获取K线数据
        return {
            "success": True,
            "data": [
                {"date": "2023-04-26", "open": 15.32, "high": 15.67, "low": 15.25, "close": 15.45, "volume": 12568900, "amount": 192356780},
                {"date": "2023-04-27", "open": 15.45, "high": 15.89, "low": 15.28, "close": 15.67, "volume": 13526800, "amount": 210589300}
                # 更多K线数据...
            ],
            "total": 2
        }
    except Exception as e:
        logger.error(f"获取K线数据出错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{stock_code}/indicators")
async def get_stock_indicators(
    stock_code: str,
    indicators: str = Query("macd,kdj,rsi", description="需要获取的指标,逗号分隔"),
    period: str = Query("daily", description="周期,如daily,weekly,monthly"),
    limit: int = Query(30, description="返回条数", ge=1, le=500)
):
    """获取股票技术指标数据"""
    try:
        # 实际应用中这里应该计算并返回指标数据
        return {
            "success": True,
            "data": {
                "macd": [
                    {"date": "2023-04-26", "dif": 0.25, "dea": 0.18, "macd": 0.14},
                    {"date": "2023-04-27", "dif": 0.28, "dea": 0.20, "macd": 0.16}
                ],
                "kdj": [
                    {"date": "2023-04-26", "k": 65.2, "d": 58.3, "j": 72.1},
                    {"date": "2023-04-27", "k": 68.5, "d": 60.1, "j": 76.9}
                ],
                "rsi": [
                    {"date": "2023-04-26", "rsi6": 58.3, "rsi12": 62.1, "rsi24": 55.8},
                    {"date": "2023-04-27", "rsi6": 60.2, "rsi12": 63.5, "rsi24": 56.4}
                ]
            }
        }
    except Exception as e:
        logger.error(f"获取技术指标数据出错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{stock_code}/forecast")
async def get_stock_forecast(
    stock_code: str,
    days: int = Query(5, description="预测天数", ge=1, le=30)
):
    """获取股票价格预测"""
    try:
        # 实际应用中这里应该调用AI服务进行预测
        return {
            "success": True,
            "data": {
                "stock_code": stock_code,
                "current_price": 15.67,
                "predictions": [
                    {"date": "2023-04-28", "price": 15.82, "lower_bound": 15.65, "upper_bound": 16.05, "confidence": 0.85},
                    {"date": "2023-05-01", "price": 16.05, "lower_bound": 15.80, "upper_bound": 16.35, "confidence": 0.82},
                    {"date": "2023-05-02", "price": 16.23, "lower_bound": 15.95, "upper_bound": 16.55, "confidence": 0.78},
                    {"date": "2023-05-03", "price": 16.18, "lower_bound": 15.85, "upper_bound": 16.50, "confidence": 0.75},
                    {"date": "2023-05-04", "price": 16.35, "lower_bound": 15.90, "upper_bound": 16.75, "confidence": 0.72}
                ]
            }
        }
    except Exception as e:
        logger.error(f"获取股票预测数据出错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 
