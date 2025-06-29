import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as patches
from datetime import datetime, timedelta
import sys

class SimpleThreeWhiteSoldiersDetector:
    """Simple Three White Soldiers pattern detector"""
    
    def __init__(self):
        self.name = "三个白武士检测器"
        self.description = "检测三个白武士K线形态"
        
        # Default parameters
        self.params = {
            'min_body_size_ratio': 0.7,      # Minimum body size to total range ratio
            'max_upper_shadow_ratio': 0.1,   # Maximum upper shadow to body ratio
            'min_price_increase': 0.03,      # Minimum daily price increase (3%)
            'max_price_increase': 0.06,      # Maximum daily price increase (6%)
            'volume_increase_threshold': 0.3, # Volume increase threshold (30%)
            'min_pattern_length': 3,         # Pattern length (3 candles)
            'min_total_increase': 0.09       # Minimum total price increase over pattern (9%)
        }
    
    def detect_pattern(self, data):
        """
        Detect Three White Soldiers pattern in price data
        
        Args:
            data (pd.DataFrame): OHLCV data
            
        Returns:
            list: List of pattern detection dates
        """
        print("Analyzing data for Three White Soldiers patterns...")
        
        # Create a copy of the data
        df = data.copy()
        
        # Calculate candle features
        df['body_size'] = abs(df['close'] - df['open'])
        df['total_range'] = df['high'] - df['low']
        df['body_size_ratio'] = df['body_size'] / df['total_range'].where(df['total_range'] != 0, 0.01)
        df['is_bullish'] = df['close'] > df['open']
        df['upper_shadow'] = df['high'] - df[['open', 'close']].max(axis=1)
        df['upper_shadow_ratio'] = df.apply(
            lambda x: x['upper_shadow'] / x['body_size'] if x['body_size'] > 0 and x['is_bullish'] else 10, 
            axis=1
        )
        df['daily_return'] = df['close'].pct_change()
        
        # Volume features
        df['volume_5d_avg'] = df['volume'].rolling(window=5).mean()
        df['volume_ratio'] = df['volume'] / df['volume_5d_avg'].shift(1)
        
        # Detected patterns
        patterns = []
        signals = pd.Series(0, index=data.index)
        
        # Need at least pattern_length candles plus some history
        if len(df) < 10:
            print("Not enough data for pattern detection")
            return patterns, signals
        
        # Detect patterns
        for i in range(5, len(df) - self.params['min_pattern_length'] + 1):
            end_idx = i + self.params['min_pattern_length'] - 1
            window = df.iloc[i:end_idx+1]
            
            # Check for 3 consecutive bullish candles
            if not window['is_bullish'].all():
                continue
            
            # Check if closing prices are increasing
            closes = window['close'].values
            if not all(closes[j] > closes[j-1] for j in range(1, len(window))):
                continue
            
            # Check body size ratio (at least 70% of total range - stricter than Red Three Soldiers)
            if not all(window['body_size_ratio'] >= self.params['min_body_size_ratio']):
                continue
            
            # Check for minimal upper shadows (stricter than Red Three Soldiers)
            if not all(window['upper_shadow_ratio'] <= self.params['max_upper_shadow_ratio']):
                continue
            
            # Check daily returns (3-6% gains - larger than Red Three Soldiers)
            daily_returns = window['daily_return'].values[1:]  # Skip first (can't calculate return)
            if not all(self.params['min_price_increase'] <= ret <= self.params['max_price_increase'] 
                      for ret in daily_returns if not np.isnan(ret)):
                continue
            
            # Check total price increase (minimum 9% across 3 candles)
            total_increase = (window['close'].iloc[-1] - window['open'].iloc[0]) / window['open'].iloc[0]
            if total_increase < self.params['min_total_increase']:
                continue
            
            # Check volume characteristics (at least two days with increased volume)
            volume_ratios = window['volume_ratio'].values
            increased_volume_days = sum(ratio >= 1 + self.params['volume_increase_threshold'] 
                                       for ratio in volume_ratios if not np.isnan(ratio))
            if increased_volume_days < 2:  # Stricter than Red Three Soldiers
                continue
            
            # Pattern detected at the last candle of the window
            pattern_date = window.index[-1]
            patterns.append(pattern_date)
            
            # Generate signal (1 for buy)
            signals.loc[pattern_date] = 1
            
            print(f"Pattern detected at {pattern_date}")
        
        print(f"Total patterns detected: {len(patterns)}")
        return patterns, signals

