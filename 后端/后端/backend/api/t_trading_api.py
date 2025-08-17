from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import pandas as pd
from datetime import datetime, timedelta

from strategies.t_trading_strategy import TTradingStrategy
from utils.t_trading_utils import TTradingTracker, calculate_t_trade_impact
from services.ai_t_trading_service import AITTradingService, TradingEnvironment

router = APIRouter(prefix="/api/t-trading", tags=["t-trading"])

# 全局实例
t_trading_strategy = TTradingStrategy()
t_trading_tracker = TTradingTracker()
ai_t_trading_service = AITTradingService()  # 新增AI服务实例

# 数据模型
class StockInfo(BaseModel):
    code: str
    name: str
    current_price: float
    open_price: float
    intraday_high: float
    intraday_low: float
    avg_volume: float
    current_volume: float
    base_position: int
    base_cost: float

class TradeRequest(BaseModel):
    stock_code: str
    stock_name: str
    price: float
    quantity: int
    trade_type: str  # 'buy' 或 'sell'
    mode: str = 'positive'  # 'positive' 或 'negative'

class StrategyConfig(BaseModel):
    mode: str = 'auto'
    base_position: int = 100
    max_daily_t_percentage: float = 0.5
    positive_t_buy_threshold: float = -0.02
    positive_t_sell_threshold: float = 0.01
    negative_t_sell_threshold: float = 0.03
    negative_t_buy_threshold: float = -0.01
    time_interval: int = 15
    enable_volume_check: bool = True
    volume_threshold: float = 2.0
    use_ai: bool = True  # 新增是否使用AI的配置

class TradeSummary(BaseModel):
    period: str
    total_trades: int
    success_rate: float
    total_profit: float
    avg_profit_per_trade: float
    positive_t_count: int
    negative_t_count: int
    best_stock: Optional[Dict[str, Any]] = None
    worst_stock: Optional[Dict[str, Any]] = None

class AIStrategySettings(BaseModel):
    enabled: bool = True
    risk_level: str = 'medium'  # 'low', 'medium', 'high'
    auto_trading: bool = False
    confidence_threshold: float = 0.65

class AIExecutionSettings(BaseModel):
    auto_execute: bool = False
    max_trade_amount: float = 10000

# 新增回测配置模型
class BacktestConfig(BaseModel):
    start_date: str
    end_date: str 
    initial_capital: float = 100000.0
    strategy_params: Optional[Dict[str, Any]] = None
    stock_code: str

# 新增环境切换模型
class EnvironmentSetting(BaseModel):
    environment: str  # "backtest" 或 "live"

# API路由
@router.post("/evaluate-opportunity", response_model=Dict[str, Any])
async def evaluate_t_opportunity(stock_info: StockInfo):
    """
    评估是否存在T交易机会
    """
    # 转换为市场数据字典
    market_data = {
        'code': stock_info.code,
        'name': stock_info.name,
        'current_price': stock_info.current_price,
        'open_price': stock_info.open_price,
        'intraday_high': stock_info.intraday_high,
        'intraday_low': stock_info.intraday_low,
        'avg_volume': stock_info.avg_volume,
        'current_volume': stock_info.current_volume,
        'base_position': stock_info.base_position,
        'base_cost': stock_info.base_cost
    }
    
    # 使用AI服务评估(如果enabled = True)
    if t_trading_strategy.parameters.get('use_ai', True):
        opportunity = await ai_t_trading_service.evaluate_opportunity(market_data)
    else:
        # 使用传统规则引擎评估
        opportunity = t_trading_tracker.get_t_opportunity(
            stock_code=stock_info.code,
            current_price=stock_info.current_price,
            intraday_high=stock_info.intraday_high,
            intraday_low=stock_info.intraday_low,
            open_price=stock_info.open_price,
            avg_volume=stock_info.avg_volume,
            current_volume=stock_info.current_volume,
            base_position=stock_info.base_position
        )
    
    # 如果没有预期成本影响分析,添加它
    if opportunity['has_opportunity'] and opportunity['mode'] is not None and 'expected_cost_impact' not in opportunity:
        # 假设一个预期成功的T交易
        mock_trade = {
            'quantity': opportunity.get('suggested_quantity', int(stock_info.base_position * 0.2)),
            'profit': 0  # 先假设利润为0
        }
        
        # 计算预期利润(基于历史平均或阈值)
        expected_profit_rate = 0.005  # 预期0.5%的利润率
        if opportunity['mode'] == 'positive':
            mock_trade['profit'] = mock_trade['quantity'] * stock_info.current_price * expected_profit_rate
        else:
            mock_trade['profit'] = mock_trade['quantity'] * stock_info.current_price * expected_profit_rate
            
        # 计算对成本的影响
        cost_impact = calculate_t_trade_impact(
            stock_info.base_position,
            stock_info.base_cost,
            [mock_trade]
        )
        
        opportunity['expected_cost_impact'] = cost_impact
    
    return opportunity

