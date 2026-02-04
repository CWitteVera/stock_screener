# Watchlist System Documentation

## Overview

The Smart Watchlist System tracks stocks with early momentum signals and automatically identifies potential trading opportunities before they meet full buy criteria.

## Features

### 🎯 Core Capabilities
- **Manual & Auto-Add**: Add stocks manually or automatically based on early signals
- **Momentum Tracking**: Track score trends (IMPROVING, DECLINING, STABLE)
- **Alert System**: Get notified when stocks meet trading criteria (15%+ return, 80%+ confidence)
- **Days to Criteria**: Estimate when a stock will meet buy threshold
- **Smart Filtering**: Auto-detect early signals like MACD crossovers, RSI momentum, volume surges

### 📊 Auto-Add Criteria

Stocks are automatically added when they show **at least 2** of these signals:

1. **Score Improving** (60-79 range) - Good but not yet excellent
2. **Near Threshold** - Return: 10-14% OR Confidence: 70-79%
3. **MACD Crossover** - Bullish crossover within last 3 days
4. **RSI Momentum** - RSI in 45-65 zone (momentum building)
5. **Volume Surge** - Volume increasing over 3 days + above average

### 🔔 Alert Triggers

Alerts fire when:
- Return potential ≥ 15% AND
- Confidence ≥ 80%

## Files

```
/core/
  ├── watchlist_manager.py    # Main management class
  ├── auto_watchlist.py        # Auto-add logic & signal detection
  ├── watchlist_console.py     # CLI interface
  └── test_watchlist.py        # Test suite

/data/watchlist/
  └── watchlist.json           # Watchlist data storage

/models/
  └── watchlist_stock.py       # WatchlistStock model
```

## CLI Usage

### View Watchlist
```bash
python core/watchlist_console.py --view
python core/watchlist_console.py --view --sort score
python core/watchlist_console.py --view --sort return_potential
```

### Add Stock
```bash
# Manual add
python core/watchlist_console.py --add AAPL

# With custom reason and notes
python core/watchlist_console.py --add TSLA --reason "BREAKOUT_SETUP" --notes "Near 52-week high"
```

### Remove Stock
```bash
python core/watchlist_console.py --remove AAPL
```

### Update All Stocks
```bash
# Refresh metrics for all watchlist stocks
python core/watchlist_console.py --update
```

### View Trending
```bash
# See stocks grouped by trend
python core/watchlist_console.py --trending
```

### Check Alerts
```bash
# See stocks that meet criteria
python core/watchlist_console.py --alerts
```

### Auto-Scan
```bash
# Scan specific stocks for watchlist candidates
python core/watchlist_console.py --auto-scan AAPL MSFT GOOGL TSLA NVDA

# Auto-add qualifying stocks
python core/watchlist_console.py --auto-scan AMD INTC MU
```

## Python API

### WatchlistManager

```python
from core.watchlist_manager import WatchlistManager

# Initialize
manager = WatchlistManager()

# Add stock
success, msg = manager.add_stock("AAPL", "NEAR_THRESHOLD", stock_obj)

# Update stock
success, msg = manager.update_stock_metrics("AAPL", updated_stock_obj)

# Get stocks by trend
improving = manager.get_stocks_by_trend("IMPROVING")
declining = manager.get_stocks_by_trend("DECLINING")
stable = manager.get_stocks_by_trend("STABLE")

# Get alerts
alerts = manager.get_alert_stocks()

# Get statistics
stats = manager.get_statistics()
# Returns: {total, improving, declining, stable, alerts, avg_days, avg_score}

# Get all stocks (sorted)
stocks = manager.get_all_stocks(sort_by="score")
# sort_by: "added_date", "score", "return_potential", "days_on_watchlist"

# Remove stock
success, msg = manager.remove_stock("AAPL")

# Check removal criteria
to_remove = manager.check_removal_criteria(max_days=30, declining_days=5)
```

### AutoWatchlist

```python
from core.auto_watchlist import AutoWatchlist

auto = AutoWatchlist()

# Check single stock
should_add, reason = auto.should_add_to_watchlist(stock)

# Scan multiple stocks
candidates = auto.scan_for_watchlist_candidates(stocks)
# Returns: [(Stock, reason), ...]

# Filter by quality
filtered = auto.filter_by_minimum_quality(
    candidates, 
    min_score=50.0, 
    min_return=8.0, 
    min_confidence=60
)

# Prioritize candidates
prioritized = auto.prioritize_candidates(filtered)
# Returns: [(Stock, reason, priority_score), ...] sorted by priority

# Get detailed signals
signals = auto.get_detailed_signals(stock)
# Returns: {
#   'symbol': 'AAPL',
#   'score_improving': True,
#   'near_threshold': True,
#   'macd_signal': False,
#   'rsi_momentum': True,
#   'volume_trend': True,
#   'current_score': 72.0,
#   'estimated_return': 12.5,
#   'confidence': 75
# }
```

### WatchlistStock Model

