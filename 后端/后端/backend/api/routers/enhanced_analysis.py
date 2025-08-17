"""
增强分析API路由
集成新增的技术指标分析,智能决策Agent,市场情绪分析等功能
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# 请求模型
class TechnicalAnalysisRequest(BaseModel):
    stock_code: str
    prices: List[float]

class SmartDecisionRequest(BaseModel):
    stock_code: str
    stock_data: Dict[str, Any]
    portfolio_data: Optional[Dict[str, Any]] = None

class SentimentAnalysisRequest(BaseModel):
    stock_code: str
    news_data: Optional[List[Dict[str, Any]]] = None
    social_data: Optional[List[str]] = None

@router.post("/technical-analysis", summary="技术指标分析")
async def technical_analysis(request: TechnicalAnalysisRequest):
    """技术指标分析API - 提供RSI,MACD,移动平均线等技术指标计算"""
    try:
        # 导入服务(延迟导入避免循环依赖)
        from services.technical_analysis import get_technical_analysis
        
        if not request.prices or len(request.prices) < 20:
            raise HTTPException(status_code=400, detail="价格数据至少需要20个数据点")
        
        result = get_technical_analysis(request.stock_code, request.prices)
        
        if 'error' in result:
            raise HTTPException(status_code=500, detail=result['error'])
        
        return {"status": "success", "data": result, "message": "技术指标分析完成"}
        
    except Exception as e:
        logger.error(f"技术分析API错误: {e}")
        raise HTTPException(status_code=500, detail=f"技术分析失败: {str(e)}")

@router.post("/smart-decision", summary="智能决策分析")
async def smart_decision(request: SmartDecisionRequest):
    """智能决策分析API - 基于多Agent协作的智能决策系统"""
    try:
        from ai.smart_decision_agent import get_smart_decision
        
        if not request.stock_data:
            raise HTTPException(status_code=400, detail="股票数据不能为空")
        
        result = await get_smart_decision(request.stock_code, request.stock_data, request.portfolio_data)
        
        if 'error' in result:
            raise HTTPException(status_code=500, detail=result['error'])
        
        return {"status": "success", "data": result, "message": "智能决策分析完成"}
        
    except Exception as e:
        logger.error(f"智能决策API错误: {e}")
        raise HTTPException(status_code=500, detail=f"智能决策失败: {str(e)}")

@router.post("/sentiment-analysis", summary="市场情绪分析")
async def sentiment_analysis(request: SentimentAnalysisRequest):
    """市场情绪分析API - 分析新闻和社交媒体数据"""
    try:
        from services.sentiment_analysis import get_market_sentiment
        
        result = get_market_sentiment(request.stock_code, request.news_data, request.social_data)
        
        if 'error' in result:
            raise HTTPException(status_code=500, detail=result['error'])
        
        return {"status": "success", "data": result, "message": "市场情绪分析完成"}
        
    except Exception as e:
        logger.error(f"情绪分析API错误: {e}")
        raise HTTPException(status_code=500, detail=f"情绪分析失败: {str(e)}")

@router.get("/analysis-status", summary="分析服务状态")
async def analysis_status():
    """获取所有增强分析服务的状态"""
    return {
        "status": "success",
        "data": {
            "technical_analysis": "active",
            "smart_decision": "active", 
            "sentiment_analysis": "active",
            "services": {
                "technical_indicators": ["RSI", "MACD", "MA"],
                "decision_agents": ["Bull_Agent", "Bear_Agent", "Risk_Agent"],
                "sentiment_sources": ["新闻分析", "社交媒体", "热点检测"]
            }
        },
        "message": "增强分析服务运行正常"
    }
