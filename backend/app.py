import os
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
import json

# Internal imports
from config import settings
from api.routers import strategy, portfolio, stock, ai, backtest, market_tracker, auto_trader
from api.routers.enhanced_analysis import router as enhanced_analysis_router
from api.routers.supabase_portfolio import router as supabase_portfolio_router
from api.routers.realtime_stock_simple import router as realtime_stock_router
from api.routers.realtime_data_api import router as realtime_data_router
from api.routers.technical_indicators_api import router as technical_indicators_router
from api.trading_api import router as trading_router
from api.t_trading_api import router as t_trading_router
from api.test_endpoint import router as test_router  # 瀵煎叆娴嬭瘯璺敱
from api.end_of_day_selection_api import router as eod_selection_router  # 瀵煎叆灏剧洏閫夎偂璺敱
from services.websocket_manager import ConnectionManager
from services.market_data_service import MarketDataService
from services.trading_service import TradingService
from services.ai_service import AIService
from services.backtest_service import BacktestService
from services.market_tracker_service import MarketTrackerService
from services.rapid_response_service import RapidResponseService
from services.auto_trader_service import AutoTraderService
from services.ai_t_trading_service import AITTradingService
from services.end_of_day_selection_service import EndOfDaySelectionService
from services.realtime_data_manager import realtime_data_manager
from strategies import StrategyFactory  # Import the StrategyFactory

# Load environment variables
load_dotenv()

# Configure logging
os.makedirs("logs", exist_ok=True)  # 确保logs目录存在
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Stock Trading System API",
    description="API for automatic stock trading system",
    version="1.0.0"
)

# Configure CORS
origins = [
    "http://localhost:8080",     # Uni-app dev server
    "http://localhost:3000",     # Alternate frontend dev server
    "http://localhost",
    "https://localhost",
    "http://localhost:9000",     # Uni-app preview server
    "capacitor://localhost",     # For mobile app
    "ionic://localhost",
    "https://aigupiao.me",       # Production domain
    "http://aigupiao.me",        # Production domain (HTTP fallback)
    "*"                          # Allow all origins in development (remove in production)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
market_data_service = MarketDataService()
trading_service = TradingService()
ai_service = AIService()
backtest_service = BacktestService()
auto_trader_service = AutoTraderService()
market_tracker_service = MarketTrackerService(ai_service=ai_service, auto_trader_service=auto_trader_service)
rapid_response_service = RapidResponseService()
ws_manager = ConnectionManager()
ai_t_trading_service = AITTradingService()  # Initialize AI T Trading Service
eod_selection_service = EndOfDaySelectionService()  # Initialize EOD Selection Service

# Basic health check endpoint
@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "message": "APP API服务正常",
        "timestamp": datetime.now().isoformat(),
        "api_version": "1.0",
        "app_support": True,
        "service": "stock-trading-backend"
    }

@app.get("/api/health")
async def api_health_check():
    """API健康检查端点"""
    return {
        "status": "healthy",
        "message": "APP API服务正常",
        "timestamp": datetime.now().isoformat(),
        "api_version": "1.0",
        "app_support": True,
        "service": "stock-trading-backend"
    }

# Include routers - Updated to use Supabase-integrated routers
app.include_router(strategy.router, prefix="/api/strategy", tags=["strategy"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["portfolio"])  # Updated with Supabase
app.include_router(supabase_portfolio_router, prefix="/api/supabase", tags=["supabase-portfolio"])
app.include_router(realtime_stock_router, prefix="/api/realtime", tags=["realtime-stock"])
app.include_router(realtime_data_router, prefix="/api/realtime-data", tags=["realtime-data"])  # 新的实时数据API
app.include_router(technical_indicators_router, prefix="/api/technical", tags=["technical-indicators"])  # 技术指标API
app.include_router(stock.router, prefix="/api/stock", tags=["stock"])  # Updated with Supabase
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])
app.include_router(backtest.router, prefix="/api/backtest", tags=["backtest"])
app.include_router(market_tracker.router, prefix="/api/market-tracker", tags=["market-tracker"])
app.include_router(auto_trader.router, prefix="/api/auto-trader", tags=["auto-trader"])
app.include_router(trading_router, prefix="/api", tags=["trading"])
app.include_router(t_trading_router, tags=["t-trading"])
app.include_router(test_router, tags=["娴嬭瘯"])  # 娉ㄥ唽娴嬭瘯璺敱
app.include_router(eod_selection_router, tags=["灏剧洏閫夎偂"])  # 娉ㄥ唽灏剧洏閫夎偂璺敱

# WebSocket connection for real-time data
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Process received data
            logger.info(f"Received data: {data}")
            
            # Here we would process commands from the frontend
            # For example, subscribing to specific stock updates
            
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

