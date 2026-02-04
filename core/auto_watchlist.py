"""
Auto-add logic for watchlist based on early signals
"""

import pandas as pd
from typing import List, Tuple, Optional
from models.stock import Stock
from core.technical_analysis import (
    check_macd_crossover,
    is_macd_bullish,
    calculate_momentum
)


class AutoWatchlist:
    """
    Detects early signals and auto-adds stocks to watchlist
    """
    
    def __init__(self):
        """Initialize auto-watchlist"""
        pass
    
    def should_add_to_watchlist(self, stock: Stock) -> Tuple[bool, Optional[str]]:
        """
        Determine if stock should be auto-added to watchlist
        
        Args:
            stock: Stock object with calculated metrics
            
        Returns:
            (should_add, reason)
        """
        # Check all criteria
        reasons = []
        
        # 1. Score improving significantly
        if self._check_score_improving(stock):
            reasons.append("SCORE_IMPROVING")
        
        # 2. Near threshold (return 10-14%, confidence 70-79%)
        if self._check_near_threshold(stock):
            reasons.append("NEAR_THRESHOLD")
        
        # 3. Early MACD bullish crossover
        if self._check_macd_early_signal(stock):
            reasons.append("MACD_CROSSOVER")
        
        # 4. RSI momentum building (45-65 zone)
        if self._check_rsi_momentum(stock):
            reasons.append("RSI_MOMENTUM")
        
        # 5. Volume increasing over 3 days
        if self._check_volume_trend(stock):
            reasons.append("VOLUME_SURGE")
        
        # Must have at least 2 signals to add
        if len(reasons) >= 2:
            primary_reason = reasons[0]
            return True, primary_reason
        
        return False, None
    
    def _check_score_improving(self, stock: Stock) -> bool:
        """
        Check if score is improving by 5+ points
        
        For initial screening, we check if current score is strong
        (In real tracking, we'd compare to previous score)
        """
        # Score must be decent but not yet at threshold
        if stock.overall_score and 60 <= stock.overall_score < 80:
            return True
        return False
    
    def _check_near_threshold(self, stock: Stock) -> bool:
        """
        Check if near trading threshold
        Return: 10-14%, Confidence: 70-79%
        """
        return_ok = False
        confidence_ok = False
        
        if stock.estimated_return:
            if 10.0 <= stock.estimated_return <= 14.0:
                return_ok = True
        
        if stock.confidence:
            if 70 <= stock.confidence <= 79:
                confidence_ok = True
        
        # Must be near threshold on at least one metric
        return return_ok or confidence_ok
    
    def _check_macd_early_signal(self, stock: Stock) -> bool:
        """
        Check for early MACD bullish crossover (within last 3 days)
        """
        if stock.history is None or len(stock.history) < 30:
            return False
        
        try:
            # Check for recent crossover
            has_crossover, days_ago = check_macd_crossover(stock.history, lookback_days=3)
            
            if has_crossover:
                return True
            
            # Also check if MACD is bullish and histogram expanding
            if (stock.macd is not None and 
                stock.macd_signal is not None and 
                stock.macd > stock.macd_signal):
                
                # Check if histogram is expanding
                if 'MACD_hist' in stock.history.columns:
                    hist = stock.history['MACD_hist'].tail(3)
                    if len(hist) >= 2 and hist.iloc[-1] > hist.iloc[-2] > 0:
                        return True
            
        except Exception:
            pass
        
        return False
    
    def _check_rsi_momentum(self, stock: Stock) -> bool:
        """
        Check if RSI is in momentum building zone (45-65)
        """
        if stock.rsi is None:
            return False
        
        # Ideal momentum zone
        if 45 <= stock.rsi <= 65:
            # Bonus: Check if RSI is rising
            if stock.history is not None and 'RSI' in stock.history.columns:
                rsi_series = stock.history['RSI'].tail(5)
                if len(rsi_series) >= 3:
                    # RSI should be trending up
                    if rsi_series.iloc[-1] > rsi_series.iloc[-3]:
                        return True
            return True
        
        return False
    
    def _check_volume_trend(self, stock: Stock) -> bool:
        """
        Check if volume is increasing over last 3 days
        """
        if stock.history is None or 'Volume' not in stock.history.columns:
            return False
        
        try:
            volumes = stock.history['Volume'].tail(4)
            
            if len(volumes) < 4:
                return False
            
            # Check if last 3 days show increasing volume
            v1, v2, v3, v4 = volumes.iloc[-4], volumes.iloc[-3], volumes.iloc[-2], volumes.iloc[-1]
            
            # At least 2 out of 3 days increasing
            increasing_count = 0
            if v2 > v1:
                increasing_count += 1
            if v3 > v2:
                increasing_count += 1
            if v4 > v3:
                increasing_count += 1
            
            if increasing_count >= 2:
                # Also check if current volume is above average
                if 'Volume_SMA_20' in stock.history.columns:
                    avg_vol = stock.history['Volume_SMA_20'].iloc[-1]
                    if not pd.isna(avg_vol) and v4 > avg_vol * 1.2:
                        return True
                else:
                    return True
            
        except Exception:
            pass
        
        return False
    
    def scan_for_watchlist_candidates(
        self, 
        stocks: List[Stock]
    ) -> List[Tuple[Stock, str]]:
        """
        Scan list of stocks for watchlist candidates
        
        Args:
            stocks: List of Stock objects to scan
            
        Returns:
            List of (Stock, reason) tuples for candidates
        """
        candidates = []
        
        for stock in stocks:
            should_add, reason = self.should_add_to_watchlist(stock)
            
            if should_add and reason:
                candidates.append((stock, reason))
        
        return candidates
    
    def get_detailed_signals(self, stock: Stock) -> dict:
        """
        Get detailed breakdown of all signals for a stock
        
        Args:
            stock: Stock to analyze
            
        Returns:
            Dict with signal status for each criterion
        """
        return {
            'symbol': stock.symbol,
            'score_improving': self._check_score_improving(stock),
            'near_threshold': self._check_near_threshold(stock),
            'macd_signal': self._check_macd_early_signal(stock),
            'rsi_momentum': self._check_rsi_momentum(stock),
            'volume_trend': self._check_volume_trend(stock),
            'current_score': stock.overall_score,
            'estimated_return': stock.estimated_return,
            'confidence': stock.confidence,
        }
    
    def filter_by_minimum_quality(
        self, 
        candidates: List[Tuple[Stock, str]],
        min_score: float = 50.0,
        min_return: float = 8.0,
        min_confidence: int = 60
    ) -> List[Tuple[Stock, str]]:
        """
        Filter candidates by minimum quality thresholds
        
        Args:
            candidates: List of (Stock, reason) tuples
            min_score: Minimum overall score
            min_return: Minimum return potential
            min_confidence: Minimum confidence
            
        Returns:
            Filtered list of candidates
        """
        filtered = []
        
        for stock, reason in candidates:
            # Check minimums
            if stock.overall_score and stock.overall_score < min_score:
                continue
            
            if stock.estimated_return and stock.estimated_return < min_return:
                continue
            
            if stock.confidence and stock.confidence < min_confidence:
                continue
            
            filtered.append((stock, reason))
        
        return filtered
    
    def prioritize_candidates(
        self, 
        candidates: List[Tuple[Stock, str]]
    ) -> List[Tuple[Stock, str, float]]:
        """
        Prioritize watchlist candidates by score
        
        Args:
            candidates: List of (Stock, reason) tuples
            
        Returns:
            List of (Stock, reason, priority_score) tuples, sorted by priority
        """
        prioritized = []
        
        for stock, reason in candidates:
            # Calculate priority score
            priority = 0.0
            
            # Base score
            if stock.overall_score:
                priority += stock.overall_score * 0.4
            
            # Return potential
            if stock.estimated_return:
                priority += min(stock.estimated_return, 20) * 2.0
            
            # Confidence
            if stock.confidence:
                priority += stock.confidence * 0.3
            
            # MACD crossover gets bonus
            if reason == "MACD_CROSSOVER":
                priority += 10
            
            # Near threshold gets bonus
            if reason == "NEAR_THRESHOLD":
                priority += 15
            
            prioritized.append((stock, reason, priority))
        
        # Sort by priority (highest first)
        prioritized.sort(key=lambda x: x[2], reverse=True)
        
        return prioritized
