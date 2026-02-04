"""
Day trade opportunity model
"""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime, time

@dataclass
class DayTradeOpportunity:
    """
    Intraday trading opportunity (1-5% target)
    """
    # Identification
    symbol: str
    name: str
    current_price: float
    sector: str
    
    # Entry/Exit prices
    entry_price: float
    target_price: float
    stop_price: float
    
    # Return estimates
    estimated_return_pct: float
    estimated_return_dollars: float
    estimated_time_minutes: int  # Estimated time to target
    confidence: int  # 0-100%
    
    # Position sizing
    shares: int
    position_value: float
    
    # Pre-market analysis
    premarket_gap_pct: float = 0.0
    premarket_volume_ratio: float = 0.0  # Ratio vs average
    
    # Intraday indicators
    atr_pct: float = 0.0  # Average True Range as %
    current_volume_ratio: float = 0.0
    
    # Technical scores
    setup_score: float = 0.0  # Quality of technical setup
    catalyst_score: float = 0.0  # News/catalyst strength
    momentum_score: float = 0.0
    overall_score: float = 0.0
    
    # Trade management
    force_exit_time: time = time(15, 45)  # Default 3:45 PM
    current_time: Optional[datetime] = None
    
    # Setup type
    setup_type: str = ""  # "BREAKOUT", "REVERSAL", "MOMENTUM", "GAP_FILL"
    catalyst: str = ""  # Description of news catalyst
    
    # Support/Resistance
    support_levels: List[float] = field(default_factory=list)
    resistance_levels: List[float] = field(default_factory=list)
    
    # Risk management
    max_loss_pct: float = 2.0  # -2% stop loss
    max_loss_dollars: float = 0.0
    risk_reward_ratio: float = 0.0
    
    def __post_init__(self):
        """Calculate derived fields"""
        if self.max_loss_dollars == 0.0:
            self.max_loss_dollars = self.position_value * (self.max_loss_pct / 100)
        
        if self.risk_reward_ratio == 0.0 and self.max_loss_dollars > 0:
            self.risk_reward_ratio = self.estimated_return_dollars / self.max_loss_dollars
    
    def to_dict(self):
        """Convert to dictionary for export"""
        return {
            'symbol': self.symbol,
            'name': self.name,
            'current_price': self.current_price,
            'sector': self.sector,
            'entry_price': self.entry_price,
            'target_price': self.target_price,
            'stop_price': self.stop_price,
            'estimated_return_pct': self.estimated_return_pct,
            'estimated_return_dollars': self.estimated_return_dollars,
            'estimated_time_minutes': self.estimated_time_minutes,
            'confidence': self.confidence,
            'shares': self.shares,
            'position_value': self.position_value,
            'premarket_gap_pct': self.premarket_gap_pct,
            'premarket_volume_ratio': self.premarket_volume_ratio,
            'atr_pct': self.atr_pct,
            'current_volume_ratio': self.current_volume_ratio,
            'setup_score': self.setup_score,
            'catalyst_score': self.catalyst_score,
            'momentum_score': self.momentum_score,
            'overall_score': self.overall_score,
            'setup_type': self.setup_type,
            'catalyst': self.catalyst,
            'max_loss_pct': self.max_loss_pct,
            'max_loss_dollars': self.max_loss_dollars,
            'risk_reward_ratio': self.risk_reward_ratio,
        }
    
    def is_high_confidence(self, min_confidence: int = 85) -> bool:
        """Check if opportunity meets high confidence threshold"""
        return self.confidence >= min_confidence
    
    def time_until_force_exit(self) -> Optional[int]:
        """Calculate minutes until force exit time"""
        if not self.current_time:
            return None
        
        # Create datetime for force exit today
        force_exit_dt = datetime.combine(
            self.current_time.date(),
            self.force_exit_time
        )
        
        # Calculate difference in minutes
        delta = force_exit_dt - self.current_time
        return int(delta.total_seconds() / 60)
    
    def should_force_exit(self) -> bool:
        """Check if it's time to force exit"""
        if not self.current_time:
            return False
        
        current_time_only = self.current_time.time()
        return current_time_only >= self.force_exit_time
