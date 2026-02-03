"""
Return potential estimation engine
"""

import pandas as pd
import numpy as np
from typing import Tuple
from core.technical_analysis import find_support_resistance, calculate_momentum

def estimate_return_potential(stock_data: dict, df: pd.DataFrame) -> Tuple[float, float, int]:
    """
    Calculate realistic return potential based on:
    1. Historical volatility (average 5-7 day range)
    2. Technical targets (next resistance level)
    3. Momentum projection (current rate of change)
    
    Returns: (estimated_return_percent, confidence_score, days_to_target)
    """
    
    current_price = stock_data['current_price']
    
    if len(df) < 30:
        return 0.0, 0.0, 10
    
    # 1. Historical volatility analysis - average 5-7 day move
    historical_return = calculate_historical_volatility(df)
    
    # 2. Technical target (next resistance)
    technical_return = calculate_technical_target(df, current_price)
    
    # 3. Momentum projection
    momentum_return = calculate_momentum_projection(df)
    
    # Weighted average of the three methods
    estimated_return = (
        historical_return * 0.4 +   # Historical moves
        technical_return * 0.3 +     # Technical target
        momentum_return * 0.3        # Momentum continuation
    )
    
    # Calculate confidence based on agreement between signals
    confidence = calculate_confidence_score(
        historical_return, 
        technical_return, 
        momentum_return,
        df
    )
    
    # Estimate days to target based on recent momentum
    days_to_target = estimate_days_to_target(df, estimated_return)
    
    return estimated_return, confidence, days_to_target

def calculate_historical_volatility(df: pd.DataFrame, lookback: int = 20) -> float:
    """
    Calculate average 5-7 day price range from recent history
    """
    recent_data = df.tail(lookback)
    
    # Calculate rolling 5-day high-low ranges
    avg_ranges = []
    for i in range(len(recent_data) - 5):
        window = recent_data.iloc[i:i+5]
        high = window['High'].max()
        low = window['Low'].min()
        mid = (high + low) / 2
        range_pct = ((high - low) / mid) * 100
        avg_ranges.append(range_pct)
    
    if not avg_ranges:
        return 0.0
    
    # Return average of these ranges
    return np.mean(avg_ranges)

def calculate_technical_target(df: pd.DataFrame, current_price: float) -> float:
    """
    Calculate return to next resistance level
    """
    levels = find_support_resistance(df)
    
    resistance_levels = levels.get('resistance_levels', [])
    
    if not resistance_levels:
        # Use overall resistance
        resistance = levels.get('resistance', current_price)
    else:
        # Use closest resistance above current price
        resistance = resistance_levels[0]
    
    if resistance <= current_price:
        return 0.0
    
    return ((resistance - current_price) / current_price) * 100

def calculate_momentum_projection(df: pd.DataFrame) -> float:
    """
    Project continuation of current momentum
    Conservative estimate (50% of current momentum)
    """
    current_momentum = calculate_momentum(df, period=5)
    
    # Only project positive momentum
    if current_momentum <= 0:
        return 0.0
    
    # Conservative projection: 50% continuation
    return current_momentum * 0.5

def calculate_confidence_score(hist_ret: float, tech_ret: float, 
                               mom_ret: float, df: pd.DataFrame) -> float:
    """
    Calculate confidence score based on:
    - Agreement between different return estimates
    - Technical signal strength
    - Volume confirmation
    """
    
    # Base confidence from agreement
    returns = [hist_ret, tech_ret, mom_ret]
    avg_return = np.mean(returns)
    
    if avg_return == 0:
        return 0.0
    
    # Calculate variance (lower is better)
    variance = np.var(returns)
    relative_variance = variance / (avg_return ** 2) if avg_return > 0 else 1.0
    
    # Agreement score (0-30 points)
    if relative_variance < 0.1:
        agreement_score = 30
    elif relative_variance < 0.3:
        agreement_score = 20
    else:
        agreement_score = 10
    
    # Technical strength (0-40 points)
    technical_score = calculate_technical_strength(df)
    
    # Volume confirmation (0-30 points)
    volume_score = calculate_volume_confidence(df)
    
    total_confidence = agreement_score + technical_score + volume_score
    
    return min(total_confidence, 100)

def calculate_technical_strength(df: pd.DataFrame) -> float:
    """Calculate strength of technical signals"""
    score = 0.0
    
    # Check MACD
    if 'MACD' in df.columns and 'MACD_signal' in df.columns:
        if not pd.isna(df['MACD'].iloc[-1]) and not pd.isna(df['MACD_signal'].iloc[-1]):
            if df['MACD'].iloc[-1] > df['MACD_signal'].iloc[-1]:
                score += 15
    
    # Check RSI in good range
    if 'RSI' in df.columns:
        rsi = df['RSI'].iloc[-1]
        if not pd.isna(rsi) and 45 <= rsi <= 70:
            score += 15
    
    # Check price above moving averages
    if 'SMA_20' in df.columns and not pd.isna(df['SMA_20'].iloc[-1]):
        if df['Close'].iloc[-1] > df['SMA_20'].iloc[-1]:
            score += 10
    
    return score

def calculate_volume_confidence(df: pd.DataFrame) -> float:
    """Calculate confidence from volume patterns"""
    score = 0.0
    
    if 'Volume_SMA_20' not in df.columns:
        return score
    
    current_vol = df['Volume'].iloc[-1]
    avg_vol = df['Volume_SMA_20'].iloc[-1]
    
    if pd.isna(avg_vol) or avg_vol == 0:
        return score
    
    vol_ratio = current_vol / avg_vol
    
    # High volume is bullish
    if vol_ratio > 1.5:
        score += 20
    elif vol_ratio > 1.0:
        score += 10
    
    # Check volume trend (increasing)
    recent_vols = df['Volume'].tail(5)
    if len(recent_vols) >= 3:
        if recent_vols.iloc[-1] > recent_vols.iloc[-3]:
            score += 10
    
    return score

def estimate_days_to_target(df: pd.DataFrame, target_return: float) -> int:
    """
    Estimate number of days to reach target based on recent momentum
    """
    
    # Calculate recent daily returns
    recent_data = df.tail(10)
    daily_returns = recent_data['Close'].pct_change().dropna()
    
    if len(daily_returns) == 0:
        return 7  # Default
    
    # Average daily return
    avg_daily_return_pct = daily_returns.mean() * 100
    
    if avg_daily_return_pct <= 0:
        return 10  # Max time if no positive momentum
    
    # Estimate days needed
    days = target_return / avg_daily_return_pct
    
    # Clamp between 5 and 10 days
    days = max(5, min(10, int(days)))
    
    return days
