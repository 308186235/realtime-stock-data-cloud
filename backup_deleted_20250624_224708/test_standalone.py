import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import matplotlib.dates as mdates
import matplotlib.patches as patches
from inverted_three_red_strategy_standalone import InvertedThreeRedStrategy

def generate_sample_data(days=100):
    """Generate sample data with an inverted three red pattern"""
    # Create date range
    date_range = [datetime.now() - timedelta(days=i) for i in range(days, 0, -1)]
    date_range = [d.strftime('%Y-%m-%d') for d in date_range]
    
    # Initialize with random price movements
    np.random.seed(42)  # For reproducibility
    close = 100 + np.random.randn(days).cumsum()
    
    # Ensure overall uptrend for the first part
    for i in range(1, int(days * 0.8)):
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
    
    # Create inverted three red pattern near the end (high position)
    high_pattern_start = days - 20
    
    # Create strong uptrend before the pattern
    for i in range(high_pattern_start-10, high_pattern_start):
        close[i] = close[i-1] * (1 + np.random.uniform(0.01, 0.025))
        open_prices[i] = close[i-1] * (1 - np.random.uniform(0, 0.01))
        high[i] = close[i] * (1 + np.random.uniform(0.005, 0.015))
        low[i] = open_prices[i] * (1 - np.random.uniform(0, 0.01))
        volume[i] = volume[i-1] * (1 + np.random.uniform(0.05, 0.2))
    
    # First bullish candle (large body)
    open_prices[high_pattern_start] = close[high_pattern_start-1] * 0.99
    close[high_pattern_start] = open_prices[high_pattern_start] * 1.04
    high[high_pattern_start] = close[high_pattern_start] * 1.01
    low[high_pattern_start] = open_prices[high_pattern_start] * 0.998
    volume[high_pattern_start] = volume[high_pattern_start-1] * 1.5
    
    # Second bullish candle (medium body with some upper shadow)
    open_prices[high_pattern_start+1] = close[high_pattern_start] * 0.995
    close[high_pattern_start+1] = open_prices[high_pattern_start+1] * 1.025
    high[high_pattern_start+1] = close[high_pattern_start+1] * 1.02
    low[high_pattern_start+1] = open_prices[high_pattern_start+1] * 0.998
    volume[high_pattern_start+1] = volume[high_pattern_start] * 0.9
    
    # Third bullish candle (small body with large upper shadow)
    open_prices[high_pattern_start+2] = close[high_pattern_start+1] * 0.998
    close[high_pattern_start+2] = open_prices[high_pattern_start+2] * 1.01
    high[high_pattern_start+2] = close[high_pattern_start+2] * 1.03
    low[high_pattern_start+2] = open_prices[high_pattern_start+2] * 0.999
    volume[high_pattern_start+2] = volume[high_pattern_start+1] * 1.5
    
    # Create a confirmation candle (bearish)
    open_prices[high_pattern_start+3] = close[high_pattern_start+2]
    close[high_pattern_start+3] = open_prices[high_pattern_start+3] * 0.97
    high[high_pattern_start+3] = open_prices[high_pattern_start+3] * 1.01
    low[high_pattern_start+3] = close[high_pattern_start+3] * 0.995
    volume[high_pattern_start+3] = volume[high_pattern_start+2] * 1.3
    
    # Create another inverted three red pattern in the middle (mid position)
    mid_pattern_start = int(days * 0.5)
    
    # First bullish candle (large body)
    open_prices[mid_pattern_start] = close[mid_pattern_start-1] * 0.99
    close[mid_pattern_start] = open_prices[mid_pattern_start] * 1.03
    high[mid_pattern_start] = close[mid_pattern_start] * 1.01
    low[mid_pattern_start] = open_prices[mid_pattern_start] * 0.998
    volume[mid_pattern_start] = volume[mid_pattern_start-1] * 1.4
    
    # Second bullish candle (medium body)
    open_prices[mid_pattern_start+1] = close[mid_pattern_start] * 0.995
    close[mid_pattern_start+1] = open_prices[mid_pattern_start+1] * 1.02
    high[mid_pattern_start+1] = close[mid_pattern_start+1] * 1.01
    low[mid_pattern_start+1] = open_prices[mid_pattern_start+1] * 0.998
    volume[mid_pattern_start+1] = volume[mid_pattern_start] * 0.8
    
    # Third bullish candle (small body with upper shadow)
    open_prices[mid_pattern_start+2] = close[mid_pattern_start+1] * 0.998
    close[mid_pattern_start+2] = open_prices[mid_pattern_start+2] * 1.008
    high[mid_pattern_start+2] = close[mid_pattern_start+2] * 1.025
    low[mid_pattern_start+2] = open_prices[mid_pattern_start+2] * 0.999
    volume[mid_pattern_start+2] = volume[mid_pattern_start+1] * 0.7
    
    # Create a low position pattern
    low_pattern_start = int(days * 0.2)
    
    # Create downtrend before the pattern
    for i in range(low_pattern_start-10, low_pattern_start):
        close[i] = close[i-1] * (1 - np.random.uniform(0.01, 0.02))
        open_prices[i] = close[i-1] * (1 + np.random.uniform(0, 0.01))
        high[i] = open_prices[i] * (1 + np.random.uniform(0, 0.01))
        low[i] = close[i] * (1 - np.random.uniform(0.005, 0.015))
        volume[i] = volume[i-1] * (1 - np.random.uniform(0, 0.1))
    
    # First bullish candle (large body)
    open_prices[low_pattern_start] = close[low_pattern_start-1] * 0.99
    close[low_pattern_start] = open_prices[low_pattern_start] * 1.035
    high[low_pattern_start] = close[low_pattern_start] * 1.005
    low[low_pattern_start] = open_prices[low_pattern_start] * 0.998
    volume[low_pattern_start] = volume[low_pattern_start-1] * 0.9
    
    # Second bullish candle (medium body)
    open_prices[low_pattern_start+1] = close[low_pattern_start] * 0.998
    close[low_pattern_start+1] = open_prices[low_pattern_start+1] * 1.025
    high[low_pattern_start+1] = close[low_pattern_start+1] * 1.01
    low[low_pattern_start+1] = open_prices[low_pattern_start+1] * 0.998
    volume[low_pattern_start+1] = volume[low_pattern_start] * 0.8
    
    # Third bullish candle (small body with upper shadow)
    open_prices[low_pattern_start+2] = close[low_pattern_start+1] * 0.998
    close[low_pattern_start+2] = open_prices[low_pattern_start+2] * 1.01
    high[low_pattern_start+2] = close[low_pattern_start+2] * 1.025
    low[low_pattern_start+2] = open_prices[low_pattern_start+2] * 0.999
    volume[low_pattern_start+2] = volume[low_pattern_start+1] * 0.7
    
    # Create DataFrame
    df = pd.DataFrame({
        'date': date_range,
        'open': open_prices,
        'high': high,
        'low': low,
        'close': close,
        'volume': volume
    })
    
    # Create metadata to highlight pattern areas in chart
    pattern_areas = {
        'high': {'start': high_pattern_start, 'end': high_pattern_start+2},
        'mid': {'start': mid_pattern_start, 'end': mid_pattern_start+2},
        'low': {'start': low_pattern_start, 'end': low_pattern_start+2}
    }
    
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
            start_date = mdates.date2num(data.index[start_idx])
            end_date = mdates.date2num(data.index[end_idx])
            
            # Calculate the width correctly in date coordinates
            width = end_date - start_date + 0.8  # Add a bit more for visibility
            
            # Create rectangle patch
            rect = patches.Rectangle(
                (start_date, min_price),
                width, max_price - min_price,
                linewidth=1,
                edgecolor='orange',
                facecolor='orange',
                alpha=0.1
            )
            ax1.add_patch(rect)
            
            # Add label
            label_y = max_price
            ax1.text(start_date, label_y, f"{position.capitalize()} Pattern", 
                    fontsize=9, color='orange')
    
    # Fix the boolean indexing issue by ensuring signals has the same index as data
    signals_series = pd.Series(signals, index=data.index)
    
    # Plot signals
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
    
    # Add a 5-day moving average on the chart
    ma5 = data['close'].rolling(window=5).mean()
    ax1.plot(data.index, ma5, color='blue', linewidth=1, label='5-day MA')
    
    # Add labels and title
    ax1.set_title('Inverted Three Red Pattern Detection')
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
    plt.savefig('inverted_three_red_pattern.png')
    print("Chart saved as 'inverted_three_red_pattern.png'")

