"""
Watchlist stock model for momentum tracking
"""

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional

@dataclass
class WatchlistStock:
    """
    Stock being tracked for future opportunities
    """
    symbol: str
    added_date: date
    reason: str  # "IMPROVING_TREND", "OVERSOLD_BOUNCE", "BREAKOUT_SETUP", "MANUAL"
    
    # Initial metrics (when added)
    initial_score: float = 0.0
    initial_return_potential: float = 0.0
    initial_confidence: int = 0
    
    # Current metrics (updated daily)
    current_score: float = 0.0
    current_return_potential: float = 0.0
    current_confidence: int = 0
    
    # Trend tracking
    score_trend: str = "STABLE"  # "IMPROVING", "DECLINING", "STABLE"
    days_on_watchlist: int = 0
    days_until_potential: Optional[int] = None  # Estimated days until it meets criteria
    
    # Alert settings
    alert_when_return_reaches: float = 15.0  # Alert when return potential hits 15%
    alert_when_confidence_reaches: int = 80  # Alert when confidence hits 80%
    alert_enabled: bool = True
    alert_triggered: bool = False
    
    # Additional info
    notes: str = ""
    last_updated: Optional[date] = None
    
    def __post_init__(self):
        """Initialize derived fields"""
        if self.last_updated is None:
            self.last_updated = self.added_date
        
        # Calculate days on watchlist
        self.days_on_watchlist = (date.today() - self.added_date).days
    
    def update_metrics(self, score: float, return_potential: float, confidence: int):
        """
        Update current metrics and determine trend
        
        Args:
            score: New overall score
            return_potential: New estimated return %
            confidence: New confidence level
        """
        # Store old values for trend calculation
        old_score = self.current_score
        
        # Update metrics
        self.current_score = score
        self.current_return_potential = return_potential
        self.current_confidence = confidence
        self.last_updated = date.today()
        
        # Determine trend
        if old_score > 0:
            score_change = score - old_score
            if score_change >= 5:
                self.score_trend = "IMPROVING"
            elif score_change <= -5:
                self.score_trend = "DECLINING"
            else:
                self.score_trend = "STABLE"
        
        # Check if alert should trigger
        if self.alert_enabled and not self.alert_triggered:
            if (self.current_return_potential >= self.alert_when_return_reaches and 
                self.current_confidence >= self.alert_when_confidence_reaches):
                self.alert_triggered = True
    
    def get_score_change(self) -> float:
        """Calculate score change since added"""
        if self.initial_score == 0:
            return 0.0
        return self.current_score - self.initial_score
    
    def get_return_change(self) -> float:
        """Calculate return potential change since added"""
        return self.current_return_potential - self.initial_return_potential
    
    def get_confidence_change(self) -> int:
        """Calculate confidence change since added"""
        return self.current_confidence - self.initial_confidence
    
    def meets_criteria(self, min_return: float = 15.0, min_confidence: int = 80) -> bool:
        """Check if stock now meets trading criteria"""
        return (self.current_return_potential >= min_return and 
                self.current_confidence >= min_confidence)
    
    def estimate_days_to_criteria(self, min_return: float = 15.0, min_confidence: int = 80) -> Optional[int]:
        """
        Estimate days until stock meets criteria based on current trend
        
        Returns:
            Estimated days (None if declining or already meets criteria)
        """
        if self.meets_criteria(min_return, min_confidence):
            return 0
        
        if self.score_trend == "DECLINING":
            return None
        
        if self.days_on_watchlist < 3:
            return None  # Need more data
        
        # Calculate daily improvement rate
        score_change = self.get_score_change()
        daily_score_change = score_change / self.days_on_watchlist
        
        if daily_score_change <= 0:
            return None
        
        # Rough estimation: assume score correlates with meeting criteria
        # A score improvement of 10 points roughly equals meeting threshold
        score_needed = 10  # Arbitrary threshold for improvement
        days_estimate = int(score_needed / daily_score_change)
        
        return max(1, min(days_estimate, 90))  # Cap at 1-90 days
    
    def to_dict(self):
        """Convert to dictionary for export"""
        return {
            'symbol': self.symbol,
            'added_date': self.added_date.isoformat() if self.added_date else None,
            'reason': self.reason,
            'initial_score': self.initial_score,
            'initial_return_potential': self.initial_return_potential,
            'initial_confidence': self.initial_confidence,
            'current_score': self.current_score,
            'current_return_potential': self.current_return_potential,
            'current_confidence': self.current_confidence,
            'score_trend': self.score_trend,
            'days_on_watchlist': self.days_on_watchlist,
            'days_until_potential': self.days_until_potential,
            'alert_when_return_reaches': self.alert_when_return_reaches,
            'alert_when_confidence_reaches': self.alert_when_confidence_reaches,
            'alert_enabled': self.alert_enabled,
            'alert_triggered': self.alert_triggered,
            'notes': self.notes,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create from dictionary"""
        if data.get('added_date'):
            data['added_date'] = date.fromisoformat(data['added_date'])
        if data.get('last_updated'):
            data['last_updated'] = date.fromisoformat(data['last_updated'])
        return cls(**data)
