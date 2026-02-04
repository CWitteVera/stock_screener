"""
Calculate prediction accuracy metrics
"""

from typing import List, Dict, Any, Optional
from models.ledger_entry import LedgerEntry


def calculate_return_accuracy(predicted: float, actual: float) -> float:
    """
    Calculate how accurate the return prediction was
    
    Args:
        predicted: Predicted return percentage
        actual: Actual return percentage
        
    Returns:
        Accuracy score (0-100), where 100 is perfect prediction
        
    Formula:
        - Compare absolute values to handle long/short symmetry
        - 10% error = 0% accuracy
        - Linear interpolation between 0% and 10% error
        
    Example:
        >>> calculate_return_accuracy(10.0, 9.5)  # 0.5% error
        95.0
        >>> calculate_return_accuracy(10.0, 5.0)  # 5% error
        50.0
    """
    if predicted == 0:
        return 0.0
    
    predicted_abs = abs(predicted)
    actual_abs = abs(actual)
    error = abs(predicted_abs - actual_abs)
    
    # 10% error = 0% accuracy, linear scale
    accuracy = max(0, 100 - (error * 10))
    return round(accuracy, 2)


def calculate_timeline_accuracy(predicted_days: int, actual_days: int) -> float:
    """
    Calculate how accurate the timeline prediction was
    
    Args:
        predicted_days: Predicted days to target
        actual_days: Actual days to target
        
    Returns:
        Accuracy score (0-100)
        
    Formula:
        - 10 days error = 0% accuracy
        - Linear interpolation
        
    Example:
        >>> calculate_timeline_accuracy(5, 5)
        100.0
        >>> calculate_timeline_accuracy(5, 8)  # 3 days off
        70.0
    """
    if predicted_days <= 0:
        return 0.0
    
    days_error = abs(predicted_days - actual_days)
    
    # 10 days error = 0% accuracy
    accuracy = max(0, 100 - (days_error * 10))
    return round(accuracy, 2)


def calculate_entry_quality(predicted_price: float, actual_price: float) -> float:
    """
    Calculate entry quality based on slippage from predicted entry
    
    Args:
        predicted_price: Predicted/intended entry price
        actual_price: Actual entry price achieved
        
    Returns:
        Quality score (0-100), where 100 is no slippage
        
    Formula:
        - 5% slippage = 0% quality
        - Penalizes both positive and negative slippage
        
    Example:
        >>> calculate_entry_quality(100.0, 100.0)  # Perfect entry
        100.0
        >>> calculate_entry_quality(100.0, 101.0)  # 1% slippage
        80.0
    """
    if predicted_price <= 0:
        return 0.0
    
    slippage_pct = abs((actual_price - predicted_price) / predicted_price * 100)
    
    # 5% slippage = 0% quality
    quality = max(0, 100 - (slippage_pct * 20))
    return round(quality, 2)


def get_overall_accuracy(ledger_entries: List[LedgerEntry]) -> Dict[str, Any]:
    """
    Calculate overall accuracy metrics across multiple trades
    
    Args:
        ledger_entries: List of closed trade entries
        
    Returns:
        Dictionary with overall accuracy statistics
        
    Example:
        >>> entries = get_closed_trades()
        >>> accuracy = get_overall_accuracy(entries)
        >>> print(f"Return accuracy: {accuracy['return_accuracy']:.1f}%")
    """
    if not ledger_entries:
        return {
            'return_accuracy': 0.0,
            'timeline_accuracy': 0.0,
            'entry_quality': 0.0,
            'total_trades': 0,
            'trades_with_return_data': 0,
            'trades_with_timeline_data': 0,
            'trades_with_entry_data': 0
        }
    
    # Filter only closed trades
    closed = [e for e in ledger_entries if e.exit_date is not None]
    
    if not closed:
        return {
            'return_accuracy': 0.0,
            'timeline_accuracy': 0.0,
            'entry_quality': 0.0,
            'total_trades': 0,
            'trades_with_return_data': 0,
            'trades_with_timeline_data': 0,
            'trades_with_entry_data': 0
        }
    
    # Collect accuracy metrics
    return_accuracies = []
    timeline_accuracies = []
    entry_qualities = []
    
    for entry in closed:
        # Return accuracy
        if entry.return_accuracy is not None:
            return_accuracies.append(entry.return_accuracy)
        elif entry.actual_return_pct is not None:
            acc = calculate_return_accuracy(
                entry.predicted_return_pct,
                entry.actual_return_pct
            )
            return_accuracies.append(acc)
        
        # Timeline accuracy
        if entry.timeline_accuracy is not None:
            timeline_accuracies.append(entry.timeline_accuracy)
        elif entry.actual_days is not None and entry.predicted_days > 0:
            acc = calculate_timeline_accuracy(
                entry.predicted_days,
                entry.actual_days
            )
            timeline_accuracies.append(acc)
        
        # Entry quality
        if entry.entry_quality is not None:
            entry_qualities.append(entry.entry_quality)
        elif entry.actual_entry is not None and entry.predicted_entry > 0:
            qual = calculate_entry_quality(
                entry.predicted_entry,
                entry.actual_entry
            )
            entry_qualities.append(qual)
    
    return {
        'return_accuracy': round(sum(return_accuracies) / len(return_accuracies), 2) if return_accuracies else 0.0,
        'timeline_accuracy': round(sum(timeline_accuracies) / len(timeline_accuracies), 2) if timeline_accuracies else 0.0,
        'entry_quality': round(sum(entry_qualities) / len(entry_qualities), 2) if entry_qualities else 0.0,
        'total_trades': len(closed),
        'trades_with_return_data': len(return_accuracies),
        'trades_with_timeline_data': len(timeline_accuracies),
        'trades_with_entry_data': len(entry_qualities)
    }


def get_accuracy_by_confidence(ledger_entries: List[LedgerEntry]) -> Dict[str, Dict[str, float]]:
    """
    Group accuracy metrics by confidence level
    
    Args:
        ledger_entries: List of closed trade entries
        
    Returns:
        Dictionary mapping confidence buckets to accuracy stats
        
    Example:
        >>> entries = get_closed_trades()
        >>> by_conf = get_accuracy_by_confidence(entries)
        >>> print(by_conf['85-100']['return_accuracy'])
    """
    # Group by confidence buckets
    buckets = {
        '0-50': [],
        '50-70': [],
        '70-85': [],
        '85-100': []
    }
    
    closed = [e for e in ledger_entries if e.exit_date is not None]
    
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
    
    # Calculate accuracy for each bucket
    result = {}
    for bucket, entries in buckets.items():
        if entries:
            result[bucket] = get_overall_accuracy(entries)
    
    return result


def get_accuracy_by_trade_type(ledger_entries: List[LedgerEntry]) -> Dict[str, Dict[str, float]]:
    """
    Get accuracy metrics grouped by trade type (SWING vs DAY)
    
    Args:
        ledger_entries: List of closed trade entries
        
    Returns:
        Dictionary with accuracy metrics for each trade type
    """
    swing_trades = [e for e in ledger_entries if e.trade_type == "SWING"]
    day_trades = [e for e in ledger_entries if e.trade_type == "DAY"]
    
    return {
        'SWING': get_overall_accuracy(swing_trades),
        'DAY': get_overall_accuracy(day_trades)
    }
