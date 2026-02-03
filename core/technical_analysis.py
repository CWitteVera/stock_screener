"""
Technical analysis calculations using pandas-ta
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional

def calculate_all_indicators(hist_data: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate all technical indicators from historical data
    """
    df = hist_data.copy()
    
    if len(df) < 50:
        # Not enough data
        return df
    
    # RSI (14-period)
    df['RSI'] = calculate_rsi(df['Close'], period=14)
    
    # MACD (12, 26, 9)
    macd_data = calculate_macd(df['Close'])
    df['MACD'] = macd_data['macd']
    df['MACD_signal'] = macd_data['signal']
    df['MACD_hist'] = macd_data['histogram']
    
    # Moving Averages
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    
    # Volume moving average
    df['Volume_SMA_20'] = df['Volume'].rolling(window=20).mean()
    
    # ATR (Average True Range) for volatility
    df['ATR'] = calculate_atr(df, period=14)
    
    # Bollinger Bands
    bb = calculate_bollinger_bands(df['Close'])
    df['BB_upper'] = bb['upper']
    df['BB_middle'] = bb['middle']
    df['BB_lower'] = bb['lower']
    
    return df

def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """Calculate RSI indicator"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict:
    """Calculate MACD indicator"""
    exp1 = prices.ewm(span=fast, adjust=False).mean()
    exp2 = prices.ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    histogram = macd - signal_line
    
    return {
        'macd': macd,
        'signal': signal_line,
        'histogram': histogram
    }

def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Calculate Average True Range"""
    high = df['High']
    low = df['Low']
    close = df['Close']
    
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    
    return atr

def calculate_bollinger_bands(prices: pd.Series, period: int = 20, std_dev: int = 2) -> Dict:
    """Calculate Bollinger Bands"""
    middle = prices.rolling(window=period).mean()
    std = prices.rolling(window=period).std()
    upper = middle + (std * std_dev)
    lower = middle - (std * std_dev)
    
    return {
        'upper': upper,
        'middle': middle,
        'lower': lower
    }

def check_macd_crossover(df: pd.DataFrame, lookback_days: int = 3) -> Tuple[bool, Optional[int]]:
    """
    Check for recent MACD bullish crossover
    Returns (has_crossover, days_ago)
    """
    if 'MACD' not in df.columns or 'MACD_signal' not in df.columns:
        return False, None
    
    last_n_days = df.tail(lookback_days + 1)
    
    if len(last_n_days) < 2:
        return False, None
    
    for i in range(len(last_n_days) - 1):
        prev_macd = last_n_days['MACD'].iloc[i]
        prev_signal = last_n_days['MACD_signal'].iloc[i]
        curr_macd = last_n_days['MACD'].iloc[i+1]
        curr_signal = last_n_days['MACD_signal'].iloc[i+1]
        
        # Check for valid values
        if pd.isna(prev_macd) or pd.isna(prev_signal) or pd.isna(curr_macd) or pd.isna(curr_signal):
            continue
        
        # Bullish crossover: MACD crosses above signal
        if prev_macd <= prev_signal and curr_macd > curr_signal:
            days_ago = len(last_n_days) - i - 2
            return True, days_ago
    
    return False, None

def is_macd_bullish(df: pd.DataFrame) -> bool:
    """Check if MACD is currently bullish (above signal line)"""
    if 'MACD' not in df.columns or 'MACD_signal' not in df.columns:
        return False
    
    last_macd = df['MACD'].iloc[-1]
    last_signal = df['MACD_signal'].iloc[-1]
    
    if pd.isna(last_macd) or pd.isna(last_signal):
        return False
    
    return last_macd > last_signal

def is_histogram_expanding(df: pd.DataFrame, lookback: int = 3) -> bool:
    """Check if MACD histogram is expanding (getting more positive)"""
    if 'MACD_hist' not in df.columns:
        return False
    
    hist = df['MACD_hist'].tail(lookback)
    
    if len(hist) < 2 or hist.isna().any():
        return False
    
    # Check if histogram is increasing
    return hist.iloc[-1] > hist.iloc[-2]

def calculate_momentum(df: pd.DataFrame, period: int = 5) -> float:
    """Calculate price momentum over period"""
    if len(df) < period + 1:
        return 0.0
    
    current_price = df['Close'].iloc[-1]
    past_price = df['Close'].iloc[-(period+1)]
    
    return ((current_price - past_price) / past_price) * 100

def find_support_resistance(df: pd.DataFrame, lookback: int = 20) -> Dict:
    """Find key support and resistance levels"""
    recent_data = df.tail(lookback)
    
    support = recent_data['Low'].min()
    resistance = recent_data['High'].max()
    current_price = df['Close'].iloc[-1]
    
    # Find intermediate levels
    high_points = recent_data['High'].nlargest(5).values
    low_points = recent_data['Low'].nsmallest(5).values
    
    # Filter resistance levels above current price
    resistance_levels = [r for r in high_points if r > current_price]
    # Filter support levels below current price
    support_levels = [s for s in low_points if s < current_price]
    
    return {
        'support': support,
        'resistance': resistance,
        'support_levels': sorted(support_levels, reverse=True),
        'resistance_levels': sorted(resistance_levels)
    }

def calculate_volatility_percent(df: pd.DataFrame, period: int = 20) -> float:
    """Calculate daily volatility as percentage"""
    if 'ATR' not in df.columns or len(df) < period:
        return 0.0
    
    atr = df['ATR'].iloc[-1]
    current_price = df['Close'].iloc[-1]
    
    if pd.isna(atr) or current_price == 0:
        return 0.0
    
    return (atr / current_price) * 100
