#!/usr/bin/env python3
"""
Trading Ledger Console - CLI interface for the trading ledger system
"""

import argparse
import sys
from pathlib import Path
from datetime import date

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ledger.trading_ledger import TradingLedger
from ledger.accuracy_calculator import get_overall_accuracy, get_accuracy_by_confidence
from ledger.performance_metrics import (
    get_win_rate,
    get_profit_loss_summary,
    get_metrics_by_type,
    get_best_worst_trades,
    get_expectancy
)
from ledger.reports import (
    export_to_csv,
    export_to_json,
    generate_summary_report,
    export_summary_to_file,
    export_html_report
)


def view_ledger(ledger: TradingLedger, show_open_only: bool = False, 
               show_closed_only: bool = False):
    """Display all ledger entries"""
    if show_open_only:
        entries = ledger.get_open_trades()
        title = "OPEN TRADES"
    elif show_closed_only:
        entries = ledger.get_closed_trades()
        title = "CLOSED TRADES"
    else:
        entries = ledger.entries
        title = "ALL TRADES"
    
    if not entries:
        print(f"\n{title}: None")
        return
    
    print(f"\n{'=' * 100}")
    print(f"{title} ({len(entries)} total)")
    print('=' * 100)
    print(f"{'ID':<20} {'Symbol':<8} {'Type':<6} {'Entry':<12} {'Exit':<12} {'Return':<10} {'Status':<10}")
    print('-' * 100)
    
    for entry in entries:
        entry_date = entry.entry_date.strftime('%Y-%m-%d') if entry.entry_date else 'N/A'
        exit_date = entry.exit_date.strftime('%Y-%m-%d') if entry.exit_date else 'OPEN'
        
        return_str = f"{entry.actual_return_pct:+6.2f}%" if entry.actual_return_pct is not None else "N/A"
        status = entry.outcome or ("EXECUTED" if entry.executed else "MONITORED")
        
        print(f"{entry.trade_id:<20} {entry.symbol:<8} {entry.trade_type:<6} "
              f"{entry_date:<12} {exit_date:<12} {return_str:<10} {status:<10}")
    
    print('=' * 100)


def view_accuracy(ledger: TradingLedger):
    """Display accuracy metrics"""
    closed = ledger.get_closed_trades()
    
    if not closed:
        print("\nNo closed trades to analyze.")
        return
    
    overall = get_overall_accuracy(closed)
    by_confidence = get_accuracy_by_confidence(closed)
    
    print("\n" + "=" * 70)
    print("PREDICTION ACCURACY METRICS")
    print("=" * 70)
    
    print("\nOVERALL ACCURACY")
    print("-" * 70)
    print(f"Return Accuracy:      {overall['return_accuracy']:6.2f}%  ({overall['trades_with_return_data']} trades)")
    print(f"Timeline Accuracy:    {overall['timeline_accuracy']:6.2f}%  ({overall['trades_with_timeline_data']} trades)")
    print(f"Entry Quality:        {overall['entry_quality']:6.2f}%  ({overall['trades_with_entry_data']} trades)")
    
    if by_confidence:
        print("\nACCURACY BY CONFIDENCE LEVEL")
        print("-" * 70)
        print(f"{'Confidence':<15} {'Trades':<8} {'Return Acc':<12} {'Timeline Acc':<12} {'Entry Quality':<12}")
        print("-" * 70)
        
        for bucket in ['85-100', '70-85', '50-70', '0-50']:
            if bucket in by_confidence:
                data = by_confidence[bucket]
                print(f"{bucket:<15} {data['total_trades']:<8} "
                      f"{data['return_accuracy']:>10.2f}%  "
                      f"{data['timeline_accuracy']:>10.2f}%  "
                      f"{data['entry_quality']:>10.2f}%")
    
    print("=" * 70)


