# UI Enhancements - Dual Dashboard

## Overview
The Streamlit UI has been enhanced with a comprehensive dual dashboard that supports both swing trading and day trading strategies in a single unified interface.

## New Features

### 1. Capital Account Sidebar
**Location:** Left sidebar, top section

**Features:**
- Current capital display with progress indicator
- Progress bar to $7k goal (for Pattern Day Trading eligibility)
- Next paycheck countdown
- Trading statistics (Total Trades, Win Rate, Total Profit, Return %)
- Time-to-goal projections (Current Pace, Best Case, Conservative)

**Usage:**
The capital account automatically initializes with default values ($4000 starting capital, $100 biweekly paychecks). Update these values in the CapitalAccount model as needed.

### 2. Trading Mode Selection
**Location:** Left sidebar, below capital account

**Modes:**
- **📊 Swing Trading** - Scan for 15%+ swing trades (5-10 days)
- **⚡ Day Trade Monitor** - Monitor 2%+ intraday opportunities
- **🔴 Execute Day Trades** - Only available when capital ≥ $7k

**Behavior:**
- Enable one or both trading modes
- Day trade execution locked until $7k threshold
- Monitor mode shows "MONITOR ONLY" badge when capital < $7k

### 3. View Modes (Tabs)
**Location:** Main content area

#### Tab 1: 📊 Today's Opportunities
Dual-column dashboard showing opportunities side-by-side:

**Left Column - Swing Trades:**
- Shows top 5 swing trade opportunities
- 15%+ return targets
- 5-10 day timeframe
- Confidence scores and technical analysis
- Entry, target, and stop prices

**Right Column - Day Trade Monitor:**
- Shows top 5 day trade setups
- 2%+ intraday targets
- 85%+ confidence threshold
- Mode indicator (MONITOR or EXECUTE)
- Real-time opportunity scanning

**Scan Controls:**
- Sector selection
- Minimum return target slider
- Max loss per trade slider
- "Start Scan" button

#### Tab 2: 💼 Active Positions
- Existing position monitoring functionality
- Enter symbol to check position status
- View P&L, progress to target, exit signals
- Technical indicators for open positions

#### Tab 3: 📚 Trading Ledger
**Top Metrics:**
- Total Trades
- Win Rate
- Total Return %
- Average per Trade

**Accuracy Metrics:**
- Prediction Accuracy - How often predictions match reality
- Confidence Calibration - How well confidence scores predict success
- ROI Accuracy - How close actual returns match predictions

**Ledger Table:**
- Complete trade history
- Columns: Date, Type, Symbol, Entry, Target, Stop, Predicted Return, Confidence, Executed, Status
- Sortable and filterable

**Export Options:**
- CSV Export - Download ledger as CSV
- JSON Export - Download ledger as JSON
- Metrics Export - Download performance metrics

#### Tab 4: 🔧 Debug & Analysis
**Filtering Pipeline:**
- Funnel visualization showing how stocks are filtered
- Stages: Initial Universe → Price Filter → Volume Filter → Technical Filter → Final
- Rejection reason breakdown

**Individual Stock Analyzer:**
- Analyze specific stocks for swing or day trading
- See why a stock passed or failed filters
- View detailed metrics and scores
- Useful for understanding why stocks were excluded

### 4. Enhanced Welcome Screen
**Features:**
- Overview of Swing Trading, Day Trading, and Capital Tracking
- Current stats from your capital account
- Quick start guide
- Feature highlights

## Usage Examples

### Scenario 1: New User Starting with Swing Trading
1. Open application - capital starts at $4000
2. Keep "📊 Swing Trading" checked
3. Leave "⚡ Day Trade Monitor" unchecked
4. Select a sector (e.g., Technology)
5. Click "Start Scan"
6. Review swing opportunities in left column
7. Track trades in ledger as you execute them

### Scenario 2: Monitoring Day Trades
1. Check "⚡ Day Trade Monitor" in sidebar
2. Select "📊 Today's Opportunities" view
3. Click "Start Scan"
4. Right column shows day trade setups
5. Note "MONITOR ONLY" indicator (capital < $7k)
6. Review opportunities without executing
7. Track progress toward $7k goal

### Scenario 3: Dual Dashboard Trading
1. Enable both "📊 Swing Trading" and "⚡ Day Trade Monitor"
2. Run scan with selected sector
3. View both opportunity types side-by-side
4. Choose best opportunities from either column
5. Track all trades in unified ledger

