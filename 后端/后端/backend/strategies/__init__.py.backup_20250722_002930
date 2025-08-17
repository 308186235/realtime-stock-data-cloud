import logging
# 基础策略类
try:
    from .base_strategy import BaseStrategy
except ImportError:
    BaseStrategy = None

# 导入所有策略类，使用try-except处理导入错误
try:
    from .ma_cross import MACrossStrategy
except ImportError:
    MACrossStrategy = None

try:
    from .rsi_strategy import RSIStrategy
except ImportError:
    RSIStrategy = None

try:
    from .bollinger_bands import BollingerBandsStrategy
except ImportError:
    BollingerBandsStrategy = None

try:
    from .risk_control_strategy import RiskControlStrategy
except ImportError:
    RiskControlStrategy = None

try:
    from .trading_checklist import TradingChecklistStrategy
except ImportError:
    TradingChecklistStrategy = None

try:
    from .end_of_day_selection_strategy import EndOfDaySelectionStrategy
except ImportError:
    EndOfDaySelectionStrategy = None

try:
    from .dark_cloud_cover_strategy import DarkCloudCoverStrategy
except ImportError:
    DarkCloudCoverStrategy = None

try:
    from .morning_star_strategy import MorningStarStrategy
except ImportError:
    MorningStarStrategy = None

try:
    from .triple_crash_strategy import TripleCrashStrategy
except ImportError:
    TripleCrashStrategy = None

try:
    from .rising_obstacle_strategy import RisingObstacleStrategy
except ImportError:
    RisingObstacleStrategy = None

try:
    from .rising_obstacle_detector import RisingObstacleDetector
except ImportError:
    RisingObstacleDetector = None

try:
    from .three_white_soldiers_strategy import ThreeWhiteSoldiersStrategy
except ImportError:
    ThreeWhiteSoldiersStrategy = None

try:
    from .top_three_ducks_strategy import TopThreeDucksStrategy
except ImportError:
    TopThreeDucksStrategy = None

try:
    from .double_green_parallel_strategy import DoubleGreenParallelStrategy
except ImportError:
    DoubleGreenParallelStrategy = None

try:
    from .sentiment_strategy import SentimentStrategy
except ImportError:
    SentimentStrategy = None

try:
    from .three_black_crows_strategy import ThreeBlackCrowsStrategy
except ImportError:
    ThreeBlackCrowsStrategy = None

try:
    from .rising_separation_strategy import RisingSeparationStrategy
except ImportError:
    RisingSeparationStrategy = None

try:
    from .inverted_three_red_strategy import InvertedThreeRedStrategy
except ImportError:
    InvertedThreeRedStrategy = None

try:
    from .red_three_soldiers_strategy import RedThreeSoldiersStrategy
except ImportError:
    RedThreeSoldiersStrategy = None

try:
    from .double_black_crows_strategy import DoubleBlackCrowsStrategy
except ImportError:
    DoubleBlackCrowsStrategy = None

try:
    from .double_black_crows_detector import DoubleBlackCrowsDetector
except ImportError:
    DoubleBlackCrowsDetector = None

logger = logging.getLogger(__name__)

# Strategy registry - 只包含成功导入的策略
STRATEGY_REGISTRY = {}

# 动态添加成功导入的策略
if MACrossStrategy:
    STRATEGY_REGISTRY['ma_cross'] = MACrossStrategy
if RSIStrategy:
    STRATEGY_REGISTRY['rsi'] = RSIStrategy
if BollingerBandsStrategy:
    STRATEGY_REGISTRY['bollinger_bands'] = BollingerBandsStrategy
if RiskControlStrategy:
    STRATEGY_REGISTRY['risk_control'] = RiskControlStrategy
if TradingChecklistStrategy:
    STRATEGY_REGISTRY['trading_checklist'] = TradingChecklistStrategy
if EndOfDaySelectionStrategy:
    STRATEGY_REGISTRY['eod_selection'] = EndOfDaySelectionStrategy