def generate_sample_data(days=100):
    """Generate sample data with Three White Soldiers patterns"""
    print("Generating sample data...")
    
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
    
    # Create a low position Three White Soldiers pattern (bottom reversal)
    # First create a downtrend
    low_start = 20
    for i in range(10, low_start):
        close[i] = close[i-1] * (1 - np.random.uniform(0.01, 0.02))
        open_prices[i] = close[i-1] * (1 + np.random.uniform(0, 0.005))
        high[i] = open_prices[i] * (1 + np.random.uniform(0.001, 0.01))
        low[i] = close[i] * (1 - np.random.uniform(0.01, 0.02))
        volume[i] = volume[i-1] * (1 - np.random.uniform(0, 0.1))
    
    # Then create the Three White Soldiers pattern
    # First bullish candle
    open_prices[low_start] = close[low_start-1] * 0.99
    close[low_start] = open_prices[low_start] * 1.03  # 3% gain
    high[low_start] = close[low_start] * 1.003  # minimal upper shadow
    low[low_start] = open_prices[low_start] * 0.995
    volume[low_start] = volume[low_start-1] * 1.3
    
    # Second bullish candle
    open_prices[low_start+1] = close[low_start] * 0.998
    close[low_start+1] = open_prices[low_start+1] * 1.04  # 4% gain
    high[low_start+1] = close[low_start+1] * 1.004  # minimal upper shadow
    low[low_start+1] = open_prices[low_start+1] * 0.996
    volume[low_start+1] = volume[low_start] * 1.4
    
    # Third bullish candle
    open_prices[low_start+2] = close[low_start+1] * 0.999
    close[low_start+2] = open_prices[low_start+2] * 1.035  # 3.5% gain
    high[low_start+2] = close[low_start+2] * 1.003  # minimal upper shadow
    low[low_start+2] = open_prices[low_start+2] * 0.997
    volume[low_start+2] = volume[low_start+1] * 1.5
    
    # Record pattern area
    pattern_areas['low'] = {'start': low_start, 'end': low_start+2}
    
    # Create a high position Three White Soldiers pattern with high volume (warning sign)
    high_start = 70
    # First create an uptrend
    for i in range(high_start-10, high_start):
        close[i] = close[i-1] * (1 + np.random.uniform(0.005, 0.015))
        open_prices[i] = close[i-1] * (1 - np.random.uniform(0, 0.005))
        high[i] = close[i] * (1 + np.random.uniform(0.002, 0.008))
        low[i] = open_prices[i] * (1 - np.random.uniform(0.002, 0.008))
        volume[i] = volume[i-1] * (1 + np.random.uniform(0.05, 0.15))
    
    # Create Three White Soldiers pattern with high volume
    # First bullish candle
    open_prices[high_start] = close[high_start-1] * 0.997
    close[high_start] = open_prices[high_start] * 1.035  # 3.5% gain
    high[high_start] = close[high_start] * 1.004  # minimal upper shadow
    low[high_start] = open_prices[high_start] * 0.996
    volume[high_start] = volume[high_start-1] * 1.4
    
    # Second bullish candle
    open_prices[high_start+1] = close[high_start] * 0.999
    close[high_start+1] = open_prices[high_start+1] * 1.03  # 3% gain
    high[high_start+1] = close[high_start+1] * 1.005  # minimal upper shadow
    low[high_start+1] = open_prices[high_start+1] * 0.997
    volume[high_start+1] = volume[high_start+1] * 1.6
    
    # Third bullish candle with minimal upper shadow
    open_prices[high_start+2] = close[high_start+1] * 1.001
    close[high_start+2] = open_prices[high_start+2] * 1.04  # 4% gain
    high[high_start+2] = close[high_start+2] * 1.003  # minimal upper shadow
    low[high_start+2] = open_prices[high_start+2] * 0.998
    volume[high_start+2] = volume[high_start+1] * 2.5  # Very high volume
    
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
    print(f"Sample data generated with shape: {df.shape}")
    
    return df, pattern_areas

