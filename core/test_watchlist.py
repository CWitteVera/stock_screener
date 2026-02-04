"""
Test script for watchlist system (no network required)
"""

import sys
from pathlib import Path
from datetime import date
import pandas as pd
import numpy as np

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.watchlist_manager import WatchlistManager
from core.auto_watchlist import AutoWatchlist
from models.watchlist_stock import WatchlistStock
from models.stock import Stock


def create_mock_stock(symbol: str, score: float, return_potential: float, confidence: int) -> Stock:
    """Create a mock Stock object for testing"""
    
    # Create mock historical data
    dates = pd.date_range(end=date.today(), periods=100)
    prices = np.random.randn(100).cumsum() + 100
    prices = np.abs(prices)  # Ensure positive
    
    hist = pd.DataFrame({
        'Close': prices,
        'High': prices * 1.02,
        'Low': prices * 0.98,
        'Open': prices,
        'Volume': np.random.randint(1000000, 5000000, 100),
    }, index=dates)
    
    # Add technical indicators
    hist['RSI'] = 55.0
    hist['MACD'] = 0.5
    hist['MACD_signal'] = 0.3
    hist['MACD_hist'] = 0.2
    hist['SMA_20'] = prices * 0.99
    hist['SMA_50'] = prices * 0.98
    hist['Volume_SMA_20'] = 2000000
    hist['ATR'] = 2.0
    
    stock = Stock(
        symbol=symbol,
        name=f"{symbol} Inc.",
        current_price=prices[-1],
        sector="Technology",
        market_cap=1000000000,
        volume=3000000,
        avg_volume=2000000,
        history=hist,
        info={}
    )
    
    # Set metrics
    stock.overall_score = score
    stock.estimated_return = return_potential
    stock.confidence = confidence
    stock.rsi = 55.0
    stock.macd = 0.5
    stock.macd_signal = 0.3
    
    return stock


def test_watchlist_manager():
    """Test WatchlistManager functionality"""
    print("\n" + "="*80)
    print("TESTING WATCHLIST MANAGER")
    print("="*80)
    
    # Create test manager with temp file
    test_path = "/tmp/test_watchlist.json"
    manager = WatchlistManager(data_path=test_path)
    
    # Test 1: Add stocks
    print("\n1. Adding stocks...")
    stock1 = create_mock_stock("AAPL", 72.0, 12.5, 75)
    success, msg = manager.add_stock("AAPL", "NEAR_THRESHOLD", stock1)
    print(f"   {msg}")
    assert success, "Failed to add AAPL"
    
    stock2 = create_mock_stock("MSFT", 68.0, 11.0, 72)
    success, msg = manager.add_stock("MSFT", "MACD_CROSSOVER", stock2)
    print(f"   {msg}")
    assert success, "Failed to add MSFT"
    
    stock3 = create_mock_stock("GOOGL", 85.0, 16.5, 82)
    success, msg = manager.add_stock("GOOGL", "IMPROVING_TREND", stock3)
    print(f"   {msg}")
    assert success, "Failed to add GOOGL"
    
    # Test 2: View all stocks
    print("\n2. Getting all stocks...")
    stocks = manager.get_all_stocks()
    print(f"   Total stocks: {len(stocks)}")
    assert len(stocks) == 3, "Should have 3 stocks"
    
    # Test 3: Update metrics
    print("\n3. Updating stock metrics...")
    stock1_updated = create_mock_stock("AAPL", 78.0, 14.0, 78)
    success, msg = manager.update_stock_metrics("AAPL", stock1_updated)
    print(f"   {msg}")
    assert success, "Failed to update AAPL"
    
    # Test 4: Check trend detection
    print("\n4. Checking trend detection...")
    aapl = manager.get_stock("AAPL")
    print(f"   AAPL trend: {aapl.score_trend}")
    print(f"   Score change: {aapl.get_score_change():.1f}")
    
    # Test 5: Alert trigger
    print("\n5. Testing alert triggers...")
    stock_alert = create_mock_stock("GOOGL", 90.0, 16.0, 85)
    success, msg = manager.update_stock_metrics("GOOGL", stock_alert)
    print(f"   {msg}")
    
    alerts = manager.get_alert_stocks()
    print(f"   Stocks with alerts: {len(alerts)}")
    if alerts:
        for stock in alerts:
            print(f"   - {stock.symbol}: {stock.current_return_potential:.1f}%, {stock.current_confidence}%")
    
    # Test 6: Filter by trend
    print("\n6. Filtering by trend...")
    improving = manager.get_stocks_by_trend("IMPROVING")
    print(f"   Improving stocks: {[s.symbol for s in improving]}")
    
    # Test 7: Statistics
    print("\n7. Getting statistics...")
    stats = manager.get_statistics()
    print(f"   Total: {stats['total']}")
    print(f"   Improving: {stats['improving']}")
    print(f"   Declining: {stats['declining']}")
    print(f"   Stable: {stats['stable']}")
    print(f"   Alerts: {stats['alerts']}")
    print(f"   Avg Score: {stats['avg_score']:.1f}")
    
    # Test 8: Remove stock
    print("\n8. Removing stock...")
    success, msg = manager.remove_stock("MSFT")
    print(f"   {msg}")
    assert success, "Failed to remove MSFT"
    
    stocks = manager.get_all_stocks()
    print(f"   Remaining stocks: {len(stocks)}")
    assert len(stocks) == 2, "Should have 2 stocks"
    
    print("\n✅ All WatchlistManager tests passed!")


