# Quick UI Reference - Enhanced Dual Dashboard

## What's New?

### 🎯 Dual Dashboard
- **Split View:** Swing trades (left) + Day trades (right)
- **Side-by-side:** Compare both opportunity types instantly
- **Unified Interface:** One scan, two strategies

### 💰 Capital Tracking
- **Progress Bar:** Visual progress toward $7k goal
- **Paycheck Counter:** Days until next paycheck
- **Stats Display:** Win rate, total profit, return %
- **Goal Projections:** Time estimates to reach $7k

### 📚 Trading Ledger
- **Full History:** All trades in one place
- **Performance Metrics:** Win rate, accuracy, calibration
- **Export Options:** CSV, JSON, metrics download
- **Accuracy Analysis:** Compare predictions vs. actuals

### 🔧 Debug Tools
- **Filter Pipeline:** See exactly what's filtered out
- **Stock Analyzer:** Check why specific stocks passed/failed
- **Rejection Reasons:** Understand filtering decisions

## Quick Start

### Running the App
```bash
cd /home/runner/work/stock_screener/stock_screener
streamlit run main.py
```

### First-Time Setup
1. App opens with $4000 starting capital
2. Enable "📊 Swing Trading" (checked by default)
3. Select sector (Technology, Healthcare, etc.)
4. Click "🔍 Start Scan"
5. Review opportunities in left column

### Adding Day Trading
1. Check "⚡ Day Trade Monitor" in sidebar
2. See "MONITOR ONLY" message (capital < $7k)
3. Click scan to see day trade setups
4. Right column shows intraday opportunities
5. Track progress to $7k in capital display

### When You Reach $7k
1. Capital hits $7000+
2. "🔴 Execute Day Trades" checkbox appears
3. Enable to switch from monitor to execute mode
4. Right column badge changes to "EXECUTE"
5. Can now trade within PDT rules

## Key Features

### Sidebar Components
```
┌─────────────────────────────┐
│ 💰 Capital Account          │
│   Current: $4,000           │
│   Progress: [████----] 57%  │
│   Next paycheck: 12 days    │
├─────────────────────────────┤
│ Trading Modes               │
│   ☑ Swing Trading           │
│   ☐ Day Trade Monitor       │
│   ☐ Execute Day Trades      │
├─────────────────────────────┤
│ Select View                 │
│   ○ Today's Opportunities   │
│   ○ Active Positions        │
│   ○ Trading Ledger          │
│   ○ Debug & Analysis        │
└─────────────────────────────┘
```

### Main Dashboard Layout
```
┌─────────────────────────────────────────────────────────┐
│  Swing Trades (15%+)   │   Day Trades (2%+)             │
├────────────────────────┼────────────────────────────────┤
│ #1 NVDA - Nvidia       │   #1 TSLA - Tesla              │
│    Return: 16.5%       │      Return: 3.2%              │
│    Confidence: 82%     │      Confidence: 88%           │
│    Score: 85/100       │      Score: 91/100             │
├────────────────────────┼────────────────────────────────┤
│ #2 AMD - Advanced      │   #2 AAPL - Apple              │
│    Return: 15.2%       │      Return: 2.8%              │
│    Confidence: 78%     │      Confidence: 86%           │
│    Score: 81/100       │      Score: 88/100             │
└────────────────────────┴────────────────────────────────┘
```

## File Structure

### New Files
- `ui/enhanced_dashboard.py` - All new UI components
- `UI_ENHANCEMENTS.md` - Full documentation
- `QUICK_UI_REFERENCE.md` - This file

### Modified Files
- `main.py` - Updated to use new components

### Unchanged Files
- `ui/dashboard.py` - Original components preserved
- All core screener logic unchanged
- All existing features still work

## Common Tasks

### Task: Scan for Both Strategies
1. Check both "Swing Trading" and "Day Trade Monitor"
2. Select sector
3. Click "Start Scan"
4. View both columns side-by-side

### Task: Check Ledger Performance
1. Select "📚 Trading Ledger" view
2. Review metrics at top
3. Scroll through trade history
4. Export if needed

### Task: Debug Why Stock Excluded
1. Select "🔧 Debug & Analysis" view
2. Go to "Stock Analyzer" tab
3. Enter symbol (e.g., "NVDA")
4. Click "Analyze for Swing Trade" or "Analyze for Day Trade"
5. See detailed filter results

### Task: Track Progress to $7k
1. Look at sidebar capital section
2. Check progress bar percentage
3. View "Time to $7k Goal" expansion
4. See projections for different scenarios

## Keyboard Shortcuts
None currently - all interaction is click-based via Streamlit.

## Configuration

### Change Starting Capital
Edit `models/capital_account.py`:
```python
starting_capital: float = 4000.0  # Change this value
```

### Change Paycheck Settings
Edit `models/capital_account.py`:
```python
paycheck_amount: float = 100.0          # Change amount
paycheck_frequency_days: int = 14       # Change frequency
```

### Adjust Display Limits
Edit `ui/enhanced_dashboard.py`:
```python
for i, trade in enumerate(trades[:5], 1):  # Change :5 to show more
```

## Troubleshooting

**Q: Day trade checkbox not showing?**
A: Capital must be ≥ $7000. Check sidebar display.

**Q: No results after scan?**
A: Enable at least one mode, try different sector, or lower threshold.

**Q: Ledger shows no data?**
A: Need closed trades with exit dates. Add completed trades first.

**Q: Export buttons don't work?**
A: Ensure ledger has entries. Empty ledger can't export.

## API & Data Sources

- **Primary:** yfinance (FREE, unlimited)
- **Optional:** FMP (enhanced fundamentals)
- **No authentication required** for basic features

## Performance Tips

1. **Limit day trade scanning** - Only scans first 10 tickers per sector
2. **Use debug tab sparingly** - Individual analysis is slower
3. **Export ledger regularly** - Backup your data
4. **Keep ledger reasonable size** - Archive old trades periodically

## Next Steps

1. Run the app: `streamlit run main.py`
2. Review UI_ENHANCEMENTS.md for full details
3. Try each view mode to familiarize yourself
4. Start with swing trading only
5. Add day trading when comfortable
6. Track everything in ledger

## Support

- Full docs: `UI_ENHANCEMENTS.md`
- Code comments in: `ui/enhanced_dashboard.py`
- Test suite: Run Python test in docs
- Examples: Try different sectors and modes

---
*Enhanced UI Version 1.0 - Dual Dashboard with Capital Tracking*
