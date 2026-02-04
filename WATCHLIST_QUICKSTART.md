# Watchlist System - Quick Start

## Overview

The Smart Watchlist System tracks stocks with early momentum signals before they meet full buy criteria (15% return + 80% confidence).

## Installation

No additional dependencies needed - uses existing requirements.txt

## Quick Commands

### View Watchlist
```bash
python core/watchlist_console.py --view
```

### Add Stock Manually
```bash
python core/watchlist_console.py --add AAPL
python core/watchlist_console.py --add TSLA --notes "Breakout setup"
```

### Update All Stocks
```bash
python core/watchlist_console.py --update
```

### Check Alerts (Ready to Trade)
```bash
python core/watchlist_console.py --alerts
```

### View by Trend
```bash
python core/watchlist_console.py --trending
```

### Auto-Scan for Candidates
```bash
python core/watchlist_console.py --auto-scan AAPL MSFT GOOGL NVDA AMD
```

## Auto-Add Criteria

Stocks auto-added when they show **2+ of these signals**:

1. **Score Improving** - Score in 60-79 range (good but not yet excellent)
2. **Near Threshold** - Return 10-14% OR Confidence 70-79%
3. **MACD Crossover** - Bullish crossover in last 3 days
4. **RSI Momentum** - RSI in 45-65 zone (building momentum)
5. **Volume Surge** - Volume increasing 3+ days + above average

## Alert System

Alerts trigger when stock reaches:
- **Return ≥ 15%** AND **Confidence ≥ 80%**

## Daily Workflow

```bash
# Morning routine (before market)
python core/watchlist_console.py --update
python core/watchlist_console.py --alerts

# Review trends
python core/watchlist_console.py --trending

# Full view
python core/watchlist_console.py --view --sort score
```

## Example Output

```
📋 WATCHLIST STOCKS
Symbol   Days   Reason              Score      Return     Conf    Trend         Days to  Alert
                                                                                 Criteria
AAPL     5      NEAR_THRESHOLD      72.0       13.0%      75%     📈 IMPROVING  7        
MSFT     3      MACD_CROSSOVER      68.0       11.5%      72%     ➡️ STABLE     -        
GOOGL    8      IMPROVING_TREND     85.0       16.0%      82%     📈 IMPROVING  0        🔔

Total: 3 | Improving: 2 | Declining: 0 | Stable: 1 | Alerts: 1
```

## Files Location

- **Manager**: `core/watchlist_manager.py`
- **Auto-Add**: `core/auto_watchlist.py`
- **CLI**: `core/watchlist_console.py`
- **Data**: `data/watchlist/watchlist.json`
- **Docs**: `core/WATCHLIST_README.md`
- **Tests**: `core/test_watchlist.py`

## Testing

```bash
python core/test_watchlist.py
```

## Integration with Screener

```python
from core.watchlist_manager import WatchlistManager
from core.auto_watchlist import AutoWatchlist

# After screening
screened_stocks = screener.screen_stocks(symbols)

# Auto-populate watchlist
manager = WatchlistManager()
auto = AutoWatchlist()

candidates = auto.scan_for_watchlist_candidates(screened_stocks)
for stock, reason in candidates:
    manager.add_stock(stock.symbol, reason, stock)
```

## Tips

1. **Run daily updates** to track momentum changes
2. **Check alerts** to find stocks ready to trade
3. **Use auto-scan** to discover new opportunities
4. **Review trends** to spot momentum shifts
5. **Clean up** declining stocks or those on list too long

## Full Documentation

See `core/WATCHLIST_README.md` for:
- Complete API reference
- All CLI commands
- Python API examples
- Customization options
- Integration patterns

## Support

- Run tests: `python core/test_watchlist.py`
- Check syntax: `python -m py_compile core/watchlist_*.py`
- View help: `python core/watchlist_console.py --help`