def test_auto_watchlist():
    """Test AutoWatchlist functionality"""
    print("\n" + "="*80)
    print("TESTING AUTO WATCHLIST")
    print("="*80)
    
    auto = AutoWatchlist()
    
    # Test 1: Should add - near threshold + momentum
    print("\n1. Testing stock that should be added...")
    stock1 = create_mock_stock("NVDA", 70.0, 12.0, 75)
    should_add, reason = auto.should_add_to_watchlist(stock1)
    print(f"   NVDA: should_add={should_add}, reason={reason}")
    assert should_add, "NVDA should be added"
    
    # Test 2: Should not add - too low quality
    print("\n2. Testing stock that should NOT be added...")
    stock2 = create_mock_stock("XYZ", 40.0, 5.0, 50)
    should_add, reason = auto.should_add_to_watchlist(stock2)
    print(f"   XYZ: should_add={should_add}, reason={reason}")
    assert not should_add, "XYZ should not be added"
    
    # Test 3: Scan candidates
    print("\n3. Scanning for candidates...")
    stocks = [
        create_mock_stock("AAPL", 72.0, 12.5, 75),
        create_mock_stock("MSFT", 68.0, 11.0, 72),
        create_mock_stock("TSLA", 85.0, 16.5, 82),
        create_mock_stock("WEAK", 30.0, 3.0, 40),
    ]
    
    candidates = auto.scan_for_watchlist_candidates(stocks)
    print(f"   Found {len(candidates)} candidates:")
    for stock, reason in candidates:
        print(f"   - {stock.symbol}: {reason}")
    
    # Test 4: Filter by quality
    print("\n4. Filtering by quality...")
    filtered = auto.filter_by_minimum_quality(candidates, min_score=50.0)
    print(f"   Filtered to {len(filtered)} candidates:")
    for stock, reason in filtered:
        print(f"   - {stock.symbol}: {reason} (score: {stock.overall_score:.1f})")
    
    # Test 5: Prioritize
    print("\n5. Prioritizing candidates...")
    prioritized = auto.prioritize_candidates(filtered)
    print(f"   Prioritized {len(prioritized)} candidates:")
    for stock, reason, priority in prioritized:
        print(f"   - {stock.symbol}: {reason} (priority: {priority:.1f})")
    
    # Test 6: Get detailed signals
    print("\n6. Getting detailed signals...")
    signals = auto.get_detailed_signals(stocks[0])
    print(f"   {signals['symbol']} signals:")
    print(f"   - Score improving: {signals['score_improving']}")
    print(f"   - Near threshold: {signals['near_threshold']}")
    print(f"   - MACD signal: {signals['macd_signal']}")
    print(f"   - RSI momentum: {signals['rsi_momentum']}")
    print(f"   - Volume trend: {signals['volume_trend']}")
    
    print("\n✅ All AutoWatchlist tests passed!")


def test_watchlist_stock_model():
    """Test WatchlistStock model"""
    print("\n" + "="*80)
    print("TESTING WATCHLIST STOCK MODEL")
    print("="*80)
    
    # Create test stock
    print("\n1. Creating WatchlistStock...")
    ws = WatchlistStock(
        symbol="AAPL",
        added_date=date.today(),
        reason="NEAR_THRESHOLD",
        initial_score=65.0,
        initial_return_potential=10.0,
        initial_confidence=70,
        current_score=65.0,
        current_return_potential=10.0,
        current_confidence=70,
    )
    print(f"   Created: {ws.symbol}")
    
    # Test update
    print("\n2. Updating metrics...")
    ws.update_metrics(72.0, 13.0, 75)
    print(f"   New score: {ws.current_score}")
    print(f"   Trend: {ws.score_trend}")
    print(f"   Score change: {ws.get_score_change()}")
    
    # Test alert trigger
    print("\n3. Testing alert...")
    ws.update_metrics(85.0, 16.0, 85)
    print(f"   Alert triggered: {ws.alert_triggered}")
    assert ws.alert_triggered, "Alert should be triggered"
    
    # Test serialization
    print("\n4. Testing serialization...")
    data = ws.to_dict()
    print(f"   Converted to dict: {len(data)} fields")
    
    ws2 = WatchlistStock.from_dict(data)
    print(f"   Restored from dict: {ws2.symbol}")
    assert ws2.symbol == ws.symbol, "Symbol mismatch"
    
    print("\n✅ All WatchlistStock tests passed!")


if __name__ == "__main__":
    try:
        test_watchlist_stock_model()
        test_watchlist_manager()
        test_auto_watchlist()
        
        print("\n" + "="*80)
        print("🎉 ALL TESTS PASSED!")
        print("="*80)
        print("\nWatchlist system is ready to use!")
        print("\nUsage:")
        print("  python core/watchlist_console.py --help")
        print("  python core/watchlist_console.py --add AAPL")
        print("  python core/watchlist_console.py --view")
        print("  python core/watchlist_console.py --update")
        print("  python core/watchlist_console.py --alerts")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