@router.post("/ai-recommendation", response_model=Dict[str, Any])
async def get_ai_recommendation(stock_info: StockInfo):
    """
    获取AI推荐的交易行动
    """
    try:
        recommendation = await ai_t_trading_service.recommend_trade_action(stock_info.dict())
        return recommendation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI推荐失败: {str(e)}")

@router.post("/auto-trade-decision", response_model=Dict[str, Any])
async def get_auto_trade_decision(
    stock_info: StockInfo, 
    risk_level: str = Query("medium", description="风险等级: low, medium, high")
):
    """
    获取AI自动交易决策
    """
    try:
        # 获取交易历史
        trade_history = await get_trade_history(days=7)
        
        # 获取AI交易决策
        decision = await ai_t_trading_service.auto_trading_decision(
            stock_info.dict(), 
            trade_history, 
            risk_level
        )
        
        return decision
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI决策失败: {str(e)}")

@router.post("/record-trade", response_model=Dict[str, Any])
async def record_t_trade(trade: TradeRequest):
    """
    记录T交易操作
    """
    # 找出匹配的未完成交易
    matching_trades = []
    for t in t_trading_tracker.trades:
        if (t['stock_code'] == trade.stock_code and 
            t['status'] == 'pending' and
            ((trade.trade_type == 'buy' and t['buy_price'] == 0) or 
             (trade.trade_type == 'sell' and t['sell_price'] == 0))):
            matching_trades.append(t)
    
    result = {}
    
    # 如果是买入操作
    if trade.trade_type == 'buy':
        # 检查是否有等待买入的反T交易
        pending_sell = next((t for t in matching_trades if t['trade_type'] == 'sell_only' and t['mode'] == 'negative'), None)
        
        if pending_sell:
            # 完成反T交易
            complete_trade = t_trading_tracker.record_trade(
                trade_type='complete',
                stock_code=trade.stock_code,
                stock_name=trade.stock_name,
                buy_price=trade.price,
                sell_price=pending_sell['sell_price'],
                quantity=min(trade.quantity, pending_sell['quantity']),
                mode='negative'
            )
            result = {"status": "success", "message": "反T交易完成", "trade": complete_trade}
        else:
            # 记录新的买入操作(正T的开始)
            new_trade = t_trading_tracker.record_trade(
                trade_type='buy_only',
                stock_code=trade.stock_code,
                stock_name=trade.stock_name,
                buy_price=trade.price,
                sell_price=0,
                quantity=trade.quantity,
                mode='positive'
            )
            result = {"status": "success", "message": "正T买入记录成功", "trade": new_trade}
    
    # 如果是卖出操作
    elif trade.trade_type == 'sell':
        # 检查是否有等待卖出的正T交易
        pending_buy = next((t for t in matching_trades if t['trade_type'] == 'buy_only' and t['mode'] == 'positive'), None)
        
        if pending_buy:
            # 完成正T交易
            complete_trade = t_trading_tracker.record_trade(
                trade_type='complete',
                stock_code=trade.stock_code,
                stock_name=trade.stock_name,
                buy_price=pending_buy['buy_price'],
                sell_price=trade.price,
                quantity=min(trade.quantity, pending_buy['quantity']),
                mode='positive'
            )
            result = {"status": "success", "message": "正T交易完成", "trade": complete_trade}
        else:
            # 记录新的卖出操作(反T的开始)
            new_trade = t_trading_tracker.record_trade(
                trade_type='sell_only',
                stock_code=trade.stock_code,
                stock_name=trade.stock_name,
                buy_price=0,
                sell_price=trade.price,
                quantity=trade.quantity,
                mode='negative'
            )
            result = {"status": "success", "message": "反T卖出记录成功", "trade": new_trade}
    
    else:
        raise HTTPException(status_code=400, detail="无效的交易类型")
    
    # 保存交易记录
    t_trading_tracker.save_history()
    
    return result

