#!/usr/bin/env python3
"""
Example script demonstrating the Trading Ledger System

This script shows how to:
1. Create and log trades
2. Close trades
3. View performance
4. Export data
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ledger import trade_logger
from ledger.trading_ledger import TradingLedger
from ledger.reports import generate_summary_report, export_to_csv
from models.trade import Trade
from models.day_trade_opportunity import DayTradeOpportunity


def example_swing_trade():
    """Example: Log and close a swing trade"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Swing Trade")
    print("="*70)
    
    # Create a swing trade
    trade = Trade(
        symbol='AAPL',
        name='Apple Inc.',
        entry_price=180.00,
        target_price=195.00,
        stop_price=175.00,
        estimated_return=8.33,
        confidence=85,
        days_to_target=10,
        score=9.5,
        sector='Technology',
        shares=100,
        position_value=18000,
        target_profit=1500,
        max_loss=500,
        risk_reward_ratio=3.0,
        current_price=180.00
    )
    
    # Log the entry
    entry = trade_logger.log_trade_entry(
        trade,
        executed=True,
        notes='Strong breakout above resistance at $180'
    )
    
    print(f"✓ Trade logged: {entry.trade_id}")
    print(f"  Symbol: {entry.symbol}")
    print(f"  Entry: ${entry.predicted_entry:.2f}")
    print(f"  Target: ${entry.predicted_target:.2f}")
    print(f"  Confidence: {entry.predicted_confidence}%")
    
    # Close the trade
    closed = trade_logger.log_trade_exit(
        entry.trade_id,
        exit_price=192.00,
        exit_reason='TARGET_HIT',
        lessons_learned='Momentum was stronger than expected. Hit target in 7 days.'
    )
    
    print(f"\n✓ Trade closed:")
    print(f"  Exit: ${closed.actual_exit:.2f}")
    print(f"  Return: {closed.actual_return_pct:+.2f}%")
    print(f"  Outcome: {closed.outcome}")
    print(f"  Return Accuracy: {closed.return_accuracy:.1f}%")
    print(f"  Entry Quality: {closed.entry_quality:.1f}%")


def example_day_trade():
    """Example: Log a day trade (monitored, not executed)"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Day Trade (Monitored)")
    print("="*70)
    
    # Create a day trade opportunity
    day_trade = DayTradeOpportunity(
        symbol='TSLA',
        name='Tesla Inc.',
        current_price=250.00,
        sector='Automotive',
        entry_price=250.00,
        target_price=257.50,
        stop_price=247.50,
        estimated_return_pct=3.0,
        estimated_return_dollars=750,
        estimated_time_minutes=120,
        confidence=90,
        shares=100,
        position_value=25000
    )
    
    # Log as monitored (not executed)
    entry = trade_logger.log_trade_entry(
        day_trade,
        executed=False,
        notes='Gap and go setup at market open. Did not execute due to volatility.'
    )
    
    print(f"✓ Opportunity logged: {entry.trade_id}")
    print(f"  Symbol: {entry.symbol}")
    print(f"  Type: {entry.trade_type}")
    print(f"  Status: MONITORED (not executed)")
    print(f"  Entry: ${entry.predicted_entry:.2f}")
    print(f"  Target: ${entry.predicted_target:.2f}")


def example_performance_analysis():
    """Example: Analyze performance"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Performance Analysis")
    print("="*70)
    
    ledger = TradingLedger()
    
    # Get performance summary
    summary = ledger.get_performance_summary()
    
    print(f"\nOverall Performance:")
    print(f"  Total Trades: {summary['total_trades']}")
    print(f"  Win Rate: {summary['win_rate']:.2f}%")
    print(f"  Average Return: {summary['avg_return']:+.2f}%")
    print(f"  Total Return: {summary['total_return']:+.2f}%")
    
    # Get accuracy metrics
    accuracy = ledger.calculate_accuracy_metrics()
    
    print(f"\nPrediction Accuracy:")
    print(f"  Return Accuracy: {accuracy['return_accuracy']:.1f}%")
    print(f"  Timeline Accuracy: {accuracy['timeline_accuracy']:.1f}%")
    print(f"  Entry Quality: {accuracy['entry_quality']:.1f}%")
    
    # Get confidence calibration
    calibration = ledger.get_confidence_calibration()
    
    if calibration:
        print(f"\nConfidence Calibration:")
        for bucket, stats in sorted(calibration.items()):
            print(f"  {bucket}: {stats['win_rate']:.1f}% win rate "
                  f"({stats['count']} trades, avg: {stats['avg_return']:+.2f}%)")


def example_export():
    """Example: Export data"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Export Data")
    print("="*70)
    
    ledger = TradingLedger()
    
    # Export to CSV
    csv_path = Path(__file__).parent.parent / "data" / "ledger" / "example_export.csv"
    from ledger.reports import export_to_csv
    export_to_csv(ledger.entries, str(csv_path))
    
    # Generate summary report
    report = generate_summary_report(ledger.entries)
    
    print(f"\nSummary Report Preview:")
    print("-" * 70)
    print('\n'.join(report.split('\n')[:20]))  # First 20 lines
    print("...")


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("TRADING LEDGER SYSTEM - EXAMPLES")
    print("="*70)
    
    # Run examples
    example_swing_trade()
    example_day_trade()
    example_performance_analysis()
    example_export()
    
    print("\n" + "="*70)
    print("EXAMPLES COMPLETE")
    print("="*70)
    print("\nView your trades with:")
    print("  python ledger/ledger_console.py --view")
    print("\nSee performance with:")
    print("  python ledger/ledger_console.py --performance")
    print("")


if __name__ == "__main__":
    main()
