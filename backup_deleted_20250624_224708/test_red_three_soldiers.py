import pandas as pd
import numpy as np
import sys
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as patches
from datetime import datetime, timedelta

# Add backend directory to path
sys.path.append('.')
from backend.strategies import get_strategy

def generate_sample_data(days=100):
    """Generate sample data with Red Three Soldiers patterns at different positions"""
    # Create date range
    date_range = [datetime.now() - timedelta(days=i) for i in range(days, 0, -1)]
    date_range = [d.strftime('%Y-%m-%d') for d in date_range]
    
    # Initialize with random price movements
    np.random.seed(42)  # For reproducibility
    close = 100 + np.random.randn(days).cumsum()
    
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
    
    # Pattern areas to track
    pattern_areas = {}
    
    # Create a low position Red Three Soldiers pattern (bottom reversal)
    # First create a downtrend
    low_start = 15
    for i in range(5, low_start):
        close[i] = close[i-1] * (1 - np.random.uniform(0.01, 0.02))
        open_prices[i] = close[i-1] * (1 + np.random.uniform(0, 0.005))
        high[i] = open_prices[i] * (1 + np.random.uniform(0.001, 0.01))
        low[i] = close[i] * (1 - np.random.uniform(0.01, 0.02))
        volume[i] = volume[i-1] * (1 - np.random.uniform(0, 0.1))
    
    # Then create the Red Three Soldiers pattern
    # First bullish candle
    open_prices[low_start] = close[low_start-1] * 0.99
    close[low_start] = open_prices[low_start] * 1.02
    high[low_start] = close[low_start] * 1.005
    low[low_start] = open_prices[low_start] * 0.995
    volume[low_start] = volume[low_start-1] * 1.3
    
    # Second bullish candle
    open_prices[low_start+1] = close[low_start] * 0.998
    close[low_start+1] = open_prices[low_start+1] * 1.025
    high[low_start+1] = close[low_start+1] * 1.007
    low[low_start+1] = open_prices[low_start+1] * 0.996
    volume[low_start+1] = volume[low_start] * 1.4
    
    # Third bullish candle
    open_prices[low_start+2] = close[low_start+1] * 0.999
    close[low_start+2] = open_prices[low_start+2] * 1.02
    high[low_start+2] = close[low_start+2] * 1.005
    low[low_start+2] = open_prices[low_start+2] * 0.997
    volume[low_start+2] = volume[low_start+1] * 1.5
    
    # Add confirmation candle (bullish follow-through)
    open_prices[low_start+3] = close[low_start+2] * 1.002
    close[low_start+3] = open_prices[low_start+3] * 1.03
    high[low_start+3] = close[low_start+3] * 1.01
    low[low_start+3] = open_prices[low_start+3] * 0.998
    volume[low_start+3] = volume[low_start+2] * 1.6
    
    # Record pattern area
    pattern_areas['low'] = {'start': low_start, 'end': low_start+2}
    
    # Create a middle position Red Three Soldiers pattern (continuation)
    mid_start = 45
    # First create some consolidation
    for i in range(mid_start-5, mid_start):
        close[i] = close[i-1] * (1 + np.random.uniform(-0.005, 0.005))
        open_prices[i] = close[i-1] * (1 + np.random.uniform(-0.005, 0.005))
        high[i] = max(open_prices[i], close[i]) * (1 + np.random.uniform(0.002, 0.008))
        low[i] = min(open_prices[i], close[i]) * (1 - np.random.uniform(0.002, 0.008))
        volume[i] = volume[i-1] * (1 + np.random.uniform(-0.1, 0.1))
    
    # Then create the Red Three Soldiers pattern
    # First bullish candle
    open_prices[mid_start] = close[mid_start-1] * 0.995
    close[mid_start] = open_prices[mid_start] * 1.02
    high[mid_start] = close[mid_start] * 1.005
    low[mid_start] = open_prices[mid_start] * 0.997
    volume[mid_start] = volume[mid_start-1] * 1.2
    
    # Second bullish candle
    open_prices[mid_start+1] = close[mid_start] * 0.997
    close[mid_start+1] = open_prices[mid_start+1] * 1.018
    high[mid_start+1] = close[mid_start+1] * 1.006
    low[mid_start+1] = open_prices[mid_start+1] * 0.998
    volume[mid_start+1] = volume[mid_start] * 1.1
    
    # Third bullish candle
    open_prices[mid_start+2] = close[mid_start+1] * 0.998
    close[mid_start+2] = open_prices[mid_start+2] * 1.015
    high[mid_start+2] = close[mid_start+2] * 1.004
    low[mid_start+2] = open_prices[mid_start+2] * 0.996
    volume[mid_start+2] = volume[mid_start+1] * 1.3
    
    # Record pattern area
    pattern_areas['middle'] = {'start': mid_start, 'end': mid_start+2}
    
    # Create a high position Red Three Soldiers pattern (warning signal)
    high_start = 75
    # First create an uptrend
    for i in range(high_start-10, high_start):
        close[i] = close[i-1] * (1 + np.random.uniform(0.005, 0.015))
        open_prices[i] = close[i-1] * (1 - np.random.uniform(0, 0.005))
        high[i] = close[i] * (1 + np.random.uniform(0.002, 0.008))
        low[i] = open_prices[i] * (1 - np.random.uniform(0.002, 0.008))
        volume[i] = volume[i-1] * (1 + np.random.uniform(0.05, 0.15))
    
    # Then create the Red Three Soldiers pattern with high volume (warning sign)
    # First bullish candle
    open_prices[high_start] = close[high_start-1] * 0.997
    close[high_start] = open_prices[high_start] * 1.02
    high[high_start] = close[high_start] * 1.008
    low[high_start] = open_prices[high_start] * 0.996
    volume[high_start] = volume[high_start-1] * 1.4
    
    # Second bullish candle
    open_prices[high_start+1] = close[high_start] * 0.999
    close[high_start+1] = open_prices[high_start+1] * 1.018
    high[high_start+1] = close[high_start+1] * 1.01
    low[high_start+1] = open_prices[high_start+1] * 0.997
    volume[high_start+1] = volume[high_start] * 1.6
    
    # Third bullish candle with very high volume (warning sign)
    open_prices[high_start+2] = close[high_start+1] * 1.001
    close[high_start+2] = open_prices[high_start+2] * 1.015
    high[high_start+2] = close[high_start+2] * 1.012
    low[high_start+2] = open_prices[high_start+2] * 0.998
    volume[high_start+2] = volume[high_start+1] * 2.5  # Extremely high volume
    
    # Add bearish reversal candle after the pattern
    open_prices[high_start+3] = close[high_start+2] * 1.005
    close[high_start+3] = open_prices[high_start+3] * 0.96
    high[high_start+3] = open_prices[high_start+3] * 1.008
    low[high_start+3] = close[high_start+3] * 0.995
    volume[high_start+3] = volume[high_start+2] * 1.2
    
    # Record pattern area
    pattern_areas['high'] = {'start': high_start, 'end': high_start+2}
    
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
    return df, pattern_areas

