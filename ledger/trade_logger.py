"""
Simple convenience functions for logging trades
"""

from typing import Optional, Any
from .trading_ledger import TradingLedger
from models.ledger_entry import LedgerEntry

# Global ledger instance
_ledger = None


def _get_ledger() -> TradingLedger:
    """Get or create global ledger instance"""
    global _ledger
    if _ledger is None:
        _ledger = TradingLedger()
    return _ledger


def log_trade_entry(trade: Any, executed: bool = True, notes: str = "") -> LedgerEntry:
    """
    Log a trade entry to the ledger
    
    Args:
        trade: Trade or DayTradeOpportunity object
        executed: Whether the trade was actually executed (default: True)
        notes: Additional notes about the trade
        
    Returns:
        Created LedgerEntry with unique trade_id
        
    Example:
        >>> trade = Trade(...)
        >>> entry = log_trade_entry(trade, executed=True, notes="Strong breakout setup")
        >>> print(f"Trade logged with ID: {entry.trade_id}")
    """
    ledger = _get_ledger()
    return ledger.add_trade_entry(trade, executed=executed, notes=notes)


def log_trade_exit(trade_id: str, exit_price: float, 
                   exit_reason: str = "MANUAL",
                   lessons_learned: str = "") -> Optional[LedgerEntry]:
    """
    Log the exit of a trade
    
    Args:
        trade_id: Unique trade identifier from log_trade_entry
        exit_price: Actual exit price
        exit_reason: Reason for exit (TARGET_HIT, STOP_LOSS, TIME_LIMIT, MANUAL)
        lessons_learned: What was learned from this trade
        
    Returns:
        Updated LedgerEntry or None if trade not found
        
    Example:
        >>> entry = log_trade_exit(
        ...     "AAPL_20240204_123456",
        ...     exit_price=185.50,
        ...     exit_reason="TARGET_HIT",
        ...     lessons_learned="Trend was stronger than expected"
        ... )
    """
    ledger = _get_ledger()
    return ledger.update_trade_exit(
        trade_id=trade_id,
        exit_price=exit_price,
        exit_reason=exit_reason,
        lessons_learned=lessons_learned
    )


def get_trade_by_id(trade_id: str) -> Optional[LedgerEntry]:
    """
    Get a trade entry by its ID
    
    Args:
        trade_id: Unique trade identifier
        
    Returns:
        LedgerEntry or None if not found
        
    Example:
        >>> entry = get_trade_by_id("AAPL_20240204_123456")
        >>> if entry:
        ...     print(f"Trade status: {entry.outcome or 'OPEN'}")
    """
    ledger = _get_ledger()
    return ledger.get_trade_by_id(trade_id)


def get_all_trades() -> list:
    """
    Get all trade entries
    
    Returns:
        List of all LedgerEntry objects
    """
    ledger = _get_ledger()
    return ledger.entries


def get_open_trades() -> list:
    """
    Get all currently open trades
    
    Returns:
        List of open LedgerEntry objects
    """
    ledger = _get_ledger()
    return ledger.get_open_trades()


def get_closed_trades() -> list:
    """
    Get all closed trades
    
    Returns:
        List of closed LedgerEntry objects
    """
    ledger = _get_ledger()
    return ledger.get_closed_trades()


def reload_ledger() -> None:
    """
    Reload ledger from disk (useful after external modifications)
    """
    global _ledger
    _ledger = None
    _get_ledger()
