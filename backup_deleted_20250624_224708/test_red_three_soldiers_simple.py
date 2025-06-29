import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import sys

class SimpleRedThreeSoldiersStrategy:
    """Red Three Soldiers pattern detection strategy"""
    
    def __init__(self):
        self.name = "红三兵策略"
        self.description = "基于红三兵K线组合的多方启动交易策略"
        
        # Default parameters
        self.params = {
            'min_body_size_ratio': 0.6,      # Minimum body size to total range ratio
            'max_upper_shadow_ratio': 0.15,  # Maximum upper shadow to body ratio
            'price_increase_threshold': 0.01, # Minimum daily price increase
            'volume_increase_threshold': 0.2, # Volume increase threshold
            'min_pattern_length': 3,         # Pattern length (3 candles)
            'min_total_increase': 0.03       # Minimum total price increase over pattern
        }
    
    def detect_pattern(self, data):
        """
        Detect Red Three Soldiers pattern in price data
        
        Args:
            data (pd.DataFrame): OHLCV data
            
        Returns:
            list: List of pattern detection dates
        """
        print("Analyzing data for Red Three Soldiers patterns...")
        sys.stdout.flush()
        
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
        
        # Need at least 3 candles plus some history
        if len(df) < 10:
            print("Not enough data for pattern detection")
            sys.stdout.flush()
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
            
            # Check body size ratio (at least 60% of total range)
            if not all(window['body_size_ratio'] >= self.params['min_body_size_ratio']):
                continue
            
            # Check for minimal upper shadows
            if not all(window['upper_shadow_ratio'] <= self.params['max_upper_shadow_ratio']):
                continue
            
            # Check total price increase
            total_increase = (window['close'].iloc[-1] - window['open'].iloc[0]) / window['open'].iloc[0]
            if total_increase < self.params['min_total_increase']:
                continue
            
            # Check volume characteristics (at least one day with increased volume)
            volume_ratios = window['volume_ratio'].values
            increased_volume_days = sum(ratio >= 1 + self.params['volume_increase_threshold'] 
                                       for ratio in volume_ratios if not np.isnan(ratio))
            if increased_volume_days < 1:
                continue
            
            # Pattern detected at the last candle of the window
            pattern_date = window.index[-1]
            patterns.append(pattern_date)
            
            # Generate signal (1 for buy)
            signals.loc[pattern_date] = 1
            
            print(f"Pattern detected at {pattern_date}")
            sys.stdout.flush()
        
        print(f"Total patterns detected: {len(patterns)}")
        sys.stdout.flush()
        return patterns, signals

def generate_sample_data(days=100):
    """Generate sample data with Red Three Soldiers patterns"""
    print("Generating sample data...")
    sys.stdout.flush()
    
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
    low_start = 20
    for i in range(10, low_start):
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
    
    # Record pattern area
    pattern_areas['low'] = {'start': low_start, 'end': low_start+2}
    
    # Create a high position Red Three Soldiers pattern with high volume (warning sign)
    high_start = 70
    # First create an uptrend
    for i in range(high_start-10, high_start):
        close[i] = close[i-1] * (1 + np.random.uniform(0.005, 0.015))
        open_prices[i] = close[i-1] * (1 - np.random.uniform(0, 0.005))
        high[i] = close[i] * (1 + np.random.uniform(0.002, 0.008))
        low[i] = open_prices[i] * (1 - np.random.uniform(0.002, 0.008))
        volume[i] = volume[i-1] * (1 + np.random.uniform(0.05, 0.15))
    
    # Create Red Three Soldiers pattern with high volume
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
    
    # Third bullish candle with minimal upper shadow
    open_prices[high_start+2] = close[high_start+1] * 1.001
    close[high_start+2] = open_prices[high_start+2] * 1.015
    high[high_start+2] = close[high_start+2] * 1.012
    low[high_start+2] = open_prices[high_start+2] * 0.998
    volume[high_start+2] = volume[high_start+1] * 2.0
    
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
    sys.stdout.flush()
    
    return df, pattern_areas

def plot_candlestick(data, signals, pattern_areas=None, patterns=None):
    """Plot candlestick chart with signals"""
    print("Plotting candlestick chart...")
    sys.stdout.flush()
    
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
        sys.stdout.flush()
        
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
        sys.stdout.flush()
        
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
        sys.stdout.flush()
        
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
    
    print("Saving chart...")
    sys.stdout.flush()
    
    plt.tight_layout()
    
    try:
        plt.savefig('red_three_soldiers_simple.png')
        print("Chart saved as 'red_three_soldiers_simple.png'")
    except Exception as e:
        print(f"Error saving chart: {e}")
    
    sys.stdout.flush()

def main():
    print("Starting Red Three Soldiers pattern detection test...")
    sys.stdout.flush()
    
    try:
        # Generate sample data
        data, pattern_areas = generate_sample_data(days=100)
        print(f"Generated data with shape: {data.shape}")
        sys.stdout.flush()
        
        # Initialize detector
        detector = SimpleRedThreeSoldiersStrategy()
        
        # Detect patterns
        patterns, signals = detector.detect_pattern(data)
        
        # Print results
        print(f"Found {len(patterns)} Red Three Soldiers pattern(s):")
        sys.stdout.flush()
        
        for date in patterns:
            print(f"Date: {date}")
            sys.stdout.flush()
        
        # Print signal count
        signal_count = len(signals[signals != 0])
        print(f"Generated {signal_count} trading signals")
        sys.stdout.flush()
        
        # Plot and save results
        plot_candlestick(data, signals, pattern_areas, patterns)
        
        print("\n红三兵 (Red Three Soldiers) Pattern Analysis:")
        print("--------------------------------------------")
        print("The Red Three Soldiers pattern consists of three consecutive bullish candles")
        print("with similar body size, minimal upper shadows, and increasing closing prices.")
        print("\nKey characteristics:")
        print("- Three consecutive bullish candles")
        print("- Minimal upper shadows (strong buyer control)")
        print("- Similar body size without significant expansion or contraction")
        print("- Each candle closes higher than the previous one")
        print("- Gradual increase in trading volume")
        print("\nTrading implications:")
        print("- Strong bullish reversal signal at the end of downtrends")
        print("- Continuation signal during established uptrends")
        print("- Warning signal when accompanied by excessive volume at market highs")
        sys.stdout.flush()
        
    except Exception as e:
        print(f"Error during execution: {e}")
        import traceback
        traceback.print_exc()
        sys.stdout.flush()

if __name__ == "__main__":
    main()