def plot_candlestick(data, signals, pattern_areas=None):
    """Plot candlestick chart with signals"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10), gridspec_kw={'height_ratios': [3, 1]})
    
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
        ax1.plot([date, date], [op, cl], color=color, linewidth=3)
        
        # Plot high/low wicks
        ax1.plot([date, date], [lo, min(op, cl)], color=color, linewidth=1)
        ax1.plot([date, date], [max(op, cl), hi], color=color, linewidth=1)
    
    # Highlight pattern areas if provided
    if pattern_areas:
        for position, area in pattern_areas.items():
            start_idx = area['start']
            end_idx = area['end']
            
            # Calculate price range for the pattern (with some padding)
            pattern_data = data.iloc[start_idx:end_idx+1]
            min_price = pattern_data['low'].min() * 0.995
            max_price = pattern_data['high'].max() * 1.005
            
            # Get date range for the pattern
            start_date = data.index[start_idx]
            end_date = data.index[end_idx]
            
            # Calculate the width correctly in date coordinates
            width = mdates.date2num(end_date) - mdates.date2num(start_date) + 0.8  # Add a bit more for visibility
            
            # Create rectangle patch
            rect = patches.Rectangle(
                (mdates.date2num(start_date), min_price),
                width, max_price - min_price,
                linewidth=1,
                edgecolor='blue',
                facecolor='blue',
                alpha=0.1
            )
            ax1.add_patch(rect)
            
            # Add label
            label_y = max_price
            ax1.text(mdates.date2num(start_date), label_y, f"{position.capitalize()} Position Pattern", 
                    fontsize=9, color='blue')
    
    # Plot buy/sell signals
    signals_series = pd.Series(signals, index=data.index)
    buy_signals = data[signals_series == 1]
    sell_signals = data[signals_series == -1]
    
    if not buy_signals.empty:
        ax1.scatter(buy_signals.index, buy_signals['low']*0.99, 
                   marker='^', color='lime', s=100, label='Buy Signal')
    
    if not sell_signals.empty:
        ax1.scatter(sell_signals.index, sell_signals['high']*1.01, 
                   marker='v', color='red', s=100, label='Sell Signal')
    
    # Plot volume
    volume_data = data['volume']
    ax2.bar(data.index, volume_data, color='skyblue', alpha=0.7)
    ax2.set_ylabel('Volume')
    
    # Add a 5-day and 10-day moving average on the chart
    ma5 = data['close'].rolling(window=5).mean()
    ma10 = data['close'].rolling(window=10).mean()
    ax1.plot(data.index, ma5, color='blue', linewidth=1, label='5-day MA')
    ax1.plot(data.index, ma10, color='red', linewidth=1, label='10-day MA')
    
    # Add labels and title
    ax1.set_title('Red Three Soldiers Pattern Detection')
    ax1.set_ylabel('Price')
    ax1.grid(True, alpha=0.3)
    ax2.grid(True, alpha=0.3)
    
    # Format date on x-axis
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    
    # Rotate date labels for better visibility
    fig.autofmt_xdate()
    
    # Add legend
    ax1.legend()
    
    plt.tight_layout()
    plt.savefig('red_three_soldiers_pattern.png')
    print("Chart saved as 'red_three_soldiers_pattern.png'")

def main():
    # Generate sample data
    data, pattern_areas = generate_sample_data(days=100)
    
    # Initialize strategy
    strategy = get_strategy('red_three_soldiers')
    
    # Modify some parameters to make pattern detection more sensitive
    custom_params = strategy.get_default_parameters()
    custom_params['downtrend_threshold'] = 0.03  # Lower the downtrend threshold
    custom_params['min_total_increase'] = 0.03   # Reduce minimum increase requirement
    
    strategy = get_strategy('red_three_soldiers', custom_params)
    
    # Generate signals
    signals = strategy.generate_signals(data)
    
    # Print results
    signals_series = pd.Series(signals, index=data.index)
    signal_days = data[signals_series != 0]
    print(f"Found {len(signal_days)} signal(s):")
    for day, signal in zip(signal_days.index, signals_series[signals_series != 0]):
        signal_type = "BUY" if signal == 1 else "SELL"
        print(f"Date: {day}, Signal: {signal_type}")
    
    # Plot and save results
    plot_candlestick(data, signals, pattern_areas)
    
    print("\n红三兵 (Red Three Soldiers) Pattern Analysis:")
    print("--------------------------------------------")
    print("The Red Three Soldiers pattern consists of three consecutive bullish candles")
    print("with similar body size, minimal upper shadows, and increasing closing prices.")
    print("\nSignal characteristics:")
    print("- Low position: Strong BUY signal (bottom reversal)")
    print("- Mid position: Continue holding or add positions (continuation)")
    print("- High position: Warning sign when volume is excessive (potential exhaustion)")
    print("\nConfirmation elements:")
    print("- Volume should gradually increase or remain stable")
    print("- Position relative to trend and moving averages")
    print("- Technical indicators (MACD golden cross, RSI)")
    print("\nRisk management suggestions:")
    print("- Set stop loss at the lowest point of the pattern")
    print("- Target profit at previous resistance levels or using measured move")
    print("- Be cautious of high-volume Red Three Soldiers in extended uptrends")

if __name__ == "__main__":
    main() 