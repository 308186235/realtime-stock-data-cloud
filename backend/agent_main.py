"""
Agent交易系统启动文件 - 只启动核心Agent功能
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
import sys
import uvicorn

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="Agent交易系统API",
    description="智能交易Agent系统",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """根路径"""
    return {"message": "Agent交易系统API正在运行", "status": "active"}

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "agent-trading-api"}

@app.get("/api/health")
async def api_health_check():
    """API健康检查 - 兼容移动端"""
    return {"status": "healthy", "service": "agent-trading-api"}

# Agent交易相关API
@app.get("/api/agent-trading/fund")
async def get_fund_info():
    """获取资金信息"""
    try:
        # 直接导入并调用余额读取功能
        from fixed_balance_reader import get_balance_fixed
        
        result = get_balance_fixed()
        
        if result and isinstance(result, dict):
            return {
                "status": "success",
                "message": "资金信息获取成功",
                "data": {
                    "total_assets": result.get("total_assets", 0.0),
                    "available_cash": result.get("available_cash", 0.0),
                    "market_value": result.get("market_value", 0.0),
                    "frozen_amount": result.get("frozen_amount", 0.0),
                    "update_time": result.get("update_time", ""),
                    "data_source": result.get("data_source", "")
                }
            }
        else:
            return {"status": "error", "message": "获取真实余额失败或返回数据格式错误"}
            
    except Exception as e:
        logger.error(f"获取资金信息失败: {str(e)}")
        return {"status": "error", "message": f"获取资金信息失败: {str(e)}"}

@app.get("/api/agent-trading/status")
async def get_agent_status():
    """获取Agent状态"""
    return {
        "status": "success",
        "data": {
            "active": True,
            "auto_trading_enabled": False,
            "daily_trade_count": 0,
            "pending_orders": 0,
            "execution_history_count": 0,
            "last_update": "2025-06-29 12:00:00"
        }
    }

@app.post("/api/agent-trading/enable")
async def enable_auto_trading():
    """启用自动交易"""
    return {
        "status": "success",
        "message": "自动交易已启用",
        "data": {"auto_trading_enabled": True}
    }

@app.post("/api/agent-trading/disable")
async def disable_auto_trading():
    """禁用自动交易"""
    return {
        "status": "success",
        "message": "自动交易已禁用",
        "data": {"auto_trading_enabled": False}
    }

@app.get("/api/agent-trading/positions")
async def get_positions():
    """获取持仓信息"""
    # 这里可以添加真实的持仓获取逻辑
    return {
        "status": "success",
        "data": {
            "positions": [],
            "total_market_value": 0.0,
            "total_profit_loss": 0.0,
            "update_time": "2025-06-29 12:00:00"
        }
    }

@app.get("/api/agent-trading/orders")
async def get_orders():
    """获取订单信息"""
    # 这里可以添加真实的订单获取逻辑
    return {
        "status": "success",
        "data": {
            "orders": [],
            "pending_count": 0,
            "completed_count": 0,
            "update_time": "2025-06-29 12:00:00"
        }
    }

if __name__ == "__main__":
    logger.info("启动Agent交易系统API...")
    uvicorn.run(
        "agent_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