def main():
    # Generate sample data
    data, pattern_areas = generate_sample_data(days=100)
    
    # Initialize strategy
    strategy = InvertedThreeRedStrategy()
    
    # Modify some parameters to make pattern detection more sensitive
    custom_params = strategy.get_default_parameters()
    custom_params['uptrend_threshold'] = 0.03  # Lower the uptrend threshold
    custom_params['min_upper_shadow_ratio'] = 0.8  # Reduce upper shadow requirement
    custom_params['body_size_decrease_ratio'] = 0.7  # Make body size decrease requirement more forgiving
    
    strategy = InvertedThreeRedStrategy(custom_params)
    
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
    
    print("\n倒三红形 (Inverted Three Red) Pattern Analysis:")
    print("--------------------------------------------")
    print("The Inverted Three Red pattern consists of three consecutive bullish candles")
    print("with decreasing body size and increasing upper shadows.")
    print("\nSignal characteristics:")
    print("- High position: SELL signal (potential stalling or reversal)")
    print("- Mid position: Variable (hold or reduce positions)")
    print("- Low position: Potential BUY signal (for a reversal)")
    print("\nConfirmation elements:")
    print("- Volume characteristics (decreasing or sudden surge with upper shadow)")
    print("- Position relative to trend and moving averages")
    print("- Technical indicators (MACD, RSI)")

if __name__ == "__main__":
    main() 