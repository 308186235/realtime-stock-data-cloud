"""
账户余额API路由
提供账户余额相关的API端点
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import logging
from datetime import datetime
import random

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/")
async def get_account_balance():
    """获取账户余额"""
    try:
        # 模拟账户余额数据
        balance_data = {
            "account_info": {
                "account_id": "DW123456789",
                "account_name": "东吴秀才账户",
                "account_type": "股票账户",
                "status": "正常",
                "last_update": datetime.now().isoformat()
            },
            "balance": {
                "total_assets": 125680.50,
                "available_cash": 23450.80,
                "frozen_cash": 1200.00,
                "market_value": 101029.70,
                "total_profit_loss": 8650.30,
                "profit_loss_percent": 7.38
            },
            "positions": [
                {
                    "stock_code": "000001",
                    "stock_name": "平安银行",
                    "quantity": 1000,
                    "cost_price": 12.50,
                    "current_price": 13.20,
                    "market_value": 13200.00,
                    "profit_loss": 700.00,
                    "profit_loss_percent": 5.60
                },
                {
                    "stock_code": "000002",
                    "stock_name": "万科A",
                    "quantity": 2000,
                    "cost_price": 18.80,
                    "current_price": 19.45,
                    "market_value": 38900.00,
                    "profit_loss": 1300.00,
                    "profit_loss_percent": 3.46
                },
                {
                    "stock_code": "600036",
                    "stock_name": "招商银行",
                    "quantity": 1500,
                    "cost_price": 32.60,
                    "current_price": 33.15,
                    "market_value": 49725.00,
                    "profit_loss": 825.00,
                    "profit_loss_percent": 1.69
                }
            ],
            "today_trading": {
                "buy_amount": 5600.00,
                "sell_amount": 3200.00,
                "net_amount": 2400.00,
                "commission": 12.50,
                "stamp_tax": 3.20,
                "transfer_fee": 0.60,
                "total_fees": 16.30
            },
            "risk_metrics": {
                "position_concentration": 0.78,
                "sector_concentration": 0.65,
                "leverage_ratio": 0.85,
                "var_95": -2340.50,
                "risk_level": "中等"
            }
        }
        
        return {
            "success": True,
            "data": balance_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"获取账户余额失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取账户余额失败: {str(e)}")

@router.get("/summary")
async def get_balance_summary():
    """获取账户余额摘要"""
    try:
        summary_data = {
            "total_assets": 125680.50,
            "available_cash": 23450.80,
            "market_value": 101029.70,
            "today_profit_loss": 1250.30,
            "total_profit_loss": 8650.30,
            "profit_loss_percent": 7.38,
            "position_count": 3,
            "last_update": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "data": summary_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"获取账户余额摘要失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取账户余额摘要失败: {str(e)}")

@router.get("/positions")
async def get_positions():
    """获取持仓信息"""
    try:
        positions_data = [
            {
                "stock_code": "000001",
                "stock_name": "平安银行",
                "quantity": 1000,
                "available_quantity": 1000,
                "cost_price": 12.50,
                "current_price": 13.20,
                "market_value": 13200.00,
                "profit_loss": 700.00,
                "profit_loss_percent": 5.60,
                "weight": 0.105,
                "sector": "银行",
                "buy_date": "2025-01-01"
            },
            {
                "stock_code": "000002",
                "stock_name": "万科A",
                "quantity": 2000,
                "available_quantity": 2000,
                "cost_price": 18.80,
                "current_price": 19.45,
                "market_value": 38900.00,
                "profit_loss": 1300.00,
                "profit_loss_percent": 3.46,
                "weight": 0.310,
                "sector": "房地产",
                "buy_date": "2024-12-28"
            },
            {
                "stock_code": "600036",
                "stock_name": "招商银行",
                "quantity": 1500,
                "available_quantity": 1500,
                "cost_price": 32.60,
                "current_price": 33.15,
                "market_value": 49725.00,
                "profit_loss": 825.00,
                "profit_loss_percent": 1.69,
                "weight": 0.396,
                "sector": "银行",
                "buy_date": "2024-12-25"
            }
        ]
        
        return {
            "success": True,
            "data": {
                "positions": positions_data,
                "total_count": len(positions_data),
                "total_market_value": sum(p["market_value"] for p in positions_data),
                "total_profit_loss": sum(p["profit_loss"] for p in positions_data)
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"获取持仓信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取持仓信息失败: {str(e)}")

@router.get("/history")
async def get_balance_history(days: int = 30):
    """获取账户余额历史"""
    try:
        # 生成模拟历史数据
        history_data = []
        base_value = 125680.50
        
        for i in range(min(days, 30)):
            # 模拟每日波动
            daily_change = random.uniform(-0.03, 0.03)  # ±3%的日波动
            value = base_value * (1 + daily_change * i / 30)
            
            history_data.append({
                "date": (datetime.now().date() - timedelta(days=days-i-1)).isoformat(),
                "total_assets": round(value, 2),
                "profit_loss": round(value - 117030.20, 2),  # 假设初始投入
                "profit_loss_percent": round((value - 117030.20) / 117030.20 * 100, 2)
            })
        
        return {
            "success": True,
            "data": {
                "history": history_data,
                "period_days": days,
                "start_value": history_data[0]["total_assets"] if history_data else 0,
                "end_value": history_data[-1]["total_assets"] if history_data else 0,
                "total_return": history_data[-1]["profit_loss_percent"] if history_data else 0
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"获取账户余额历史失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取账户余额历史失败: {str(e)}")

@router.get("/performance")
async def get_performance_metrics():
    """获取账户绩效指标"""
    try:
        performance_data = {
            "returns": {
                "total_return": 7.38,
                "annual_return": 15.67,
                "monthly_return": 1.23,
                "weekly_return": 0.45,
                "daily_return": 0.12
            },
            "risk": {
                "volatility": 18.45,
                "max_drawdown": -8.92,
                "sharpe_ratio": 1.34,
                "sortino_ratio": 1.78,
                "calmar_ratio": 1.76
            },
            "trading": {
                "win_rate": 68.5,
                "profit_factor": 2.34,
                "average_win": 156.78,
                "average_loss": -89.45,
                "total_trades": 234,
                "winning_trades": 160
            },
            "benchmark": {
                "benchmark_name": "沪深300",
                "benchmark_return": 5.23,
                "alpha": 2.15,
                "beta": 0.85,
                "correlation": 0.76,
                "tracking_error": 12.34
            }
        }
        
        return {
            "success": True,
            "data": performance_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"获取绩效指标失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取绩效指标失败: {str(e)}")

@router.post("/refresh")
async def refresh_balance():
    """刷新账户余额"""
    try:
        # 模拟刷新操作
        import asyncio
        await asyncio.sleep(1)  # 模拟刷新时间
        
        return {
            "success": True,
            "message": "账户余额刷新成功",
            "data": {
                "refresh_time": datetime.now().isoformat(),
                "status": "completed"
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"刷新账户余额失败: {e}")
        raise HTTPException(status_code=500, detail=f"刷新账户余额失败: {str(e)}")

# 需要导入timedelta
from datetime import timedelta
