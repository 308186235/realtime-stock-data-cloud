import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as patches
from datetime import datetime, timedelta

def generate_comparison_data(days=150):
    """Generate sample data with both patterns for comparison"""
    print("Generating comparison data...")
    
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
    
    # SECTION 1: DOWNTREND → RED THREE SOLDIERS (REVERSAL) → UPTREND
    section1_start = 25
    section1_end = 60
    
    # Create downtrend
    for i in range(section1_start, section1_start + 15):
        close[i] = close[i-1] * (1 - np.random.uniform(0.005, 0.015))
        open_prices[i] = close[i-1] * (1 + np.random.uniform(0, 0.005))
        high[i] = open_prices[i] * (1 + np.random.uniform(0.001, 0.01))
        low[i] = close[i] * (1 - np.random.uniform(0.005, 0.015))
        volume[i] = volume[i-1] * (1 - np.random.uniform(0, 0.1))
    
    # Create Red Three Soldiers pattern
    rts_start = section1_start + 15
    
    # First bullish candle
    open_prices[rts_start] = close[rts_start-1] * 0.99
    close[rts_start] = open_prices[rts_start] * 1.02
    high[rts_start] = close[rts_start] * 1.005
    low[rts_start] = open_prices[rts_start] * 0.995
    volume[rts_start] = volume[rts_start-1] * 1.3
    
    # Second bullish candle
    open_prices[rts_start+1] = close[rts_start] * 0.998
    close[rts_start+1] = open_prices[rts_start+1] * 1.025
    high[rts_start+1] = close[rts_start+1] * 1.007
    low[rts_start+1] = open_prices[rts_start+1] * 0.996
    volume[rts_start+1] = volume[rts_start] * 1.4
    
    # Third bullish candle
    open_prices[rts_start+2] = close[rts_start+1] * 0.999
    close[rts_start+2] = open_prices[rts_start+2] * 1.02
    high[rts_start+2] = close[rts_start+2] * 1.005
    low[rts_start+2] = open_prices[rts_start+2] * 0.997
    volume[rts_start+2] = volume[rts_start+1] * 1.5
    
    # Record pattern area
    pattern_areas['red_three_soldiers'] = {'start': rts_start, 'end': rts_start+2}
    
    # Create subsequent uptrend
    for i in range(rts_start+3, section1_end):
        close[i] = close[i-1] * (1 + np.random.uniform(0.005, 0.015))
        open_prices[i] = close[i-1] * (1 - np.random.uniform(0, 0.005))
        high[i] = close[i] * (1 + np.random.uniform(0.002, 0.01))
        low[i] = open_prices[i] * (1 - np.random.uniform(0.002, 0.01))
        volume[i] = volume[i-1] * (1 + np.random.uniform(0, 0.1))
    
    # SECTION 2: UPTREND → INVERTED THREE RED (TOP REVERSAL) → DOWNTREND
    section2_start = 80
    section2_end = 115
    
    # Create uptrend
    for i in range(section2_start, section2_start + 15):
        close[i] = close[i-1] * (1 + np.random.uniform(0.005, 0.015))
        open_prices[i] = close[i-1] * (1 - np.random.uniform(0, 0.005))
        high[i] = close[i] * (1 + np.random.uniform(0.002, 0.01))
        low[i] = open_prices[i] * (1 - np.random.uniform(0.002, 0.01))
        volume[i] = volume[i-1] * (1 + np.random.uniform(0, 0.1))
    
    # Create Inverted Three Red pattern
    itr_start = section2_start + 15
    
    # First bullish candle (large body)
    open_prices[itr_start] = close[itr_start-1] * 0.995
    close[itr_start] = open_prices[itr_start] * 1.03
    high[itr_start] = close[itr_start] * 1.01
    low[itr_start] = open_prices[itr_start] * 0.998
    volume[itr_start] = volume[itr_start-1] * 1.5
    
    # Second bullish candle (medium body with upper shadow)
    open_prices[itr_start+1] = open_prices[itr_start] * 1.005
    close[itr_start+1] = open_prices[itr_start+1] * 1.02
    high[itr_start+1] = close[itr_start+1] * 1.015
    low[itr_start+1] = open_prices[itr_start+1] * 0.998
    volume[itr_start+1] = volume[itr_start] * 0.9
    
    # Third bullish candle (small body with large upper shadow)
    open_prices[itr_start+2] = open_prices[itr_start+1] * 1.002
    close[itr_start+2] = open_prices[itr_start+2] * 1.005
    high[itr_start+2] = close[itr_start+2] * 1.03
    low[itr_start+2] = open_prices[itr_start+2] * 0.999
    volume[itr_start+2] = volume[itr_start+1] * 1.4
    
    # Record pattern area
    pattern_areas['inverted_three_red'] = {'start': itr_start, 'end': itr_start+2}
    
    # Create subsequent downtrend
    for i in range(itr_start+3, section2_end):
        close[i] = close[i-1] * (1 - np.random.uniform(0.005, 0.015))
        open_prices[i] = close[i-1] * (1 + np.random.uniform(0, 0.005))
        high[i] = open_prices[i] * (1 + np.random.uniform(0.001, 0.01))
        low[i] = close[i] * (1 - np.random.uniform(0.005, 0.015))
        volume[i] = volume[i-1] * (1 - np.random.uniform(0, 0.1))
    
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