@router.post("/update-strategy-config", response_model=Dict[str, Any])
async def update_strategy_config(config: StrategyConfig):
    """
    更新T交易策略配置
    """
    # 更新策略参数
    t_trading_strategy.parameters.update(config.dict())
    
    return {
        "status": "success",
        "message": "策略配置已更新",
        "config": t_trading_strategy.parameters
    }

@router.post("/update-ai-settings", response_model=Dict[str, Any])
async def update_ai_settings(settings: AIStrategySettings):
    """
    更新AI策略设置
    """
    # 更新AI设置
    t_trading_strategy.parameters['use_ai'] = settings.enabled
    t_trading_strategy.parameters['ai_risk_level'] = settings.risk_level
    t_trading_strategy.parameters['ai_auto_trading'] = settings.auto_trading
    t_trading_strategy.parameters['ai_confidence_threshold'] = settings.confidence_threshold
    
    return {
        "status": "success",
        "message": "AI策略设置已更新",
        "settings": {
            "enabled": settings.enabled,
            "risk_level": settings.risk_level,
            "auto_trading": settings.auto_trading,
            "confidence_threshold": settings.confidence_threshold
        }
    }

@router.get("/ai-settings", response_model=AIStrategySettings)
async def get_ai_settings():
    """
    获取当前AI策略设置
    """
    return AIStrategySettings(
        enabled=t_trading_strategy.parameters.get('use_ai', True),
        risk_level=t_trading_strategy.parameters.get('ai_risk_level', 'medium'),
        auto_trading=t_trading_strategy.parameters.get('ai_auto_trading', False),
        confidence_threshold=t_trading_strategy.parameters.get('ai_confidence_threshold', 0.65)
    )

@router.post("/train-ai-model", response_model=Dict[str, Any])
async def train_ai_model():
    """
    训练AI模型
    """
    try:
        # 获取历史数据,用于训练
        historical_data = []
        trade_results = t_trading_tracker.trades
        
        # 训练模型
        success = await ai_t_trading_service.train_models(historical_data, trade_results)
        
        if success:
            return {
                "status": "success",
                "message": "AI模型训练成功"
            }
        else:
            return {
                "status": "warning",
                "message": "AI模型训练未完成,可能是数据不足或最近已训练"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"训练AI模型失败: {str(e)}")

@router.get("/summary", response_model=TradeSummary)
async def get_trading_summary(days: int = Query(30, description="统计周期(天)")):
    """
    获取T交易统计摘要
    """
    summary = t_trading_tracker.get_summary(days)
    return summary

@router.post("/start-trading-day", response_model=Dict[str, Any])
async def start_trading_day(date: Optional[str] = None):
    """
    开始新的交易日
    """
    t_trading_tracker.start_trading_day(date)
    t_trading_strategy.reset_daily_counters()
    
    return {
        "status": "success",
        "message": f"开始T交易日: {t_trading_tracker.today_date}",
        "date": t_trading_tracker.today_date
    }

@router.post("/end-trading-day", response_model=Dict[str, Any])
async def end_trading_day():
    """
    结束当前交易日
    """
    if t_trading_tracker.today_date is None:
        raise HTTPException(status_code=400, detail="当前没有活跃的交易日")
    
    date = t_trading_tracker.today_date
    daily_trades = len(t_trading_tracker.daily_trades)
    daily_profit = sum(t['profit'] for t in t_trading_tracker.daily_trades)
    
    t_trading_tracker.end_trading_day()
    
    return {
        "status": "success",
        "message": f"结束交易日: {date}",
        "date": date,
        "trades_count": daily_trades,
        "daily_profit": daily_profit
    }

