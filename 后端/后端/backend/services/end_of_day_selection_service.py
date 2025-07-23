import pandas as pd
import numpy as np
from datetime import datetime, timedelta, time
import logging
import json
import os
import asyncio

from strategies import StrategyFactory

logger = logging.getLogger(__name__)

class EndOfDaySelectionService:
    """
    尾盘选股服务
    
    负责在尾盘时间执行选股策略,生成适合T+0或次日交易的股票推荐。
    
    主要功能:
    1. 获取实时行情数据
    2. 应用尾盘选股策略
    3. 根据综合评分过滤和排序股票
    4. 返回符合条件的股票列表,包含交易信号和原因
    5. 支持定时执行和多种策略模式
    """
    
    def __init__(self, config=None):
        """
        初始化尾盘选股服务
        
        Args:
            config (dict, optional): 服务配置
        """
        self.config = config or {}
        
        # 默认配置
        default_config = {
            'min_score_threshold': 0.7,           # 最低综合评分阈值
            'max_stock_count': 10,                # 最大推荐股票数量
            'eod_start_time': '14:30',            # 尾盘开始时间
            'eod_end_time': '15:00',              # 尾盘结束时间
            'strategy_parameters': {},            # 策略特定参数
            'exclude_st': True,                   # 是否排除ST股票
            'exclude_new': True,                  # 是否排除新股
            'min_price': 5.0,                     # 最低股价
            'max_price': 100.0,                   # 最高股价
            'data_cache_path': './data/eod_stock_cache/', # 数据缓存路径
            'result_save_path': './data/eod_selection_results/', # 结果保存路径
            'scheduled_run_times': ['14:30', '14:45', '14:55'], # 定时执行时间
            'active_strategies': ['base', 'guocheng', 'zhinanzhen', 'tn6', 'jingchuan', 'qiankun', 'jiufang'], # 激活的策略
            'strategy_schedules': {               # 根据时间段执行不同策略
                '14:30': ['base', 'guocheng', 'zhinanzhen'],
                '14:45': ['base', 'tn6', 'jingchuan', 'qiankun'],
                '14:55': ['base', 'guocheng', 'zhinanzhen', 'tn6', 'jingchuan', 'qiankun', 'jiufang']
            }
        }
        
        # 合并配置
        for key, value in default_config.items():
            if key not in self.config:
                self.config[key] = value
        
        # 创建数据缓存目录
        os.makedirs(self.config['data_cache_path'], exist_ok=True)
        os.makedirs(self.config['result_save_path'], exist_ok=True)
        
        # 获取策略实例
        self.strategy = StrategyFactory.get_strategy('end_of_day_selection', self.config['strategy_parameters'])
        
        # 初始化数据缓存
        self.stock_data_cache = {}
        
        # 初始化调度器任务
        self.scheduler_task = None
    
    def is_eod_time(self):
        """
        检查当前是否是尾盘时间
        
        Returns:
            bool: 是否在尾盘时间段
        """
        now = datetime.now().time()
        eod_start = datetime.strptime(self.config['eod_start_time'], '%H:%M').time()
        eod_end = datetime.strptime(self.config['eod_end_time'], '%H:%M').time()
        
        return eod_start <= now <= eod_end and self.is_trading_day()
    
    def is_trading_day(self):
        """
        检查当前是否是交易日
        
        Returns:
            bool: 是否是交易日
        """
        # 实际应用中应检查交易日历表
        # 这里简化为工作日判断
        today = datetime.now()
        return today.weekday() < 5  # 0-4为周一至周五
    
    def get_current_time_strategies(self):
        """
        根据当前时间获取应执行的策略
        
        Returns:
            list: 策略名称列表
        """
        current_time = datetime.now().time()
        current_time_str = current_time.strftime('%H:%M')
        
        # 检查是否有特定时间点的策略配置
        for schedule_time, strategies in self.config['strategy_schedules'].items():
            schedule_time_obj = datetime.strptime(schedule_time, '%H:%M').time()
            
            # 如果当前时间在某个时间点的5分钟内,使用该时间点的策略配置
            time_diff = (current_time.hour * 60 + current_time.minute) - (schedule_time_obj.hour * 60 + schedule_time_obj.minute)
            if 0 <= time_diff < 5:
                return strategies
        
        # 默认使用所有激活的策略
        return self.config['active_strategies']
    
    async def get_stock_list(self):
        """
        获取股票列表
        
        Returns:
            list: 符合筛选条件的股票列表
        """
        # 实际应用中应从数据源获取股票列表
        # 这里模拟一个简化的列表
        stocks = [
            {'code': 'SH600519', 'name': '贵州茅台'},
            {'code': 'SH600036', 'name': '招商银行'},
            {'code': 'SZ000858', 'name': '五粮液'},
            {'code': 'SH601318', 'name': '中国平安'},
            {'code': 'SZ000651', 'name': '格力电器'},
            {'code': 'SH600276', 'name': '恒瑞医药'},
            {'code': 'SH600887', 'name': '伊利股份'},
            {'code': 'SZ000333', 'name': '美的集团'},
            {'code': 'SH601888', 'name': '中国中免'},
            {'code': 'SH600030', 'name': '中信证券'},
            {'code': 'SH601166', 'name': '兴业银行'},
            {'code': 'SH600900', 'name': '长江电力'},
            {'code': 'SH601668', 'name': '中国建筑'},
            {'code': 'SH601288', 'name': '农业银行'},
            {'code': 'SH601398', 'name': '工商银行'}
        ]
        
        # 过滤ST股票和新股
        if self.config['exclude_st']:
            stocks = [s for s in stocks if 'ST' not in s['name']]
        
        # 实际应用中还应加入新股过滤等逻辑
        
        return stocks
    
    async def get_stock_data(self, stock_code):
        """
        获取单只股票的交易数据
        
        Args:
            stock_code (str): 股票代码
            
        Returns:
            pd.DataFrame: 股票交易数据
        """
        # 检查缓存
        if stock_code in self.stock_data_cache:
            # 检查缓存是否是今天的数据
            cached_data = self.stock_data_cache[stock_code]
            if cached_data['date'].iloc[-1] == datetime.now().date():
                return cached_data
        
        # 实际应用中应从数据API获取数据
        # 这里生成模拟数据
        
        # 生成日期和时间
        today = datetime.now().date()
        time_slots = pd.date_range(
            start=datetime.combine(today, time(9, 30)),
            end=datetime.combine(today, time(15, 0)),
            freq='1min'
        )
        
        # 过滤掉中午休市时间
        time_slots = [t for t in time_slots if not (time(11, 30) <= t.time() <= time(13, 0))]
        
        # 生成随机价格和成交量数据
        np.random.seed(int(stock_code[-4:]))  # 使用股票代码最后4位作为随机种子
        
        # 基础价格
        base_price = 50.0 + np.random.uniform(-30, 30)
        
        # 日内价格变动
        price_changes = np.random.normal(0, 0.005, len(time_slots)).cumsum()
        open_price = base_price * (1 + price_changes[0])
        close_prices = base_price * (1 + price_changes)
        
        # 确保价格不会为负
        close_prices = np.maximum(close_prices, 0.1)
        
        # 生成高低价
        high_prices = close_prices * (1 + np.random.uniform(0, 0.01, len(time_slots)))
        low_prices = close_prices * (1 - np.random.uniform(0, 0.01, len(time_slots)))
        
        # 确保高低价合理
        for i in range(len(time_slots)):
            if i > 0:
                high_prices[i] = max(high_prices[i], close_prices[i])
                low_prices[i] = min(low_prices[i], close_prices[i])
        
        # 尾盘做一些特殊处理,增加一些尾盘变化
        eod_index = int(len(time_slots) * 0.9)  # 尾盘开始位置
        
        # 生成尾盘波动
        eod_trend = np.random.choice([-1, 1], p=[0.3, 0.7])  # 70%概率上涨
        eod_factor = np.linspace(0, 0.01 * eod_trend, len(time_slots) - eod_index)
        
        close_prices[eod_index:] = close_prices[eod_index:] * (1 + eod_factor)
        high_prices[eod_index:] = np.maximum(high_prices[eod_index:], close_prices[eod_index:])
        low_prices[eod_index:] = np.minimum(low_prices[eod_index:], close_prices[eod_index:])
        
        # 成交量
        base_volume = 10000 + np.random.uniform(0, 90000)
        volumes = base_volume * (1 + np.random.uniform(-0.5, 1.5, len(time_slots)))
        
        # 尾盘成交量变化
        eod_volume_factor = np.random.uniform(1.0, 2.5)  # 尾盘成交量放大系数
        volumes[eod_index:] = volumes[eod_index:] * eod_volume_factor
        
        # 创建DataFrame
        data = pd.DataFrame({
            'date': [ts.date() for ts in time_slots],
            'time': [ts.time() for ts in time_slots],
            'open': [open_price] + list(close_prices[:-1]),
            'high': high_prices,
            'low': low_prices,
            'close': close_prices,
            'volume': volumes,
            'code': stock_code,
            'name': next((s['name'] for s in await self.get_stock_list() if s['code'] == stock_code), 'Unknown')
        })
        
        # 计算市值和换手率
        total_shares = 1e9  # 假设总股本10亿
        float_shares = 5e8   # 假设流通股本5亿
        
        data['total_shares'] = total_shares
        data['float_shares'] = float_shares
        data['market_cap'] = data['close'] * total_shares
        data['turnover_rate'] = data['volume'] / float_shares
        
        # 缓存数据
        self.stock_data_cache[stock_code] = data
        
        return data
    
    async def select_stocks(self, strategies=None):
        """
        执行尾盘选股
        
        Args:
            strategies (list, optional): 要执行的策略列表,如果为None则使用当前时间配置
            
        Returns:
            list: 选股结果列表
        """
        # 检查是否是尾盘时间
        if not self.is_eod_time() and not self.config.get('force_run', False):
            logger.warning("当前不是尾盘时间,选股服务未执行")
            return []
        
        # 获取要执行的策略
        if strategies is None:
            strategies = self.get_current_time_strategies()
            
        logger.info(f"正在执行尾盘选股,使用策略: {', '.join(strategies)}")
        
        # 更新策略参数
        self.strategy.parameters['active_strategies'] = strategies
        
        # 获取股票列表
        stocks = await self.get_stock_list()
        
        # 存储选股结果
        results = []
        
        # 处理每只股票
        for stock in stocks:
            try:
                # 获取股票数据
                stock_data = await self.get_stock_data(stock['code'])
                
                # 应用选股策略
                stock_result = self.strategy.generate_signals(stock_data)
                
                # 检查是否有结果
                if not stock_result.empty:
                    # 添加到结果集
                    result_dict = stock_result.iloc[0].to_dict()
                    result_dict['timestamp'] = datetime.now().isoformat()
                    result_dict['strategies_used'] = strategies
                    results.append(result_dict)
            except Exception as e:
                logger.error(f"处理股票 {stock['code']} 时出错: {str(e)}")
        
        # 按综合评分排序
        if results:
            results = sorted(results, key=lambda x: x['composite_score'], reverse=True)
            
            # 应用评分阈值过滤
            results = [r for r in results if r['composite_score'] >= self.config['min_score_threshold']]
            
            # 限制结果数量
            results = results[:self.config['max_stock_count']]
        
        # 保存结果
        self.save_results(results, strategies)
        
        return results
    
    def save_results(self, results, strategies=None):
        """
        保存选股结果
        
        Args:
            results (list): 选股结果列表
            strategies (list, optional): 使用的策略列表
        """
        if not results:
            return
            
        # 创建结果文件名
        today_str = datetime.now().strftime('%Y%m%d')
        timestamp = datetime.now().strftime('%H%M%S')
        filename = f"eod_selection_{today_str}_{timestamp}.json"
        filepath = os.path.join(self.config['result_save_path'], filename)
        
        # 将日期和时间转换为字符串
        for result in results:
            if isinstance(result.get('date'), datetime.date):
                result['date'] = result['date'].strftime('%Y-%m-%d')
        
        # 如果未提供策略列表,使用当前策略
        if strategies is None:
            strategies = self.strategy.parameters.get('active_strategies', [])
        
        # 保存为JSON文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'strategies_used': strategies,
                'results': results
            }, f, ensure_ascii=False, indent=2)
        
        logger.info(f"选股结果已保存至: {filepath}")
    
    def load_latest_results(self):
        """
        加载最新的选股结果
        
        Returns:
            list: 最新的选股结果
        """
        result_dir = self.config['result_save_path']
        if not os.path.exists(result_dir):
            return []
            
        # 获取最新的结果文件
        result_files = [f for f in os.listdir(result_dir) if f.startswith('eod_selection_') and f.endswith('.json')]
        if not result_files:
            return []
            
        # 按文件名排序,取最新的
        result_files.sort(reverse=True)
        latest_file = os.path.join(result_dir, result_files[0])
        
        # 读取结果
        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('results', [])
        except Exception as e:
            logger.error(f"加载选股结果时出错: {str(e)}")
            return []
    
    def format_results_for_frontend(self, results):
        """
        将选股结果格式化为前端需要的格式
        
        Args:
            results (list): 选股结果
            
        Returns:
            list: 格式化后的结果
        """
        formatted_results = []
        
        for result in results:
            # 获取策略评分
            strategy_scores = result.get('strategy_scores', {})
            
            # 格式化评分为百分比
            composite_score = round(result.get('composite_score', 0) * 100)
            
            # 计算维度评分 (如果有包含各个维度的score)
            if 'volume_score' in result and 'trend_score' in result and 'technical_score' in result:
                volume_score = round(result.get('volume_score', 0) * 100)
                trend_score = round(result.get('trend_score', 0) * 100)
                technical_score = round(result.get('technical_score', 0) * 100)
            else:
                # 从策略得分中提取不同维度的信息
                volume_score, trend_score, technical_score = 0, 0, 0
                strategies_count = 0
                
                # 从不同策略中估算维度分数
                for strategy, score in strategy_scores.items():
                    strategies_count += 1
                    if strategy in ['base', 'guocheng', 'tn6']:
                        volume_score += score * 100
                    if strategy in ['base', 'zhinanzhen', 'jiufang']:
                        trend_score += score * 100
                    if strategy in ['base', 'jingchuan', 'qiankun']:
                        technical_score += score * 100
                
                # 取平均分
                if strategies_count > 0:
                    volume_score = round(volume_score / strategies_count)
                    trend_score = round(trend_score / strategies_count)
                    technical_score = round(technical_score / strategies_count)
            
            # 创建前端显示对象
            formatted_result = {
                'symbol': result.get('code', ''),
                'name': result.get('name', ''),
                'price': round(float(result.get('price', 0)), 2),
                'changePercent': round(float(result.get('change_percent', 0)), 2),
                'momentum': round(trend_score / 100, 2),
                'valuation': 0.75,  # 假设估值指标
                'liquidity': round(volume_score / 100, 2),
                'sentiment': round(technical_score / 100, 2),
                'composite': round(composite_score / 100, 2),
                't0Signal': result.get('t0_signal', '观望'),
                't0Reason': result.get('t0_reason', ''),
                'strategyScores': {k: round(v, 2) for k, v in strategy_scores.items()},
                'strategiesUsed': result.get('strategies_used', []),
                'timestamp': result.get('timestamp', datetime.now().isoformat()),
                'volumeAnalysis': {
                    'volumeRatio': round(2 * volume_score / 100, 2),  # 简化的量比
                    'pattern': {
                        'name': '温和放量' if volume_score > 70 else '正常'
                    }
                }
            }
            
            formatted_results.append(formatted_result)
        
        return formatted_results

    async def start_scheduler(self):
        """
        启动定时执行调度器
        """
        if self.scheduler_task is not None:
            logger.warning("调度器已经在运行中")
            return
            
        self.scheduler_task = asyncio.create_task(self._scheduler_loop())
        logger.info("尾盘选股调度器已启动")
    
    async def stop_scheduler(self):
        """
        停止定时执行调度器
        """
        if self.scheduler_task is None:
            logger.warning("调度器未运行")
            return
            
        self.scheduler_task.cancel()
        try:
            await self.scheduler_task
        except asyncio.CancelledError:
            pass
        self.scheduler_task = None
        logger.info("尾盘选股调度器已停止")
    
    async def _scheduler_loop(self):
        """
        调度器循环任务
        """
        try:
            while True:
                # 检查是否是交易日
                if not self.is_trading_day():
                    # 非交易日,休眠1小时
                    logger.info("非交易日,调度器休眠中")
                    await asyncio.sleep(3600)
                    continue
                
                # 获取当前时间
                now = datetime.now()
                current_time_str = now.strftime('%H:%M')
                
                # 检查是否到达调度时间
                if current_time_str in self.config['scheduled_run_times']:
                    logger.info(f"开始执行定时尾盘选股任务,时间: {current_time_str}")
                    
                    # 获取当前时间对应的策略
                    strategies = self.config['strategy_schedules'].get(
                        current_time_str, 
                        self.config['active_strategies']
                    )
                    
                    # 执行选股
                    self.config['force_run'] = True
                    await self.select_stocks(strategies)
                    self.config['force_run'] = False
                    
                    # 等待一分钟,避免重复执行
                    await asyncio.sleep(60)
                else:
                    # 检查下一个调度时间
                    next_run_time = None
                    for run_time in self.config['scheduled_run_times']:
                        run_time_obj = datetime.strptime(run_time, '%H:%M').time()
                        run_datetime = datetime.combine(now.date(), run_time_obj)
                        
                        if run_datetime > now:
                            if next_run_time is None or run_datetime < next_run_time:
                                next_run_time = run_datetime
                    
                    if next_run_time is None:
                        # 今天没有更多调度任务,休眠到明天
                        tomorrow = now.date() + timedelta(days=1)
                        next_run_time = datetime.combine(tomorrow, datetime.strptime(self.config['scheduled_run_times'][0], '%H:%M').time())
                    
                    # 计算休眠时间
                    sleep_seconds = (next_run_time - now).total_seconds()
                    
                    # 最多休眠10分钟,以便能够响应配置变更
                    sleep_seconds = min(sleep_seconds, 600)
                    
                    logger.debug(f"调度器将在{sleep_seconds:.0f}秒后唤醒")
                    await asyncio.sleep(sleep_seconds)
                    
        except asyncio.CancelledError:
            logger.info("尾盘选股调度器任务已取消")
        except Exception as e:
            logger.error(f"尾盘选股调度器出错: {str(e)}")
            # 出错后等待1分钟再重试
            await asyncio.sleep(60)
            # 重启调度器
            self.scheduler_task = asyncio.create_task(self._scheduler_loop()) 
 