def plot_comparative_analysis(data, pattern_areas):
    """Plot candlestick chart with highlighted patterns for comparison"""
    print("Plotting comparative analysis...")
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12), gridspec_kw={'height_ratios': [3, 1]})
    
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
    
    # Highlight pattern areas
    if 'red_three_soldiers' in pattern_areas:
        area = pattern_areas['red_three_soldiers']
        start_idx, end_idx = area['start'], area['end']
        
        # Calculate price range for the pattern (with some padding)
        pattern_data = data.iloc[start_idx:end_idx+1]
        min_price = pattern_data['low'].min() * 0.995
        max_price = pattern_data['high'].max() * 1.005
        
        # Get date range for the pattern
        start_date = data.index[start_idx]
        end_date = data.index[end_idx]
        
        # Calculate the width correctly in date coordinates
        width = mdates.date2num(end_date) - mdates.date2num(start_date) + 0.8
        
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
        
        # Add label and annotation
        label_y = max_price
        ax1.text(mdates.date2num(start_date), label_y, "Red Three Soldiers", 
                fontsize=10, color='blue', weight='bold')
        
        # Add explanation annotation
        ax1.annotate(
            "Bullish Reversal Pattern\n- Similar body size\n- Minimal upper shadows\n- Increasing volume",
            xy=(mdates.date2num(end_date), min_price),
            xytext=(mdates.date2num(end_date) + 5, min_price),
            fontsize=9,
            bbox=dict(boxstyle="round,pad=0.5", facecolor='lightblue', alpha=0.5),
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0.3")
        )
    
    if 'inverted_three_red' in pattern_areas:
        area = pattern_areas['inverted_three_red']
        start_idx, end_idx = area['start'], area['end']
        
        # Calculate price range for the pattern (with some padding)
        pattern_data = data.iloc[start_idx:end_idx+1]
        min_price = pattern_data['low'].min() * 0.995
        max_price = pattern_data['high'].max() * 1.005
        
        # Get date range for the pattern
        start_date = data.index[start_idx]
        end_date = data.index[end_idx]
        
        # Calculate the width correctly in date coordinates
        width = mdates.date2num(end_date) - mdates.date2num(start_date) + 0.8
        
        # Create rectangle patch
        rect = patches.Rectangle(
            (mdates.date2num(start_date), min_price),
            width, max_price - min_price,
            linewidth=1,
            edgecolor='orange',
            facecolor='orange',
            alpha=0.1
        )
        ax1.add_patch(rect)
        
        # Add label and annotation
        label_y = max_price
        ax1.text(mdates.date2num(start_date), label_y, "Inverted Three Red", 
                fontsize=10, color='orange', weight='bold')
        
        # Add explanation annotation
        ax1.annotate(
            "Bearish Reversal Pattern\n- Decreasing body size\n- Increasing upper shadows\n- Volume pattern changes",
            xy=(mdates.date2num(end_date), min_price),
            xytext=(mdates.date2num(end_date) + 5, min_price),
            fontsize=9,
            bbox=dict(boxstyle="round,pad=0.5", facecolor='lightsalmon', alpha=0.5),
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0.3")
        )
    
    # Plot volume
    volume_data = data['volume']
    ax2.bar(data.index, volume_data, color='skyblue', alpha=0.7)
    ax2.set_ylabel('Volume')
    
    # Add moving averages
    ma5 = data['close'].rolling(window=5).mean()
    ma20 = data['close'].rolling(window=20).mean()
    ax1.plot(data.index, ma5, color='blue', linewidth=1, label='5-day MA')
    ax1.plot(data.index, ma20, color='red', linewidth=1, label='20-day MA')
    
    # Add labels and title
    ax1.set_title('Comparative Analysis: Red Three Soldiers vs Inverted Three Red Patterns', fontsize=14)
    ax1.set_ylabel('Price')
    ax1.grid(True, alpha=0.3)
    ax2.grid(True, alpha=0.3)
    
    # Format date on x-axis
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate()
    
    # Add legend
    ax1.legend()
    
    # Add educational box with pattern comparison
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.3)
    comparison_text = (
        "PATTERN COMPARISON\n"
        "=====================\n"
        "Red Three Soldiers:\n"
        "- Bullish reversal pattern\n"
        "- Similar body sizes\n"
        "- Minimal upper shadows\n"
        "- Steady or increasing volume\n"
        "- Strong buying pressure\n"
        "\n"
        "Inverted Three Red:\n"
        "- Bearish reversal pattern\n"
        "- Decreasing body sizes\n"
        "- Increasing upper shadows\n"
        "- Volume often decreases or spikes\n"
        "- Weakening buying pressure"
    )
    
    # Position the text box in figure coords to stay in place regardless of data
    ax1.text(0.02, 0.98, comparison_text, transform=ax1.transAxes, fontsize=10,
             verticalalignment='top', bbox=props)
    
    plt.tight_layout()
    plt.savefig('candlestick_pattern_comparison.png')
    print("Chart saved as 'candlestick_pattern_comparison.png'")

