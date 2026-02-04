"""
Ledger entry model for tracking trades
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import date

@dataclass
class LedgerEntry:
    """
    Complete record of a trade (executed or monitored)
    """
    # Identification
    trade_id: str
    trade_type: str  # "SWING" or "DAY"
    symbol: str
    entry_date: date
    exit_date: Optional[date] = None
    
    # Predicted values
    predicted_entry: float = 0.0
    predicted_target: float = 0.0
    predicted_stop: float = 0.0
    predicted_return_pct: float = 0.0
    predicted_confidence: int = 0
    predicted_days: int = 0
    
    # Actual values
    actual_entry: Optional[float] = None
    actual_exit: Optional[float] = None
    actual_return_pct: Optional[float] = None
    actual_days: Optional[int] = None
    executed: bool = False  # True if trade was executed, False if only monitored
    
    # Results
    profit_loss: Optional[float] = None
    outcome: Optional[str] = None  # "WIN", "LOSS", "BREAK_EVEN"
    exit_reason: Optional[str] = None  # "TARGET_HIT", "STOP_LOSS", "TIME_LIMIT", "MANUAL"
    
    # Accuracy metrics (calculated on exit)
    return_accuracy: Optional[float] = None  # How close prediction was to actual
    timeline_accuracy: Optional[float] = None
    entry_quality: Optional[float] = None  # Slippage from predicted entry
    
    # Notes
    notes: str = ""
    lessons_learned: str = ""
    
    def to_dict(self):
        """Convert to dictionary for export"""
        return {
            'trade_id': self.trade_id,
            'trade_type': self.trade_type,
            'symbol': self.symbol,
            'entry_date': self.entry_date.isoformat() if self.entry_date else None,
            'exit_date': self.exit_date.isoformat() if self.exit_date else None,
            'predicted_entry': self.predicted_entry,
            'predicted_target': self.predicted_target,
            'predicted_stop': self.predicted_stop,
            'predicted_return_pct': self.predicted_return_pct,
            'predicted_confidence': self.predicted_confidence,
            'predicted_days': self.predicted_days,
            'actual_entry': self.actual_entry,
            'actual_exit': self.actual_exit,
            'actual_return_pct': self.actual_return_pct,
            'actual_days': self.actual_days,
            'executed': self.executed,
            'profit_loss': self.profit_loss,
            'outcome': self.outcome,
            'exit_reason': self.exit_reason,
            'return_accuracy': self.return_accuracy,
            'timeline_accuracy': self.timeline_accuracy,
            'entry_quality': self.entry_quality,
            'notes': self.notes,
            'lessons_learned': self.lessons_learned,
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create from dictionary"""
        # Convert date strings to date objects
        if data.get('entry_date'):
            data['entry_date'] = date.fromisoformat(data['entry_date'])
        if data.get('exit_date'):
            data['exit_date'] = date.fromisoformat(data['exit_date'])
        return cls(**data)
    
    def calculate_accuracy_metrics(self):
        """
        Calculate accuracy metrics after trade exits
        """
        if self.actual_exit is None or self.actual_entry is None:
            return
        
        # Return accuracy - how close was our return prediction?
        if self.predicted_return_pct != 0:
            predicted_abs = abs(self.predicted_return_pct)
            actual_abs = abs(self.actual_return_pct) if self.actual_return_pct else 0
            error = abs(predicted_abs - actual_abs)
            self.return_accuracy = max(0, 100 - (error * 10))  # 10% error = 0% accuracy
        
        # Timeline accuracy
        if self.predicted_days > 0 and self.actual_days:
            days_error = abs(self.predicted_days - self.actual_days)
            self.timeline_accuracy = max(0, 100 - (days_error * 10))  # 10 days error = 0% accuracy
        
        # Entry quality (slippage)
        if self.predicted_entry > 0 and self.actual_entry:
            slippage_pct = abs((self.actual_entry - self.predicted_entry) / self.predicted_entry * 100)
            self.entry_quality = max(0, 100 - (slippage_pct * 20))  # 5% slippage = 0% quality
