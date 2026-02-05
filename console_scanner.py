#!/usr/bin/env python3
"""
Console Scanner - CLI version of the swing trading screener
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.screener import AdaptiveScreener
from core.o_position_manager import OPositionManager
from models.position import Position
from ui.export import format_results_text, format_trade_summary, export_to_fidelity_csv, export_full_analysis_csv
from utils.logger import logger

def display_stage_breakdown(stage_data):
    """Display filtering funnel in console"""
    print("\n" + "="*70)
    print("📊 FILTERING BREAKDOWN")
    print("="*70)
    print(f"\nUniverse: {stage_data.get('universe_name', 'Unknown')}")
    print(f"Total Scanned: {stage_data.get('total_scanned', 0)} stocks")
    print(f"Total Time: {stage_data.get('total_time', 0):.1f}s")
    print("\n" + "-"*70)
    
    for stage in stage_data['stages']:
        stage_num = stage['stage']
        stage_name = stage['name']
        description = stage['description']
        input_count = stage['input_count']
        passed = stage['passed_count']
        failed = stage['failed_count']
        pass_rate = stage['pass_rate']
        time_sec = stage['time_seconds']
        
        print(f"\nStage {stage_num}: {stage_name}")
        print(f"  {description}")
        print(f"  Input:   {input_count:,} stocks")
        print(f"  ✅ Passed: {passed:,} stocks ({pass_rate:.1f}%)")
        print(f"  ❌ Failed: {failed:,} stocks")
        if time_sec > 0:
            print(f"  Time: {time_sec:.1f}s")
    
    print("\n" + "="*70)

def main():
    parser = argparse.ArgumentParser(
        description='Swing Trading Stock Screener - Console Version',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan Technology sector for 15%+ opportunities
  python console_scanner.py --sector Technology
  
  # Scan Healthcare for 8%+ opportunities  
  python console_scanner.py --sector Healthcare --min-return 8
  
  # Scan custom watchlist
  python console_scanner.py --watchlist watchlists/custom.txt
  
  # Scan S&P 500 universe
  python console_scanner.py --universe sp500 --min-return 5 --min-confidence 60
  
  # Scan all markets (1000+ stocks)
  python console_scanner.py --universe all_markets --min-return 0 --min-confidence 0
  
  # Monitor active position
  python console_scanner.py --monitor NVDA
  
  # Export results to Fidelity CSV
  python console_scanner.py --sector Technology --export fidelity
        """
    )
    
    parser.add_argument(
        '--sector',
        choices=['Technology', 'Healthcare', 'Energy', 'Financials', 'Consumer', 'Communications'],
        help='Sector to scan'
    )
    
    parser.add_argument(
        '--watchlist',
        help='Path to custom watchlist file'
    )
    
    parser.add_argument(
        '--universe',
        choices=['sp500', 'nasdaq100', 'high_volume', 'all_markets'],
        help='Scan entire stock universe (500-1000+ stocks)'
    )
    
    parser.add_argument(
        '--min-return',
        type=float,
        default=15.0,
        help='Minimum return target percentage (default: 15%%)'
    )
    
    parser.add_argument(
        '--min-confidence',
        type=int,
        default=60,
        help='Minimum confidence percentage (0-100, default: 60)'
    )
    
    parser.add_argument(
        '--monitor',
        help='Monitor active position for symbol (e.g., NVDA)'
    )
    
    parser.add_argument(
        '--export',
        choices=['fidelity', 'csv', 'json', 'text'],
        help='Export results to file format'
    )
    
    parser.add_argument(
        '--output',
        default='trades',
        help='Output filename prefix (default: trades)'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.monitor and not args.sector and not args.watchlist and not args.universe:
        parser.error("Must specify --sector, --watchlist, --universe, or --monitor")
    
    screener = AdaptiveScreener()
    
    try:
        if args.monitor:
            # Monitor existing position
            print(f"\n🔍 Monitoring position: {args.monitor}")
            print("="*60)
            position = screener.monitor_position(args.monitor)
            
            if position:
                print_position_status(position)
            else:
                print(f"❌ No active position found for {args.monitor}")
                print("   Use the screener to find a trade first.")
        
        elif args.universe:
            # Scan universe
            print(f"\n🔍 Scanning {args.universe} universe")
            print(f"   Target return: {args.min_return}%+")
            print(f"   Minimum confidence: {args.min_confidence}%+")
            print("="*60)
            
            results = screener.scan_universe(args.universe, args.min_return, args.min_confidence)
            
            # Display stage breakdown if available
            if 'stage_breakdown' in results:
                display_stage_breakdown(results['stage_breakdown'])
            
            print_results(results, args)
        
        elif args.watchlist:
            # Scan custom watchlist
            print(f"\n🔍 Scanning custom watchlist: {args.watchlist}")
            print(f"   Target return: {args.min_return}%+")
            print("="*60)
            
            results = screener.scan_watchlist(args.watchlist, args.min_return)
            print_results(results, args)
        
        else:
            # Scan sector
            print(f"\n🔍 Scanning {args.sector} sector")
            print(f"   Target return: {args.min_return}%+")
            print("="*60)
            
            results = screener.scan_sector(args.sector, args.min_return)
            print_results(results, args)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Scan interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error during scan: {str(e)}", exc_info=True)
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)

