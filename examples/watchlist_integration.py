"""
Example: Integration of watchlist with main screener

This script demonstrates how to:
1. Run the main screener
2. Auto-populate watchlist with near-threshold stocks
3. Update watchlist daily
4. Generate alerts for ready stocks
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.watchlist_manager import WatchlistManager
from core.auto_watchlist import AutoWatchlist
from models.stock import Stock
from typing import List


def example_screener_integration(screened_stocks: List[Stock]):
    """
    Example: Integrate watchlist with screener results
    
    Args:
        screened_stocks: List of Stock objects from main screener
    """
    
    print("\n" + "="*80)
    print("WATCHLIST INTEGRATION EXAMPLE")
    print("="*80)
    
    # Initialize
    manager = WatchlistManager()
    auto = AutoWatchlist()
    
    # 1. Separate stocks into buy-now vs watchlist
    print("\n1. Analyzing screener results...")
    
    buy_now = []
    watchlist_candidates = []
    
    for stock in screened_stocks:
        # Strong stocks (15%+ return, 80%+ confidence) -> buy now
        if stock.estimated_return >= 15.0 and stock.confidence >= 80:
            buy_now.append(stock)
        else:
            # Others might be watchlist candidates
            watchlist_candidates.append(stock)
    
    print(f"   Buy Now: {len(buy_now)} stocks")
    print(f"   Potential Watchlist: {len(watchlist_candidates)} stocks")
    
    # 2. Auto-scan for watchlist candidates
    print("\n2. Scanning for watchlist candidates...")
    
    candidates = auto.scan_for_watchlist_candidates(watchlist_candidates)
    
    if candidates:
        print(f"   Found {len(candidates)} candidates with early signals")
        
        # Filter by quality
        candidates = auto.filter_by_minimum_quality(candidates)
        print(f"   After quality filter: {len(candidates)} candidates")
        
        # Prioritize
        prioritized = auto.prioritize_candidates(candidates)
        
        # 3. Auto-add to watchlist
        print("\n3. Adding to watchlist...")
        added_count = 0
        
        for stock, reason, priority in prioritized[:10]:  # Top 10
            if stock.symbol not in manager.watchlist:
                success, msg = manager.add_stock(stock.symbol, reason, stock)
                if success:
                    added_count += 1
                    print(f"   ✓ {stock.symbol}: {reason} (priority: {priority:.1f})")
        
        print(f"\n   Added {added_count} stocks to watchlist")
    else:
        print("   No watchlist candidates found")
    
    # 4. Show watchlist summary
    print("\n4. Current Watchlist Summary")
    print("-"*80)
    
    stats = manager.get_statistics()
    print(f"   Total: {stats['total']}")
    print(f"   Improving: {stats['improving']}")
    print(f"   Alerts: {stats['alerts']}")
    
    # 5. Check for ready stocks
    alerts = manager.get_alert_stocks()
    
    if alerts:
        print(f"\n5. READY TO TRADE ({len(alerts)} stocks)")
        print("-"*80)
        for stock in alerts:
            print(f"   🔔 {stock.symbol}")
            print(f"      Return: {stock.current_return_potential:.1f}%")
            print(f"      Confidence: {stock.current_confidence}%")
            print(f"      Days on watchlist: {stock.days_on_watchlist}")
    else:
        print("\n5. No stocks ready to trade yet")


def example_daily_update():
    """
    Example: Daily watchlist update routine
    """
    
    print("\n" + "="*80)
    print("DAILY WATCHLIST UPDATE")
    print("="*80)
    
    manager = WatchlistManager()
    
    if not manager.watchlist:
        print("\nWatchlist is empty")
        return
    
    print(f"\nUpdating {len(manager.watchlist)} stocks...")
    
    # In real usage, you'd fetch actual stock data
    # For this example, we just show the structure
    
    def fetch_stock_data(symbol: str) -> Stock:
        """Fetch real-time stock data (implement with yfinance)"""
        # This would call yfinance in real usage
        pass
    
    # Update all
    results = manager.update_all_stocks(fetch_stock_data)
    
    # Show results
    improving = manager.get_stocks_by_trend("IMPROVING")
    alerts = manager.get_alert_stocks()
    
    print(f"\n📈 Improving: {len(improving)}")
    print(f"🔔 Alerts: {len(alerts)}")
    
    if alerts:
        print("\nReady to trade:")
        for stock in alerts:
            print(f"  • {stock.symbol}: {stock.current_return_potential:.1f}% / {stock.current_confidence}%")


def example_cleanup():
    """
    Example: Clean up old watchlist stocks
    """
    
    print("\n" + "="*80)
    print("WATCHLIST CLEANUP")
    print("="*80)
    
    manager = WatchlistManager()
    
    # Find stocks to remove
    to_remove = manager.check_removal_criteria(
        max_days=30,  # Remove after 30 days
        declining_days=5  # Remove if declining
    )
    
    if to_remove:
        print(f"\nSuggested removals: {len(to_remove)}")
        for symbol in to_remove:
            stock = manager.get_stock(symbol)
            print(f"  • {symbol}: {stock.days_on_watchlist} days, trend: {stock.score_trend}")
            
            # Auto-remove declining stocks
            if stock.score_trend == "DECLINING":
                manager.remove_stock(symbol, reason="Declining trend")
                print(f"    ✓ Removed")
    else:
        print("\nNo cleanup needed")


if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                    WATCHLIST INTEGRATION EXAMPLES                          ║
╚════════════════════════════════════════════════════════════════════════════╝

This file demonstrates how to integrate the watchlist system with your
existing stock screener workflow.

Three main use cases:

1. SCREENER INTEGRATION
   - Run main screener
   - Auto-populate watchlist with near-threshold stocks
   - Track momentum until they're ready to buy

2. DAILY UPDATE
   - Update all watchlist stocks with latest data
   - Check for alerts (stocks ready to trade)
   - Review improving/declining trends

3. CLEANUP
   - Remove stocks on watchlist too long
   - Remove declining stocks
   - Keep watchlist fresh and relevant

USAGE:

In your main screener flow:
  from examples.watchlist_integration import example_screener_integration
  
  # After screening
  stocks = screener.screen_stocks(symbols)
  example_screener_integration(stocks)

As a daily cron job:
  python core/watchlist_console.py --update
  python core/watchlist_console.py --alerts

Weekly cleanup:
  python examples/watchlist_integration.py  # Run cleanup

See core/WATCHLIST_README.md for full API documentation.
    """)
