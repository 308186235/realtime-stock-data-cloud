"""
技术指标API - 提供各种技术分析指标计算
"""
from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Dict, Any, Optional
import logging
import time
import random
from datetime import datetime, timedelta

from services.technical_indicators import technical_indicators

logger = logging.getLogger(__name__)

router = APIRouter()

def generate_mock_ohlc_data(stock_code: str, days: int = 60) -> List[Dict]:
    """生成模拟OHLC数据用于测试"""
    base_price = {
        '000001': 12.50,
        '600000': 10.80,
        '600519': 1680.00,
        '000858': 128.50,
        '002415': 39.20
    }.get(stock_code, 20.00)
    
    ohlc_data = []
    current_price = base_price
    
    for i in range(days):
        # 模拟价格波动
        change_percent = random.uniform(-0.05, 0.05)  # -5% 到 +5%
        
        open_price = current_price
        high_price = open_price * random.uniform(1.0, 1.08)
        low_price = open_price * random.uniform(0.92, 1.0)
        close_price = open_price * (1 + change_percent)
        
        # 确保high >= max(open, close) 和 low <= min(open, close)
        high_price = max(high_price, open_price, close_price)
        low_price = min(low_price, open_price, close_price)
        
        volume = random.randint(1000000, 50000000)
        
        ohlc_data.append({
            'date': (datetime.now() - timedelta(days=days-i-1)).strftime('%Y-%m-%d'),
            'open': round(open_price, 2),
            'high': round(high_price, 2),
            'low': round(low_price, 2),
            'close': round(close_price, 2),
            'volume': volume
        })
        
        current_price = close_price
    
    return ohlc_data

@router.get("/indicators/{stock_code}")
async def get_stock_indicators(
    stock_code: str,
    period: int = Query(60, description="数据周期（天数）"),
    indicators: Optional[str] = Query(None, description="指定指标，用逗号分隔，如：ma5,ma20,rsi,macd")
):
    """获取股票的技术指标"""
    try:
        # 生成模拟数据（实际应用中应从数据库获取）
        ohlc_data = generate_mock_ohlc_data(stock_code, period)
        
        if not ohlc_data:
            raise HTTPException(status_code=404, detail="未找到股票数据")
        
        # 计算所有指标
        all_indicators = technical_indicators.calculate_all_indicators(ohlc_data)
        
        # 如果指定了特定指标，只返回这些指标
        if indicators:
            requested_indicators = [ind.strip() for ind in indicators.split(',')]
            filtered_indicators = {
                key: value for key, value in all_indicators.items() 
                if key in requested_indicators
            }
            result_indicators = filtered_indicators
        else:
            result_indicators = all_indicators
        
        # 获取最新指标值
        latest_indicators = technical_indicators.get_latest_indicators(stock_code, ohlc_data)
        
        return {
            "success": True,
            "stock_code": stock_code,
            "period": period,
            "data_points": len(ohlc_data),
            "indicators": result_indicators,
            "latest_values": latest_indicators,
            "timestamp": time.time()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"计算技术指标失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/indicators/{stock_code}/latest")