def plot_candlestick(data, signals, pattern_areas=None, patterns=None):
    """Plot candlestick chart with signals"""
    print("Plotting candlestick chart...")
    
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
        print(f"Highlighting {len(pattern_areas)} pattern areas")
        
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
            width = mdates.date2num(end_date) - mdates.date2num(start_date) + 0.8
            
            # Create rectangle patch
            rect = plt.Rectangle(
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
            ax1.text(mdates.date2num(start_date), label_y, f"{position.capitalize()} Position", 
                    fontsize=9, color='blue')
    
    # Highlight detected patterns
    if patterns:
        print(f"Highlighting {len(patterns)} detected patterns")
        
        for date in patterns:
            ax1.axvline(x=date, color='purple', linestyle='--', alpha=0.6)
            ax1.text(mdates.date2num(date), data.loc[date, 'low'] * 0.98, 
                     "Pattern\nDetected", 
                     fontsize=8, 
                     color='purple',
                     ha='center')
    
    # Plot buy signals
    signal_dates = signals[signals != 0].index
    if len(signal_dates) > 0:
        print(f"Plotting {len(signal_dates)} trading signals")
        
        ax1.scatter(signal_dates, 
                   [data.loc[date, 'low'] * 0.97 for date in signal_dates], 
                   marker='^', 
                   color='lime', 
                   s=100, 
                   label='Buy Signal')
    
    # Plot volume
    volume_data = data['volume']
    ax2.bar(data.index, volume_data, color='skyblue', alpha=0.7)
    ax2.set_ylabel('Volume')
    
    # Add a 5-day and 20-day moving average on the chart
    ma5 = data['close'].rolling(window=5).mean()
    ma20 = data['close'].rolling(window=20).mean()
    ax1.plot(data.index, ma5, color='blue', linewidth=1, label='5-day MA')
    ax1.plot(data.index, ma20, color='red', linewidth=1, label='20-day MA')
    
    # Add labels and title
    ax1.set_title('Three White Soldiers Pattern Detection')
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
    
    print("Saving chart...")
    
    plt.tight_layout()
    
    try:
        plt.savefig('three_white_soldiers_simple.png')
        print("Chart saved as 'three_white_soldiers_simple.png'")
    except Exception as e:
        print(f"Error saving chart: {e}")

def create_comparison_table():
    """Create comparison table between Red Three Soldiers and Three White Soldiers"""
    print("\nPattern Comparison - Red Three Soldiers vs Three White Soldiers:")
    print("=" * 60)
    print(f"{'Feature':<20} | {'Red Three Soldiers':<25} | {'Three White Soldiers':<25}")
    print("-" * 60)
    print(f"{'Candle Size':<20} | {'Smaller (1-3% gains)':<25} | {'Larger (3-6% gains)':<25}")
    print(f"{'Upper Shadow':<20} | {'Short (≤15% of body)':<25} | {'Very short (≤10% of body)':<25}")
    print(f"{'Volume Pattern':<20} | {'Moderate increase':<25} | {'Stronger increase (≥30%)':<25}")
    print(f"{'Total Increase':<20} | {'≥4% across 3 candles':<25} | {'≥9% across 3 candles':<25}")
    print(f"{'Signal Strength':<20} | {'Moderate':<25} | {'Strong':<25}")
    print(f"{'Position Size':<20} | {'30% at low positions':<25} | {'50% at low positions':<25}")
    print(f"{'Best Location':<20} | {'Low to mid position':<25} | {'Low position (reversal)':<25}")
    print(f"{'Warning Signs':<20} | {'High position + volume':<25} | {'High position + excess volume':<25}")
    print("=" * 60)

def main():
    print("Starting Three White Soldiers pattern detection test...")
    
    try:
        # Generate sample data
        data, pattern_areas = generate_sample_data(days=100)
        
        # Initialize detector
        detector = SimpleThreeWhiteSoldiersDetector()
        
        # Detect patterns
        patterns, signals = detector.detect_pattern(data)
        
        # Print results
        print(f"Found {len(patterns)} Three White Soldiers pattern(s):")
        for date in patterns:
            print(f"Date: {date}")
        
        # Plot and save results
        plot_candlestick(data, signals, pattern_areas, patterns)
        
        # Display comparison table
        create_comparison_table()
        
        print("\n三个白武士 (Three White Soldiers) Pattern Analysis:")
        print("--------------------------------------------")
        print("The Three White Soldiers pattern consists of three consecutive bullish candles")
        print("with medium to large body size (3-6% gains), minimal upper shadows, and increasing volume.")
        print("\nTrading implications:")
        print("- Strong bullish reversal signal at the end of downtrends")
        print("- Stronger signal and more decisive action than Red Three Soldiers")
        print("- More aggressive position sizing (50% vs 30% for Red Three Soldiers)")
        print("- Higher profit targets due to stronger momentum")
        print("- Risk management: set stop loss at the lowest point of the pattern")
        
    except Exception as e:
        print(f"Error during execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 