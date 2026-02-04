"""
Export and reporting functionality
"""

import csv
import json
from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime

from models.ledger_entry import LedgerEntry
from .performance_metrics import (
    get_win_rate,
    get_profit_loss_summary,
    get_avg_profit_per_trade,
    get_best_worst_trades,
    get_expectancy
)
from .accuracy_calculator import get_overall_accuracy


def export_to_csv(entries: List[LedgerEntry], filepath: str) -> bool:
    """
    Export ledger entries to CSV file
    
    Args:
        entries: List of ledger entries to export
        filepath: Path to output CSV file
        
    Returns:
        True if successful, False otherwise
        
    Example:
        >>> entries = get_all_trades()
        >>> export_to_csv(entries, "data/ledger/export.csv")
    """
    if not entries:
        print("No entries to export")
        return False
    
    try:
        # Ensure directory exists
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', newline='') as f:
            # Define CSV columns
            fieldnames = [
                'trade_id', 'trade_type', 'symbol', 'entry_date', 'exit_date',
                'predicted_entry', 'predicted_target', 'predicted_stop',
                'predicted_return_pct', 'predicted_confidence', 'predicted_days',
                'actual_entry', 'actual_exit', 'actual_return_pct', 'actual_days',
                'executed', 'profit_loss', 'outcome', 'exit_reason',
                'return_accuracy', 'timeline_accuracy', 'entry_quality',
                'notes', 'lessons_learned'
            ]
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for entry in entries:
                # Convert dates to strings
                row = entry.to_dict()
                writer.writerow(row)
        
        print(f"✓ Exported {len(entries)} entries to {filepath}")
        return True
        
    except Exception as e:
        print(f"Error exporting to CSV: {e}")
        return False


def export_to_json(entries: List[LedgerEntry], filepath: str) -> bool:
    """
    Export ledger entries to JSON file
    
    Args:
        entries: List of ledger entries to export
        filepath: Path to output JSON file
        
    Returns:
        True if successful, False otherwise
        
    Example:
        >>> entries = get_all_trades()
        >>> export_to_json(entries, "data/ledger/export.json")
    """
    if not entries:
        print("No entries to export")
        return False
    
    try:
        # Ensure directory exists
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w') as f:
            data = [entry.to_dict() for entry in entries]
            json.dump(data, f, indent=2)
        
        print(f"✓ Exported {len(entries)} entries to {filepath}")
        return True
        
    except Exception as e:
        print(f"Error exporting to JSON: {e}")
        return False


def generate_summary_report(entries: List[LedgerEntry]) -> str:
    """
    Generate a comprehensive text summary report
    
    Args:
        entries: List of ledger entries
        
    Returns:
        Formatted string report
        
    Example:
        >>> entries = get_all_trades()
        >>> report = generate_summary_report(entries)
        >>> print(report)
    """
    if not entries:
        return "No trades to report on."
    
    # Calculate metrics
    closed = [e for e in entries if e.exit_date is not None]
    executed = [e for e in entries if e.executed]
    open_trades = [e for e in entries if e.exit_date is None]
    
    pl_summary = get_profit_loss_summary(executed)
    accuracy = get_overall_accuracy(closed)
    best, worst = get_best_worst_trades(closed, n=3)
    expectancy = get_expectancy(closed)
    
    # Separate by trade type
    swing_trades = [e for e in closed if e.trade_type == "SWING"]
    day_trades = [e for e in closed if e.trade_type == "DAY"]
    
    # Build report
    lines = []
    lines.append("=" * 70)
    lines.append("TRADING LEDGER SUMMARY REPORT")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 70)
    lines.append("")
    
    # Overall statistics
    lines.append("OVERALL STATISTICS")
    lines.append("-" * 70)
    lines.append(f"Total Trades:        {len(entries)}")
    lines.append(f"Open Trades:         {len(open_trades)}")
    lines.append(f"Closed Trades:       {len(closed)}")
    lines.append(f"Executed Trades:     {len(executed)}")
    lines.append(f"Monitored Only:      {len(entries) - len(executed)}")
    lines.append("")
    
    # Trade type breakdown
    lines.append("TRADE TYPE BREAKDOWN")
    lines.append("-" * 70)
    lines.append(f"Swing Trades:        {len(swing_trades)}")
    lines.append(f"Day Trades:          {len(day_trades)}")
    lines.append("")
    
    # Performance metrics
    if executed:
        lines.append("PERFORMANCE METRICS (Executed Trades Only)")
        lines.append("-" * 70)
        lines.append(f"Win Rate:            {pl_summary['win_rate']:.2f}%")
        lines.append(f"Total Return:        {pl_summary['total_return_pct']:.2f}%")
        lines.append(f"Avg Return:          {pl_summary['avg_return_pct']:.2f}%")
        lines.append(f"Expectancy:          {expectancy:.2f}%")
        lines.append("")
        lines.append(f"Winning Trades:      {pl_summary['winning_trades']}")
        lines.append(f"Losing Trades:       {pl_summary['losing_trades']}")
        lines.append(f"Break Even:          {pl_summary['break_even_trades']}")
        lines.append("")
        lines.append(f"Largest Win:         {pl_summary['largest_win_pct']:.2f}%")
        lines.append(f"Largest Loss:        {pl_summary['largest_loss_pct']:.2f}%")
        lines.append(f"Avg Win:             {pl_summary['avg_win_pct']:.2f}%")
        lines.append(f"Avg Loss:            {pl_summary['avg_loss_pct']:.2f}%")
        lines.append("")
    
    # Accuracy metrics
    if closed:
        lines.append("PREDICTION ACCURACY")
        lines.append("-" * 70)
        lines.append(f"Return Accuracy:     {accuracy['return_accuracy']:.2f}%")
        lines.append(f"Timeline Accuracy:   {accuracy['timeline_accuracy']:.2f}%")
        lines.append(f"Entry Quality:       {accuracy['entry_quality']:.2f}%")
        lines.append(f"Trades Analyzed:     {accuracy['total_trades']}")
        lines.append("")
    
    # Best trades
    if best:
        lines.append("TOP 3 BEST TRADES")
        lines.append("-" * 70)
        for i, trade in enumerate(best, 1):
            lines.append(f"{i}. {trade.symbol:6s} {trade.actual_return_pct:+6.2f}%  "
                        f"({trade.entry_date} -> {trade.exit_date})")
        lines.append("")
    
    # Worst trades
    if worst:
        lines.append("TOP 3 WORST TRADES")
        lines.append("-" * 70)
        for i, trade in enumerate(worst, 1):
            lines.append(f"{i}. {trade.symbol:6s} {trade.actual_return_pct:+6.2f}%  "
                        f"({trade.entry_date} -> {trade.exit_date})")
        lines.append("")
    
    # Open positions
    if open_trades:
        lines.append("OPEN POSITIONS")
        lines.append("-" * 70)
        for trade in open_trades:
            status = "EXECUTED" if trade.executed else "MONITORED"
            lines.append(f"{trade.symbol:6s} {status:10s} Entry: ${trade.actual_entry or trade.predicted_entry:.2f}  "
                        f"Target: ${trade.predicted_target:.2f}  ({trade.entry_date})")
        lines.append("")
    
    lines.append("=" * 70)
    
    return "\n".join(lines)


