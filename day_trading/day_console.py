"""
Command-line interface for day trading system
"""

import argparse
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from day_trading.day_screener import DayScreener
from day_trading.live_monitor import LiveMonitor
from config.settings import (
    CURRENT_CAPITAL,
    ENABLE_DAY_TRADING_THRESHOLD,
    PDT_WEEKLY_LIMIT,
    DAY_TRADE_CHECK_INTERVAL,
)


class DayTradingCLI:
    """Command-line interface for day trading operations"""
    
    def __init__(self):
        self.screener = DayScreener()
        self.monitor = LiveMonitor()
        self.capital = CURRENT_CAPITAL
        self.educational_mode = self.capital < ENABLE_DAY_TRADING_THRESHOLD
    
    def run_scan(self, symbol: str = None):
        """Run morning pre-market scan"""
        print("\n" + "=" * 80)
        print("🌅 DAY TRADING MORNING SCAN")
        print("=" * 80)
        
        # Display mode
        self._display_trading_mode()
        
        # PDT warning
        self._check_pdt_limit()
        
        print()
        
        if symbol:
            # Scan single symbol
            opp = self.screener.scan_single_stock(symbol)
            if opp:
                self._prompt_add_to_monitor(opp)
        else:
            # Scan all sectors
            opportunities = self.screener.scan_all_sectors()
            
            if opportunities:
                print("\n" + "=" * 80)
                print("🏆 TOP OPPORTUNITIES")
                print("=" * 80)
                
                for i, opp in enumerate(opportunities[:5], 1):
                    print(f"\n#{i} {opp.symbol} - Overall Score: {opp.overall_score:.1f}/100")
                    self.screener._print_opportunity(opp)
                
                # Prompt to add to monitoring
                print("\n" + "-" * 80)
                self._prompt_add_multiple_to_monitor(opportunities[:5])
            else:
                print("\n⚠️  No high-confidence opportunities found today")
                print("   Try again later or adjust confidence threshold")
    
    def monitor_symbol(self, symbol: str, executed: bool = False):
        """Add a specific symbol to monitoring"""
        print(f"\n🔍 Analyzing {symbol} for monitoring...")
        
        opp = self.screener.scan_single_stock(symbol)
        
        if opp:
            self.monitor.add_trade(opp, executed=executed)
            print(f"\n✅ {symbol} added to monitoring")
            print(f"   Will check every {DAY_TRADE_CHECK_INTERVAL} minutes")
        else:
            print(f"\n❌ {symbol} does not meet day trading criteria")
    
    def show_status(self):
        """Show status of all monitored trades"""
        print("\n" + "=" * 80)
        print("📊 DAY TRADING STATUS")
        print("=" * 80)
        
        # Display mode
        self._display_trading_mode()
        
        # Check positions
        self.monitor.check_positions()
        
        # Show PDT count
        print("\n" + "-" * 80)
        self._check_pdt_limit()
    
    def check_positions(self):
        """Check all active positions"""
        self.monitor.check_positions()
    
    def _display_trading_mode(self):
        """Display current trading mode"""
        print(f"\n💰 Capital: ${self.capital:,.2f}")
        
        if self.educational_mode:
            print(f"📚 Mode: EDUCATIONAL (Monitor-only)")
            print(f"   Need ${ENABLE_DAY_TRADING_THRESHOLD - self.capital:,.2f} more to enable execution")
        else:
            print(f"💰 Mode: ACTIVE DAY TRADING")
            print(f"   Trades will be executed (PDT rules apply)")
    
    def _check_pdt_limit(self):
        """Check Pattern Day Trader limit"""
        # Count executed trades in last 5 trading days
        executed_trades = [
            t for t in self.monitor.monitored_trades
            if t.executed and t.entry_time > datetime.now() - timedelta(days=7)
        ]
        
        trade_count = len(executed_trades)
        remaining = PDT_WEEKLY_LIMIT - trade_count
        
        print(f"\n📋 PDT Status: {trade_count}/{PDT_WEEKLY_LIMIT} day trades used this week")
        
        if remaining <= 0:
            print(f"   ⚠️  WARNING: PDT limit reached! No more day trades until next week")
        elif remaining == 1:
            print(f"   ⚠️  CAUTION: Only {remaining} day trade remaining this week")
        else:
            print(f"   ✅ {remaining} day trades remaining this week")
    
    def _prompt_add_to_monitor(self, opp):
        """Prompt user to add opportunity to monitoring"""
        if self.educational_mode:
            print(f"\n💡 Add {opp.symbol} to educational monitoring? (y/n): ", end="")
        else:
            print(f"\n💡 Add {opp.symbol} to monitoring? Execute trade? (y/n/execute): ", end="")
        
        # Note: In actual use, would get user input
        # For automated/scripted use, auto-add in monitor mode
        print("\n   (Auto-adding in monitor mode for scripted execution)")
        self.monitor.add_trade(opp, executed=False)
    
    def _prompt_add_multiple_to_monitor(self, opportunities):
        """Prompt to add multiple opportunities"""
        print("\n💡 Add opportunities to monitoring?")
        print("   Enter symbol(s) separated by space, or 'all' for top 3, or 'none': ", end="")
        
        # Auto-add top 3 for demo
        print("\n   (Auto-adding top 3 for demo)")
        for opp in opportunities[:3]:
            self.monitor.add_trade(opp, executed=False)


