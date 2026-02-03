"""
Stock data model
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
import pandas as pd

@dataclass
class Stock:
    """Stock data container"""
    symbol: str
    name: str
    current_price: float
    sector: str
    market_cap: float
    volume: float
    avg_volume: float
    history: pd.DataFrame
    info: Dict[str, Any]
    
    # Technical indicators (calculated later)
    rsi: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    atr: Optional[float] = None
    
    # Scoring (calculated later)
    macd_score: Optional[float] = None
    rsi_score: Optional[float] = None
    volume_score: Optional[float] = None
    breakout_score: Optional[float] = None
    momentum_score: Optional[float] = None
    overall_score: Optional[float] = None
    
    # Return estimation
    estimated_return: Optional[float] = None
    confidence: Optional[float] = None
    days_to_target: Optional[int] = None
    
    def __str__(self):
        return f"Stock({self.symbol}, ${self.current_price:.2f})"
    
    def passes_basic_filters(self, min_price: float, max_price: float, 
                            min_volume: float, min_market_cap: float) -> bool:
        """Check if stock passes basic screening filters"""
        if self.current_price < min_price or self.current_price > max_price:
            return False
        if self.volume < min_volume:
            return False
        if self.market_cap < min_market_cap:
            return False
        return True
