# 暂时注释掉有依赖问题的导入
# from .strategy_optimizer import StrategyOptimizer
# from .agent_system import TradingAgent, AgentAPI
# from .market_analyzer import MarketAnalyzer
# from .decision_engine import DecisionEngine
# from .risk_manager import RiskManager
# from .strategy_fusion import StrategyFusion
# from .agent_api import AgentWebAPI
# from .learning_manager import LearningManager
# from .reinforcement_learning import DeepQLearner, A2CLearner, FeatureExtractor
# from .experience_memory import ExperienceMemory

# 只导入核心的Agent交易器
try:
    from .agent_hotkey_trader import AgentHotkeyTrader
except ImportError:
    AgentHotkeyTrader = None

# 尝试导入其他AI组件
try:
    from .agent_system import TradingAgent, AgentAPI
except ImportError:
    TradingAgent = None
    AgentAPI = None

try:
    from .agent_api import AgentWebAPI
except ImportError:
    AgentWebAPI = None

# Add version and author information
__version__ = '1.0.0'
__author__ = 'AI Trading System' 
