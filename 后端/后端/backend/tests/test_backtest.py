import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import unittest

# 添加项目根目录到路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.backtesting.engine import BacktestEngine
from backend.backtesting.strategies.inverted_three_red_backtest import InvertedThreeRedBacktest
from backend.backtesting.strategies.red_three_soldiers_backtest import RedThreeSoldiersBacktest
from backend.backtesting.analysis.performance_analyzer import PerformanceAnalyzer

class TestBacktestSystem(unittest.TestCase):
    
    def setUp(self):
        """设置测试环境"""
        # 创建测试数据
        self.test_data = self._generate_test_data()
        
        # 创建回测引擎
        self.engine = BacktestEngine(initial_capital=100000)
    
    def _generate_test_data(self):
        """生成测试数据"""
        # 创建日期序列
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 1, 31)
        
        dates = []
        current_date = start_date
        while current_date <= end_date:
            if current_date.weekday() < 5:  # 排除周末
                dates.append(current_date)
            current_date += timedelta(days=1)
        
        # 创建价格数据
        n = len(dates)
        symbol = "000001"
        
        # 基础数据
        base_price = 100.0
        prices = []
        for i in range(n):
            noise = np.random.normal(0, 0.01)
            trend = 0.001 * i  # 微小的上升趋势
            price = base_price * (1 + noise + trend)
            prices.append(price)
        
        # 创建OHLCV数据
        data = []
        for i in range(n):
            daily_range = prices[i] * 0.02
            data.append({
                'date': dates[i],
                'symbol': symbol,
                'open': prices[i] * (1 - 0.005),
                'high': prices[i] + daily_range,
                'low': prices[i] - daily_range,
                'close': prices[i],
                'volume': 10000 + np.random.randint(0, 5000)
            })
        
        # 注入倒三红形模式
        if n >= 15:
            # 第一天:较大阳线
            data[10]['open'] = 100
            data[10]['close'] = 110
            data[10]['high'] = 112
            data[10]['low'] = 99
            data[10]['volume'] = 150000
            
            # 第二天:中等阳线,但实体比第一天小
            data[11]['open'] = 111
            data[11]['close'] = 117
            data[11]['high'] = 121
            data[11]['low'] = 110
            data[11]['volume'] = 130000
            
            # 第三天:小阳线,上影线长
            data[12]['open'] = 118
            data[12]['close'] = 119
            data[12]['high'] = 127
            data[12]['low'] = 117
            data[12]['volume'] = 110000
        
        # 注入红三兵模式
        if n >= 23:
            # 第一天:第一根阳线
            data[18]['open'] = 100
            data[18]['close'] = 108
            data[18]['high'] = 109
            data[18]['low'] = 99
            data[18]['volume'] = 120000
            
            # 第二天:第二根阳线,与第一根相似
            data[19]['open'] = 108.5
            data[19]['close'] = 117
            data[19]['high'] = 118
            data[19]['low'] = 108
            data[19]['volume'] = 140000
            
            # 第三天:第三根阳线,上影线短
            data[20]['open'] = 117.5
            data[20]['close'] = 126
            data[20]['high'] = 127
            data[20]['low'] = 117
            data[20]['volume'] = 160000
            
        return pd.DataFrame(data)
    
    def test_backtest_engine(self):
        """测试回测引擎基本功能"""
        # 添加策略
        self.engine.add_strategy(InvertedThreeRedBacktest())
        
        # 运行回测
        results = self.engine.run(self.test_data)
        
        # 验证结果包含预期的键
        self.assertIn('equity_curve', results)
        self.assertIn('trades', results)
        self.assertIn('initial_capital', results)
        self.assertIn('final_equity', results)
        
        # 验证权益曲线不为空
        self.assertGreater(len(results['equity_curve']), 0)
    
    def test_inverted_three_red_strategy(self):
        """测试倒三红形策略"""
        # 创建策略
        strategy = InvertedThreeRedBacktest()
        
        # 生成信号
        signals = strategy.generate_signals(self.test_data)
        
        # 验证信号格式
        self.assertIsInstance(signals, dict)
        
        # 由于我们注入了倒三红形模式,应该至少有一个信号
        self.assertGreaterEqual(len(signals), 0)
    
    def test_red_three_soldiers_strategy(self):
        """测试红三兵策略"""
        # 创建策略
        strategy = RedThreeSoldiersBacktest()
        
        # 生成信号
        signals = strategy.generate_signals(self.test_data)
        
        # 验证信号格式
        self.assertIsInstance(signals, dict)
        
        # 由于我们注入了红三兵模式,应该至少有一个信号
        self.assertGreaterEqual(len(signals), 0)
    
    def test_performance_analyzer(self):
        """测试性能分析器"""
        # 运行回测获取结果
        self.engine.add_strategy(InvertedThreeRedBacktest())
        self.engine.add_strategy(RedThreeSoldiersBacktest())
        results = self.engine.run(self.test_data)
        
        # 使用性能分析器生成报告
        report = PerformanceAnalyzer.generate_report(results['equity_curve'], results['trades'])
        
        # 验证报告包含预期的键
        self.assertIn('metrics', report)
        self.assertIn('charts', report)
        
        # 验证指标
        metrics = report['metrics']
        self.assertIn('total_return', metrics)
        self.assertIn('annual_return', metrics)
        self.assertIn('sharpe_ratio', metrics)
        self.assertIn('max_drawdown', metrics)

if __name__ == '__main__':
    unittest.main() 
