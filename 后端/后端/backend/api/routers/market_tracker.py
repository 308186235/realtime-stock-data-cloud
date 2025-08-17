from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import logging
import json
import asyncio

# Import services
from services.market_tracker_service import MarketTrackerService

# ******************************************************************************
# NOTE: This API router is essential for the AI trading system and is actively used
# even though the dedicated "市场追踪" frontend UI has been removed. These endpoints
# provide access to market tracking data that is used by the AI analysis and trading
# features through the AI Analysis section of the frontend.
# ******************************************************************************

router = APIRouter()
logger = logging.getLogger(__name__)

# Dependency to get market tracker service
def get_market_tracker_service():
    return MarketTrackerService()

# Models for request/response
class StartTrackingRequest(BaseModel):
    stock_code: str
    prediction_days: int = Field(default=10, ge=1, le=30)

class UpdateTrackerRequest(BaseModel):
    tracker_id: str

class StopTrackingRequest(BaseModel):
    tracker_id: str

class AlertThresholdsRequest(BaseModel):
    price_change: Optional[float] = None
    divergence: Optional[float] = None
    accuracy_drop: Optional[float] = None

class SubscribeAlertRequest(BaseModel):
    tracker_id: str
    subscriber_id: str
    alert_types: Optional[List[str]] = None

class UnsubscribeAlertRequest(BaseModel):
    tracker_id: str
    subscriber_id: str

# 实时连接的WebSocket客户端字典
websocket_clients = {}

