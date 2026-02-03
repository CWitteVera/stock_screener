"""
Composite scoring engine for stocks
"""

import pandas as pd
import numpy as np
from typing import Dict
from core.technical_analysis import (
    check_macd_crossover, is_macd_bullish, is_histogram_expanding,
    calculate_momentum, find_support_resistance
)
from config.settings import (
    MACD_WEIGHT, RSI_WEIGHT, VOLUME_WEIGHT, 
    BREAKOUT_WEIGHT, MOMENTUM_WEIGHT
)

def calculate_overall_score(stock_data: dict, df: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate comprehensive score for a stock
    Returns dict with individual scores and overall score
    """
    
    scores = {
        'macd_score': calculate_macd_score(df),
        'rsi_score': calculate_rsi_score(df),
        'volume_score': calculate_volume_score(df),
        'breakout_score': calculate_breakout_score(df, stock_data['current_price']),
        'momentum_score': calculate_momentum_score(df),
    }
    
    # Calculate weighted overall score
    overall = (
        scores['macd_score'] * MACD_WEIGHT +
        scores['rsi_score'] * RSI_WEIGHT +
        scores['volume_score'] * VOLUME_WEIGHT +
        scores['breakout_score'] * BREAKOUT_WEIGHT +
        scores['momentum_score'] * MOMENTUM_WEIGHT
    )
    
    scores['overall_score'] = overall
    
    return scores

def calculate_macd_score(df: pd.DataFrame) -> float:
    """
    Calculate MACD score (0-100)
    
    Criteria:
    - Bullish crossover in last 3 days: +40 points
    - MACD above signal line: +20 points
    - Histogram expanding: +20 points
    - Strong trend: +20 points
    """
    score = 0.0
    
    if 'MACD' not in df.columns:
        return score
    
    # Check for recent crossover
    has_crossover, days_ago = check_macd_crossover(df, lookback_days=3)
    if has_crossover:
        score += 40
    
    # MACD above signal line
    if is_macd_bullish(df):
        score += 20
    
    # Histogram expanding
    if is_histogram_expanding(df):
        score += 20
    
    # Strong positive trend (MACD value is significantly positive)
    macd_val = df['MACD'].iloc[-1]
    if not pd.isna(macd_val) and macd_val > 0:
        # Normalize based on recent MACD range
        recent_macd = df['MACD'].tail(20)
        macd_range = recent_macd.max() - recent_macd.min()
        if macd_range > 0:
            strength = min((macd_val / macd_range) * 20, 20)
            score += strength
    
    return min(score, 100)

def calculate_rsi_score(df: pd.DataFrame) -> float:
    """
    Calculate RSI score (0-100)
    
    Criteria:
    - RSI 45-65 (momentum zone): +50 points
    - RSI rising: +25 points
    - Not overbought (<70): +25 points
    """
    score = 0.0
    
    if 'RSI' not in df.columns:
        return score
    
    rsi = df['RSI'].iloc[-1]
    
    if pd.isna(rsi):
        return score
    
    # Optimal momentum zone
    if 45 <= rsi <= 65:
        score += 50
    elif 35 <= rsi < 45 or 65 < rsi <= 70:
        score += 25  # Still acceptable
    
    # RSI rising (bullish)
    if len(df) >= 3:
        prev_rsi = df['RSI'].iloc[-3]
        if not pd.isna(prev_rsi) and rsi > prev_rsi:
            score += 25
    
    # Not overbought
    if rsi < 70:
        score += 25
    elif rsi < 80:
        score += 10  # Slightly overbought but ok
    
    return min(score, 100)

def calculate_volume_score(df: pd.DataFrame) -> float:
    """
    Calculate Volume score (0-100)
    
    Criteria:
    - Volume >2x 20-day average: +50 points
    - Volume trend increasing: +30 points
    - Consistent high volume: +20 points
    """
    score = 0.0
    
    if 'Volume_SMA_20' not in df.columns:
        return score
    
    current_vol = df['Volume'].iloc[-1]
    avg_vol = df['Volume_SMA_20'].iloc[-1]
    
    if pd.isna(avg_vol) or avg_vol == 0:
        return score
    
    vol_ratio = current_vol / avg_vol
    
    # High volume spike
    if vol_ratio > 2.0:
        score += 50
    elif vol_ratio > 1.5:
        score += 35
    elif vol_ratio > 1.0:
        score += 20
    
    # Volume trend increasing
    recent_vols = df['Volume'].tail(5)
    if len(recent_vols) >= 3:
        if recent_vols.iloc[-1] > recent_vols.iloc[-3]:
            score += 30
        elif recent_vols.iloc[-1] > recent_vols.iloc[-2]:
            score += 15
    
    # Consistent above-average volume
    last_5_vols = df['Volume'].tail(5)
    last_5_avg = df['Volume_SMA_20'].tail(5)
    
    if len(last_5_vols) == len(last_5_avg):
        above_avg_count = sum(last_5_vols.values > last_5_avg.values)
        if above_avg_count >= 4:
            score += 20
        elif above_avg_count >= 3:
            score += 10
    
    return min(score, 100)

def calculate_breakout_score(df: pd.DataFrame, current_price: float) -> float:
    """
    Calculate Breakout score (0-100)
    
    Criteria:
    - Breaking 20-day high: +40 points
    - Above 20-day and 50-day MA: +30 points
    - Clear support level below: +30 points
    """
    score = 0.0
    
    # Check for 20-day high breakout
    recent_20 = df.tail(20)
    high_20 = recent_20['High'].max()
    
    if current_price >= high_20 * 0.99:  # Within 1% of high
        score += 40
    elif current_price >= high_20 * 0.97:  # Within 3%
        score += 20
    
    # Above moving averages
    ma_score = 0
    if 'SMA_20' in df.columns:
        sma_20 = df['SMA_20'].iloc[-1]
        if not pd.isna(sma_20) and current_price > sma_20:
            ma_score += 15
    
    if 'SMA_50' in df.columns:
        sma_50 = df['SMA_50'].iloc[-1]
        if not pd.isna(sma_50) and current_price > sma_50:
            ma_score += 15
    
    score += ma_score
    
    # Support level analysis
    levels = find_support_resistance(df)
    support_levels = levels.get('support_levels', [])
    
    if support_levels:
        # Has clear support below
        nearest_support = support_levels[0]
        distance_to_support = ((current_price - nearest_support) / current_price) * 100
        
        # Ideal support is 5-10% below
        if 5 <= distance_to_support <= 10:
            score += 30
        elif 3 <= distance_to_support <= 15:
            score += 20
        elif distance_to_support > 2:
            score += 10
    
    return min(score, 100)

def calculate_momentum_score(df: pd.DataFrame) -> float:
    """
    Calculate Momentum score (0-100)
    
    Criteria:
    - 5-day return 5-15%: +50 points
    - Price acceleration: +25 points
    - Higher highs pattern: +25 points
    """
    score = 0.0
    
    # 5-day return
    momentum_5d = calculate_momentum(df, period=5)
    
    if 5 <= momentum_5d <= 15:
        score += 50
    elif 3 <= momentum_5d < 5 or 15 < momentum_5d <= 20:
        score += 35
    elif 1 <= momentum_5d < 3:
        score += 20
    
    # Price acceleration (momentum increasing)
    momentum_3d = calculate_momentum(df, period=3)
    if momentum_3d > momentum_5d * 0.6:  # Recent momentum is strong
        score += 25
    elif momentum_3d > 0:
        score += 10
    
    # Higher highs pattern
    if len(df) >= 5:
        last_5_highs = df['High'].tail(5)
        # Check if making higher highs
        is_higher_highs = True
        for i in range(1, len(last_5_highs)):
            if last_5_highs.iloc[i] < last_5_highs.iloc[i-1] * 0.98:  # Allow small dips
                is_higher_highs = False
                break
        
        if is_higher_highs:
            score += 25
        elif last_5_highs.iloc[-1] > last_5_highs.iloc[0]:
            score += 10
    
    return min(score, 100)