@router.get("/trade-history", response_model=List[Dict[str, Any]])
async def get_trade_history(
    days: int = Query(7, description="查询天数"),
    stock_code: Optional[str] = Query(None, description="股票代码筛选")
):
    """
    获取T交易历史记录
    """
    # 计算日期范围
    end_date = datetime.now().date()
    start_date = (end_date - timedelta(days=days)).strftime("%Y-%m-%d")
    
    # 过滤交易
    filtered_trades = []
    for trade in t_trading_tracker.trades:
        if trade['date'] >= start_date:
            if stock_code is None or trade['stock_code'] == stock_code:
                filtered_trades.append(trade)
    
    return filtered_trades

@router.get("/cost-impact", response_model=Dict[str, Any])
async def get_cost_impact(
    stock_code: str = Query(..., description="股票代码"),
    base_position: int = Query(..., description="底仓数量"),
    base_cost: float = Query(..., description="底仓成本")
):
    """
    计算T交易对特定股票持仓成本的影响
    """
    # 过滤该股票的完整T交易
    filtered_trades = [
        t for t in t_trading_tracker.trades 
        if t['stock_code'] == stock_code and t['trade_type'] == 'complete'
    ]
    
    # 计算成本影响
    impact = calculate_t_trade_impact(base_position, base_cost, filtered_trades)
    
    return {
        "stock_code": stock_code,
        "trades_count": len(filtered_trades),
        "total_profit": sum(t['profit'] for t in filtered_trades),
        "impact": impact
    }

@router.post("/update-ai-execution-settings", response_model=Dict[str, Any])
async def update_ai_execution_settings(settings: AIExecutionSettings):
    """
    更新AI交易自动执行设置
    """
    result = await ai_t_trading_service.update_settings({
        "auto_execute": settings.auto_execute,
        "max_trade_amount": settings.max_trade_amount
    })
    
    return result

@router.get("/ai-execution-settings", response_model=AIExecutionSettings)
async def get_ai_execution_settings():
    """
    获取AI交易自动执行设置
    """
    # 从服务获取当前设置
    return AIExecutionSettings(
        auto_execute=ai_t_trading_service.auto_execute,
        max_trade_amount=ai_t_trading_service.max_trade_amount
    )

@router.post("/ai-trade-decision")
async def get_ai_trade_decision(
    stock_info: StockInfo,
    historical_data: Optional[List[Dict]] = None
):
    """
    获取AI的综合交易决策,整合所有分析因素
    
    Args:
        stock_info: 股票信息
        historical_data: 历史数据(可选)
        
    Returns:
        AI综合决策结果
    """
    try:
        market_data = {
            "code": stock_info.code,
            "name": stock_info.name,
            "current_price": stock_info.current_price,
            "open_price": stock_info.open_price,
            "intraday_high": stock_info.intraday_high,
            "intraday_low": stock_info.intraday_low,
            "avg_volume": stock_info.avg_volume,
            "current_volume": stock_info.current_volume,
            "base_position": stock_info.base_position,
            "base_cost": stock_info.base_cost
        }
        
        # 使用统一AI决策模型生成综合决策
        decision = await ai_t_trading_service.unified_decision_model(market_data, historical_data)
        
        return {
            "success": True,
            "data": decision,
            "message": "AI决策已生成"
        }
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "message": f"生成AI决策失败: {str(e)}"
        }

@router.post("/set-environment", response_model=Dict[str, Any])
async def set_trading_environment(setting: EnvironmentSetting):
    """
    设置交易环境(回测或实盘)
    
    Args:
        setting: 环境设置,包含environment字段,可选值为"backtest"或"live"
    
    Returns:
        设置结果
    """
    try:
        if setting.environment not in [TradingEnvironment.BACKTEST, TradingEnvironment.LIVE]:
            return {
                "success": False,
                "message": f"无效的环境设置: {setting.environment},有效值为 '{TradingEnvironment.BACKTEST}' 或 '{TradingEnvironment.LIVE}'"
            }
            
        success = ai_t_trading_service.set_environment(setting.environment)
        
        if success:
            # 更新策略参数
            t_trading_strategy.parameters['environment'] = setting.environment
            
            # 根据环境调整其他参数
            if setting.environment == TradingEnvironment.BACKTEST:
                t_trading_strategy.parameters['use_ai'] = True  # 回测环境默认启用AI
                
            return {
                "success": True,
                "message": f"交易环境已切换为: {setting.environment}",
                "environment": setting.environment
            }
        else:
            return {
                "success": False,
                "message": "环境切换失败"
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"设置交易环境失败: {str(e)}"
        }