def main():
    print("Starting pattern comparison...")
    
    # Generate sample data with both patterns
    data, pattern_areas = generate_comparison_data(days=150)
    print(f"Generated data with shape: {data.shape}")
    
    # Plot comparative analysis
    plot_comparative_analysis(data, pattern_areas)
    
    # Summarize pattern characteristics
    print("\nPattern Comparison Summary:")
    print("=" * 50)
    print("\nRed Three Soldiers Pattern:")
    print("-" * 30)
    print("• Shape: Three consecutive bullish candles with similar body size")
    print("• Shadows: Minimal upper shadows (strong buyer control)")
    print("• Volume: Gradually increasing or steady volume")
    print("• Position: Most reliable at the end of downtrends")
    print("• Meaning: Bullish reversal - beginning of a new uptrend")
    print("• Risk Management: Stop loss at pattern's lowest point")
    
    print("\nInverted Three Red Pattern:")
    print("-" * 30)
    print("• Shape: Three consecutive bullish candles with decreasing body size")
    print("• Shadows: Increasing upper shadows (selling pressure at highs)")
    print("• Volume: Either decreasing (exhaustion) or final day surge with long upper shadow")
    print("• Position: Most reliable at market tops after strong uptrends")
    print("• Meaning: Bearish reversal - exhaustion of buying pressure")
    print("• Risk Management: Reduce positions, especially in high market positions")
    
    print("\nKey Differences:")
    print("-" * 30)
    print("• Body Size: Similar size (RTS) vs. Decreasing size (ITR)")
    print("• Upper Shadows: Minimal (RTS) vs. Increasing length (ITR)")
    print("• Market Sentiment: Strengthening buyers (RTS) vs. Weakening buyers (ITR)")
    print("• Reliability: Higher in respective position (low for RTS, high for ITR)")

if __name__ == "__main__":
    main()