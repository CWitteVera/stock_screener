"""
Capital account model for tracking capital progression
"""

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional, Dict

@dataclass
class CapitalAccount:
    """
    Track capital progression over time
    """
    starting_capital: float = 4000.0
    current_capital: float = 4000.0
    
    # Paycheck tracking
    paycheck_amount: float = 100.0
    paycheck_frequency_days: int = 14
    next_paycheck_date: date = None
    
    # Trading stats
    total_invested: float = 0.0
    total_profit: float = 0.0
    total_dividends: float = 0.0
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    
    def __post_init__(self):
        """Initialize next paycheck date if not set"""
        if self.next_paycheck_date is None:
            self.next_paycheck_date = date.today() + timedelta(days=self.paycheck_frequency_days)
    
    def add_paycheck(self, amount: Optional[float] = None, paycheck_date: Optional[date] = None):
        """
        Log paycheck deposit
        
        Args:
            amount: Paycheck amount (default: use self.paycheck_amount)
            paycheck_date: Date of deposit (default: today)
        """
        deposit_amount = amount if amount is not None else self.paycheck_amount
        self.current_capital += deposit_amount
        
        # Update next paycheck date
        base_date = paycheck_date if paycheck_date else date.today()
        self.next_paycheck_date = base_date + timedelta(days=self.paycheck_frequency_days)
    
    def record_trade_result(self, profit_loss: float, was_win: bool = None):
        """
        Update capital after trade
        
        Args:
            profit_loss: Profit or loss from trade (negative for loss)
            was_win: Whether trade was a win (determined automatically if None)
        """
        self.current_capital += profit_loss
        self.total_profit += profit_loss
        self.total_trades += 1
        
        if was_win is None:
            was_win = profit_loss > 0
        
        if was_win:
            self.winning_trades += 1
        else:
            self.losing_trades += 1
    
    def get_win_rate(self) -> float:
        """Calculate win rate percentage"""
        if self.total_trades == 0:
            return 0.0
        return (self.winning_trades / self.total_trades) * 100
    
    def get_total_return_pct(self) -> float:
        """Calculate total return percentage from starting capital"""
        if self.starting_capital == 0:
            return 0.0
        return ((self.current_capital - self.starting_capital) / self.starting_capital) * 100
    
    def time_to_goal(self, goal_amount: float = 7000.0) -> Dict[str, any]:
        """
        Calculate time to reach goal
        
        Returns:
            Dictionary with different scenarios:
            - paychecks_only: Days to goal with just paychecks
            - current_performance: Days with current trading performance
            - optimistic: Days if 80%+ win rate continues
            - pessimistic: Days if win rate drops to 50%
        """
        remaining = goal_amount - self.current_capital
        
        if remaining <= 0:
            return {
                'goal_reached': True,
                'message': f'Goal of ${goal_amount:,.2f} already reached!'
            }
        
        # Paychecks only
        paychecks_needed = remaining / self.paycheck_amount
        days_paychecks_only = int(paychecks_needed * self.paycheck_frequency_days)
        
        # Current performance (if trading)
        avg_profit_per_trade = self.total_profit / self.total_trades if self.total_trades > 0 else 0
        
        if avg_profit_per_trade > 0:
            # Estimate trades per month (assuming 2 trades/week)
            trades_per_month = 8
            monthly_trading_profit = avg_profit_per_trade * trades_per_month
            monthly_total = monthly_trading_profit + (self.paycheck_amount * 2)  # 2 paychecks/month
            
            months_needed = remaining / monthly_total
            days_current_performance = int(months_needed * 30)
        else:
            days_current_performance = days_paychecks_only
        
        # Optimistic scenario (80% win rate, $150 avg profit per winning trade)
        optimistic_monthly = (0.8 * 150 * 8) + (self.paycheck_amount * 2)
        days_optimistic = int((remaining / optimistic_monthly) * 30)
        
        # Pessimistic scenario (50% win rate, $100 avg profit per winning trade)
        pessimistic_monthly = (0.5 * 100 * 8) + (self.paycheck_amount * 2)
        days_pessimistic = int((remaining / pessimistic_monthly) * 30)
        
        return {
            'goal_reached': False,
            'remaining': remaining,
            'paychecks_only': {
                'days': days_paychecks_only,
                'date': date.today() + timedelta(days=days_paychecks_only)
            },
            'current_performance': {
                'days': days_current_performance,
                'date': date.today() + timedelta(days=days_current_performance)
            },
            'optimistic': {
                'days': days_optimistic,
                'date': date.today() + timedelta(days=days_optimistic)
            },
            'pessimistic': {
                'days': days_pessimistic,
                'date': date.today() + timedelta(days=days_pessimistic)
            }
        }
    
    def to_dict(self):
        """Convert to dictionary for export"""
        return {
            'starting_capital': self.starting_capital,
            'current_capital': self.current_capital,
            'paycheck_amount': self.paycheck_amount,
            'paycheck_frequency_days': self.paycheck_frequency_days,
            'next_paycheck_date': self.next_paycheck_date.isoformat() if self.next_paycheck_date else None,
            'total_invested': self.total_invested,
            'total_profit': self.total_profit,
            'total_dividends': self.total_dividends,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': self.get_win_rate(),
            'total_return_pct': self.get_total_return_pct(),
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create from dictionary"""
        if data.get('next_paycheck_date'):
            data['next_paycheck_date'] = date.fromisoformat(data['next_paycheck_date'])
        return cls(**{k: v for k, v in data.items() if k not in ['win_rate', 'total_return_pct']})
