"""
CLI interface for watchlist management
"""

import argparse
import sys
from pathlib import Path
from datetime import date
from typing import Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.watchlist_manager import WatchlistManager
from core.auto_watchlist import AutoWatchlist
from models.stock import Stock
from core.technical_analysis import calculate_all_indicators
from core.scoring_engine import calculate_overall_score
from core.return_estimator import estimate_return_potential
import yfinance as yf


def fetch_stock_data(symbol: str) -> Optional[Stock]:
    """
    Fetch stock data from Yahoo Finance
    
    Args:
        symbol: Stock symbol
        
    Returns:
        Stock object or None if error
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        hist = ticker.history(period="3mo")
        
        if hist.empty or len(hist) < 50:
            print(f"❌ Not enough data for {symbol}")
            return None
        
        # Calculate indicators
        hist = calculate_all_indicators(hist)
        
        # Create Stock object
        stock = Stock(
            symbol=symbol.upper(),
            name=info.get('longName', symbol),
            current_price=hist['Close'].iloc[-1],
            sector=info.get('sector', 'Unknown'),
            market_cap=info.get('marketCap', 0),
            volume=hist['Volume'].iloc[-1],
            avg_volume=hist['Volume'].mean(),
            history=hist,
            info=info
        )
        
        # Set technical indicators
        stock.rsi = hist['RSI'].iloc[-1] if 'RSI' in hist.columns else None
        stock.macd = hist['MACD'].iloc[-1] if 'MACD' in hist.columns else None
        stock.macd_signal = hist['MACD_signal'].iloc[-1] if 'MACD_signal' in hist.columns else None
        stock.macd_histogram = hist['MACD_hist'].iloc[-1] if 'MACD_hist' in hist.columns else None
        stock.sma_20 = hist['SMA_20'].iloc[-1] if 'SMA_20' in hist.columns else None
        stock.sma_50 = hist['SMA_50'].iloc[-1] if 'SMA_50' in hist.columns else None
        stock.atr = hist['ATR'].iloc[-1] if 'ATR' in hist.columns else None
        
        # Calculate scores
        stock_data = {
            'current_price': stock.current_price,
            'volume': stock.volume,
            'symbol': stock.symbol
        }
        scores = calculate_overall_score(stock_data, hist)
        stock.overall_score = scores['overall_score']
        stock.macd_score = scores['macd_score']
        stock.rsi_score = scores['rsi_score']
        stock.volume_score = scores['volume_score']
        stock.breakout_score = scores['breakout_score']
        stock.momentum_score = scores['momentum_score']
        
        # Estimate return
        stock_data = {
            'current_price': stock.current_price,
            'volume': stock.volume,
            'symbol': stock.symbol
        }
        estimated_return, confidence, days_to_target = estimate_return_potential(stock_data, hist)
        stock.estimated_return = estimated_return
        stock.confidence = int(confidence)
        stock.days_to_target = days_to_target
        
        return stock
        
    except Exception as e:
        print(f"❌ Error fetching {symbol}: {e}")
        return None


def view_watchlist(manager: WatchlistManager, sort_by: str = "added_date"):
    """Display all watchlist stocks"""
    stocks = manager.get_all_stocks(sort_by=sort_by)
    
    if not stocks:
        print("\n📋 Watchlist is empty")
        return
    
    print("\n" + "="*120)
    print("📋 WATCHLIST STOCKS")
    print("="*120)
    
    # Header
    print(f"{'Symbol':<8} {'Days':<6} {'Reason':<18} {'Score':<10} {'Return':<10} {'Conf':<7} {'Trend':<12} {'Days to':<8} {'Alert':<7}")
    print(f"{'      ':<8} {'     ':<6} {'      ':<18} {'      ':<10} {'      ':<10} {'    ':<7} {'     ':<12} {'Criteria':<8} {'     ':<7}")
    print("-"*120)
    
    for stock in stocks:
        # Format values
        score = f"{stock.current_score:.1f}"
        ret = f"{stock.current_return_potential:.1f}%"
        conf = f"{stock.current_confidence}%"
        
        # Trend with emoji
        trend_emoji = {
            "IMPROVING": "📈",
            "DECLINING": "📉",
            "STABLE": "➡️"
        }.get(stock.score_trend, "")
        trend = f"{trend_emoji} {stock.score_trend}"
        
        days_to = str(stock.days_until_potential) if stock.days_until_potential else "-"
        alert = "🔔" if stock.alert_triggered else ""
        
        print(f"{stock.symbol:<8} {stock.days_on_watchlist:<6} {stock.reason:<18} {score:<10} {ret:<10} {conf:<7} {trend:<12} {days_to:<8} {alert:<7}")
        
        if stock.notes:
            print(f"         Note: {stock.notes}")
    
    print("-"*120)
    
    # Statistics
    stats = manager.get_statistics()
    print(f"\nTotal: {stats['total']} | Improving: {stats['improving']} | Declining: {stats['declining']} | Stable: {stats['stable']} | Alerts: {stats['alerts']}")
    print(f"Avg Days: {stats['avg_days']} | Avg Score: {stats['avg_score']}")
    print()


def add_stock(manager: WatchlistManager, symbol: str, reason: str = "MANUAL", notes: str = ""):
    """Add stock to watchlist"""
    print(f"\n🔍 Fetching data for {symbol}...")
    
    stock = fetch_stock_data(symbol)
    
    if stock is None:
        return
    
    success, msg = manager.add_stock(symbol.upper(), reason, stock, notes)
    
    if success:
        print(f"✅ {msg}")
        
        # Show details
        ws = manager.get_stock(symbol.upper())
        if ws:
            print(f"\n   Score: {ws.current_score:.1f}")
            print(f"   Return Potential: {ws.current_return_potential:.1f}%")
            print(f"   Confidence: {ws.current_confidence}%")
            print(f"   Alert Threshold: {ws.alert_when_return_reaches:.1f}% / {ws.alert_when_confidence_reaches}%")
    else:
        print(f"❌ {msg}")


def remove_stock(manager: WatchlistManager, symbol: str):
    """Remove stock from watchlist"""
    success, msg = manager.remove_stock(symbol.upper())
    
    if success:
        print(f"✅ {msg}")
    else:
        print(f"❌ {msg}")


def update_watchlist(manager: WatchlistManager):
    """Update all watchlist stocks"""
    stocks = manager.get_all_stocks()
    
    if not stocks:
        print("\n📋 Watchlist is empty")
        return
    
    print(f"\n🔄 Updating {len(stocks)} stocks...")
    print("-"*80)
    
    results = manager.update_all_stocks(fetch_stock_data)
    
    # Display results
    for symbol, msg in results.items():
        if "ALERT" in msg:
            print(f"🔔 {symbol}: {msg}")
        elif "Error" in msg:
            print(f"❌ {symbol}: {msg}")
        else:
            print(f"✓ {symbol}: {msg}")
    
    print("-"*80)
    print("✅ Update complete!")


def show_trending(manager: WatchlistManager):
    """Show stocks by trend"""
    print("\n" + "="*100)
    print("📊 TRENDING ANALYSIS")
    print("="*100)
    
    # Improving
    improving = manager.get_stocks_by_trend("IMPROVING")
    if improving:
        print(f"\n📈 IMPROVING ({len(improving)} stocks)")
        print("-"*100)
        for stock in improving:
            change = stock.get_score_change()
            print(f"  {stock.symbol:<8} Score: {stock.current_score:.1f} (+{change:.1f}) | Return: {stock.current_return_potential:.1f}% | Conf: {stock.current_confidence}%")
    
    # Declining
    declining = manager.get_stocks_by_trend("DECLINING")
    if declining:
        print(f"\n📉 DECLINING ({len(declining)} stocks)")
        print("-"*100)
        for stock in declining:
            change = stock.get_score_change()
            print(f"  {stock.symbol:<8} Score: {stock.current_score:.1f} ({change:.1f}) | Return: {stock.current_return_potential:.1f}% | Conf: {stock.current_confidence}%")
    
    # Stable
    stable = manager.get_stocks_by_trend("STABLE")
    if stable:
        print(f"\n➡️  STABLE ({len(stable)} stocks)")
        print("-"*100)
        for stock in stable:
            print(f"  {stock.symbol:<8} Score: {stock.current_score:.1f} | Return: {stock.current_return_potential:.1f}% | Conf: {stock.current_confidence}%")
    
    print()


def show_alerts(manager: WatchlistManager):
    """Show stocks with triggered alerts"""
    alerts = manager.get_alert_stocks()
    
    if not alerts:
        print("\n📋 No alerts triggered")
        return
    
    print("\n" + "="*100)
    print(f"🔔 ALERTS ({len(alerts)} stocks)")
    print("="*100)
    
    for stock in alerts:
        print(f"\n{stock.symbol} - MEETS CRITERIA!")
        print(f"  Added: {stock.added_date} ({stock.days_on_watchlist} days ago)")
        print(f"  Reason: {stock.reason}")
        print(f"  Current Score: {stock.current_score:.1f}")
        print(f"  Return Potential: {stock.current_return_potential:.1f}% (threshold: {stock.alert_when_return_reaches:.1f}%)")
        print(f"  Confidence: {stock.current_confidence}% (threshold: {stock.alert_when_confidence_reaches}%)")
        print(f"  Trend: {stock.score_trend}")
        
        if stock.notes:
            print(f"  Notes: {stock.notes}")
    
    print()


def auto_scan(manager: WatchlistManager, symbols: list):
    """Auto-scan stocks for watchlist candidates"""
    print(f"\n🔍 Auto-scanning {len(symbols)} stocks for watchlist candidates...")
    print("-"*80)
    
    auto = AutoWatchlist()
    stocks = []
    
    # Fetch stock data
    for symbol in symbols:
        stock = fetch_stock_data(symbol)
        if stock:
            stocks.append(stock)
    
    # Find candidates
    candidates = auto.scan_for_watchlist_candidates(stocks)
    
    if not candidates:
        print("No watchlist candidates found")
        return
    
    # Filter by quality
    candidates = auto.filter_by_minimum_quality(candidates)
    
    # Prioritize
    prioritized = auto.prioritize_candidates(candidates)
    
    print(f"\n✅ Found {len(prioritized)} candidates:")
    print("-"*80)
    
    for stock, reason, priority in prioritized:
        # Check if already on watchlist
        if stock.symbol in manager.watchlist:
            status = "(already on watchlist)"
        else:
            status = ""
        
        print(f"\n{stock.symbol} - {reason} {status}")
        print(f"  Priority: {priority:.1f}")
        print(f"  Score: {stock.overall_score:.1f}")
        print(f"  Return: {stock.estimated_return:.1f}%")
        print(f"  Confidence: {stock.confidence}%")
        
        # Get detailed signals
        signals = auto.get_detailed_signals(stock)
        signal_list = []
        if signals['score_improving']:
            signal_list.append("Score Improving")
        if signals['near_threshold']:
            signal_list.append("Near Threshold")
        if signals['macd_signal']:
            signal_list.append("MACD Crossover")
        if signals['rsi_momentum']:
            signal_list.append("RSI Momentum")
        if signals['volume_trend']:
            signal_list.append("Volume Surge")
        
        print(f"  Signals: {', '.join(signal_list)}")
        
        # Auto-add if not already on watchlist
        if stock.symbol not in manager.watchlist:
            success, msg = manager.add_stock(stock.symbol, reason, stock)
            if success:
                print(f"  ✅ Auto-added to watchlist")
    
    print()


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Watchlist Manager - Track stocks with momentum and alerts"
    )
    
    parser.add_argument("--view", action="store_true", help="View all watchlist stocks")
    parser.add_argument("--add", type=str, metavar="SYMBOL", help="Add stock to watchlist")
    parser.add_argument("--remove", type=str, metavar="SYMBOL", help="Remove stock from watchlist")
    parser.add_argument("--update", action="store_true", help="Update all stock metrics")
    parser.add_argument("--trending", action="store_true", help="Show stocks by trend")
    parser.add_argument("--alerts", action="store_true", help="Show triggered alerts")
    parser.add_argument("--auto-scan", type=str, nargs="+", metavar="SYMBOL", help="Auto-scan symbols for candidates")
    parser.add_argument("--reason", type=str, default="MANUAL", help="Reason for adding stock")
    parser.add_argument("--notes", type=str, default="", help="Additional notes")
    parser.add_argument("--sort", type=str, default="added_date", 
                       choices=["added_date", "score", "return_potential", "days_on_watchlist"],
                       help="Sort order for --view")
    
    args = parser.parse_args()
    
    # Initialize manager
    manager = WatchlistManager()
    
    # Execute commands
    if args.view:
        view_watchlist(manager, sort_by=args.sort)
    
    elif args.add:
        add_stock(manager, args.add, args.reason, args.notes)
    
    elif args.remove:
        remove_stock(manager, args.remove)
    
    elif args.update:
        update_watchlist(manager)
    
    elif args.trending:
        show_trending(manager)
    
    elif args.alerts:
        show_alerts(manager)
    
    elif args.auto_scan:
        auto_scan(manager, args.auto_scan)
    
    else:
        # No command provided, show help
        parser.print_help()


if __name__ == "__main__":
    main()
