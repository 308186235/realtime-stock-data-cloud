import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from backend.strategies.inverted_three_red_strategy import InvertedThreeRedStrategy

def generate_sample_data(days=100):
    """Generate sample data with an inverted three red pattern"""
    # Create date range
    date_range = [datetime.now() - timedelta(days=i) for i in range(days, 0, -1)]
    date_range = [d.strftime('%Y-%m-%d') for d in date_range]
    
    # Initialize with random price movements
    np.random.seed(42)  # For reproducibility
    close = 100 + np.random.randn(days).cumsum()
    
    # Ensure overall uptrend
    for i in range(1, days):
        if i % 5 == 0:  # Add some upward bias every 5 days
            close[i] = close[i-1] * (1 + np.random.uniform(0.01, 0.03))
    
    # Base data with random movements
    daily_range = np.random.uniform(1, 3, days)
    high = close + daily_range / 2
    low = close - daily_range / 2
    
    # Generate open prices (random within previous day's range)
    open_prices = np.zeros(days)
    open_prices[0] = close[0] - np.random.uniform(0, daily_range[0]/2)
    for i in range(1, days):
        open_prices[i] = close[i-1] + np.random.uniform(-daily_range[i-1]/4, daily_range[i-1]/4)
    
    # Generate volume with some randomness
    volume = np.random.uniform(1000, 5000, days)
    
    # Create inverted three red pattern near the end
    pattern_start = days - 10
    
    # First bullish candle (large body)
    open_prices[pattern_start] = close[pattern_start-1] * 0.995
    close[pattern_start] = open_prices[pattern_start] * 1.03
    high[pattern_start] = close[pattern_start] * 1.01
    low[pattern_start] = open_prices[pattern_start] * 0.998
    volume[pattern_start] = volume[pattern_start-1] * 1.5
    
    # Second bullish candle (medium body with upper shadow)
    open_prices[pattern_start+1] = open_prices[pattern_start] * 1.005
    close[pattern_start+1] = open_prices[pattern_start+1] * 1.02
    high[pattern_start+1] = close[pattern_start+1] * 1.015
    low[pattern_start+1] = open_prices[pattern_start+1] * 0.998
    volume[pattern_start+1] = volume[pattern_start] * 0.9
    
    # Third bullish candle (small body with large upper shadow)
    open_prices[pattern_start+2] = open_prices[pattern_start+1] * 1.002
    close[pattern_start+2] = open_prices[pattern_start+2] * 1.005
    high[pattern_start+2] = close[pattern_start+2] * 1.03
    low[pattern_start+2] = open_prices[pattern_start+2] * 0.999
    volume[pattern_start+2] = volume[pattern_start+1] * 1.4
    
    # Create DataFrame
    df = pd.DataFrame({
        'date': date_range,
        'open': open_prices,
        'high': high,
        'low': low,
        'close': close,
        'volume': volume
    })
    
    df.set_index('date', inplace=True)
    return df

def plot_candlestick(data, signals):
    """Plot candlestick chart with signals"""
    plt.figure(figsize=(15, 8))
    
    # Convert index to datetime if it's not already
    if not isinstance(data.index, pd.DatetimeIndex):
        data.index = pd.to_datetime(data.index)
    
    # Plot candlesticks
    for i in range(len(data)):
        date = data.index[i]
        op, hi, lo, cl = data.iloc[i][['open', 'high', 'low', 'close']]
        
        # Color candle based on price movement
        color = 'green' if cl >= op else 'red'
        
        # Plot candle body
        plt.plot([date, date], [op, cl], color=color, linewidth=3)
        
        # Plot high/low wicks
        plt.plot([date, date], [lo, min(op, cl)], color=color, linewidth=1)
        plt.plot([date, date], [max(op, cl), hi], color=color, linewidth=1)
    
    # Plot signals
    buy_signals = data[signals == 1]
    sell_signals = data[signals == -1]
    
    if not buy_signals.empty:
        plt.scatter(buy_signals.index, buy_signals['low']*0.99, 
                   marker='^', color='lime', s=100, label='Buy Signal')
    
    if not sell_signals.empty:
        plt.scatter(sell_signals.index, sell_signals['high']*1.01, 
                   marker='v', color='red', s=100, label='Sell Signal')
    
    plt.title('Inverted Three Red Pattern Detection')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig('inverted_three_red_pattern.png')
    print("Chart saved as 'inverted_three_red_pattern.png'")

def main():
    # Generate sample data
    data = generate_sample_data(days=60)
    
    # Initialize strategy
    strategy = InvertedThreeRedStrategy()
    
    # Generate signals
    signals = strategy.generate_signals(data)
    
    # Print results
    signal_days = data[signals != 0]
    print(f"Found {len(signal_days)} signal(s):")
    for day, signal in zip(signal_days.index, signals[signals != 0]):
        signal_type = "BUY" if signal == 1 else "SELL"
        print(f"Date: {day}, Signal: {signal_type}")
    
    # Plot and save results
    plot_candlestick(data, signals)

if __name__ == "__main__":
    main() 