if DarkCloudCoverStrategy:
    STRATEGY_REGISTRY['dark_cloud_cover'] = DarkCloudCoverStrategy
if MorningStarStrategy:
    STRATEGY_REGISTRY['morning_star'] = MorningStarStrategy
if TripleCrashStrategy:
    STRATEGY_REGISTRY['triple_crash'] = TripleCrashStrategy
if RisingObstacleStrategy:
    STRATEGY_REGISTRY['rising_obstacle'] = RisingObstacleStrategy
if ThreeWhiteSoldiersStrategy:
    STRATEGY_REGISTRY['three_white_soldiers'] = ThreeWhiteSoldiersStrategy
if TopThreeDucksStrategy:
    STRATEGY_REGISTRY['top_three_ducks'] = TopThreeDucksStrategy
if DoubleGreenParallelStrategy:
    STRATEGY_REGISTRY['double_green_parallel'] = DoubleGreenParallelStrategy
if SentimentStrategy:
    STRATEGY_REGISTRY['sentiment'] = SentimentStrategy
if ThreeBlackCrowsStrategy:
    STRATEGY_REGISTRY['three_black_crows'] = ThreeBlackCrowsStrategy
if RisingSeparationStrategy:
    STRATEGY_REGISTRY['rising_separation'] = RisingSeparationStrategy
if InvertedThreeRedStrategy:
    STRATEGY_REGISTRY['inverted_three_red'] = InvertedThreeRedStrategy
if RedThreeSoldiersStrategy:
    STRATEGY_REGISTRY['red_three_soldiers'] = RedThreeSoldiersStrategy
if DoubleBlackCrowsStrategy:
    STRATEGY_REGISTRY['double_black_crows'] = DoubleBlackCrowsStrategy

def get_strategy(strategy_name, parameters=None):
    """
    Factory function to get a strategy instance by name
    
    Args:
        strategy_name (str): Name of the strategy
        parameters (dict, optional): Strategy parameters
        
    Returns:
        BaseStrategy: Strategy instance
    """
    if strategy_name not in STRATEGY_REGISTRY:
        logger.error(f"Unknown strategy: {strategy_name}")
        raise ValueError(f"Unknown strategy: {strategy_name}")
    
    strategy_class = STRATEGY_REGISTRY[strategy_name]
    return strategy_class(parameters)

def list_available_strategies():
    """
    Get a list of available strategies with descriptions
    
    Returns:
        list: List of available strategies
    """
    strategies = []
    for name, strategy_class in STRATEGY_REGISTRY.items():
        instance = strategy_class()
        strategies.append({
            'name': name,
            'title': instance.name,
            'description': instance.description
        })
    return strategies

def get_strategy_details(strategy_name):
    """
    Get details for a specific strategy
    
    Args:
        strategy_name (str): Name of the strategy
        
    Returns:
        dict: Strategy details including parameters
    """
    if strategy_name not in STRATEGY_REGISTRY:
        logger.error(f"Unknown strategy: {strategy_name}")
        raise ValueError(f"Unknown strategy: {strategy_name}")
    
    strategy_class = STRATEGY_REGISTRY[strategy_name]
    instance = strategy_class()
    
    return {
        'name': strategy_name,
        'title': instance.name,
        'description': instance.description,
        'default_parameters': instance.get_default_parameters(),
        'parameter_ranges': instance.get_parameter_ranges()
    }

def backtest_strategy(strategy_name, data, parameters=None, initial_capital=10000.0):
    """
    Backtest a strategy with the given data and parameters
    
    Args:
        strategy_name (str): Name of the strategy
        data (pd.DataFrame): Historical data
        parameters (dict, optional): Strategy parameters
        initial_capital (float): Initial capital
        
    Returns:
        dict: Backtest results
    """
    strategy = get_strategy(strategy_name, parameters)
    return strategy.backtest(data, initial_capital)

