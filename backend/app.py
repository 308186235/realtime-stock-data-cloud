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
from api.trading_api import router as trading_router
from api.t_trading_api import router as t_trading_router
from api.test_endpoint import router as test_router  # 瀵煎叆娴嬭瘯璺敱
from api.end_of_day_selection_api import router as eod_selection_router  # 瀵煎叆灏剧洏閫夎偂璺敱
from services.websocket_manager import ConnectionManager
from services.market_data import MarketDataService
from services.trading_service import TradingService
from services.ai_service import AIService
from services.backtest_service import BacktestService
from services.market_tracker_service import MarketTrackerService
from services.rapid_response_service import RapidResponseService
from services.auto_trader_service import AutoTraderService
from services.ai_t_trading_service import AITTradingService
from services.end_of_day_selection_service import EndOfDaySelectionService
from strategies import StrategyFactory  # Import the StrategyFactory

# Load environment variables
load_dotenv()

# Configure logging
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

# Include routers
app.include_router(strategy.router, prefix="/api/strategy", tags=["strategy"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["portfolio"])
app.include_router(stock.router, prefix="/api/stock", tags=["stock"])
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
    
    # Initialize the scheduler for scheduled tasks
    scheduler = BackgroundScheduler()
    
    # Schedule market data updates
    scheduler.add_job(
        market_data_service.update_market_data, 
        'interval', 
        minutes=5, 
        id='market_data_update'
    )
    
    # Schedule market tracker updates
    scheduler.add_job(
        market_tracker_service.update_all_trackers,
        'interval',
        minutes=15,
        id='tracker_update'
    )
    
    # Start EOD selection scheduler
    await eod_selection_service.start_scheduler()
    logger.info("End-of-day selection scheduler started")
    
    # Start the scheduler
    scheduler.start()
    logger.info("Scheduler started")
    
    # Load initial data
    await market_data_service.initialize()
    logger.info("Market data service initialized")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down the application...")
    
    # Stop the EOD selection scheduler
    await eod_selection_service.stop_scheduler()
    logger.info("End-of-day selection scheduler stopped")


app.include_router(enhanced_analysis_router, prefix="/api/enhanced-analysis", tags=["enhanced-analysis"])  # 注册增强分析路由

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

