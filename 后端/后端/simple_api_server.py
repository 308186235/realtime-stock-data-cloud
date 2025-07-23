from fastapi import FastAPI, HTTPException, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import uuid
import json
from pydantic import BaseModel

# 创建FastAPI应用
app = FastAPI(
    title="交易系统API测试服务器",
    description="简化版API服务器用于测试前后端连接",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# 设置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 模拟数据存储
# 模拟数据已禁用

# 模型定义
class StrategyConfig(BaseModel):
    type: str
    params: Dict[str, Any] = {}

class RiskConfig(BaseModel):
    enabled: bool = True
    max_position_size: float = 0.2
    max_drawdown: float = 0.1
    fixed_stop_loss: float = 0.05
    trailing_stop_loss: float = 0.08
    time_stop_loss: int = 10
    position_sizing_method: str = "risk"
    risk_per_trade: float = 0.02

class TechnicalIndicatorConfig(BaseModel):
    enabled: bool = True
    indicators: List[str] = ["ma", "ema", "macd", "rsi", "bollinger"]

class BenchmarkConfig(BaseModel):
    enabled: bool = False
    symbol: str = "000001.SS"

class BacktestRequest(BaseModel):
    strategies: List[StrategyConfig]
    symbols: List[str]
    start_date: str
    end_date: str
    initial_capital: float = 100000.0
    commission: float = 0.0003
    name: Optional[str] = None
    risk_management: Optional[RiskConfig] = None
    technical_indicators: Optional[TechnicalIndicatorConfig] = None
    benchmark_comparison: Optional[BenchmarkConfig] = None

class BacktestSaveRequest(BaseModel):
    backtest_id: str
    name: str

# 辅助函数 - 模拟认证
def get_current_user():
    """模拟获取当前用户"""
    return {
        "username": "test_user",
        "role": "user",
        "is_active": True
    }

# 认证API测试端点
@app.get("/api/auth/test")
async def auth_test():
    """测试认证API是否可用"""
    return {
        "message": "认证API服务器正常工作",
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    }

# 回测API测试端点
@app.get("/api/backtesting/test")
async def backtesting_test():
    """测试回测API是否可用"""
    return {
        "message": "回测API服务器正常工作",
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    }

# 前端会调用的主要API
@app.post("/api/auth/token")
async def mock_login(form_data: dict = Body(...)):
    """模拟登录API"""
    return {
        "access_token": "test_access_token",
        "token_type": "bearer",
        "username": "test_user",
        "expires_at": (datetime.now() + timedelta(minutes=30)).isoformat()
    }

@app.get("/api/auth/me")
async def get_user_info():
    """获取当前用户"""
    return get_current_user()

@app.post("/api/backtesting/run")
async def run_backtest(request: BacktestRequest):
    """执行回测"""
    # 生成回测ID
    backtest_id = str(uuid.uuid4())
    
    # 获取当前用户
    current_user = get_current_user()
    
    # 创建模拟回测结果
    trades = []
    
    # 根据请求的股票和日期创建模拟交易数据
    for symbol in request.symbols:
        # 模拟买入交易
        buy_date = datetime.strptime(request.start_date, "%Y-%m-%d") + timedelta(days=5)
        trades.append({
            "date": buy_date.isoformat(),
            "symbol": symbol,
            "action": "BUY",
            "price": 150.0,
            "shares": 100,
            "cost": 15000.0,
            "profit": 0.0
        })
        
        # 模拟卖出交易
        sell_date = datetime.strptime(request.end_date, "%Y-%m-%d") - timedelta(days=5)
        trades.append({
            "date": sell_date.isoformat(),
            "symbol": symbol,
            "action": "SELL",
            "price": 180.0,
            "shares": 100,
            "revenue": 18000.0,
            "profit": 3000.0
        })
    
    # 创建模拟图表数据 (Base64编码图像数据太长,这里用占位符代替)
    charts = {
        "equity_curve": "base64_encoded_equity_curve_image",
        "drawdown_curve": "base64_encoded_drawdown_curve_image",
        "monthly_returns": "base64_encoded_monthly_returns_image",
        "trade_distribution": "base64_encoded_trade_distribution_image"
    }
    
    # 创建模拟指标数据
    metrics = {
        "total_return": 0.20,
        "annual_return": 0.15,
        "sharpe_ratio": 1.8,
        "max_drawdown": 0.05,
        "win_rate": 0.75,
        "profit_factor": 2.5,
        "trade_count": len(trades) // 2,  # 买入+卖出算一次交易
        "avg_trade_duration": 30,
        "volatility": 0.12
    }
    
    # 创建模拟基准比较数据
    benchmark_report = None
    if request.benchmark_comparison and request.benchmark_comparison.enabled:
        benchmark_report = {
            "symbol": request.benchmark_comparison.symbol,
            "strategy_return": 0.20,
            "benchmark_return": 0.10,
            "alpha": 0.10,
            "beta": 0.9,
            "correlation": 0.75,
            "information_ratio": 1.2,
            "tracking_error": 0.08
        }
    
    # 保存完整结果
    report = {
        "metrics": metrics,
        "charts": charts
    }
    
    saved_results = {
        "id": backtest_id,
        "name": request.name or f"回测 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "request": request.dict(),
        "results": {
            "trades": trades,
            "equity_curve": [{"date": d.isoformat(), "equity": 100000 * (1 + 0.001 * i)} for i, d in enumerate([
                datetime.strptime(request.start_date, "%Y-%m-%d") + timedelta(days=i) 
                for i in range((datetime.strptime(request.end_date, "%Y-%m-%d") - datetime.strptime(request.start_date, "%Y-%m-%d")).days)
            ])]
        },
        "report": report,
        "benchmark_report": benchmark_report,
        "created_at": datetime.now().isoformat(),
        "user_id": current_user["username"]
    }
    
    # 存储结果
    mock_backtest_results[backtest_id] = saved_results
    
    # 准备响应
    response = {
        "backtest_id": backtest_id,
        "metrics": metrics,
        "charts": charts,
        "trades": trades,
        "benchmark_report": benchmark_report
    }
    
    return response

@app.get("/api/backtesting/results/{backtest_id}")
async def get_backtest_results(backtest_id: str):
    """获取回测结果"""
    if backtest_id not in mock_backtest_results:
        raise HTTPException(status_code=404, detail="回测结果不存在")
    
    return mock_backtest_results[backtest_id]

@app.post("/api/backtesting/save")
async def save_backtest(request: BacktestSaveRequest):
    """保存回测结果"""
    if request.backtest_id not in mock_backtest_results:
        raise HTTPException(status_code=404, detail="回测结果不存在")
    
    # 更新名称
    mock_backtest_results[request.backtest_id]["name"] = request.name
    
    return {"status": "success", "message": "回测结果已保存"}

@app.get("/api/backtesting/history")
async def get_backtest_history():
    """获取回测历史"""
    history = []
    
    for backtest_id, result in mock_backtest_results.items():
        history.append({
            "id": backtest_id,
            "name": result["name"],
            "symbols": result["request"]["symbols"],
            "start_date": result["request"]["start_date"],
            "end_date": result["request"]["end_date"],
            "total_return": result["report"]["metrics"]["total_return"],
            "created_at": result["created_at"]
        })
    
    # 按创建时间倒序排序
    history.sort(key=lambda x: x["created_at"], reverse=True)
    
    return history

@app.get("/api/backtesting/indicators")
async def get_available_indicators():
    """获取可用的技术指标列表"""
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
    
    return indicators

@app.get("/api/backtesting/benchmarks")
async def get_available_benchmarks():
    """获取可用的基准指数列表"""
    benchmarks = [
        {"symbol": "000001.SS", "name": "上证指数", "market": "中国"},
        {"symbol": "399001.SZ", "name": "深证成指", "market": "中国"},
        {"symbol": "399006.SZ", "name": "创业板指", "market": "中国"},
        {"symbol": "SPY", "name": "标普500ETF", "market": "美国"},
        {"symbol": "QQQ", "name": "纳斯达克100ETF", "market": "美国"},
        {"symbol": "^HSI", "name": "恒生指数", "market": "香港"}
    ]
    
    return benchmarks

# 主入口
if __name__ == "__main__":
    print("启动简化版API测试服务器...")
    print("服务器将运行在 http://localhost:8000")
    print("API文档地址: http://localhost:8000/api/docs")
    print("按 Ctrl+C 停止服务器")
    
    uvicorn.run(
        "simple_api_server:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True
    ) 