### Scenario 4: Reaching $7k Threshold
1. Capital reaches $7000+
2. "🔴 Execute Day Trades" checkbox becomes available
3. Check to enable execution mode
4. Day trade column changes from "MONITOR" to "EXECUTE"
5. Can now execute day trades within PDT rules

### Scenario 5: Analyzing Ledger Performance
1. Select "📚 Trading Ledger" view
2. Review win rate and accuracy metrics
3. Check prediction vs. actual performance
4. Export data for external analysis
5. Use insights to improve strategy

### Scenario 6: Debugging Filter Results
1. Select "🔧 Debug & Analysis" view
2. View filtering pipeline to see how many stocks passed each stage
3. Use Individual Stock Analyzer to check specific symbols
4. Understand why certain stocks were included/excluded
5. Refine strategy based on insights

## Technical Details

### Session State Variables
- `capital_account` - CapitalAccount instance
- `ledger` - TradingLedger instance
- `enable_swing` - Boolean for swing trading mode
- `enable_day_monitor` - Boolean for day trading monitor
- `execute_day_trades` - Boolean for day trade execution
- `last_scan_results` - Dict with most recent scan results

### Component Functions

#### `render_capital_sidebar(capital_account)`
Renders capital tracking in sidebar with progress bars and metrics.

#### `render_dual_opportunities(swing_trades, day_opportunities, capital_account, execute_day_trades)`
Renders split-screen view with swing and day opportunities.

#### `render_ledger_tab(ledger)`
Displays trading ledger with performance metrics and export options.

#### `render_debug_tab(scan_results)`
Shows filtering pipeline visualization and stock analyzer tool.

### Data Flow
1. User enables trading modes and clicks "Start Scan"
2. `render_opportunities_tab()` runs appropriate scanners
3. Swing scanner: `AdaptiveScreener.scan_sector()`
4. Day scanner: `DayScreener.analyze_stock()` for each ticker
5. Results passed to `render_dual_opportunities()`
6. Opportunities displayed in respective columns

## Customization

### Adjusting Capital Settings
Edit `models/capital_account.py`:
```python
starting_capital: float = 4000.0  # Change initial capital
paycheck_amount: float = 100.0     # Change paycheck amount
paycheck_frequency_days: int = 14  # Change frequency
```

### Changing Day Trade Thresholds
Edit `config/settings.py`:
```python
DAY_TRADE_MIN_RETURN = 1.0        # Minimum return
DAY_TRADE_TARGET_RETURN = 2.5     # Target return
DAY_TRADE_MIN_CONFIDENCE = 85     # Minimum confidence
```

### Modifying Display Limits
In `ui/enhanced_dashboard.py`:
```python
for i, trade in enumerate(trades[:5], 1):  # Change 5 to show more/fewer
```

## Troubleshooting

### Issue: Day trading checkbox not appearing
**Solution:** Capital must be ≥ $7000. Check capital account in sidebar.

### Issue: Ledger showing no metrics
**Solution:** No closed trades yet. Ledger needs completed trades with exit data.

### Issue: Scan returns no results
**Solution:** 
- Check if both modes are disabled
- Try different sector
- Lower minimum return threshold
- Check Debug tab for filter statistics

### Issue: Export buttons not working
**Solution:** Ensure ledger has entries. Empty ledger cannot be exported.

## Best Practices

1. **Start Simple:** Begin with swing trading only until comfortable
2. **Track Everything:** Add all trades to ledger for accurate metrics
3. **Monitor Progress:** Use capital account to track toward $7k goal
4. **Use Debug Tab:** Understand why stocks pass/fail filters
5. **Export Regularly:** Backup ledger data via CSV/JSON exports
6. **Review Metrics:** Check accuracy scores to improve predictions
7. **Wait for $7k:** Don't try to day trade until capital threshold reached

## Future Enhancements
Potential future additions:
- Real-time capital sync with broker API
- Automatic ledger updates from executed trades
- Email/SMS alerts for high-confidence opportunities
- Portfolio allocation optimizer
- Risk management dashboard
- Trade journal with notes and screenshots

## Support
For issues or questions:
- Check troubleshooting section above
- Review code comments in `ui/enhanced_dashboard.py`
- Examine existing ledger entries for data format examples
- Test with individual stocks using Debug tab analyzer