# WebSocket connection for rapid response service
@app.websocket("/rapid-ws/{client_id}")
async def rapid_websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    try:
        # 娉ㄥ唽WebSocket杩炴帴
        await rapid_response_service.register_websocket(client_id, websocket)
        
        # 鍙戦€佺‘璁ゆ秷鎭?
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "client_id": client_id,
            "message": "宸茶繛鎺ュ埌蹇€熷搷搴旀湇鍔?"
        })
        
        # 鍙戦€佹渶杩戠殑淇彿
        recent_signals = await rapid_response_service.get_recent_signals(limit=5)
        if recent_signals:
            await websocket.send_json({
                "type": "recent_signals",
                "signals": recent_signals
            })
        
        # 澶勭悊鏉ヨ嚜瀹㈡埛绔殑娑堟伅
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                
                # 鏍规嵁娑堟伅绫诲瀷澶勭悊
                if message.get("type") == "quick_update":
                    # 澶勭悊蹇€熸洿鏂拌姹?                    if "tracker_id" in message:
                        tracker_id = message["tracker_id"]
                        # 鑾峰彇缂撳瓨鏁版嵁鎴栨墽琛屽揩閫熸洿鏂?                        cached_data = await rapid_response_service.get_cached_data(f"tracker_{tracker_id}")
                        
                        if cached_data:
                            # 鍙戦€佺紦瀛樻暟鎹?
                            await websocket.send_json({
                                "type": "update",
                                "source": "cache",
                                "data": cached_data
                            })
                        else:
                            # 执行蹇€熸洿鏂板苟缂撳瓨缁撴灉
                            result = await market_tracker_service.update_tracker(tracker_id)
                            await rapid_response_service.cache_data(f"tracker_{tracker_id}", result)
                            
                            # 鍙戦€佹洿鏂扮粨鏋?
                            await websocket.send_json({
                                "type": "update",
                                "source": "fresh",
                                "data": result
                            })
                
                elif message.get("type") == "process_signal":
                    # 澶勭悊淇彿璇锋眰
                    if "signal" in message:
                        signal_data = message["signal"]
                        result = await rapid_response_service.process_trading_signal(signal_data)
                        
                        # 鍙戦€佸鐞嗙粨鏋?
                        await websocket.send_json({
                            "type": "signal_processed",
                            "result": result
                        })
                
            except json.JSONDecodeError:
                logger.error(f"鏃犳晥鐨凧SON娑堟伅: {data}")
            except Exception as e:
                logger.error(f"澶勭悊WebSocket娑堟伅鏃跺嚭閿? {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })
    
    except WebSocketDisconnect:
        # 娉ㄩ攢WebSocket杩炴帴
        await rapid_response_service.unregister_websocket(client_id)
        logger.info(f"WebSocket瀹㈡埛绔柇寮€杩炴帴: {client_id}")
    
    except Exception as e:
        logger.error(f"WebSocket澶勭悊鏃跺嚭閿? {e}")
        try:
            # 娉ㄩ攢WebSocket杩炴帴
            await rapid_response_service.unregister_websocket(client_id)
        except:
            pass

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up the application...")

    # 暂时注释掉定时任务，避免启动错误
    # TODO: 修复MarketDataService和其他服务的方法

    logger.info("Application startup completed")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down the application...")
    
    # Stop the EOD selection scheduler
    await eod_selection_service.stop_scheduler()
    logger.info("End-of-day selection scheduler stopped")


app.include_router(enhanced_analysis_router, prefix="/api/enhanced-analysis", tags=["enhanced-analysis"])

# 应用启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化"""
    try:
        # 启动实时数据管理器
        await realtime_data_manager.start()
        logger.info("实时数据管理器已启动")

        # 启动原有的实时数据模拟（作为备用）
        try:
            from api.routers.realtime_stock_simple import start_simulation
            await start_simulation()
            logger.info("备用实时数据模拟已启动")
        except Exception as e:
            logger.warning(f"备用实时数据模拟启动失败: {str(e)}")

    except Exception as e:
        logger.error(f"启动事件失败: {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的清理"""
    try:
        # 停止实时数据管理器
        await realtime_data_manager.stop()
        logger.info("实时数据管理器已停止")

        # 停止原有的实时数据模拟
        try:
            from api.routers.realtime_stock_simple import stop_simulation
            await stop_simulation()
            logger.info("备用实时数据模拟已停止")
        except Exception as e:
            logger.warning(f"备用实时数据模拟停止失败: {str(e)}")

    except Exception as e:
        logger.error(f"关闭事件失败: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    import os
    PORT = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=PORT,
        log_level="info",
        access_log=True
    )