class StrategyFactory:
    """Factory class for creating and managing trading strategies."""
    
    # Available strategies for end-of-day selection
    EOD_STRATEGIES = {
        'base': "基础尾盘策略 - 基于量价关系和技术指标",
        'guocheng': "国诚投顾策略 - 尾盘资金动向和技术指标共振",
        'zhinanzhen': "指南针策略 - 红锦鲤摆尾,尾盘回踩均线后快速拉升",
        'tn6': "尾盘选股王(tn6)策略 - 结合资金流,技术指标和新闻事件",
        'jingchuan': "经传短线策略 - 捕捞季节和主力追踪指标共振",
        'qiankun': "乾坤六道策略 - 六大道指标共振",
        'jiufang': "九方智投策略 - 尾盘K线形态与量价关系"
    }
    
    @staticmethod
    def get_strategy(strategy_id, parameters=None):
        """
        Get a strategy instance by ID.
        
        Args:
            strategy_id (str): Strategy identifier
            parameters (dict, optional): Strategy parameters
            
        Returns:
            BaseStrategy: Strategy instance
        
        Raises:
            ValueError: If strategy ID is not recognized
        """
        if strategy_id == 'ma_cross':
            return MACrossStrategy(parameters)
        elif strategy_id == 'rsi_strategy':
            return RSIStrategy(parameters)
        elif strategy_id == 'bollinger_bands':
            return BollingerBandsStrategy(parameters)
        elif strategy_id == 'end_of_day_selection':
            return EndOfDaySelectionStrategy(parameters)
        elif strategy_id == 'rising_obstacle':
            return RisingObstacleStrategy(parameters)
        elif strategy_id == 'double_black_crows':
            return DoubleBlackCrowsStrategy(parameters)
        else:
            raise ValueError(f"Unknown strategy ID: {strategy_id}")
    
    @staticmethod
    def get_all_strategies():
        """
        Get all available strategies.
        
        Returns:
            list: List of strategy instances with default parameters
        """
        return [
            MACrossStrategy(),
            RSIStrategy(),
            BollingerBandsStrategy(),
            EndOfDaySelectionStrategy(),
            RisingObstacleStrategy(),
            DoubleBlackCrowsStrategy()
        ]
    
    @staticmethod
    def get_strategy_info(strategy_id):
        """
        Get information about a strategy.
        
        Args:
            strategy_id (str): Strategy identifier
            
        Returns:
            dict: Strategy information including name, description, and parameters
            
        Raises:
            ValueError: If strategy ID is not recognized
        """
        strategy = StrategyFactory.get_strategy(strategy_id)
        
        return {
            'id': strategy_id,
            'name': strategy.name,
            'description': strategy.description,
            'parameters': strategy.get_default_parameters(),
            'parameter_ranges': strategy.get_parameter_ranges()
        }
    
    @staticmethod
    def get_all_strategies_info():
        """
        Get information about all available strategies.
        
        Returns:
            list: List of strategy information dictionaries
        """
        strategies = [
            {'id': 'ma_cross', 'strategy': MACrossStrategy()},
            {'id': 'rsi_strategy', 'strategy': RSIStrategy()},
            {'id': 'bollinger_bands', 'strategy': BollingerBandsStrategy()},
            {'id': 'end_of_day_selection', 'strategy': EndOfDaySelectionStrategy()},
            {'id': 'rising_obstacle', 'strategy': RisingObstacleStrategy()},
            {'id': 'double_black_crows', 'strategy': DoubleBlackCrowsStrategy()}
        ]
        
        return [
            {
                'id': s['id'],
                'name': s['strategy'].name,
                'description': s['strategy'].description,
                'parameters': s['strategy'].get_default_parameters(),
                'parameter_ranges': s['strategy'].get_parameter_ranges()
            }
            for s in strategies
        ]
    
    @staticmethod
    def get_eod_strategies():
        """
        Get all available end-of-day selection strategies.
        
        Returns:
            dict: Dictionary of strategy IDs and descriptions
        """
        return StrategyFactory.EOD_STRATEGIES 
