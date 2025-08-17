from fastapi import APIRouter, Depends, HTTPException, Body, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

from backend.models import get_db
from backend.services.backtest_service import get_backtest_service
from backend.services.data_service import get_available_symbols
from backend.services.user_service import get_current_user
from backend.models.models import Backtest, TechnicalIndicator, Benchmark

router = APIRouter(prefix="/backtesting", tags=["backtesting"])

# 测试端点
@router.get("/test")
async def backtesting_test():
    """测试回测API是否可用"""
    return {
        "message": "回测API服务器正常工作",
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    }

# 运行回测
@router.post("/run")
async def run_backtest(
    request: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    运行回测
    """
    try:
        # 获取回测服务
        backtest_engine = get_backtest_service(db)
        
        # 运行回测
        backtest_id = backtest_engine.run_backtest(current_user["id"], request)
        
        # 获取回测结果
        backtest = db.query(Backtest).filter(Backtest.backtest_id == backtest_id).first()
        
        if not backtest:
            raise HTTPException(status_code=404, detail="回测结果不存在")
        
        # 返回结果
        return {
            "backtest_id": backtest_id,
            "metrics": backtest.results.get("metrics", {}),
            "charts": backtest.results.get("charts", {}),
            "trades": backtest.results.get("trades", []),
            "benchmark_report": backtest.results.get("benchmark_report")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"运行回测失败: {str(e)}")

# 获取回测结果
@router.get("/results/{backtest_id}")
async def get_backtest_results(
    backtest_id: str,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    获取回测结果
    """
    backtest = db.query(Backtest).filter(Backtest.backtest_id == backtest_id).first()
    
    if not backtest:
        raise HTTPException(status_code=404, detail="回测结果不存在")
    
    # 检查权限
    user_ids = [user.id for user in backtest.users]
    if current_user["id"] not in user_ids and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="无权访问此回测结果")
    
    # 返回结果
    return {
        "id": backtest.backtest_id,
        "name": backtest.name,
        "description": backtest.description,
        "start_date": backtest.start_date,
        "end_date": backtest.end_date,
        "initial_capital": backtest.initial_capital,
        "commission": backtest.commission,
        "request": backtest.config,
        "results": backtest.results,
        "created_at": backtest.created_at.isoformat(),
        "updated_at": backtest.updated_at.isoformat(),
        "status": backtest.status
    }

# 保存回测
@router.post("/save")
async def save_backtest(
    request: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    保存回测结果
    """
    backtest_id = request.get("backtest_id")
    name = request.get("name")
    
    if not backtest_id or not name:
        raise HTTPException(status_code=400, detail="缺少回测ID或名称")
    
    backtest = db.query(Backtest).filter(Backtest.backtest_id == backtest_id).first()
    
    if not backtest:
        raise HTTPException(status_code=404, detail="回测结果不存在")
    
    # 检查权限
    user_ids = [user.id for user in backtest.users]
    if current_user["id"] not in user_ids and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="无权修改此回测结果")
    
    # 更新名称
    backtest.name = name
    db.commit()
    
    return {"status": "success", "message": "回测结果已保存"}

# 获取回测历史
@router.get("/history")
async def get_backtest_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    获取用户的回测历史
    """
    # 查询用户的回测
    user_backtests = (
        db.query(Backtest)
        .filter(Backtest.users.any(id=current_user["id"]))
        .order_by(Backtest.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    # 构建响应
    history = []
    for backtest in user_backtests:
        history.append({
            "id": backtest.backtest_id,
            "name": backtest.name,
            "symbols": backtest.config.get("symbols", []),
            "start_date": backtest.start_date,
            "end_date": backtest.end_date,
            "total_return": backtest.results.get("metrics", {}).get("total_return", 0),
            "created_at": backtest.created_at.isoformat()
        })
    
    return history

# 获取可用的技术指标列表
@router.get("/indicators")
async def get_available_indicators(
    db: Session = Depends(get_db)
):
    """
    获取可用的技术指标列表
    """
    # 从数据库获取指标
    indicators = db.query(TechnicalIndicator).all()
    
    # 如果数据库中没有,返回预定义列表
    if not indicators:
        indicators = [
            {"id": "ma", "name": "移动平均线", "parameters": [{"name": "periods", "type": "list_int", "default": [5, 10, 20, 50, 200]}]},
            {"id": "ema", "name": "指数移动平均线", "parameters": [{"name": "periods", "type": "list_int", "default": [5, 10, 20, 50, 200]}]},
            {"id": "macd", "name": "MACD", "parameters": [
                {"name": "fast_period", "type": "int", "default": 12},
                {"name": "slow_period", "type": "int", "default": 26},
                {"name": "signal_period", "type": "int", "default": 9}
            ]},
            {"id": "rsi", "name": "相对强弱指数", "parameters": [{"name": "period", "type": "int", "default": 14}]},
            {"id": "bollinger", "name": "布林带", "parameters": [
                {"name": "period", "type": "int", "default": 20},
                {"name": "std_dev", "type": "float", "default": 2.0}
            ]},
            {"id": "stochastic", "name": "随机指标", "parameters": [
                {"name": "k_period", "type": "int", "default": 14},
                {"name": "d_period", "type": "int", "default": 3}
            ]},
            {"id": "atr", "name": "平均真实范围", "parameters": [{"name": "period", "type": "int", "default": 14}]},
            {"id": "obv", "name": "能量潮指标", "parameters": []},
            {"id": "mfi", "name": "资金流量指标", "parameters": [{"name": "period", "type": "int", "default": 14}]}
        ]
    else:
        # 转换为响应格式
        indicators = [
            {
                "id": indicator.name,
                "name": indicator.display_name,
                "parameters": indicator.parameters
            }
            for indicator in indicators
        ]
    
    return indicators

# 获取可用的基准指数列表
@router.get("/benchmarks")
async def get_available_benchmarks(
    db: Session = Depends(get_db)
):
    """
    获取可用的基准指数列表
    """
    # 从数据库获取基准
    benchmarks = db.query(Benchmark).all()
    
    # 如果数据库中没有,返回预定义列表
    if not benchmarks:
        benchmarks = [
            {"symbol": "000001.SS", "name": "上证指数", "market": "中国"},
            {"symbol": "399001.SZ", "name": "深证成指", "market": "中国"},
            {"symbol": "399006.SZ", "name": "创业板指", "market": "中国"},
            {"symbol": "SPY", "name": "标普500ETF", "market": "美国"},
            {"symbol": "QQQ", "name": "纳斯达克100ETF", "market": "美国"},
            {"symbol": "^HSI", "name": "恒生指数", "market": "香港"}
        ]
    else:
        # 转换为响应格式
        benchmarks = [
            {
                "symbol": benchmark.symbol,
                "name": benchmark.name,
                "market": benchmark.market
            }
            for benchmark in benchmarks
        ]
    
    return benchmarks

# 获取可用的股票列表
@router.get("/symbols")
async def get_symbols():
    """
    获取可用的股票列表
    """
    return get_available_symbols() 