def export_summary_to_file(entries: List[LedgerEntry], filepath: str) -> bool:
    """
    Export summary report to text file
    
    Args:
        entries: List of ledger entries
        filepath: Path to output text file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        report = generate_summary_report(entries)
        
        with open(filepath, 'w') as f:
            f.write(report)
        
        print(f"✓ Summary report saved to {filepath}")
        return True
        
    except Exception as e:
        print(f"Error saving summary report: {e}")
        return False


def export_html_report(entries: List[LedgerEntry], filepath: str) -> bool:
    """
    Export summary report as HTML file
    
    Args:
        entries: List of ledger entries
        filepath: Path to output HTML file
        
    Returns:
        True if successful, False otherwise
    """
    if not entries:
        print("No entries to export")
        return False
    
    try:
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        # Calculate metrics
        closed = [e for e in entries if e.exit_date is not None]
        executed = [e for e in entries if e.executed]
        pl_summary = get_profit_loss_summary(executed)
        accuracy = get_overall_accuracy(closed)
        
        # Build HTML
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Trading Ledger Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
        .metric {{ font-size: 1.2em; margin: 10px 0; }}
        .positive {{ color: green; }}
        .negative {{ color: red; }}
    </style>
</head>
<body>
    <h1>Trading Ledger Report</h1>
    <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <h2>Performance Summary</h2>
    <div class="metric">Win Rate: <strong>{pl_summary['win_rate']:.2f}%</strong></div>
    <div class="metric">Total Return: <strong class="{'positive' if pl_summary['total_return_pct'] > 0 else 'negative'}">{pl_summary['total_return_pct']:+.2f}%</strong></div>
    <div class="metric">Average Return: <strong>{pl_summary['avg_return_pct']:.2f}%</strong></div>
    
    <h2>All Trades</h2>
    <table>
        <tr>
            <th>Symbol</th>
            <th>Type</th>
            <th>Entry Date</th>
            <th>Exit Date</th>
            <th>Return %</th>
            <th>Outcome</th>
        </tr>
"""
        
        for entry in closed:
            return_class = 'positive' if entry.actual_return_pct and entry.actual_return_pct > 0 else 'negative'
            return_value = f"{entry.actual_return_pct:.2f}%" if entry.actual_return_pct else 'N/A'
            html += f"""        <tr>
            <td>{entry.symbol}</td>
            <td>{entry.trade_type}</td>
            <td>{entry.entry_date}</td>
            <td>{entry.exit_date or 'OPEN'}</td>
            <td class="{return_class}">{return_value}</td>
            <td>{entry.outcome or 'OPEN'}</td>
        </tr>
"""
        
        html += """    </table>
</body>
</html>"""
        
        with open(filepath, 'w') as f:
            f.write(html)
        
        print(f"✓ HTML report saved to {filepath}")
        return True
        
    except Exception as e:
        print(f"Error saving HTML report: {e}")
        return False
