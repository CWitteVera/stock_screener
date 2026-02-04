"""
Main trading ledger class for managing trade records
"""

import json
import os
from datetime import date, datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

from models.ledger_entry import LedgerEntry
from models.trade import Trade
from models.day_trade_opportunity import DayTradeOpportunity


class TradingLedger:
    """
    Main ledger system for tracking all trades (executed and monitored)
    """
    
    def __init__(self, ledger_path: str = None):
        """
        Initialize ledger with optional custom path
        
        Args:
            ledger_path: Path to ledger JSON file (default: data/ledger/ledger.json)
        """
        if ledger_path is None:
            base_dir = Path(__file__).parent.parent
            self.ledger_path = base_dir / "data" / "ledger" / "ledger.json"
        else:
            self.ledger_path = Path(ledger_path)
        
        # Ensure directory exists
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.entries: List[LedgerEntry] = []
        self.load()
    
    def load(self) -> None:
        """Load ledger entries from JSON file"""
        if not self.ledger_path.exists():
            self.entries = []
            return
        
        try:
            with open(self.ledger_path, 'r') as f:
                data = json.load(f)
                self.entries = [LedgerEntry.from_dict(entry) for entry in data]
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Warning: Error loading ledger ({e}). Starting with empty ledger.")
            self.entries = []
    
    def save(self) -> None:
        """Save ledger entries to JSON file"""
        try:
            with open(self.ledger_path, 'w') as f:
                data = [entry.to_dict() for entry in self.entries]
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving ledger: {e}")
            raise
    
    def add_trade_entry(self, trade: Any, executed: bool = False, 
                       notes: str = "") -> LedgerEntry:
        """
        Add a new trade entry to the ledger
        
        Args:
            trade: Trade or DayTradeOpportunity object
            executed: Whether the trade was actually executed
            notes: Additional notes
            
        Returns:
            Created LedgerEntry
        """
        # Generate unique trade ID
        trade_id = self._generate_trade_id(trade.symbol)
        
        # Determine trade type
        if isinstance(trade, DayTradeOpportunity):
            trade_type = "DAY"
            predicted_days = 0  # Intraday
        else:
            trade_type = "SWING"
            predicted_days = getattr(trade, 'days_to_target', 0)
        
        # Create ledger entry
        entry = LedgerEntry(
            trade_id=trade_id,
            trade_type=trade_type,
            symbol=trade.symbol,
            entry_date=date.today(),
            predicted_entry=trade.entry_price,
            predicted_target=trade.target_price,
            predicted_stop=trade.stop_price,
            predicted_return_pct=getattr(trade, 'estimated_return', 
                                        getattr(trade, 'estimated_return_pct', 0.0)),
            predicted_confidence=int(getattr(trade, 'confidence', 0)),
            predicted_days=predicted_days,
            executed=executed,
            notes=notes
        )
        
        # If executed, set actual entry to predicted (can be updated later)
        if executed:
            entry.actual_entry = trade.entry_price
        
        self.entries.append(entry)
        self.save()
        
        return entry
    
    def update_trade_exit(self, trade_id: str, exit_price: float, 
                         exit_reason: str = "MANUAL",
                         lessons_learned: str = "") -> Optional[LedgerEntry]:
        """
        Update trade with exit information
        
        Args:
            trade_id: Unique trade identifier
            exit_price: Actual exit price
            exit_reason: Reason for exit (TARGET_HIT, STOP_LOSS, TIME_LIMIT, MANUAL)
            lessons_learned: Lessons learned from the trade
            
        Returns:
            Updated LedgerEntry or None if not found
        """
        entry = self.get_trade_by_id(trade_id)
        if not entry:
            print(f"Warning: Trade {trade_id} not found")
            return None
        
        # Set exit data
        entry.exit_date = date.today()
        entry.actual_exit = exit_price
        entry.exit_reason = exit_reason
        entry.lessons_learned = lessons_learned
        
        # Calculate actual days (if not day trade)
        if entry.entry_date and entry.exit_date:
            entry.actual_days = (entry.exit_date - entry.entry_date).days
        
        # Calculate returns
        if entry.actual_entry and entry.actual_exit:
            entry.actual_return_pct = ((entry.actual_exit - entry.actual_entry) / 
                                      entry.actual_entry * 100)
            
            # Determine outcome
            if entry.actual_return_pct > 0.5:
                entry.outcome = "WIN"
            elif entry.actual_return_pct < -0.5:
                entry.outcome = "LOSS"
            else:
                entry.outcome = "BREAK_EVEN"
            
            # Calculate P&L if executed
            if entry.executed:
                # Would need shares count - simplified here
                entry.profit_loss = entry.actual_return_pct
        
        # Calculate accuracy metrics
        entry.calculate_accuracy_metrics()
        
        self.save()
        return entry
    
    def get_trade_by_id(self, trade_id: str) -> Optional[LedgerEntry]:
        """Get trade entry by ID"""
        for entry in self.entries:
            if entry.trade_id == trade_id:
                return entry
        return None
    
    def get_open_trades(self) -> List[LedgerEntry]:
        """Get all trades that haven't been closed"""
        return [e for e in self.entries if e.exit_date is None]
    
    def get_closed_trades(self) -> List[LedgerEntry]:
        """Get all closed trades"""
        return [e for e in self.entries if e.exit_date is not None]
    
    def get_executed_trades(self) -> List[LedgerEntry]:
        """Get only executed trades"""
        return [e for e in self.entries if e.executed]
    
    def calculate_accuracy_metrics(self) -> Dict[str, float]:
        """
        Calculate overall accuracy metrics across all closed trades
        
        Returns:
            Dictionary with accuracy metrics
        """
        closed = self.get_closed_trades()
        if not closed:
            return {
                'return_accuracy': 0.0,
                'timeline_accuracy': 0.0,
                'entry_quality': 0.0,
                'total_trades': 0
            }
        
        # Calculate averages
        return_accuracies = [e.return_accuracy for e in closed if e.return_accuracy is not None]
        timeline_accuracies = [e.timeline_accuracy for e in closed if e.timeline_accuracy is not None]
        entry_qualities = [e.entry_quality for e in closed if e.entry_quality is not None]
        
        return {
            'return_accuracy': sum(return_accuracies) / len(return_accuracies) if return_accuracies else 0.0,
            'timeline_accuracy': sum(timeline_accuracies) / len(timeline_accuracies) if timeline_accuracies else 0.0,
            'entry_quality': sum(entry_qualities) / len(entry_qualities) if entry_qualities else 0.0,
            'total_trades': len(closed)
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive performance summary
        
        Returns:
            Dictionary with performance metrics
        """
        executed = self.get_executed_trades()
        closed_executed = [e for e in executed if e.exit_date is not None]
        
        if not closed_executed:
            return {
                'total_trades': 0,
                'open_trades': len(self.get_open_trades()),
                'win_rate': 0.0,
                'avg_return': 0.0,
                'total_return': 0.0,
                'wins': 0,
                'losses': 0,
                'break_evens': 0
            }
        
        # Calculate metrics
        wins = [e for e in closed_executed if e.outcome == "WIN"]
        losses = [e for e in closed_executed if e.outcome == "LOSS"]
        break_evens = [e for e in closed_executed if e.outcome == "BREAK_EVEN"]
        
        total_return = sum(e.actual_return_pct or 0 for e in closed_executed)
        avg_return = total_return / len(closed_executed)
        
        win_rate = (len(wins) / len(closed_executed) * 100) if closed_executed else 0.0
        
        return {
            'total_trades': len(closed_executed),
            'open_trades': len([e for e in executed if e.exit_date is None]),
            'win_rate': win_rate,
            'avg_return': avg_return,
            'total_return': total_return,
            'wins': len(wins),
            'losses': len(losses),
            'break_evens': len(break_evens),
            'avg_win': sum(e.actual_return_pct for e in wins) / len(wins) if wins else 0.0,
            'avg_loss': sum(e.actual_return_pct for e in losses) / len(losses) if losses else 0.0,
        }
    
    def get_confidence_calibration(self) -> Dict[int, Dict[str, Any]]:
        """
        Analyze how well predicted confidence correlates with actual outcomes
        
        Returns:
            Dictionary mapping confidence levels to actual performance
        """
        closed = self.get_closed_trades()
        if not closed:
            return {}
        
        # Group by confidence buckets (0-50, 50-70, 70-85, 85-100)
        buckets = {
            '0-50': [],
            '50-70': [],
            '70-85': [],
            '85-100': []
        }
        
        for entry in closed:
            conf = entry.predicted_confidence
            if conf < 50:
                bucket = '0-50'
            elif conf < 70:
                bucket = '50-70'
            elif conf < 85:
                bucket = '70-85'
            else:
                bucket = '85-100'
            
            buckets[bucket].append(entry)
        
        # Calculate stats for each bucket
        result = {}
        for bucket, entries in buckets.items():
            if not entries:
                continue
            
            wins = [e for e in entries if e.outcome == "WIN"]
            win_rate = (len(wins) / len(entries) * 100) if entries else 0.0
            avg_return = sum(e.actual_return_pct or 0 for e in entries) / len(entries)
            
            result[bucket] = {
                'count': len(entries),
                'win_rate': win_rate,
                'avg_return': avg_return,
                'wins': len(wins)
            }
        
        return result
    
    def _generate_trade_id(self, symbol: str) -> str:
        """Generate unique trade ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{symbol}_{timestamp}"