async def get_latest_indicators(stock_code: str):
    """获取股票最新的技术指标值"""
    try:
        # 生成模拟数据
        ohlc_data = generate_mock_ohlc_data(stock_code, 60)
        
        if not ohlc_data:
            raise HTTPException(status_code=404, detail="未找到股票数据")
        
        # 获取最新指标值
        latest_indicators = technical_indicators.get_latest_indicators(stock_code, ohlc_data)
        
        return {
            "success": True,
            "stock_code": stock_code,
            "latest_indicators": latest_indicators,
            "timestamp": time.time()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取最新技术指标失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/indicators/calculate")
async def calculate_custom_indicators(request_data: Dict[str, Any] = Body(...)):
    """自定义计算技术指标"""
    try:
        ohlc_data = request_data.get('ohlc_data')
        indicator_types = request_data.get('indicators', [])
        
        if not ohlc_data:
            raise HTTPException(status_code=400, detail="缺少OHLC数据")
        
        # 验证数据格式
        required_fields = ['open', 'high', 'low', 'close', 'volume']
        for item in ohlc_data:
            for field in required_fields:
                if field not in item:
                    raise HTTPException(status_code=400, detail=f"数据缺少字段: {field}")
        
        # 计算指标
        if indicator_types:
            # 计算指定指标
            all_indicators = technical_indicators.calculate_all_indicators(ohlc_data)
            result_indicators = {
                key: value for key, value in all_indicators.items() 
                if key in indicator_types
            }
        else:
            # 计算所有指标
            result_indicators = technical_indicators.calculate_all_indicators(ohlc_data)
        
        return {
            "success": True,
            "data_points": len(ohlc_data),
            "indicators": result_indicators,
            "timestamp": time.time()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"自定义计算技术指标失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/indicators/{stock_code}/ma")
async def get_moving_averages(
    stock_code: str,
    periods: str = Query("5,10,20,60", description="MA周期，用逗号分隔")
):
    """获取移动平均线"""
    try:
        period_list = [int(p.strip()) for p in periods.split(',')]
        ohlc_data = generate_mock_ohlc_data(stock_code, max(period_list) + 20)
        
        closes = [item['close'] for item in ohlc_data]
        
        ma_results = {}
        for period in period_list:
            ma_values = technical_indicators.moving_average(closes, period)
            ma_results[f'ma{period}'] = ma_values
        
        return {
            "success": True,
            "stock_code": stock_code,
            "moving_averages": ma_results,
            "timestamp": time.time()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail="周期参数格式错误")
    except Exception as e:
        logger.error(f"计算移动平均线失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/indicators/{stock_code}/macd")
async def get_macd(
    stock_code: str,
    fast_period: int = Query(12, description="快线周期"),
    slow_period: int = Query(26, description="慢线周期"),
    signal_period: int = Query(9, description="信号线周期")
):
    """获取MACD指标"""
    try:
        ohlc_data = generate_mock_ohlc_data(stock_code, slow_period + 50)
        closes = [item['close'] for item in ohlc_data]
        
        macd_result = technical_indicators.macd(closes, fast_period, slow_period, signal_period)
        
        return {
            "success": True,
            "stock_code": stock_code,
            "macd": macd_result,
            "parameters": {
                "fast_period": fast_period,
                "slow_period": slow_period,
                "signal_period": signal_period
            },
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"计算MACD失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/indicators/{stock_code}/rsi")
async def get_rsi(
    stock_code: str,
    period: int = Query(14, description="RSI周期")
):
    """获取RSI指标"""
    try:
        ohlc_data = generate_mock_ohlc_data(stock_code, period + 30)
        closes = [item['close'] for item in ohlc_data]
        
        rsi_values = technical_indicators.rsi(closes, period)
        
        return {
            "success": True,
            "stock_code": stock_code,
            "rsi": rsi_values,
            "period": period,
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"计算RSI失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/indicators/{stock_code}/bollinger")
async def get_bollinger_bands(
    stock_code: str,
    period: int = Query(20, description="布林带周期"),
    std_dev: float = Query(2.0, description="标准差倍数")
):
    """获取布林带指标"""
    try:
        ohlc_data = generate_mock_ohlc_data(stock_code, period + 30)
        closes = [item['close'] for item in ohlc_data]
        
        boll_result = technical_indicators.bollinger_bands(closes, period, std_dev)
        
        return {
            "success": True,
            "stock_code": stock_code,
            "bollinger_bands": boll_result,
            "parameters": {
                "period": period,
                "std_dev": std_dev
            },
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"计算布林带失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/indicators/{stock_code}/kdj")
async def get_kdj(
    stock_code: str,
    period: int = Query(9, description="KDJ周期")
):
    """获取KDJ指标"""
    try:
        ohlc_data = generate_mock_ohlc_data(stock_code, period + 30)
        
        highs = [item['high'] for item in ohlc_data]
        lows = [item['low'] for item in ohlc_data]
        closes = [item['close'] for item in ohlc_data]
        
        kdj_result = technical_indicators.kdj(highs, lows, closes, period)
        
        return {
            "success": True,
            "stock_code": stock_code,
            "kdj": kdj_result,
            "period": period,
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"计算KDJ失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test")
async def test_indicators():
    """测试技术指标计算功能"""
    try:
        test_stock = "000001"
        ohlc_data = generate_mock_ohlc_data(test_stock, 60)
        
        # 计算所有指标
        all_indicators = technical_indicators.calculate_all_indicators(ohlc_data)
        latest_indicators = technical_indicators.get_latest_indicators(test_stock, ohlc_data)
        
        return {
            "success": True,
            "message": "技术指标计算功能正常",
            "test_stock": test_stock,
            "data_points": len(ohlc_data),
            "available_indicators": list(all_indicators.keys()),
            "latest_values": latest_indicators,
            "sample_data": ohlc_data[-5:],  # 最后5天数据
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"测试技术指标失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
