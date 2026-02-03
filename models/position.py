"""
Position tracking model
"""

from dataclasses import dataclass, asdict
from typing import Optional
from datetime import datetime, date
import json
import os
from pathlib import Path

@dataclass
class Position:
    """Active position tracker"""
    symbol: str
    name: str
    entry_price: float
    entry_date: date
    shares: int
    target_price: float
    stop_price: float
    max_hold_days: int
    
    # Current status
    current_price: Optional[float] = None
    current_value: Optional[float] = None
    unrealized_pnl: Optional[float] = None
    unrealized_pnl_percent: Optional[float] = None
    days_held: Optional[int] = None
    days_remaining: Optional[int] = None
    
    # Signals
    above_20ma: Optional[bool] = None
    rsi: Optional[float] = None
    macd_bullish: Optional[bool] = None
    volume_above_avg: Optional[bool] = None
    
    status: str = "HOLD"
    notes: str = ""
    
    def update(self, current_price: float, technical_data: dict = None):
        """Update position with current market data"""
        self.current_price = current_price
        self.current_value = self.shares * current_price
        
        entry_value = self.shares * self.entry_price
        self.unrealized_pnl = self.current_value - entry_value
        self.unrealized_pnl_percent = (self.unrealized_pnl / entry_value) * 100
        
        # Calculate days held
        today = date.today()
        delta = today - self.entry_date
        self.days_held = delta.days
        self.days_remaining = self.max_hold_days - self.days_held
        
        # Update technical signals if provided
        if technical_data:
            self.above_20ma = technical_data.get('above_20ma', None)
            self.rsi = technical_data.get('rsi', None)
            self.macd_bullish = technical_data.get('macd_bullish', None)
            self.volume_above_avg = technical_data.get('volume_above_avg', None)
        
        # Determine status
        self._update_status()
    
    def _update_status(self):
        """Determine position status based on signals"""
        if self.current_price is None:
            self.status = "UNKNOWN"
            return
        
        # Check exit conditions
        if self.current_price >= self.target_price:
            self.status = "TARGET REACHED"
        elif self.current_price <= self.stop_price:
            self.status = "STOP LOSS HIT"
        elif self.days_remaining <= 0:
            self.status = "MAX TIME REACHED"
        else:
            self.status = "HOLD"
    
    def should_exit(self) -> bool:
        """Check if position should be exited"""
        return self.status in ["TARGET REACHED", "STOP LOSS HIT", "MAX TIME REACHED"]
    
    def get_progress_percent(self) -> float:
        """Get progress towards target as percentage"""
        if self.current_price is None:
            return 0.0
        
        total_target_move = self.target_price - self.entry_price
        current_move = self.current_price - self.entry_price
        
        if total_target_move <= 0:
            return 0.0
        
        return (current_move / total_target_move) * 100
    
    def save(self):
        """Save position to file"""
        base_dir = Path(__file__).parent.parent
        positions_dir = os.path.join(base_dir, 'data', 'positions')
        os.makedirs(positions_dir, exist_ok=True)
        
        filename = f"{self.symbol}_{self.entry_date.isoformat()}.json"
        filepath = os.path.join(positions_dir, filename)
        
        # Convert to dict, handling date serialization
        data = asdict(self)
        data['entry_date'] = self.entry_date.isoformat()
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    @classmethod
    def load(cls, symbol: str):
        """Load most recent position for symbol"""
        base_dir = Path(__file__).parent.parent
        positions_dir = os.path.join(base_dir, 'data', 'positions')
        
        if not os.path.exists(positions_dir):
            return None
        
        # Find all position files for this symbol
        position_files = [f for f in os.listdir(positions_dir) 
                         if f.startswith(f"{symbol}_") and f.endswith('.json')]
        
        if not position_files:
            return None
        
        # Get most recent
        position_files.sort(reverse=True)
        filepath = os.path.join(positions_dir, position_files[0])
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Convert date string back to date
        data['entry_date'] = datetime.fromisoformat(data['entry_date']).date()
        
        return cls(**data)