```python
from models.watchlist_stock import WatchlistStock
from datetime import date

# Create
ws = WatchlistStock(
    symbol="AAPL",
    added_date=date.today(),
    reason="NEAR_THRESHOLD",
    initial_score=65.0,
    initial_return_potential=10.0,
    initial_confidence=70
)

# Update metrics (automatically detects trend)
ws.update_metrics(score=72.0, return_potential=13.0, confidence=75)

# Check properties
ws.score_trend  # "IMPROVING", "DECLINING", "STABLE"
ws.days_on_watchlist  # Days since added
ws.alert_triggered  # True if meets criteria
ws.days_until_potential  # Estimated days to criteria

# Get changes
ws.get_score_change()  # Change since added
ws.get_return_change()  # Return change
ws.get_confidence_change()  # Confidence change

# Check if meets criteria
ws.meets_criteria(min_return=15.0, min_confidence=80)

# Estimate days to criteria
days = ws.estimate_days_to_criteria()

# Serialize
data = ws.to_dict()
ws2 = WatchlistStock.from_dict(data)
```

## Workflow Examples

### Daily Watchlist Routine

```bash
# 1. Update all stocks
python core/watchlist_console.py --update

# 2. Check for alerts
python core/watchlist_console.py --alerts

# 3. View trending analysis
python core/watchlist_console.py --trending

# 4. Review full watchlist
python core/watchlist_console.py --view --sort score
```

### Finding New Candidates

```bash
# Scan a sector for candidates
python core/watchlist_console.py --auto-scan AAPL MSFT GOOGL AMZN META

# Tech sector scan
python core/watchlist_console.py --auto-scan NVDA AMD INTC MU TSM

# Auto-add qualifying stocks and review
python core/watchlist_console.py --view
```

### Integration with Main Screener

```python
from core.screener import Screener
from core.watchlist_manager import WatchlistManager
from core.auto_watchlist import AutoWatchlist

# Run main screen
screener = Screener()
screener.screen_stocks(symbols)

# Get stocks that didn't make the cut
potential_stocks = screener.get_near_threshold_stocks()

# Auto-scan for watchlist
auto = AutoWatchlist()
candidates = auto.scan_for_watchlist_candidates(potential_stocks)

# Add to watchlist
manager = WatchlistManager()
for stock, reason in candidates:
    manager.add_stock(stock.symbol, reason, stock)
```

## Data Storage

Watchlist data is stored in JSON format at:
```
/data/watchlist/watchlist.json
```

Structure:
```json
{
  "updated": "2025-02-15T10:30:00",
  "total_stocks": 5,
  "stocks": {
    "AAPL": {
      "symbol": "AAPL",
      "added_date": "2025-02-10",
      "reason": "NEAR_THRESHOLD",
      "initial_score": 65.0,
      "initial_return_potential": 10.0,
      "initial_confidence": 70,
      "current_score": 72.0,
      "current_return_potential": 13.0,
      "current_confidence": 75,
      "score_trend": "IMPROVING",
      "days_on_watchlist": 5,
      "days_until_potential": 7,
      "alert_enabled": true,
      "alert_triggered": false,
      "notes": "",
      "last_updated": "2025-02-15"
    }
  }
}
```

## Testing

Run the test suite:
```bash
python core/test_watchlist.py
```

Tests cover:
- WatchlistStock model (serialization, updates, trends, alerts)
- WatchlistManager (CRUD, filtering, statistics, alerts)
- AutoWatchlist (signal detection, scanning, prioritization)

## Customization

### Alert Thresholds

Modify per-stock alert thresholds:
```python
ws = manager.get_stock("AAPL")
ws.alert_when_return_reaches = 12.0  # Alert at 12% instead of 15%
ws.alert_when_confidence_reaches = 75  # Alert at 75% instead of 80%
manager.save()
```

### Auto-Add Criteria

Edit `core/auto_watchlist.py` to customize signal detection:

```python
# Change near-threshold range
def _check_near_threshold(self, stock: Stock) -> bool:
    # Customize: 8-13% return, 65-75% confidence
    if 8.0 <= stock.estimated_return <= 13.0:
        return True
    if 65 <= stock.confidence <= 75:
        return True
    return False

# Adjust RSI momentum zone
def _check_rsi_momentum(self, stock: Stock) -> bool:
    # Customize: 40-70 zone
    if 40 <= stock.rsi <= 70:
        return True
    return False
```

### Removal Criteria

Customize automatic removal suggestions:
```python
# Remove after 45 days or declining for 7 days
to_remove = manager.check_removal_criteria(
    max_days=45, 
    declining_days=7
)
```

## Tips

1. **Daily Updates**: Run `--update` daily before market open to refresh metrics
2. **Alert Review**: Check `--alerts` to see which stocks are ready to trade
3. **Trend Analysis**: Use `--trending` to spot momentum shifts
4. **Auto-Scan**: Regularly scan new stocks with `--auto-scan` to find opportunities
5. **Clean Up**: Remove declining stocks or those on watchlist too long
6. **Integration**: Combine with main screener to auto-populate watchlist

## Error Handling

All operations return `(success: bool, message: str)`:

```python
success, msg = manager.add_stock("AAPL", "TEST", stock)
if success:
    print(f"✅ {msg}")
else:
    print(f"❌ {msg}")
```

Common errors:
- Stock already on watchlist
- Stock not found
- Network errors (data fetch)
- Invalid symbol

## Future Enhancements

Potential additions:
- Email/SMS alerts when criteria met
- Integration with broker API for auto-trading
- Historical performance tracking (how often watchlist stocks succeed)
- Machine learning for signal prioritization
- Sector-based watchlists
- Export to portfolio tracker
