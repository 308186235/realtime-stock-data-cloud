# Trading Strategies

This module contains implementations of various trading strategies and the strategy optimization system.

## Overview

The strategies module provides a framework for creating, testing, and optimizing trading strategies. It includes:

- A base strategy class that all strategies inherit from
- Implementations of common trading strategies
- A strategy factory for easy strategy creation and management
- Integration with AI-powered optimization

## Available Strategies

### Moving Average Crossover Strategy

ID: `ma_cross`

The Moving Average Crossover strategy generates buy signals when a short-term moving average crosses above a long-term moving average, and sell signals when the short-term moving average crosses below the long-term moving average. This strategy is well-suited for trending markets.

Parameters:
- `short_period`: Period for the short-term moving average (default: 5)
- `long_period`: Period for the long-term moving average (default: 20)
- `stop_loss`: Stop loss percentage (default: 3%)
- `take_profit`: Take profit percentage (default: 8%)

### RSI Strategy

ID: `rsi_strategy`

The Relative Strength Index (RSI) strategy uses the RSI indicator to identify potential oversold and overbought conditions. It generates buy signals when the RSI falls below an oversold threshold, and sell signals when the RSI rises above an overbought threshold. This strategy is well-suited for range-bound, oscillating markets.

Parameters:
- `rsi_period`: Period for RSI calculation (default: 14)
- `overbought`: Overbought threshold (default: 70)
- `oversold`: Oversold threshold (default: 30)
- `stop_loss`: Stop loss percentage (default: 4%)

### Bollinger Bands Strategy

ID: `bollinger_bands`

The Bollinger Bands strategy uses statistical boundaries around a moving average to identify potential price extremes. It generates buy signals when the price touches the lower band, and sell signals when the price touches the upper band. This strategy works well in range-bound markets but can be less effective during strong trends.

Parameters:
- `bb_period`: Period for Bollinger Bands calculation (default: 20)
- `bb_std`: Standard deviation multiplier for band width (default: 2.0)
- `stop_loss`: Stop loss percentage (default: 3.5%)
- `profit_take`: Take profit percentage (default: 7%)

## Strategy Optimization

The strategy optimization system uses machine learning and statistical techniques to find optimal strategy parameters for specific stocks or market conditions. It supports:

- Bayesian optimization using Optuna
- Grid search for smaller datasets
- Parameter range constraints
- Performance metrics evaluation

### Optimization Process

1. The system loads historical data for the target stock
2. It evaluates different parameter combinations based on the strategy's parameter ranges
3. For each parameter set, it runs a backtest and calculates performance metrics
4. Parameters are scored based on a weighted combination of win rate, profit factor, and Sharpe ratio
5. The optimal parameter set is returned along with expected performance metrics

### Adding New Strategies

To add a new strategy:

1. Create a new file in the strategies directory
2. Implement a class that inherits from `BaseStrategy`
3. Implement the required methods: `generate_signals`, `get_default_parameters`, and `get_parameter_ranges`
4. Add the strategy to the `StrategyFactory` in `__init__.py`

## Usage

```python
from strategies import StrategyFactory

# Get a strategy instance
strategy = StrategyFactory.get_strategy('ma_cross')

# Get strategy information
strategy_info = StrategyFactory.get_strategy_info('rsi_strategy')

# Get all available strategies
all_strategies = StrategyFactory.get_all_strategies_info()
``` 
