# Trading Ledger System

A comprehensive trading ledger system for tracking, analyzing, and reporting on swing and day trades.

## Overview

The Trading Ledger System provides a complete solution for:
- **Recording trades** (executed or monitored)
- **Tracking performance** (win rate, P&L, accuracy)
- **Analyzing predictions** (return accuracy, timeline accuracy, entry quality)
- **Generating reports** (CSV, JSON, HTML, text summaries)
- **CLI interface** for easy interaction

## Features

### Core Functionality
- ✅ Track both swing trades and day trades
- ✅ Record executed trades or monitored opportunities
- ✅ Calculate prediction accuracy metrics
- ✅ Generate performance reports
- ✅ Export to multiple formats (CSV, JSON, HTML)
- ✅ Command-line interface for all operations

### Metrics Tracked
- **Performance**: Win rate, total return, average return, expectancy
- **Accuracy**: Return prediction accuracy, timeline accuracy, entry quality
- **Analysis**: Best/worst trades, metrics by symbol, confidence calibration

## File Structure

```
ledger/
├── __init__.py              # Package initialization
├── trading_ledger.py        # Main ledger class
├── trade_logger.py          # Simple logging functions
├── accuracy_calculator.py   # Prediction accuracy calculations
├── performance_metrics.py   # Performance calculations
├── reports.py               # Export and reporting
└── ledger_console.py        # CLI interface

data/ledger/
└── ledger.json              # Persistent ledger storage
```

## Quick Start

### Using the Command Line

```bash
# View all trades
python ledger/ledger_console.py --view

# View only open trades
python ledger/ledger_console.py --view --open

# View performance summary
python ledger/ledger_console.py --performance

# View accuracy metrics
python ledger/ledger_console.py --accuracy

# Generate full summary report
python ledger/ledger_console.py --summary

# Export to CSV
python ledger/ledger_console.py --export csv

# Export to specific file
python ledger/ledger_console.py --export json --output my_trades.json

# Add trade interactively
python ledger/ledger_console.py --add-trade

# Close trade interactively
python ledger/ledger_console.py --close-trade
```

### Using the Python API

```python
from ledger import trade_logger
from models.trade import Trade

# Log a swing trade entry
trade = Trade(
    symbol='AAPL',
    name='Apple Inc.',
    entry_price=180.00,
    target_price=195.00,
    stop_price=175.00,
    estimated_return=8.33,
    confidence=85,
    days_to_target=10,
    # ... other fields
)

entry = trade_logger.log_trade_entry(
    trade, 
    executed=True, 
    notes='Strong breakout setup'
)

print(f"Trade logged with ID: {entry.trade_id}")

# Close the trade
closed = trade_logger.log_trade_exit(
    entry.trade_id,
    exit_price=192.00,
    exit_reason='TARGET_HIT',
    lessons_learned='Target hit earlier than expected'
)

print(f"Return: {closed.actual_return_pct:.2f}%")
print(f"Accuracy: {closed.return_accuracy:.2f}%")
```

### Advanced API Usage

```python
from ledger.trading_ledger import TradingLedger
from ledger.performance_metrics import get_win_rate, get_expectancy
from ledger.accuracy_calculator import get_overall_accuracy

# Load ledger
ledger = TradingLedger()

# Get performance summary
summary = ledger.get_performance_summary()
print(f"Win Rate: {summary['win_rate']:.2f}%")
print(f"Total Return: {summary['total_return']:.2f}%")

# Get accuracy metrics
accuracy = ledger.calculate_accuracy_metrics()
print(f"Return Accuracy: {accuracy['return_accuracy']:.2f}%")

# Get confidence calibration
calibration = ledger.get_confidence_calibration()
for bucket, stats in calibration.items():
    print(f"{bucket}: {stats['win_rate']:.2f}% win rate")

# Get open trades
open_trades = ledger.get_open_trades()
for trade in open_trades:
    print(f"{trade.symbol}: Entered at ${trade.actual_entry}")
```

## API Reference

### TradingLedger Class

Main class for managing the trading ledger.

