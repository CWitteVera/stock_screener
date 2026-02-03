"""
Trade opportunity model
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Trade:
    """Trade opportunity container"""
    symbol: str
    name: str
    entry_price: float
    target_price: float
    stop_price: float
    estimated_return: float
    confidence: float
    days_to_target: int
    score: float
    sector: str
    
    # Position sizing
    shares: int
    position_value: float
    target_profit: float
    max_loss: float
    risk_reward_ratio: float
    
    # Technical details
    current_price: float
    rsi: Optional[float] = None
    macd_score: Optional[float] = None
    volume_score: Optional[float] = None
    breakout_score: Optional[float] = None
    momentum_score: Optional[float] = None
    
    # Additional info
    recommendation: str = "BUY"
    entry_strategy: str = ""
    support_levels: list = None
    
    def __post_init__(self):
        if self.support_levels is None:
            self.support_levels = []
    
    def to_dict(self):
        """Convert to dictionary for export"""
        return {
            'symbol': self.symbol,
            'name': self.name,
            'entry_price': self.entry_price,
            'target_price': self.target_price,
            'stop_price': self.stop_price,
            'estimated_return': self.estimated_return,
            'confidence': self.confidence,
            'days_to_target': self.days_to_target,
            'score': self.score,
            'sector': self.sector,
            'shares': self.shares,
            'position_value': self.position_value,
            'target_profit': self.target_profit,
            'max_loss': self.max_loss,
            'risk_reward_ratio': self.risk_reward_ratio,
        }
    
    def to_fidelity_csv_row(self):
        """Convert to Fidelity ATP CSV format"""
        notes = f"Target: ${self.target_price:.2f}, Stop: ${self.stop_price:.2f}"
        return {
            'Symbol': self.symbol,
            'Action': 'BUY',
            'Quantity': self.shares,
            'OrderType': 'LIMIT',
            'Price': self.entry_price,
            'TimeInForce': 'DAY',
            'Notes': notes
        }