@router.post("/start")
async def start_tracking(
    request: StartTrackingRequest,
    tracker_service: MarketTrackerService = Depends(get_market_tracker_service)
):
    """
    Start tracking a stock and comparing with AI predictions.
    
    Args:
        request: Tracking request with stock code and prediction days
        
    Returns:
        Tracking initialization result
    """
    logger.info(f"Starting market tracking for {request.stock_code}")
    
    result = await tracker_service.start_tracking(
        request.stock_code,
        request.prediction_days
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
        
    return result

@router.post("/update")
async def update_tracker(
    request: UpdateTrackerRequest,
    tracker_service: MarketTrackerService = Depends(get_market_tracker_service)
):
    """
    Update a tracker with latest market data.
    
    Args:
        request: Update request with tracker ID
        
    Returns:
        Updated tracker data
    """
    logger.info(f"Updating market tracker {request.tracker_id}")
    
    result = await tracker_service.update_tracker(request.tracker_id)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
        
    return result

@router.get("/details/{tracker_id}")
async def get_tracker_details(
    tracker_id: str,
    tracker_service: MarketTrackerService = Depends(get_market_tracker_service)
):
    """
    Get detailed information about a tracker.
    
    Args:
        tracker_id: Tracker ID
        
    Returns:
        Detailed tracker information
    """
    logger.info(f"Getting details for tracker {tracker_id}")
    
    result = await tracker_service.get_tracker_details(tracker_id)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
        
    return result

@router.get("/list")
async def get_active_trackers(
    tracker_service: MarketTrackerService = Depends(get_market_tracker_service)
):
    """
    Get list of all active trackers.
    
    Returns:
        List of active trackers
    """
    logger.info("Getting active market trackers")
    
    result = await tracker_service.get_active_trackers()
    return result

@router.post("/stop")
async def stop_tracking(
    request: StopTrackingRequest,
    tracker_service: MarketTrackerService = Depends(get_market_tracker_service)
):
    """
    Stop tracking a stock.
    
    Args:
        request: Stop request with tracker ID
        
    Returns:
        Result of operation
    """
    logger.info(f"Stopping market tracker {request.tracker_id}")
    
    result = await tracker_service.stop_tracking(request.tracker_id)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
        
    return result

@router.post("/alerts/thresholds")
async def set_alert_thresholds(
    request: AlertThresholdsRequest,
    tracker_service: MarketTrackerService = Depends(get_market_tracker_service)
):
    """
    设置警报阈值。
    
    Args:
        request: 阈值设置请求
        
    Returns:
        更新后的阈值设置
    """
    thresholds = {}
    if request.price_change is not None:
        thresholds["price_change"] = request.price_change
    if request.divergence is not None:
        thresholds["divergence"] = request.divergence
    if request.accuracy_drop is not None:
        thresholds["accuracy_drop"] = request.accuracy_drop
        
    result = await tracker_service.set_alert_thresholds(thresholds)
    return result

@router.post("/alerts/subscribe")
async def subscribe_alerts(
    request: SubscribeAlertRequest,
    tracker_service: MarketTrackerService = Depends(get_market_tracker_service)
):
    """
    订阅特定追踪器的警报。
    
    Args:
        request: 订阅请求
        
    Returns:
        订阅结果
    """
    result = await tracker_service.subscribe_alerts(
        request.tracker_id,
        request.subscriber_id,
        request.alert_types
    )
    
    return result

@router.post("/alerts/unsubscribe")
async def unsubscribe_alerts(
    request: UnsubscribeAlertRequest,
    tracker_service: MarketTrackerService = Depends(get_market_tracker_service)
):
    """
    取消订阅警报。
    
    Args:
        request: 取消订阅请求
        
    Returns:
        操作结果
    """
    result = await tracker_service.unsubscribe_alerts(
        request.tracker_id,
        request.subscriber_id
    )
    
    return result

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    client_id: str,
    tracker_service: MarketTrackerService = Depends(get_market_tracker_service)
):
    """
    WebSocket连接用于实时警报和更新。
    
    Args:
        websocket: WebSocket连接
        client_id: 客户端ID
    """
    await websocket.accept()
    
    try:
        # 存储连接
        websocket_clients[client_id] = websocket
        
        # 发送确认消息
        await websocket.send_json({"type": "connection", "status": "connected", "client_id": client_id})
        
        # 处理来自客户端的消息
        while True:
            # 接收消息
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # 根据消息类型处理
            if message["type"] == "subscribe":
                # 处理订阅请求
                if "tracker_id" in message and "alert_types" in message:
                    result = await tracker_service.subscribe_alerts(
                        message["tracker_id"],
                        client_id,
                        message["alert_types"]
                    )
                    await websocket.send_json({"type": "subscription", "result": result})
            
            elif message["type"] == "update_request":
                # 处理立即更新请求
                if "tracker_id" in message:
                    result = await tracker_service.update_tracker(message["tracker_id"])
                    await websocket.send_json({"type": "update", "result": result})
            
            # 更多消息类型处理...
    
    except WebSocketDisconnect:
        # 断开连接时清理
        if client_id in websocket_clients:
            del websocket_clients[client_id]
        logger.info(f"WebSocket client {client_id} disconnected")
    
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {e}")
        # 尝试发送错误消息
        try:
            if client_id in websocket_clients:
                await websocket.send_json({"type": "error", "message": str(e)})
        except:
            pass
        
        # 清理连接
        if client_id in websocket_clients:
            del websocket_clients[client_id]

@router.post("/quick-update/{tracker_id}")
async def quick_update_tracker(
    tracker_id: str,
    tracker_service: MarketTrackerService = Depends(get_market_tracker_service)
):
    """
    快速更新追踪器数据,优化响应时间。
    
    Args:
        tracker_id: 追踪器ID
        
    Returns:
        更新后的数据
    """
    # 立即响应一个轻量级结果
    # 然后在后台启动完整更新
    tracker = await tracker_service.get_tracker_details(tracker_id)
    
    if "error" in tracker:
        raise HTTPException(status_code=404, detail=tracker["error"])
    
    # 构建快速响应
    quick_response = {
        "tracker_id": tracker_id,
        "stock_code": tracker.get("stock_code", ""),
        "status": "updating",
        "last_update": tracker.get("comparison_metrics", {}).get("last_updated", ""),
    }
    
    # 在后台启动完整更新
    asyncio.create_task(tracker_service.update_tracker(tracker_id))
    
    return quick_response 
