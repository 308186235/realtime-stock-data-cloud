from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
import logging
import os
from fastapi.middleware.cors import CORSMiddleware
import sys
import asyncio

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入路由模块 - 使用try-except处理导入错误
try:
    from backend.api.routers import auth
except ImportError as e:
    print(f"警告: 无法导入auth路由: {e}")
    auth = None

try:
    from backend.api.routers import backtesting
except ImportError as e:
    print(f"警告: 无法导入backtesting路由: {e}")
    backtesting = None

try:
    from backend.api import agent_trading_api
except ImportError as e:
    print(f"警告: 无法导入agent_trading_api: {e}")
    agent_trading_api = None

try:
    from backend.middleware.security import setup_security_middleware
except ImportError as e:
    print(f"警告: 无法导入security中间件: {e}")
    setup_security_middleware = None

# 导入Agent系统 - 使用try-except处理导入错误
try:
    from backend.ai.agent_system import TradingAgent
except ImportError as e:
    print(f"警告: 无法导入TradingAgent: {e}")
    TradingAgent = None

try:
    from backend.ai.agent_api import AgentWebAPI
except ImportError as e:
    print(f"警告: 无法导入AgentWebAPI: {e}")
    AgentWebAPI = None

try:
    from backend.ai.learning_manager import LearningManager
except ImportError as e:
    print(f"警告: 无法导入LearningManager: {e}")
    LearningManager = None

try:
    from backend.ai.experience_memory import ExperienceMemory
except ImportError as e:
    print(f"警告: 无法导入ExperienceMemory: {e}")
    ExperienceMemory = None

try:
    from backend.ai.reinforcement_learning import DeepQLearner, FeatureExtractor
except ImportError as e:
    print(f"警告: 无法导入强化学习组件: {e}")
    DeepQLearner = None
    FeatureExtractor = None

try:
    from backend.ai.meta_learning import MetaLearner, AdaptiveStrategySelector
except ImportError as e:
    print(f"警告: 无法导入元学习组件: {e}")
    MetaLearner = None
    AdaptiveStrategySelector = None

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="智能交易Agent系统",
    description="基于强化学习的自主交易Agent系统API",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# 设置安全中间件
setup_security_middleware(app)

# 初始化Agent系统组件
agent_components = {}

# 创建学习管理器
if LearningManager:
    try:
        learning_manager = LearningManager(config={
            "experience_buffer_size": 1000,
            "learning_rate": 0.01,
            "batch_size": 64
        })
        agent_components["learning_manager"] = learning_manager
    except Exception as e:
        print(f"警告: 创建学习管理器失败: {e}")

# 创建经验记忆库
experience_memory = ExperienceMemory({
    "memory_limit": 1000,
    "use_db": True,
    "db_path": "data/experience.db"
})
agent_components["experience_memory"] = experience_memory

# 创建特征提取器
feature_extractor = FeatureExtractor()
agent_components["feature_extractor"] = feature_extractor

# 创建DQN学习器
dqn_learner = DeepQLearner({
    "learning_rate": 0.001,
    "batch_size": 64,
    "state_dim": 20,
    "action_dim": 3,
    "models_dir": "models"
})
agent_components["dqn_learner"] = dqn_learner

# 创建元学习器
meta_learner = MetaLearner({"models_dir": "models"})
agent_components["meta_learner"] = meta_learner

# 创建自适应策略选择器
strategy_selector = AdaptiveStrategySelector()
agent_components["strategy_selector"] = strategy_selector

# 创建Trading Agent
agent_config = {
    "name": "TradingAgent",
    "loop_interval": 10,
    "monitor_interval": 5,
    "components": agent_components
}
trading_agent = TradingAgent(config=agent_config)

# 创建Agent API
agent_api = AgentWebAPI(
    agent=trading_agent,
    host="0.0.0.0",
    port=8000,
    debug=False
)

# 添加路由
app.include_router(auth.router, prefix="/api")
app.include_router(backtesting.router, prefix="/api")
app.include_router(agent_api.router, prefix="/api/agent", tags=["agent"])
app.include_router(agent_trading_api.router, prefix="/api", tags=["agent-trading"])

# 导入并添加虚拟账户路由
from .api.routers import virtual_account
app.include_router(virtual_account.router, tags=["虚拟账户"])

# 挂载静态文件
# 检查静态文件目录是否存在
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../frontend/dist")
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
    logger.info(f"静态文件已挂载: {static_dir}")
else:
    logger.warning(f"静态文件目录不存在: {static_dir}")

@app.on_event("startup")
async def startup_event():
    """启动时执行的事件"""
    logger.info("智能交易Agent系统启动")
    
    # 启动Agent
    try:
        await trading_agent.start()
        logger.info("Trading Agent已启动")
    except Exception as e:
        logger.error(f"启动Trading Agent失败: {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    """关闭时执行的事件"""
    logger.info("智能交易Agent系统关闭")
    
    # 停止Agent
    try:
        await trading_agent.stop()
        logger.info("Trading Agent已停止")
    except Exception as e:
        logger.error(f"停止Trading Agent失败: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    # 启动服务器
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 
