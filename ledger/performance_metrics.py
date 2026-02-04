"""
Performance metrics calculations
"""

from typing import List, Dict, Any, Optional, Tuple
from models.ledger_entry import LedgerEntry


def get_win_rate(entries: List[LedgerEntry]) -> float:
    """
    Calculate win rate from closed trades
    
    Args:
        entries: List of trade entries
        
    Returns:
        Win rate as percentage (0-100)
        
    Example:
        >>> entries = get_closed_trades()
        >>> win_rate = get_win_rate(entries)
        >>> print(f"Win rate: {win_rate:.1f}%")
    """
    closed = [e for e in entries if e.exit_date is not None and e.outcome is not None]
    
    if not closed:
        return 0.0
    
    wins = [e for e in closed if e.outcome == "WIN"]
    return round((len(wins) / len(closed)) * 100, 2)


def get_profit_loss_summary(entries: List[LedgerEntry]) -> Dict[str, Any]:
    """
    Get comprehensive profit/loss summary
    
    Args:
        entries: List of trade entries (typically executed trades only)
        
    Returns:
        Dictionary with P&L metrics
        
    Example:
        >>> entries = get_executed_trades()
        >>> summary = get_profit_loss_summary(entries)
        >>> print(f"Total return: {summary['total_return_pct']:.2f}%")
    """
    # Filter to closed executed trades
    closed_executed = [
        e for e in entries 
        if e.exit_date is not None and e.executed and e.actual_return_pct is not None
    ]
    
    if not closed_executed:
        return {
            'total_return_pct': 0.0,
            'avg_return_pct': 0.0,
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'break_even_trades': 0,
            'largest_win_pct': 0.0,
            'largest_loss_pct': 0.0,
            'avg_win_pct': 0.0,
            'avg_loss_pct': 0.0,
            'win_rate': 0.0
        }
    
    # Separate wins and losses
    wins = [e for e in closed_executed if e.outcome == "WIN"]
    losses = [e for e in closed_executed if e.outcome == "LOSS"]
    break_evens = [e for e in closed_executed if e.outcome == "BREAK_EVEN"]
    
    # Calculate metrics
    total_return = sum(e.actual_return_pct for e in closed_executed)
    avg_return = total_return / len(closed_executed)
    
    win_returns = [e.actual_return_pct for e in wins] if wins else [0.0]
    loss_returns = [e.actual_return_pct for e in losses] if losses else [0.0]
    
    return {
        'total_return_pct': round(total_return, 2),
        'avg_return_pct': round(avg_return, 2),
        'total_trades': len(closed_executed),
        'winning_trades': len(wins),
        'losing_trades': len(losses),
        'break_even_trades': len(break_evens),
        'largest_win_pct': round(max(win_returns), 2),
        'largest_loss_pct': round(min(loss_returns), 2),
        'avg_win_pct': round(sum(win_returns) / len(win_returns), 2) if wins else 0.0,
        'avg_loss_pct': round(sum(loss_returns) / len(loss_returns), 2) if losses else 0.0,
        'win_rate': get_win_rate(closed_executed)
    }


def get_avg_profit_per_trade(entries: List[LedgerEntry]) -> float:
    """
    Calculate average profit per trade
    
    Args:
        entries: List of executed trade entries
        
    Returns:
        Average return percentage per trade
        
    Example:
        >>> avg = get_avg_profit_per_trade(entries)
        >>> print(f"Average profit per trade: {avg:.2f}%")
    """
    closed_executed = [
        e for e in entries 
        if e.exit_date is not None and e.executed and e.actual_return_pct is not None
    ]
    
    if not closed_executed:
        return 0.0
    
    total = sum(e.actual_return_pct for e in closed_executed)
    return round(total / len(closed_executed), 2)


def get_best_worst_trades(entries: List[LedgerEntry], 
                          n: int = 5) -> Tuple[List[LedgerEntry], List[LedgerEntry]]:
    """
    Get best and worst performing trades
    
    Args:
        entries: List of trade entries
        n: Number of top/bottom trades to return
        
    Returns:
        Tuple of (best_trades, worst_trades)
        
    Example:
        >>> best, worst = get_best_worst_trades(entries, n=3)
        >>> for trade in best:
        ...     print(f"{trade.symbol}: {trade.actual_return_pct:.2f}%")
    """
    closed = [
        e for e in entries 
        if e.exit_date is not None and e.actual_return_pct is not None
    ]
    
    if not closed:
        return ([], [])
    
    # Sort by return
    sorted_trades = sorted(closed, key=lambda x: x.actual_return_pct or 0, reverse=True)
    
    best = sorted_trades[:n]
    worst = sorted_trades[-n:]
    worst.reverse()  # Show worst first
    
    return (best, worst)