def view_performance(ledger: TradingLedger):
    """Display performance summary"""
    executed = ledger.get_executed_trades()
    
    if not executed:
        print("\nNo executed trades to analyze.")
        return
    
    closed_executed = [e for e in executed if e.exit_date is not None]
    
    if not closed_executed:
        print("\nNo closed executed trades yet.")
        return
    
    pl_summary = get_profit_loss_summary(executed)
    swing_metrics = get_metrics_by_type(ledger.entries, "SWING")
    day_metrics = get_metrics_by_type(ledger.entries, "DAY")
    best, worst = get_best_worst_trades(closed_executed, n=5)
    expectancy = get_expectancy(closed_executed)
    
    print("\n" + "=" * 70)
    print("PERFORMANCE SUMMARY")
    print("=" * 70)
    
    print("\nOVERALL PERFORMANCE")
    print("-" * 70)
    print(f"Total Trades:         {pl_summary['total_trades']}")
    print(f"Win Rate:             {pl_summary['win_rate']:6.2f}%")
    print(f"Total Return:         {pl_summary['total_return_pct']:+7.2f}%")
    print(f"Average Return:       {pl_summary['avg_return_pct']:+7.2f}%")
    print(f"Expectancy:           {expectancy:+7.2f}%")
    
    print("\nWINS vs LOSSES")
    print("-" * 70)
    print(f"Winning Trades:       {pl_summary['winning_trades']}")
    print(f"Losing Trades:        {pl_summary['losing_trades']}")
    print(f"Break Even:           {pl_summary['break_even_trades']}")
    print(f"Average Win:          {pl_summary['avg_win_pct']:+7.2f}%")
    print(f"Average Loss:         {pl_summary['avg_loss_pct']:+7.2f}%")
    print(f"Largest Win:          {pl_summary['largest_win_pct']:+7.2f}%")
    print(f"Largest Loss:         {pl_summary['largest_loss_pct']:+7.2f}%")
    
    print("\nBY TRADE TYPE")
    print("-" * 70)
    print(f"Swing Trades:         {swing_metrics['closed_trades']} closed, "
          f"Win Rate: {swing_metrics['win_rate']:.2f}%, "
          f"Avg: {swing_metrics['avg_profit']:+.2f}%")
    print(f"Day Trades:           {day_metrics['closed_trades']} closed, "
          f"Win Rate: {day_metrics['win_rate']:.2f}%, "
          f"Avg: {day_metrics['avg_profit']:+.2f}%")
    
    if best:
        print("\nTOP 5 BEST TRADES")
        print("-" * 70)
        for i, trade in enumerate(best, 1):
            print(f"{i}. {trade.symbol:6s} {trade.actual_return_pct:+7.2f}%  "
                  f"{trade.entry_date} -> {trade.exit_date}")
    
    if worst:
        print("\nTOP 5 WORST TRADES")
        print("-" * 70)
        for i, trade in enumerate(worst, 1):
            print(f"{i}. {trade.symbol:6s} {trade.actual_return_pct:+7.2f}%  "
                  f"{trade.entry_date} -> {trade.exit_date}")
    
    print("=" * 70)


def export_ledger(ledger: TradingLedger, format: str, output_path: str = None):
    """Export ledger to file"""
    if not ledger.entries:
        print("\nNo trades to export.")
        return
    
    if output_path is None:
        timestamp = date.today().strftime('%Y%m%d')
        base_dir = Path(__file__).parent.parent / "data" / "ledger"
        
        if format == "csv":
            output_path = base_dir / f"ledger_export_{timestamp}.csv"
        elif format == "json":
            output_path = base_dir / f"ledger_export_{timestamp}.json"
        elif format == "txt":
            output_path = base_dir / f"ledger_summary_{timestamp}.txt"
        elif format == "html":
            output_path = base_dir / f"ledger_report_{timestamp}.html"
    else:
        output_path = Path(output_path)
    
    print(f"\nExporting to {output_path}...")
    
    if format == "csv":
        success = export_to_csv(ledger.entries, str(output_path))
    elif format == "json":
        success = export_to_json(ledger.entries, str(output_path))
    elif format == "txt":
        success = export_summary_to_file(ledger.entries, str(output_path))
    elif format == "html":
        success = export_html_report(ledger.entries, str(output_path))
    else:
        print(f"Unknown format: {format}")
        return
    
    if success:
        print(f"✓ Export complete")


def add_trade_interactive(ledger: TradingLedger):
    """Interactive trade entry"""
    print("\n" + "=" * 70)
    print("ADD NEW TRADE")
    print("=" * 70)
    
    try:
        symbol = input("Symbol: ").strip().upper()
        trade_type = input("Type (SWING/DAY) [SWING]: ").strip().upper() or "SWING"
        
        entry_price = float(input("Entry Price: "))
        target_price = float(input("Target Price: "))
        stop_price = float(input("Stop Price: "))
        
        confidence = int(input("Confidence (0-100): "))
        
        if trade_type == "SWING":
            days = int(input("Predicted Days to Target: "))
        else:
            days = 0
        
        executed = input("Executed (y/n) [n]: ").strip().lower() == 'y'
        notes = input("Notes: ").strip()
        
        # Create minimal trade object
        from models.trade import Trade
        from models.day_trade_opportunity import DayTradeOpportunity
        
        return_pct = ((target_price - entry_price) / entry_price) * 100
        
        if trade_type == "DAY":
            trade = DayTradeOpportunity(
                symbol=symbol,
                name=symbol,
                current_price=entry_price,
                sector="Unknown",
                entry_price=entry_price,
                target_price=target_price,
                stop_price=stop_price,
                estimated_return_pct=return_pct,
                estimated_return_dollars=0,
                estimated_time_minutes=240,
                confidence=confidence,
                shares=0,
                position_value=0
            )
        else:
            trade = Trade(
                symbol=symbol,
                name=symbol,
                entry_price=entry_price,
                target_price=target_price,
                stop_price=stop_price,
                estimated_return=return_pct,
                confidence=confidence,
                days_to_target=days,
                score=0,
                sector="Unknown",
                shares=0,
                position_value=0,
                target_profit=0,
                max_loss=0,
                risk_reward_ratio=0,
                current_price=entry_price
            )
        
        entry = ledger.add_trade_entry(trade, executed=executed, notes=notes)
        
        print(f"\n✓ Trade added successfully!")
        print(f"  Trade ID: {entry.trade_id}")
        print(f"  Symbol: {entry.symbol}")
        print(f"  Type: {entry.trade_type}")
        print(f"  Status: {'EXECUTED' if executed else 'MONITORED'}")
        
    except KeyboardInterrupt:
        print("\n\nCancelled.")
    except Exception as e:
        print(f"\nError: {e}")