@router.get("/current-environment", response_model=Dict[str, Any])
async def get_current_environment():
    """
    获取当前交易环境
    
    Returns:
        当前环境信息
    """
    try:
        return {
            "success": True,
            "environment": ai_t_trading_service.environment,
            "parameters": {
                "max_trade_amount": ai_t_trading_service.max_trade_amount,
                "risk_level": ai_t_trading_service.risk_control_level if ai_t_trading_service.environment == TradingEnvironment.LIVE else "N/A"
            }
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"获取当前环境失败: {str(e)}"
        }

@router.post("/load-backtest-data", response_model=Dict[str, Any])
async def load_backtest_data(stock_code: str = Query(..., description="股票代码")):
    """
    加载回测数据
    
    Args:
        stock_code: 股票代码
    
    Returns:
        加载结果
    """
    try:
        if ai_t_trading_service.environment != TradingEnvironment.BACKTEST:
            return {
                "success": False,
                "message": "只能在回测环境下加载回测数据"
            }
        
        # 这里应该从数据源加载历史数据
        # 在实际应用中,可能需要实现一个数据服务来提供历史数据
        # 这里简化处理,假设从文件或数据库加载
        try:
            # 示例:从CSV文件加载
            historical_data = pd.read_csv(f"./data/historical/{stock_code}.csv")
            
            # 加载到AI服务
            success = await ai_t_trading_service.load_backtest_data(historical_data)
            
            if success:
                return {
                    "success": True,
                    "message": f"成功加载 {stock_code} 的回测数据",
                    "data_points": len(historical_data)
                }
            else:
                return {
                    "success": False,
                    "message": "加载回测数据失败"
                }
        except FileNotFoundError:
            return {
                "success": False,
                "message": f"找不到 {stock_code} 的历史数据文件"
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"加载回测数据异常: {str(e)}"
        }

@router.post("/run-backtest", response_model=Dict[str, Any])
async def run_backtest(config: BacktestConfig):
    """
    运行回测
    
    Args:
        config: 回测配置
    
    Returns:
        回测结果
    """
    try:
        if ai_t_trading_service.environment != TradingEnvironment.BACKTEST:
            return {
                "success": False,
                "message": "只能在回测环境下运行回测"
            }
        
        # 运行回测
        result = await ai_t_trading_service.run_backtest(
            start_date=config.start_date,
            end_date=config.end_date,
            initial_capital=config.initial_capital,
            strategy_params=config.strategy_params
        )
        
        return result
    except Exception as e:
        return {
            "success": False,
            "message": f"运行回测失败: {str(e)}"
        }

@router.get("/backtest-results", response_model=Dict[str, Any])
async def get_backtest_results(format: str = Query("json", description="结果格式,可选值:json或csv")):
    """
    获取回测结果
    
    Args:
        format: 结果格式
    
    Returns:
        回测结果数据
    """
    try:
        if ai_t_trading_service.environment != TradingEnvironment.BACKTEST:
            return {
                "success": False,
                "message": "只能在回测环境下获取回测结果"
            }
        
        # 导出回测结果
        result_data = ai_t_trading_service.export_backtest_results(format=format)
        
        if result_data is None:
            return {
                "success": False,
                "message": "没有回测结果数据"
            }
        
        return {
            "success": True,
            "message": "成功获取回测结果",
            "data": result_data
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"获取回测结果失败: {str(e)}"
        }

@router.post("/configure-risk-control", response_model=Dict[str, Any])
async def configure_risk_control(
    risk_level: str = Query("medium", description="风险级别: low, medium, high"),
    max_position_per_stock: float = Query(0.2, description="单只股票最大仓位比例"),
    daily_loss_limit: float = Query(0.02, description="日亏损限制比例"),
    position_sizing_method: str = Query("confidence", description="仓位确定方法: fixed, confidence, kelly")
):
    """
    配置实盘环境下的风险控制参数
    
    Args:
        risk_level: 风险控制级别
        max_position_per_stock: 单只股票最大仓位比例
        daily_loss_limit: 日亏损限制比例
        position_sizing_method: 仓位确定方法
    
    Returns:
        配置结果
    """
    try:
        if ai_t_trading_service.environment != TradingEnvironment.LIVE:
            return {
                "success": False,
                "message": "只能在实盘环境下配置风险控制参数"
            }
        
        # 配置风险控制
        result = ai_t_trading_service.configure_risk_control(
            risk_level=risk_level,
            max_position_per_stock=max_position_per_stock,
            daily_loss_limit=daily_loss_limit,
            position_sizing_method=position_sizing_method
        )
        
        return result
    except Exception as e:
        return {
            "success": False,
            "message": f"配置风险控制失败: {str(e)}"
        }