def get_metrics_by_type(entries: List[LedgerEntry], 
                       trade_type: str) -> Dict[str, Any]:
    """
    Get performance metrics filtered by trade type
    
    Args:
        entries: List of trade entries
        trade_type: "SWING" or "DAY"
        
    Returns:
        Performance metrics for that trade type
        
    Example:
        >>> swing_metrics = get_metrics_by_type(entries, "SWING")
        >>> day_metrics = get_metrics_by_type(entries, "DAY")
    """
    filtered = [e for e in entries if e.trade_type == trade_type]
    
    return {
        'trade_type': trade_type,
        'total_trades': len(filtered),
        'open_trades': len([e for e in filtered if e.exit_date is None]),
        'closed_trades': len([e for e in filtered if e.exit_date is not None]),
        'executed_trades': len([e for e in filtered if e.executed]),
        'win_rate': get_win_rate(filtered),
        'profit_loss': get_profit_loss_summary(filtered),
        'avg_profit': get_avg_profit_per_trade(filtered)
    }


def get_metrics_by_symbol(entries: List[LedgerEntry]) -> Dict[str, Dict[str, Any]]:
    """
    Get performance metrics grouped by symbol
    
    Args:
        entries: List of trade entries
        
    Returns:
        Dictionary mapping symbols to their metrics
        
    Example:
        >>> by_symbol = get_metrics_by_symbol(entries)
        >>> print(by_symbol['AAPL']['win_rate'])
    """
    # Group by symbol
    by_symbol: Dict[str, List[LedgerEntry]] = {}
    
    for entry in entries:
        if entry.symbol not in by_symbol:
            by_symbol[entry.symbol] = []
        by_symbol[entry.symbol].append(entry)
    
    # Calculate metrics for each symbol
    result = {}
    for symbol, symbol_entries in by_symbol.items():
        closed = [e for e in symbol_entries if e.exit_date is not None]
        
        result[symbol] = {
            'total_trades': len(symbol_entries),
            'closed_trades': len(closed),
            'win_rate': get_win_rate(symbol_entries),
            'avg_return': get_avg_profit_per_trade(symbol_entries)
        }
    
    return result


def get_metrics_by_confidence(entries: List[LedgerEntry]) -> Dict[str, Dict[str, Any]]:
    """
    Get performance metrics grouped by confidence level
    
    Args:
        entries: List of trade entries
        
    Returns:
        Dictionary mapping confidence buckets to metrics
        
    Example:
        >>> by_conf = get_metrics_by_confidence(entries)
        >>> high_conf = by_conf['85-100']
        >>> print(f"High confidence win rate: {high_conf['win_rate']:.1f}%")
    """
    # Group by confidence buckets
    buckets = {
        '0-50': [],
        '50-70': [],
        '70-85': [],
        '85-100': []
    }
    
    for entry in entries:
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
    
    # Calculate metrics for each bucket
    result = {}
    for bucket, bucket_entries in buckets.items():
        if not bucket_entries:
            continue
        
        result[bucket] = {
            'total_trades': len(bucket_entries),
            'win_rate': get_win_rate(bucket_entries),
            'profit_loss': get_profit_loss_summary(bucket_entries),
            'avg_return': get_avg_profit_per_trade(bucket_entries)
        }
    
    return result


def get_expectancy(entries: List[LedgerEntry]) -> float:
    """
    Calculate trading expectancy (average profit per dollar risked)
    
    Args:
        entries: List of trade entries
        
    Returns:
        Expectancy value (positive is good)
        
    Formula:
        Expectancy = (Win% × Avg Win) - (Loss% × Avg Loss)
        
    Example:
        >>> exp = get_expectancy(entries)
        >>> print(f"Expectancy: {exp:.2f}%")
    """
    closed = [
        e for e in entries 
        if e.exit_date is not None and e.actual_return_pct is not None
    ]
    
    if not closed:
        return 0.0
    
    wins = [e for e in closed if e.outcome == "WIN"]
    losses = [e for e in closed if e.outcome == "LOSS"]
    
    if not wins and not losses:
        return 0.0
    
    win_rate = len(wins) / len(closed)
    loss_rate = len(losses) / len(closed)
    
    avg_win = sum(e.actual_return_pct for e in wins) / len(wins) if wins else 0.0
    avg_loss = abs(sum(e.actual_return_pct for e in losses) / len(losses)) if losses else 0.0
    
    expectancy = (win_rate * avg_win) - (loss_rate * avg_loss)
    return round(expectancy, 2)