def print_results(results, args):
    """Print scan results to console"""
    
    # Format and print
    text = format_results_text(results)
    print(text)
    
    # Show O position analysis
    o_manager = OPositionManager(shares=69.312, avg_cost=55.90)
    print(o_manager.get_summary())
    
    # Check if should sell O for swing trade
    if results.get('trades') and len(results['trades']) > 0:
        best_trade = results['trades'][0]
        sell_analysis = o_manager.analyze_sell_signal(
            swing_return=best_trade.estimated_return,
            swing_confidence=best_trade.confidence
        )
        
        print("\n" + "="*70)
        print("💰 SWAP ANALYSIS: O vs Swing Trade")
        print("="*70)
        
        if sell_analysis['should_sell']:
            print(f"✅ {sell_analysis['recommendation']}")
            analysis = sell_analysis['analysis']
            print(f"\nProfit Breakdown:")
            print(f"  Swing Profit:     +${analysis['swing_profit']:,.2f}")
            print(f"  Lost Dividend:    -${analysis['lost_dividend']:.2f}")
            print(f"  Taxes on O:       -${analysis['o_taxes']:.2f}")
            print(f"  Net Advantage:    +${analysis['net_advantage']:.2f}")
        else:
            print(f"🔴 {sell_analysis['recommendation']}")
            print(f"Reason: {sell_analysis['reason']}")
        
        print("="*70)
    
    # Export if requested
    if args.export and results['trades']:
        export_results(results, args)

def export_results(results, args):
    """Export results to file"""
    
    trades = results['trades']
    
    if args.export == 'fidelity':
        filename = f"{args.output}_fidelity.csv"
        if export_to_fidelity_csv(trades, filename):
            print(f"\n✅ Exported to Fidelity CSV: {filename}")
    
    elif args.export == 'csv':
        filename = f"{args.output}_analysis.csv"
        if export_full_analysis_csv(trades, filename):
            print(f"\n✅ Exported to CSV: {filename}")
    
    elif args.export == 'json':
        from ui.export import export_to_json
        filename = f"{args.output}.json"
        if export_to_json(trades, filename):
            print(f"\n✅ Exported to JSON: {filename}")
    
    elif args.export == 'text':
        filename = f"{args.output}.txt"
        text = format_results_text(results)
        with open(filename, 'w') as f:
            f.write(text)
        print(f"\n✅ Exported to text file: {filename}")

def print_position_status(position):
    """Print position monitoring information"""
    
    print(f"""
═══════════════════════════════════════════════
💼 ACTIVE POSITION: {position.symbol}
═══════════════════════════════════════════════

{position.name}
Entry: {position.entry_date} | Day {position.days_held} of {position.max_hold_days}

📊 POSITION:
   Shares:  {position.shares} @ ${position.entry_price:.2f}
   Current: ${position.current_price:.2f}
   Value:   ${position.current_value:.2f}
   
💰 P&L:
   Unrealized: {'+' if position.unrealized_pnl >= 0 else ''}{position.unrealized_pnl:.2f} ({position.unrealized_pnl_percent:+.1f}%)
   Target:     ${position.target_price:.2f} ({((position.target_price / position.current_price - 1) * 100):.1f}% away)
   Progress:   {position.get_progress_percent():.0f}% {"●" * int(position.get_progress_percent()/10)}{"○" * (10 - int(position.get_progress_percent()/10))}
   
🎯 TARGETS:
   Target: ${position.target_price:.2f}
   Stop:   ${position.stop_price:.2f}
   
⏱️  Time: {position.days_remaining} days remaining

📈 SIGNALS:
   {"✅" if position.above_20ma else "❌"} {'Above' if position.above_20ma else 'Below'} 20-day MA
   {"✅" if position.rsi and 40 <= position.rsi <= 70 else "⚠️"} RSI: {position.rsi:.0f if position.rsi else 'N/A'}
   {"✅" if position.volume_above_avg else "⚠️"} Volume {'above' if position.volume_above_avg else 'below'} average
   {"✅" if position.macd_bullish else "❌"} MACD {'bullish' if position.macd_bullish else 'bearish'}
   
💡 STATUS: {position.status}
""")
    
    if position.should_exit():
        print("⚠️  EXIT SIGNAL: Consider closing this position!")
    else:
        print("   Thesis intact. Continue holding.")
    
    print("="*60)

if __name__ == '__main__':
    main()
