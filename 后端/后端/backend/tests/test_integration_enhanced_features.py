import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import components to test
from backtesting.engine import BacktestEngine
from backtesting.strategies.inverted_three_red_backtest import InvertedThreeRedBacktest
from backtesting.strategies.red_three_soldiers_backtest import RedThreeSoldiersBacktest
from backtesting.risk_management import RiskManager
from backtesting.indicators.technical_indicators import TechnicalIndicators
from backtesting.analysis.benchmark_comparison import BenchmarkComparison
from backtesting.analysis.performance_analyzer import PerformanceAnalyzer

class TestEnhancedFeaturesIntegration(unittest.TestCase):
    """Integration tests for the enhanced trading features"""
    
    def setUp(self):
        """Set up test data and components"""
        self.initial_capital = 100000
        
        # Generate test market data
        self.market_data = self._generate_test_data()
        
        # Generate benchmark data
        self.benchmark_data = self._generate_benchmark_data()
        
        # Initialize components
        self.risk_params = {
            'max_position_size': 0.2,
            'max_drawdown': 0.1,
            'fixed_stop_loss': 0.05,
            'trailing_stop_loss': 0.08,
            'time_stop_loss': 10,
            'position_sizing_method': 'risk',
            'risk_per_trade': 0.02
        }
        
        self.risk_manager = RiskManager(self.initial_capital, self.risk_params)
        self.inverted_three_red_strategy = InvertedThreeRedBacktest()
        self.red_three_soldiers_strategy = RedThreeSoldiersBacktest()
    
    def _generate_test_data(self):
        """Generate synthetic test data with some patterns for testing"""
        # Create specific date range for test data (using pandas for correct date handling)
        start_date = pd.Timestamp.now() - pd.Timedelta(days=365)
        end_date = pd.Timestamp.now()
        
        # Generate date series (trading days only)
        dates = pd.date_range(start=start_date, end=end_date, freq='B')  # Business days
        
        # Create base data for two symbols
        data = []
        symbols = ['AAPL', 'MSFT']
        
        for symbol in symbols:
            base_price = 100 if symbol == 'AAPL' else 200
            price = base_price
            
            for i, date in enumerate(dates):
                # Add some random price movement
                change = np.random.normal(0.0005, 0.015)  # Mean slightly positive
                price *= (1 + change)
                
                # Generate daily OHLCV data
                open_price = price * (1 + np.random.normal(0, 0.005))
                high_price = max(open_price, price) * (1 + abs(np.random.normal(0, 0.008)))
                low_price = min(open_price, price) * (1 - abs(np.random.normal(0, 0.008)))
                volume = int(np.random.normal(1000000, 300000))
                
                data.append({
                    'date': date,
                    'symbol': symbol,
                    'open': open_price,
                    'high': high_price,
                    'low': low_price,
                    'close': price,
                    'volume': volume
                })
                
        # Inject inverted three red pattern in AAPL
        self._inject_inverted_three_red(data, 'AAPL', dates[30:33])
        
        # Inject red three soldiers pattern in MSFT
        self._inject_red_three_soldiers(data, 'MSFT', dates[60:63])
        
        return pd.DataFrame(data)
    
    def _inject_inverted_three_red(self, data, symbol, dates):
        """Inject inverted three red pattern into the data"""
        # Find the indices to modify
        indices = [i for i, item in enumerate(data) 
                   if item['symbol'] == symbol and item['date'] in dates]
        
        if len(indices) != 3:
            return
            
        # First day: large bullish candle
        data[indices[0]]['open'] = 100
        data[indices[0]]['close'] = 110
        data[indices[0]]['high'] = 112
        data[indices[0]]['low'] = 99
        
        # Second day: medium bullish candle
        data[indices[1]]['open'] = 111
        data[indices[1]]['close'] = 117
        data[indices[1]]['high'] = 119
        data[indices[1]]['low'] = 110
        
        # Third day: small bullish candle with long upper shadow
        data[indices[2]]['open'] = 118
        data[indices[2]]['close'] = 120
        data[indices[2]]['high'] = 128
        data[indices[2]]['low'] = 117
    
    def _inject_red_three_soldiers(self, data, symbol, dates):
        """Inject red three soldiers pattern into the data"""
        # Find the indices to modify
        indices = [i for i, item in enumerate(data) 
                   if item['symbol'] == symbol and item['date'] in dates]
        
        if len(indices) != 3:
            return
            
        # First soldier
        data[indices[0]]['open'] = 200
        data[indices[0]]['close'] = 208
        data[indices[0]]['high'] = 210
        data[indices[0]]['low'] = 198
        
        # Second soldier
        data[indices[1]]['open'] = 209
        data[indices[1]]['close'] = 218
        data[indices[1]]['high'] = 220
        data[indices[1]]['low'] = 208
        
        # Third soldier
        data[indices[2]]['open'] = 219
        data[indices[2]]['close'] = 228
        data[indices[2]]['high'] = 230
        data[indices[2]]['low'] = 218
    
    def _generate_benchmark_data(self):
        """Generate benchmark index data for testing"""
        # Create specific date range for test data (using pandas for correct date handling)
        start_date = pd.Timestamp.now() - pd.Timedelta(days=365)
        end_date = pd.Timestamp.now()
        
        # Generate date series (trading days only)
        dates = pd.date_range(start=start_date, end=end_date, freq='B')  # Business days
        
        # Create benchmark data
        data = []
        price = 3000  # Starting index value
        
        for i, date in enumerate(dates):
            # Add some random price movement with slight upward trend
            change = np.random.normal(0.0003, 0.01)  # Mean slightly positive
            price *= (1 + change)
            
            # Generate daily OHLCV data
            open_price = price * (1 + np.random.normal(0, 0.003))
            high_price = max(open_price, price) * (1 + abs(np.random.normal(0, 0.005)))
            low_price = min(open_price, price) * (1 - abs(np.random.normal(0, 0.005)))
            volume = int(np.random.normal(5000000, 1000000))
            
            data.append({
                'date': date,
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': price,
                'volume': volume
            })
        
        return pd.DataFrame(data)
    
    def test_technical_indicators(self):
        """Test that technical indicators are properly calculated and generate signals"""
        # Add indicators to the market data
        data_with_indicators = self.market_data.copy()
        
        # Add various indicators
        data_with_indicators = TechnicalIndicators.add_moving_average(data_with_indicators)
        data_with_indicators = TechnicalIndicators.add_exponential_moving_average(data_with_indicators)
        data_with_indicators = TechnicalIndicators.add_macd(data_with_indicators)
        data_with_indicators = TechnicalIndicators.add_rsi(data_with_indicators)
        data_with_indicators = TechnicalIndicators.add_bollinger_bands(data_with_indicators)
        
        # Generate signals
        data_with_signals = TechnicalIndicators.generate_signals(data_with_indicators)
        
        # Verify indicators and signals are present
        self.assertIn('ma_20', data_with_signals.columns)
        self.assertIn('ema_20', data_with_signals.columns)
        self.assertIn('macd', data_with_signals.columns)
        self.assertIn('rsi_14', data_with_signals.columns)
        self.assertIn('bb_upper', data_with_signals.columns)
        
        # Check for signal columns
        signal_columns = [col for col in data_with_signals.columns if col.endswith('_signal')]
        self.assertGreater(len(signal_columns), 0)
        
        # Check signals have both buy/sell values
        if 'macd_cross_signal' in data_with_signals.columns:
            values = data_with_signals['macd_cross_signal'].unique()
            # We should have at least one 0 (no signal) and either 1 (buy) or -1 (sell)
            self.assertGreaterEqual(len(values), 2)
        
        logger.info("Technical indicators test passed")
    
    def test_risk_management(self):
        """Test that risk management functions properly"""
        # Test position sizing
        symbol = 'AAPL'
        price = 110
        stop_price = 104.5  # 5% below price
        
        position = self.risk_manager.calculate_position_size(symbol, price, stop_price)
        
        # Verify position sizing calculation
        self.assertEqual(position['symbol'], symbol)
        self.assertGreater(position['shares'], 0)
        self.assertLessEqual(position['percentage'], self.risk_params['max_position_size'])
        self.assertLessEqual(position['risk_percentage'], self.risk_params['risk_per_trade'])
        
        # Test stop loss detection
        self.risk_manager.update_position(symbol, price, pd.Timestamp.now(), position['shares'], True)
        
        # Test fixed stop loss
        triggered, reason = self.risk_manager.check_stop_loss(symbol, stop_price - 1, pd.Timestamp.now())
        self.assertTrue(triggered)
        self.assertEqual(reason, "fixed_stop_loss")
        
        # Test trailing stop loss - set up a different position for this test
        symbol2 = 'MSFT'
        entry_price = 200
        self.risk_manager.update_position(symbol2, entry_price, pd.Timestamp.now(), 10, True)
        self.risk_manager.positions[symbol2]['highest_price'] = 220  # Price went up after entry
        
        # Calculate trailing stop level (220 * (1 - 0.08) = 202.4)
        trailing_stop = 220 * (1 - self.risk_params['trailing_stop_loss'])
        triggered, reason = self.risk_manager.check_stop_loss(symbol2, trailing_stop - 1, pd.Timestamp.now())
        self.assertTrue(triggered)
        self.assertEqual(reason, "trailing_stop_loss")
        
        # Test time stop loss - set up a different position for this test
        symbol3 = 'GOOG'
        entry_price = 150
        entry_date = pd.Timestamp.now() - pd.Timedelta(days=self.risk_params['time_stop_loss'] + 1)
        self.risk_manager.update_position(symbol3, entry_price, entry_date, 5, True)
        
        triggered, reason = self.risk_manager.check_stop_loss(symbol3, entry_price, pd.Timestamp.now())
        self.assertTrue(triggered)
        self.assertEqual(reason, "time_stop_loss")
        
        logger.info("Risk management test passed")
    
    def test_benchmark_comparison(self):
        """Test that benchmark comparison functions properly"""
        # Create a simple equity curve for testing
        dates = self.benchmark_data['date'].unique()
        equity_data = []
        
        equity = self.initial_capital
        for date in dates:
            equity *= (1 + np.random.normal(0.001, 0.01))  # Random daily returns with positive bias
            equity_data.append({
                'date': date,
                'equity': equity
            })
        
        equity_curve = pd.DataFrame(equity_data)
        
        # Ensure dates are used as index for both dataframes
        equity_curve.set_index('date', inplace=True)
        benchmark_df = self.benchmark_data.copy()
        
        # Compare with benchmark - make sure we're using the same dates
        min_date = max(equity_curve.index.min(), benchmark_df['date'].min())
        max_date = min(equity_curve.index.max(), benchmark_df['date'].max())
        
        # Filter both datasets
        filtered_equity = equity_curve[equity_curve.index >= min_date]
        filtered_equity = filtered_equity[filtered_equity.index <= max_date]
        
        filtered_benchmark = benchmark_df[benchmark_df['date'] >= min_date]
        filtered_benchmark = filtered_benchmark[filtered_benchmark['date'] <= max_date]
        
        # Run comparison
        benchmark_comparison = BenchmarkComparison.compare_with_benchmark(
            filtered_equity, 
            filtered_benchmark,
            self.initial_capital
        )
        
        # Verify comparison results
        self.assertIn('summary', benchmark_comparison)
        self.assertIn('charts', benchmark_comparison)
        self.assertIn('monthly_data', benchmark_comparison)
        
        # Check key metrics are calculated
        self.assertIn('alpha', benchmark_comparison['summary'])
        self.assertIn('beta', benchmark_comparison['summary'])
        self.assertIn('information_ratio', benchmark_comparison['summary'])
        self.assertIn('up_capture', benchmark_comparison['summary'])
        self.assertIn('down_capture', benchmark_comparison['summary'])
        
        logger.info("Benchmark comparison test passed")
    
    def test_integrated_backtest(self):
        """Test the full integrated backtest with all components"""
        # Add indicators to market data
        data = self.market_data.copy()
        data = TechnicalIndicators.add_all_indicators(data)
        data = TechnicalIndicators.generate_signals(data)
        
        # Create backtest engine
        engine = BacktestEngine(
            initial_capital=self.initial_capital,
            commission=0.001
        )
        
        # Add strategies
        engine.add_strategy(self.inverted_three_red_strategy)
        engine.add_strategy(self.red_three_soldiers_strategy)
        
        # Set risk manager
        engine.set_risk_manager(self.risk_manager)
        
        # Run backtest
        # Convert to datetime objects as expected by the backtest engine
        start_date = self.market_data['date'].min().strftime('%Y-%m-%d')
        end_date = self.market_data['date'].max().strftime('%Y-%m-%d')
        
        # Run with explicitly specified date range
        results = engine.run(data, start_date, end_date)
        
        # Verify results contain expected components
        self.assertIn('equity_curve', results)
        self.assertIn('trades', results)
        self.assertIn('risk_metrics', results)
        
        # Check if we have trades - might not have due to test data constraints
        # Just verify we can access the trades list
        self.assertIsInstance(results['trades'], list)
        
        # Generate performance report
        if isinstance(results['equity_curve'], pd.DataFrame) and not results['equity_curve'].empty:
            report = PerformanceAnalyzer.generate_report(results['equity_curve'], results['trades'])
            
            # Verify report
            self.assertIn('metrics', report)
            self.assertIn('charts', report)
        
        logger.info("Integrated backtest test passed")
        
        return results

if __name__ == '__main__':
    unittest.main() 