def close_trade_interactive(ledger: TradingLedger):
    """Interactive trade exit"""
    open_trades = ledger.get_open_trades()
    
    if not open_trades:
        print("\nNo open trades to close.")
        return
    
    print("\n" + "=" * 70)
    print("CLOSE TRADE")
    print("=" * 70)
    
    print("\nOpen trades:")
    for i, trade in enumerate(open_trades, 1):
        status = "EXECUTED" if trade.executed else "MONITORED"
        print(f"{i}. {trade.trade_id} - {trade.symbol} ({status})")
    
    try:
        choice = int(input("\nSelect trade number: ")) - 1
        if choice < 0 or choice >= len(open_trades):
            print("Invalid selection.")
            return
        
        trade = open_trades[choice]
        
        exit_price = float(input("Exit Price: "))
        
        print("\nExit reasons:")
        print("1. TARGET_HIT")
        print("2. STOP_LOSS")
        print("3. TIME_LIMIT")
        print("4. MANUAL")
        
        reason_choice = input("Select reason [4]: ").strip() or "4"
        reasons = {
            "1": "TARGET_HIT",
            "2": "STOP_LOSS",
            "3": "TIME_LIMIT",
            "4": "MANUAL"
        }
        exit_reason = reasons.get(reason_choice, "MANUAL")
        
        lessons = input("Lessons Learned: ").strip()
        
        updated = ledger.update_trade_exit(
            trade.trade_id,
            exit_price,
            exit_reason,
            lessons
        )
        
        if updated:
            print(f"\n✓ Trade closed successfully!")
            print(f"  Return: {updated.actual_return_pct:+.2f}%")
            print(f"  Outcome: {updated.outcome}")
            print(f"  Return Accuracy: {updated.return_accuracy:.2f}%" if updated.return_accuracy else "")
        
    except KeyboardInterrupt:
        print("\n\nCancelled.")
    except Exception as e:
        print(f"\nError: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Trading Ledger Console - Track and analyze your trades",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --view                    # View all trades
  %(prog)s --view --open             # View open trades only
  %(prog)s --accuracy                # View accuracy metrics
  %(prog)s --performance             # View performance summary
  %(prog)s --export csv              # Export to CSV
  %(prog)s --export json output.json # Export to specific file
  %(prog)s --add-trade               # Add new trade interactively
  %(prog)s --close-trade             # Close a trade interactively
  %(prog)s --summary                 # Generate full summary report
        """
    )
    
    parser.add_argument('--view', action='store_true',
                       help='View ledger entries')
    parser.add_argument('--open', action='store_true',
                       help='Show only open trades (with --view)')
    parser.add_argument('--closed', action='store_true',
                       help='Show only closed trades (with --view)')
    parser.add_argument('--accuracy', action='store_true',
                       help='View accuracy metrics')
    parser.add_argument('--performance', action='store_true',
                       help='View performance summary')
    parser.add_argument('--export', choices=['csv', 'json', 'txt', 'html'],
                       help='Export ledger to file')
    parser.add_argument('--output', type=str,
                       help='Output file path for export')
    parser.add_argument('--add-trade', action='store_true',
                       help='Add new trade interactively')
    parser.add_argument('--close-trade', action='store_true',
                       help='Close a trade interactively')
    parser.add_argument('--summary', action='store_true',
                       help='Generate and print summary report')
    
    args = parser.parse_args()
    
    # Load ledger
    ledger = TradingLedger()
    
    # Execute commands
    if args.view:
        view_ledger(ledger, show_open_only=args.open, show_closed_only=args.closed)
    elif args.accuracy:
        view_accuracy(ledger)
    elif args.performance:
        view_performance(ledger)
    elif args.export:
        export_ledger(ledger, args.export, args.output)
    elif args.add_trade:
        add_trade_interactive(ledger)
    elif args.close_trade:
        close_trade_interactive(ledger)
    elif args.summary:
        report = generate_summary_report(ledger.entries)
        print(report)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
