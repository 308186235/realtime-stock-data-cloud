"""
同花顺交易服务API路由
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
import logging
import json
import asyncio
import os
import time
import random
from datetime import datetime, timedelta

# 创建路由器
router = APIRouter(prefix="/ths", tags=["tonghuashun"])

# 模型定义
class LoginRequest(BaseModel):
    account: str = Field(..., description="交易账号")
    password: str = Field(..., description="交易密码")
    broker_type: str = Field(..., description="券商类型")
    verification_code: Optional[str] = Field(None, description="验证码")

class OrderRequest(BaseModel):
    session_id: str = Field(..., description="会话ID")
    symbol: str = Field(..., description="证券代码")
    price: float = Field(..., description="委托价格")
    volume: int = Field(..., description="委托数量")
    direction: str = Field(..., description="交易方向,'buy'或'sell'")
    order_type: str = Field("limit", description="订单类型,'limit'(限价)或'market'(市价)")

class CancelOrderRequest(BaseModel):
    session_id: str = Field(..., description="会话ID")
    order_id: str = Field(..., description="委托编号")

# 会话存储
active_sessions = {}

# 模拟数据 - 实际应用中,这些应该从同花顺API获取
mock_account_info = {
    "balance": 100000.00,
    "available": 50000.00,
    "market_value": 50000.00,
    "total_assets": 100000.00,
    "frozen": 0.00
}

mock_positions = [
    {
        "symbol": "600519",
        "name": "贵州茅台",
        "volume": 10,
        "available": 10,
        "cost_price": 1800.00,
        "current_price": 1826.50,
        "market_value": 18265.00,
        "profit_loss": 265.00,
        "profit_loss_ratio": 0.0147
    },
    {
        "symbol": "000858",
        "name": "五粮液",
        "volume": 50,
        "available": 50,
        "cost_price": 180.00,
        "current_price": 185.20,
        "market_value": 9260.00,
        "profit_loss": 260.00,
        "profit_loss_ratio": 0.0289
    }
]

mock_orders = [
    {
        "order_id": "2023051001",
        "symbol": "600519",
        "name": "贵州茅台",
        "price": 1825.00,
        "volume": 5,
        "direction": "BUY",
        "status": "FILLED",
        "submit_time": "2023-05-10 09:30:15",
        "traded_volume": 5
    },
    {
        "order_id": "2023051002",
        "symbol": "000858",
        "name": "五粮液",
        "price": 185.00,
        "volume": 20,
        "direction": "BUY",
        "status": "PARTIAL",
        "submit_time": "2023-05-10 10:15:32",
        "traded_volume": 10
    }
]

# 东吴秀才账户模拟数据
dongwu_xiucai_account_info = {
    "balance": 150000.00,
    "available": 95000.00,
    "market_value": 55000.00,
    "total_assets": 150000.00,
    "frozen": 0.00
}

# 东吴秀才持仓模拟数据
dongwu_xiucai_positions = [
    {
        "symbol": "600519",
        "name": "贵州茅台",
        "volume": 5,
        "available": 5,
        "cost_price": 1820.00,
        "current_price": 1836.50,
        "market_value": 9182.50,
        "profit_loss": 82.50,
        "profit_loss_ratio": 0.0045
    },
    {
        "symbol": "600036",
        "name": "招商银行",
        "volume": 500,
        "available": 500,
        "cost_price": 35.50,
        "current_price": 36.80,
        "market_value": 18400.00,
        "profit_loss": 650.00,
        "profit_loss_ratio": 0.0366
    }
]

# 模拟余额历史记录
mock_balance_history = []

# API路由
@router.post("/login", response_model=Dict)
async def login(request: LoginRequest):
    """登录同花顺接口"""
    # 这里只是模拟,实际应用中需要与同花顺通信
    if request.account and request.password:
        session_id = f"ths_session_{int(time.time())}"
        active_sessions[session_id] = {
            "account": request.account,
            "broker_type": request.broker_type,
            "login_time": datetime.now().isoformat(),
            "last_activity": time.time()
        }
        
        return {
            "success": True,
            "message": "登录成功",
            "session_id": session_id
        }
    else:
        raise HTTPException(status_code=400, detail="账号或密码不能为空")

@router.post("/logout", response_model=Dict)
async def logout(session_id: str):
    """登出同花顺接口"""
    if session_id in active_sessions:
        del active_sessions[session_id]
        return {"success": True, "message": "已成功登出"}
    else:
        return {"success": False, "message": "无效的会话ID"}

@router.get("/account_info", response_model=Dict)
async def get_account_info(session_id: str):
    """获取账户资金信息"""
    if session_id not in active_sessions:
        return {"success": False, "message": "无效的会话ID"}
    
    # 检查是否是东吴秀才账户
    if active_sessions[session_id].get("broker_type") == "dongwu_xiucai":
        return {
            "success": True,
            "data": dongwu_xiucai_account_info
        }
    
    return {
        "success": True,
        "data": mock_account_info
    }

@router.get("/positions", response_model=Dict)
async def get_positions(session_id: str):
    """获取持仓列表"""
    if session_id not in active_sessions:
        return {"success": False, "message": "无效的会话ID"}
    
    # 检查是否是东吴秀才账户
    if active_sessions[session_id].get("broker_type") == "dongwu_xiucai":
        return {
            "success": True,
            "data": dongwu_xiucai_positions
        }
    
    return {
        "success": True,
        "data": mock_positions
    }

@router.post("/place_order", response_model=Dict)
async def place_order(request: OrderRequest):
    """下单"""
    if request.session_id not in active_sessions:
        return {"success": False, "message": "无效的会话ID"}
    
    # 生成订单ID
    order_id = f"order_{int(time.time())}"
    
    # 获取股票名称 - 实际应用中应该从市场数据获取
    stock_names = {
        "600519": "贵州茅台",
        "000858": "五粮液",
        "601318": "中国平安",
        "600036": "招商银行"
    }
    
    stock_name = stock_names.get(request.symbol, "未知股票")
    
    # 创建新订单
    new_order = {
        "order_id": order_id,
        "symbol": request.symbol,
        "name": stock_name,
        "price": request.price,
        "volume": request.volume,
        "direction": request.direction.upper(),
        "status": "SUBMITTED",
        "submit_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "traded_volume": 0
    }
    
    # 添加到订单列表 - 实际应用中应发送到同花顺
    mock_orders.insert(0, new_order)
    
    return {
        "success": True,
        "message": "委托已提交",
        "data": {
            "order_id": order_id
        }
    }

@router.post("/cancel_order", response_model=Dict)
async def cancel_order(request: CancelOrderRequest):
    """撤单"""
    if request.session_id not in active_sessions:
        return {"success": False, "message": "无效的会话ID"}
    
    # 查找订单
    order_found = False
    for order in mock_orders:
        if order["order_id"] == request.order_id:
            if order["status"] in ["SUBMITTED", "PARTIAL", "QUEUED"]:
                order["status"] = "CANCELLED"
                order_found = True
            else:
                return {"success": False, "message": "该委托状态不可撤单"}
    
    if not order_found:
        return {"success": False, "message": "未找到指定委托"}
    
    return {
        "success": True,
        "message": "撤单请求已提交"
    }

@router.get("/orders", response_model=Dict)
async def get_orders(session_id: str, status: Optional[str] = None, 
                     start_date: Optional[str] = None, end_date: Optional[str] = None):
    """获取委托列表"""
    if session_id not in active_sessions:
        return {"success": False, "message": "无效的会话ID"}
    
    # 筛选订单
    filtered_orders = mock_orders
    
    if status:
        filtered_orders = [order for order in filtered_orders if order["status"] == status]
    
    # 日期过滤逻辑可以在这里添加...
    
    return {
        "success": True,
        "data": filtered_orders
    }

@router.get("/trades", response_model=Dict)
async def get_trades(session_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None):
    """获取成交列表"""
    if session_id not in active_sessions:
        return {"success": False, "message": "无效的会话ID"}
    
    # 模拟成交数据 - 从已成交的订单生成
    trades = []
    for order in mock_orders:
        if order["traded_volume"] > 0:
            trades.append({
                "trade_id": f"trade_{order['order_id']}",
                "order_id": order["order_id"],
                "symbol": order["symbol"],
                "name": order["name"],
                "price": order["price"],
                "volume": order["traded_volume"],
                "direction": order["direction"],
                "trade_time": order["submit_time"]  # 简化处理,实际应不同
            })
    
    return {
        "success": True,
        "data": trades
    }

@router.get("/quotes", response_model=Dict)
async def get_quotes(session_id: str, symbols: str):
    """获取实时行情"""
    if session_id not in active_sessions:
        return {"success": False, "message": "无效的会话ID"}
    
    # 解析股票代码
    symbol_list = [s.strip() for s in symbols.split(",") if s.strip()]
    
    # 生成模拟行情数据
    quotes = {}
    mock_prices = {
        "600519": 1826.50,
        "000858": 185.20,
        "601318": 45.67,
        "600036": 38.22
    }
    
    for symbol in symbol_list:
        if symbol in mock_prices:
            quotes[symbol] = {
                "symbol": symbol,
                "price": mock_prices[symbol],
                "open": mock_prices[symbol] * 0.99,
                "high": mock_prices[symbol] * 1.02,
                "low": mock_prices[symbol] * 0.98,
                "volume": 1000000,
                "amount": mock_prices[symbol] * 1000000,
                "last_close": mock_prices[symbol] * 0.995
            }
    
    return {
        "success": True,
        "data": quotes
    }

@router.get("/balance/history", response_model=Dict)
async def get_balance_history(session_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None):
    """获取账户余额历史变化记录"""
    if session_id not in active_sessions:
        return {"success": False, "message": "无效的会话ID"}
    
    # 生成模拟数据
    if not mock_balance_history:
        # 设置默认日期范围为过去30天
        end_date_obj = datetime.now()
        if end_date:
            try:
                end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                pass
        
        start_date_obj = end_date_obj - timedelta(days=30)
        if start_date:
            try:
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                pass
        
        # 生成每一天1-3条记录
        current_date = start_date_obj
        while current_date <= end_date_obj:
            # 每天生成1-3条记录
            for _ in range(random.randint(1, 3)):
                # 随机交易时间(9:30-15:00)
                trade_hour = random.randint(9, 14)
                trade_minute = random.randint(0, 59)
                if trade_hour == 9 and trade_minute < 30:
                    trade_minute = 30 + random.randint(0, 29)
                
                trade_time = current_date.replace(hour=trade_hour, minute=trade_minute)
                
                # 随机交易类型
                is_buy = random.random() > 0.5
                
                # 随机股票
                stock_index = random.randint(0, len(mock_positions) - 1)
                stock = mock_positions[stock_index]
                
                # 随机交易量
                volume = random.randint(100, 1000)
                # 随机价格波动
                price_change = (random.random() - 0.5) * 0.05  # ±2.5%
                price = stock["current_price"] * (1 + price_change)
                
                # 计算交易金额
                amount = price * volume
                
                # 计算费用
                commission_rate = 0.0003  # 佣金费率
                transfer_fee_rate = 0.00002  # 过户费费率(上交所)
                stamp_duty_rate = 0.001  # 印花税(卖出时收取)
                
                commission = max(amount * commission_rate, 5)  # 佣金最低5元
                transfer_fee = 0
                if stock["symbol"].startswith("6"):  # 上海股票
                    transfer_fee = max(amount * transfer_fee_rate, 1)  # 过户费最低1元
                
                stamp_duty = 0
                if not is_buy:
                    stamp_duty = amount * stamp_duty_rate
                
                total_fee = commission + transfer_fee + stamp_duty
                
                # 计算余额变化
                balance_change = -amount - total_fee if is_buy else amount - total_fee
                
                # 生成记录
                mock_balance_history.append({
                    "id": f"record_{len(mock_balance_history) + 1}",
                    "time": int(trade_time.timestamp() * 1000),
                    "balance": balance_change,
                    "tradeId": f"trade_{int(trade_time.timestamp())}",
                    "type": "BUY" if is_buy else "SELL",
                    "symbol": stock["symbol"],
                    "name": stock["name"],
                    "price": round(price, 2),
                    "volume": volume,
                    "description": f"{'买入' if is_buy else '卖出'} {stock['name']}({stock['symbol']}) {volume}股",
                    "fees": {
                        "total": round(total_fee, 2),
                        "stampDuty": round(stamp_duty, 2),
                        "commission": round(commission, 2),
                        "transferFee": round(transfer_fee, 2)
                    }
                })
            
            # 下一天
            current_date += timedelta(days=1)
    
    # 按时间戳排序
    sorted_history = sorted(mock_balance_history, key=lambda x: x["time"], reverse=True)
    
    # 如果指定了日期范围,进行过滤
    if start_date or end_date:
        filtered_history = []
        start_timestamp = None
        end_timestamp = None
        
        if start_date:
            try:
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
                start_timestamp = int(start_date_obj.timestamp() * 1000)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
                end_date_obj = end_date_obj.replace(hour=23, minute=59, second=59)
                end_timestamp = int(end_date_obj.timestamp() * 1000)
            except ValueError:
                pass
        
        for record in sorted_history:
            include = True
            if start_timestamp and record["time"] < start_timestamp:
                include = False
            if end_timestamp and record["time"] > end_timestamp:
                include = False
            
            if include:
                filtered_history.append(record)
        
        sorted_history = filtered_history
    
    return {
        "success": True,
        "data": sorted_history
    }

# WebSocket连接以获取实时数据
@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket连接获取实时行情和委托状态更新"""
    await websocket.accept()
    
    if session_id not in active_sessions:
        await websocket.send_text(json.dumps({
            "success": False,
            "message": "无效的会话ID"
        }))
        await websocket.close()
        return
    
    try:
        while True:
            # 模拟定期发送更新
            await asyncio.sleep(2)
            
            # 模拟数据变化
            for position in mock_positions:
                # 随机价格波动
                price_change = position["current_price"] * (0.98 + 0.04 * time.time() % 1)
                position["current_price"] = round(price_change, 2)
                position["market_value"] = round(position["current_price"] * position["volume"], 2)
                position["profit_loss"] = round(position["market_value"] - position["cost_price"] * position["volume"], 2)
                position["profit_loss_ratio"] = round(position["profit_loss"] / (position["cost_price"] * position["volume"]), 4)
            
            # 更新账户总资产
            total_market_value = sum(p["market_value"] for p in mock_positions)
            mock_account_info["market_value"] = total_market_value
            mock_account_info["total_assets"] = mock_account_info["balance"] + total_market_value
            
            # 发送更新
            await websocket.send_text(json.dumps({
                "type": "update",
                "data": {
                    "account": mock_account_info,
                    "positions": mock_positions
                }
            }))
            
    except WebSocketDisconnect:
        # 客户端断开连接
        pass
    except Exception as e:
        logging.error(f"WebSocket异常: {str(e)}")
        await websocket.close() 