@router.get("/risk-learning-stats")
async def get_risk_learning_stats():
    """
    获取风险参数学习统计数据
    
    Returns:
        dict: 学习统计结果
    """
    try:
        if ai_t_trading_service.environment != TradingEnvironment.LIVE:
            return {
                "success": False,
                "message": "仅在实盘环境下可获取风险参数学习统计",
                "data": None
            }
            
        # 获取风险参数统计
        stats = ai_t_trading_service.get_risk_parameter_stats()
        
        return {
            "success": True,
            "message": "获取风险参数学习统计成功",
            "data": stats
        }
    except Exception as e:
        logger.error(f"获取风险参数学习统计失败: {e}")
        return {
            "success": False,
            "message": f"获取风险参数学习统计失败: {str(e)}",
            "data": None
        }
        
@router.post("/record-trade-result")
async def record_trade_result(trade_data: dict):
    """
    记录交易结果,用于风险参数学习
    
    Args:
        trade_data (dict): 交易结果数据
            - trade_id (str): 交易ID
            - result (str): 交易结果,'success', 'failure', 'neutral'
            - profit_loss (float): 盈亏金额
    
    Returns:
        dict: 记录结果
    """
    try:
        if ai_t_trading_service.environment != TradingEnvironment.LIVE:
            return {
                "success": False,
                "message": "仅在实盘环境下可记录交易结果",
                "data": None
            }
            
        # 验证必要参数
        if 'trade_id' not in trade_data or 'result' not in trade_data:
            return {
                "success": False,
                "message": "缺少必要参数: trade_id, result",
                "data": None
            }
            
        # 验证结果类型
        valid_results = ['success', 'failure', 'neutral']
        if trade_data['result'] not in valid_results:
            return {
                "success": False,
                "message": f"无效的结果类型, 有效值: {', '.join(valid_results)}",
                "data": None
            }
            
        # 记录交易结果
        profit_loss = trade_data.get('profit_loss', 0)
        result = ai_t_trading_service.record_trade_result(
            trade_data['trade_id'],
            trade_data['result'],
            profit_loss
        )
        
        if result:
            return {
                "success": True,
                "message": "交易结果记录成功",
                "data": {
                    "trade_id": trade_data['trade_id'],
                    "recorded": True
                }
            }
        else:
            return {
                "success": False,
                "message": "未找到对应的交易记录",
                "data": None
            }
            
    except Exception as e:
        logger.error(f"记录交易结果失败: {e}")
        return {
            "success": False,
            "message": f"记录交易结果失败: {str(e)}",
            "data": None
        }

@router.get("/risk-learning-history")
async def get_risk_learning_history(limit: int = 10, offset: int = 0):
    """
    获取风险参数学习历史记录
    
    Args:
        limit (int): 返回记录数量限制
        offset (int): 记录偏移量
    
    Returns:
        dict: 学习历史记录
    """
    try:
        if ai_t_trading_service.environment != TradingEnvironment.LIVE:
            return {
                "success": False,
                "message": "仅在实盘环境下可获取风险参数学习历史",
                "data": []
            }
            
        # 获取风险参数历史记录
        history = ai_t_trading_service.risk_parameter_history
        
        # 应用分页
        paginated_history = history[offset:offset+limit]
        
        return {
            "success": True,
            "message": "获取风险参数学习历史成功",
            "data": {
                "total": len(history),
                "records": paginated_history
            }
        }
    except Exception as e:
        logger.error(f"获取风险参数学习历史失败: {e}")
        return {
            "success": False,
            "message": f"获取风险参数学习历史失败: {str(e)}",
            "data": {"total": 0, "records": []}
        } 
