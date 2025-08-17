import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy

class RSIStrategy(BaseStrategy):
    """
    RSI (Relative Strength Index) Strategy.
    Generates buy signals when RSI is below oversold threshold,
    and sell signals when RSI is above overbought threshold.
    """
    
    def __init__(self, parameters=None):
        """
        Initialize RSI strategy with parameters.
        
        Args:
            parameters (dict): Strategy parameters
        """
        super().__init__(parameters)
        self.name = "RSI超买超卖策略"
        self.description = "RSI超买超卖策略利用相对强弱指标(RSI)的超买超卖区域进行交易。当RSI低于超卖阈值时产生买入信号,高于超买阈值时产生卖出信号。该策略适合震荡市场。"
        
        # Set parameters
        default_params = self.get_default_parameters()
        self.parameters = parameters or default_params
        
    def get_default_parameters(self):
        """
        Get default parameters for RSI strategy.
        
        Returns:
            dict: Default parameters
        """
        return {
            'rsi_period': 14,
            'overbought': 70,
            'oversold': 30,
            'stop_loss': 0.04       # 4% stop loss
        }
    
    def get_parameter_ranges(self):
        """
        Get valid ranges for strategy parameters.
        
        Returns:
            dict: Parameter ranges with min, max, and step values
        """
        return {
            'rsi_period': {'min': 2, 'max': 30, 'step': 1},
            'overbought': {'min': 50, 'max': 90, 'step': 5},
            'oversold': {'min': 10, 'max': 50, 'step': 5},
            'stop_loss': {'min': 0.01, 'max': 0.1, 'step': 0.005}
        }
    
    def generate_signals(self, data):
        """
        Generate trading signals based on RSI values.
        
        Args:
            data (pd.DataFrame): Historical market data with OHLCV
            
        Returns:
            pd.Series: Series of trading signals (1 for buy, -1 for sell, 0 for hold)
        """
        # Make a copy of data to avoid modifying the original
        df = data.copy()
        
        # Get parameters
        rsi_period = self.parameters['rsi_period']
        overbought = self.parameters['overbought']
        oversold = self.parameters['oversold']
        
        # Calculate RSI
        df['rsi'] = self._calculate_rsi(df['close'], rsi_period)
        
        # Initialize signals
        df['signal'] = 0
        
        # Generate RSI signals
        df.loc[df['rsi'] < oversold, 'signal'] = 1  # Buy signal when RSI is oversold
        df.loc[df['rsi'] > overbought, 'signal'] = -1  # Sell signal when RSI is overbought
        
        # Apply stop loss
        self._apply_stop_loss(df)
        
        return df['signal']
    
    def _calculate_rsi(self, prices, period=14):
        """
        Calculate Relative Strength Index.
        
        Args:
            prices (pd.Series): Price series
            period (int): RSI calculation period
            
        Returns:
            pd.Series: RSI values
        """
        # Calculate price changes
        delta = prices.diff()
        
        # Separate gains and losses
        gain = delta.copy()
        loss = delta.copy()
        gain[gain < 0] = 0
        loss[loss > 0] = 0
        loss = -loss  # Convert to positive values
        
        # Calculate average gain and loss
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        
        # Calculate RS and RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _apply_stop_loss(self, df):
        """
        Apply stop loss rules to the signals.
        
        Args:
            df (pd.DataFrame): DataFrame with signals
        """
        stop_loss = self.parameters['stop_loss']
        
        # Track entry prices and positions
        position = 0
        entry_price = 0
        
        for i in range(1, len(df)):
            prev_signal = df['signal'].iloc[i-1]
            curr_signal = df['signal'].iloc[i]
            curr_price = df['close'].iloc[i]
            
            # Check if we need to open a position
            if position == 0 and curr_signal == 1:
                position = 1
                entry_price = curr_price
            
            # Check if we need to close a position
            elif position == 1:
                # Calculate current profit/loss
                pnl = (curr_price - entry_price) / entry_price
                
                # Apply stop loss
                if pnl <= -stop_loss:
                    df.loc[df.index[i], 'signal'] = -1
                    position = 0
                    entry_price = 0
                
                # Check for sell signal
                elif curr_signal == -1:
                    position = 0
                    entry_price = 0 