**Methods:**
- `add_trade_entry(trade, executed=False, notes="")` - Add a new trade
- `update_trade_exit(trade_id, exit_price, exit_reason, lessons_learned)` - Close a trade
- `get_trade_by_id(trade_id)` - Get specific trade
- `get_open_trades()` - Get all open trades
- `get_closed_trades()` - Get all closed trades
- `get_executed_trades()` - Get only executed trades
- `calculate_accuracy_metrics()` - Get overall accuracy stats
- `get_performance_summary()` - Get performance summary
- `get_confidence_calibration()` - Analyze confidence vs actual results
- `save()` - Save ledger to disk
- `load()` - Load ledger from disk

### trade_logger Module

Simple convenience functions for logging.

**Functions:**
- `log_trade_entry(trade, executed=True, notes="")` - Log trade entry
- `log_trade_exit(trade_id, exit_price, exit_reason, lessons_learned)` - Log trade exit
- `get_trade_by_id(trade_id)` - Get trade by ID
- `get_all_trades()` - Get all trades
- `get_open_trades()` - Get open trades
- `get_closed_trades()` - Get closed trades

### accuracy_calculator Module

Calculate prediction accuracy metrics.

**Functions:**
- `calculate_return_accuracy(predicted, actual)` - Return prediction accuracy (0-100%)
- `calculate_timeline_accuracy(predicted_days, actual_days)` - Timeline accuracy
- `calculate_entry_quality(predicted_price, actual_price)` - Entry quality score
- `get_overall_accuracy(entries)` - Overall accuracy across multiple trades
- `get_accuracy_by_confidence(entries)` - Accuracy grouped by confidence level
- `get_accuracy_by_trade_type(entries)` - Accuracy by SWING vs DAY

### performance_metrics Module

Performance calculations and analysis.

**Functions:**
- `get_win_rate(entries)` - Calculate win rate
- `get_profit_loss_summary(entries)` - Comprehensive P&L summary
- `get_avg_profit_per_trade(entries)` - Average profit per trade
- `get_best_worst_trades(entries, n=5)` - Top/bottom performing trades
- `get_metrics_by_type(entries, trade_type)` - Metrics for SWING or DAY
- `get_metrics_by_symbol(entries)` - Metrics grouped by symbol
- `get_metrics_by_confidence(entries)` - Metrics grouped by confidence
- `get_expectancy(entries)` - Trading expectancy calculation

### reports Module

Export and reporting functionality.

**Functions:**
- `export_to_csv(entries, filepath)` - Export to CSV
- `export_to_json(entries, filepath)` - Export to JSON
- `generate_summary_report(entries)` - Generate text report
- `export_summary_to_file(entries, filepath)` - Save summary to file
- `export_html_report(entries, filepath)` - Generate HTML report

## Data Model

### LedgerEntry

Each trade is stored as a `LedgerEntry` with:

**Identification:**
- `trade_id` - Unique identifier
- `trade_type` - "SWING" or "DAY"
- `symbol` - Stock symbol
- `entry_date` - Date entered
- `exit_date` - Date exited (or None if open)

**Predicted Values:**
- `predicted_entry` - Predicted entry price
- `predicted_target` - Target price
- `predicted_stop` - Stop loss price
- `predicted_return_pct` - Expected return %
- `predicted_confidence` - Confidence level (0-100)
- `predicted_days` - Expected days to target

**Actual Values:**
- `actual_entry` - Actual entry price
- `actual_exit` - Actual exit price
- `actual_return_pct` - Actual return %
- `actual_days` - Actual days to target
- `executed` - Was trade executed or just monitored?

**Results:**
- `outcome` - "WIN", "LOSS", or "BREAK_EVEN"
- `exit_reason` - "TARGET_HIT", "STOP_LOSS", "TIME_LIMIT", "MANUAL"
- `profit_loss` - P&L amount

**Accuracy Metrics:**
- `return_accuracy` - How close prediction was to actual
- `timeline_accuracy` - Timeline prediction accuracy
- `entry_quality` - Entry execution quality (slippage)

**Notes:**
- `notes` - General notes
- `lessons_learned` - Lessons from this trade

## Metrics Explained

### Accuracy Metrics

**Return Accuracy (0-100%)**
- Measures how close the predicted return was to actual
- Formula: `max(0, 100 - (error × 10))`
- 10% error = 0% accuracy
- Example: Predicted +10%, got +9.5% = 95% accuracy

**Timeline Accuracy (0-100%)**
- Measures how close predicted timeline was to actual
- Formula: `max(0, 100 - (days_error × 10))`
- 10 days error = 0% accuracy
- Example: Predicted 5 days, took 3 days = 80% accuracy