def main():
    """Main entry point for day trading CLI"""
    parser = argparse.ArgumentParser(
        description="Day Trading Monitoring System - 1-5% Intraday Opportunities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run morning scan for all sectors
  python day_console.py --scan
  
  # Scan specific symbol
  python day_console.py --scan --symbol AAPL
  
  # Monitor a specific stock (educational mode)
  python day_console.py --monitor TSLA
  
  # Check status of all monitored trades
  python day_console.py --status
  
  # Set custom check interval (in minutes)
  python day_console.py --status --check-interval 10
        """
    )
    
    parser.add_argument(
        '--scan',
        action='store_true',
        help='Run morning pre-market scan for opportunities'
    )
    
    parser.add_argument(
        '--symbol',
        type=str,
        help='Specific symbol to scan or monitor'
    )
    
    parser.add_argument(
        '--monitor',
        type=str,
        metavar='SYMBOL',
        help='Add a specific stock to monitoring'
    )
    
    parser.add_argument(
        '--status',
        action='store_true',
        help="View today's monitored trades and status"
    )
    
    parser.add_argument(
        '--check-interval',
        type=int,
        default=DAY_TRADE_CHECK_INTERVAL,
        metavar='N',
        help='Set check interval in minutes (default: 15)'
    )
    
    parser.add_argument(
        '--execute',
        action='store_true',
        help='Mark trade as executed (requires sufficient capital)'
    )
    
    args = parser.parse_args()
    
    # Create CLI instance
    cli = DayTradingCLI()
    
    # Update check interval if specified
    if args.check_interval != DAY_TRADE_CHECK_INTERVAL:
        cli.monitor.check_interval = args.check_interval
    
    # Execute commands
    if args.scan:
        cli.run_scan(symbol=args.symbol)
    
    elif args.monitor:
        # Check if can execute
        can_execute = args.execute and not cli.educational_mode
        if args.execute and cli.educational_mode:
            print("\n⚠️  Cannot execute trades in educational mode")
            print(f"   Need ${ENABLE_DAY_TRADING_THRESHOLD - cli.capital:,.2f} more capital")
            print("   Adding to monitor-only mode instead\n")
        
        cli.monitor_symbol(args.monitor, executed=can_execute)
    
    elif args.status:
        cli.show_status()
    
    else:
        # No command specified, show help
        parser.print_help()
        
        # Show quick status
        print("\n" + "=" * 80)
        print("QUICK STATUS")
        print("=" * 80)
        cli.show_status()


if __name__ == "__main__":
    main()
