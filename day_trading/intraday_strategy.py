"""
Intraday strategy filters and technical analysis for day trading
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional


class IntradayStrategy:
    """
    Day trading filters and technical scoring for 1-5% intraday opportunities
    """
    
    def __init__(self):
        self.min_gap_pct = 1.0  # Minimum pre-market gap
        self.min_volume_ratio = 2.0  # Minimum volume vs average
        self.min_atr_pct = 5.0  # Minimum ATR for volatility
        
    def check_premarket_gap(self, symbol: str) -> Tuple[bool, float]:
        """
        Check for pre-market gap > 1%
        Returns: (passes_filter, gap_percentage)
        """
        try:
            ticker = yf.Ticker(symbol)
            # Get yesterday's close and current price
            hist = ticker.history(period="5d", interval="1d")
            if len(hist) < 2:
                return False, 0.0
            
            prev_close = hist['Close'].iloc[-2]
            current = ticker.info.get('currentPrice', hist['Close'].iloc[-1])
            
            gap_pct = ((current - prev_close) / prev_close) * 100
            passes = abs(gap_pct) >= self.min_gap_pct
            
            return passes, gap_pct
            
        except Exception as e:
            print(f"Error checking gap for {symbol}: {e}")
            return False, 0.0
    
    def check_volume_surge(self, symbol: str) -> Tuple[bool, float]:
        """
        Check for volume surge > 2x average
        Returns: (passes_filter, volume_ratio)
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="20d", interval="1d")
            
            if len(hist) < 10:
                return False, 0.0
            
            # Average volume (excluding today)
            avg_volume = hist['Volume'].iloc[:-1].mean()
            current_volume = hist['Volume'].iloc[-1]
            
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0.0
            passes = volume_ratio >= self.min_volume_ratio
            
            return passes, volume_ratio
            
        except Exception as e:
            print(f"Error checking volume for {symbol}: {e}")
            return False, 0.0
    
    def calculate_atr_percent(self, symbol: str, period: int = 14) -> Tuple[bool, float]:
        """
        Calculate Average True Range as percentage for intraday volatility
        Returns: (passes_filter, atr_percentage)
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1mo", interval="1d")
            
            if len(hist) < period:
                return False, 0.0
            
            # Calculate True Range
            high_low = hist['High'] - hist['Low']
            high_close = abs(hist['High'] - hist['Close'].shift())
            low_close = abs(hist['Low'] - hist['Close'].shift())
            
            tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = tr.rolling(window=period).mean().iloc[-1]
            
            # ATR as percentage of current price
            current_price = hist['Close'].iloc[-1]
            atr_pct = (atr / current_price) * 100
            
            passes = atr_pct >= self.min_atr_pct
            
            return passes, atr_pct
            
        except Exception as e:
            print(f"Error calculating ATR for {symbol}: {e}")
            return False, 0.0
    
    def check_news_catalyst(self, symbol: str) -> Tuple[float, str]:
        """
        Check for news catalysts
        Returns: (catalyst_score 0-100, catalyst_description)
        """
        try:
            ticker = yf.Ticker(symbol)
            news = ticker.news
            
            if not news or len(news) == 0:
                return 0.0, "No recent news"
            
            # Check for recent news (last 24 hours)
            recent_news = []
            now = datetime.now()
            
            for item in news[:5]:  # Check latest 5 news items
                pub_date = datetime.fromtimestamp(item.get('providerPublishTime', 0))
                age_hours = (now - pub_date).total_seconds() / 3600
                
                if age_hours < 24:
                    recent_news.append(item)
            
            if not recent_news:
                return 20.0, "No news in last 24h"
            
            # Score based on recency and number of articles
            score = min(100.0, 40.0 + (len(recent_news) * 15))
            catalyst = f"{len(recent_news)} news items in last 24h: {recent_news[0].get('title', 'N/A')[:50]}"
            
            return score, catalyst
            
        except Exception as e:
            return 0.0, "Unable to fetch news"
    
    def calculate_support_resistance(self, symbol: str) -> Tuple[List[float], List[float]]:
        """
        Calculate intraday support and resistance levels
        Returns: (support_levels, resistance_levels)
        """
        try:
            ticker = yf.Ticker(symbol)
            # Get 5-minute intervals for intraday analysis
            hist = ticker.history(period="5d", interval="5m")
            
            if len(hist) < 50:
                return [], []
            
            # Get recent high/low clusters
            highs = hist['High'].tail(100)
            lows = hist['Low'].tail(100)
            
            # Find resistance levels (recent highs)
            resistance_levels = []
            recent_high = highs.max()
            resistance_levels.append(recent_high)
            
            # Find support levels (recent lows)
            support_levels = []
            recent_low = lows.min()
            support_levels.append(recent_low)
            
            # Add pivot point
            pivot = (highs.iloc[-1] + lows.iloc[-1] + hist['Close'].iloc[-1]) / 3
            if pivot not in resistance_levels and pivot not in support_levels:
                if pivot > hist['Close'].iloc[-1]:
                    resistance_levels.append(pivot)
                else:
                    support_levels.append(pivot)
            
            return sorted(support_levels), sorted(resistance_levels, reverse=True)
            
        except Exception as e:
            print(f"Error calculating S/R for {symbol}: {e}")
            return [], []
    
    def score_technical_setup(self, symbol: str) -> float:
        """
        Score the quality of technical setup (0-100)
        Considers: trend, momentum, volume, and pattern quality
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1mo", interval="1d")
            
            if len(hist) < 20:
                return 0.0
            
            score = 0.0
            
            # Trend score (20 points): uptrend is positive
            sma_20 = hist['Close'].rolling(window=20).mean().iloc[-1]
            current_price = hist['Close'].iloc[-1]
            if current_price > sma_20:
                score += 20.0
            elif current_price > sma_20 * 0.98:  # Within 2%
                score += 10.0
            
            # Momentum score (30 points): RSI in good range
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            rsi_current = rsi.iloc[-1]
            
            if 40 <= rsi_current <= 70:
                score += 30.0
            elif 30 <= rsi_current <= 80:
                score += 15.0
            
            # Volume confirmation (25 points)
            avg_volume = hist['Volume'].rolling(window=10).mean().iloc[-1]
            current_volume = hist['Volume'].iloc[-1]
            if current_volume > avg_volume * 1.5:
                score += 25.0
            elif current_volume > avg_volume:
                score += 12.0
            
            # Recent volatility (25 points): good for day trading
            price_change_5d = abs(hist['Close'].pct_change(5).iloc[-1]) * 100
            if price_change_5d >= 5:
                score += 25.0
            elif price_change_5d >= 3:
                score += 15.0
            
            return min(100.0, score)
            
        except Exception as e:
            print(f"Error scoring setup for {symbol}: {e}")
            return 0.0
    
    def calculate_momentum_score(self, symbol: str) -> float:
        """
        Calculate momentum score (0-100)
        Based on: rate of change, MACD, and price velocity
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="2mo", interval="1d")
            
            if len(hist) < 26:
                return 0.0
            
            score = 0.0
            
            # Rate of change (40 points)
            roc_5 = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-6]) / hist['Close'].iloc[-6]) * 100
            if abs(roc_5) >= 5:
                score += 40.0
            elif abs(roc_5) >= 3:
                score += 25.0
            elif abs(roc_5) >= 1:
                score += 10.0
            
            # MACD (40 points)
            exp1 = hist['Close'].ewm(span=12, adjust=False).mean()
            exp2 = hist['Close'].ewm(span=26, adjust=False).mean()
            macd = exp1 - exp2
            signal = macd.ewm(span=9, adjust=False).mean()
            
            if macd.iloc[-1] > signal.iloc[-1]:  # Bullish
                score += 40.0
            elif macd.iloc[-1] > signal.iloc[-1] * 0.95:  # Nearly bullish
                score += 20.0
            
            # Price velocity (20 points)
            velocity = hist['Close'].diff().iloc[-3:].mean()
            if abs(velocity) > hist['Close'].iloc[-1] * 0.005:  # 0.5% per day
                score += 20.0
            elif abs(velocity) > hist['Close'].iloc[-1] * 0.002:
                score += 10.0
            
            return min(100.0, score)
            
        except Exception as e:
            print(f"Error calculating momentum for {symbol}: {e}")
            return 0.0
    
    def evaluate_stock(self, symbol: str) -> Dict:
        """
        Complete evaluation of a stock for day trading
        Returns dict with all metrics and scores
        """
        print(f"Evaluating {symbol} for day trading...")
        
        # Run all filters
        gap_pass, gap_pct = self.check_premarket_gap(symbol)
        volume_pass, volume_ratio = self.check_volume_surge(symbol)
        atr_pass, atr_pct = self.calculate_atr_percent(symbol)
        catalyst_score, catalyst = self.check_news_catalyst(symbol)
        support, resistance = self.calculate_support_resistance(symbol)
        
        # Calculate scores
        setup_score = self.score_technical_setup(symbol)
        momentum_score = self.calculate_momentum_score(symbol)
        
        # Overall score (weighted average)
        overall_score = (
            setup_score * 0.30 +
            momentum_score * 0.25 +
            catalyst_score * 0.20 +
            (min(100, atr_pct * 10) * 0.15) +  # ATR contribution
            (min(100, volume_ratio * 25) * 0.10)  # Volume contribution
        )
        
        return {
            'symbol': symbol,
            'passes_filters': gap_pass and volume_pass and atr_pass,
            'gap_pct': gap_pct,
            'volume_ratio': volume_ratio,
            'atr_pct': atr_pct,
            'catalyst_score': catalyst_score,
            'catalyst': catalyst,
            'setup_score': setup_score,
            'momentum_score': momentum_score,
            'overall_score': overall_score,
            'support_levels': support,
            'resistance_levels': resistance,
        }