**Entry Quality (0-100%)**
- Measures slippage from predicted entry price
- Formula: `max(0, 100 - (slippage% × 20))`
- 5% slippage = 0% quality
- Example: Predicted $100, entered at $101 = 80% quality

### Performance Metrics

**Win Rate**
- Percentage of winning trades
- Formula: `(wins / total_trades) × 100`

**Expectancy**
- Average profit per dollar risked
- Formula: `(Win% × Avg Win) - (Loss% × Avg Loss)`
- Positive expectancy = profitable system

## Examples

### Example 1: Log and Close a Trade

```python
from ledger import trade_logger
from models.trade import Trade

# Create and log trade
trade = Trade(
    symbol='MSFT',
    entry_price=350.00,
    target_price=375.00,
    stop_price=340.00,
    estimated_return=7.14,
    confidence=80,
    days_to_target=7,
    # ... other required fields
)

entry = trade_logger.log_trade_entry(trade, executed=True)

# Later, close the trade
closed = trade_logger.log_trade_exit(
    entry.trade_id,
    exit_price=370.00,
    exit_reason='TARGET_HIT'
)

print(f"Return: {closed.actual_return_pct:.2f}%")
print(f"Accuracy: {closed.return_accuracy:.2f}%")
```

### Example 2: Generate Performance Report

```python
from ledger.reports import generate_summary_report
from ledger import trade_logger

trades = trade_logger.get_all_trades()
report = generate_summary_report(trades)
print(report)
```

### Example 3: Analyze by Confidence Level

```python
from ledger.trading_ledger import TradingLedger

ledger = TradingLedger()
calibration = ledger.get_confidence_calibration()

for bucket, stats in calibration.items():
    print(f"Confidence {bucket}:")
    print(f"  Trades: {stats['count']}")
    print(f"  Win Rate: {stats['win_rate']:.2f}%")
    print(f"  Avg Return: {stats['avg_return']:.2f}%")
```

### Example 4: Export to CSV

```python
from ledger.reports import export_to_csv
from ledger import trade_logger

trades = trade_logger.get_all_trades()
export_to_csv(trades, "data/ledger/my_trades.csv")
```

## Edge Cases Handled

- ✅ Empty ledger (no trades yet)
- ✅ Missing accuracy data (when metrics can't be calculated)
- ✅ Monitored vs executed trades
- ✅ Open vs closed trades
- ✅ Day trades (0 days timeline)
- ✅ Invalid trade IDs
- ✅ File I/O errors

## Integration

The ledger system integrates with:
- **models/trade.py** - Swing trade opportunities
- **models/day_trade_opportunity.py** - Day trade opportunities
- **models/ledger_entry.py** - Ledger entry data model

Example integration in a trading script:

```python
from core.scanner import TradingScanner
from ledger import trade_logger

# Scan for opportunities
scanner = TradingScanner()
trades = scanner.find_swing_trades()

# Log each opportunity
for trade in trades:
    if trade.confidence >= 85:  # High confidence only
        entry = trade_logger.log_trade_entry(
            trade,
            executed=True,  # If we execute
            notes=f"Auto-logged from scanner"
        )
        print(f"Logged: {entry.trade_id}")
```

## CLI Help

```bash
python ledger/ledger_console.py --help
```

Shows all available commands and options.

## Data Storage

Ledger data is stored in JSON format at:
```
data/ledger/ledger.json
```

The file is automatically created on first use. Each trade is stored as a dictionary with all fields preserved.

## Best Practices

1. **Always log notes** - Record why you took the trade
2. **Record lessons learned** - Note what worked and what didn't
3. **Use confidence levels consistently** - Calibrate your confidence over time
4. **Monitor AND execute** - Track opportunities you didn't take
5. **Review regularly** - Use `--performance` and `--accuracy` to improve
6. **Export periodically** - Backup your data with `--export json`

## Future Enhancements

Potential additions:
- Tagging system (breakout, reversal, etc.)
- Filter trades by date range
- Chart generation
- Advanced statistics (Sharpe ratio, max drawdown)
- Integration with broker APIs
- Real-time position tracking

## Support

For issues or questions:
1. Check this README
2. Review the examples
3. Test with `--help` flag
4. Check the code comments

---

**Built for systematic trading and continuous improvement.**
