# Trading Ledger - Quick Reference

## Common Commands

### View Trades
```bash
python ledger/ledger_console.py --view              # All trades
python ledger/ledger_console.py --view --open       # Open only
python ledger/ledger_console.py --view --closed     # Closed only
```

### Performance & Accuracy
```bash
python ledger/ledger_console.py --performance       # Performance metrics
python ledger/ledger_console.py --accuracy          # Accuracy metrics
python ledger/ledger_console.py --summary           # Full summary
```

### Export
```bash
python ledger/ledger_console.py --export csv        # Export to CSV
python ledger/ledger_console.py --export json       # Export to JSON
python ledger/ledger_console.py --export txt        # Text summary
python ledger/ledger_console.py --export html       # HTML report
```

### Interactive
```bash
python ledger/ledger_console.py --add-trade         # Add new trade
python ledger/ledger_console.py --close-trade       # Close existing trade
```

## Quick API Examples

### Log a Trade
```python
from ledger import trade_logger
from models.trade import Trade

trade = Trade(symbol='AAPL', entry_price=180, ...)
entry = trade_logger.log_trade_entry(trade, executed=True)
print(entry.trade_id)
```

### Close a Trade
```python
closed = trade_logger.log_trade_exit(
    "AAPL_20240204_123456",
    exit_price=190,
    exit_reason='TARGET_HIT'
)
print(f"Return: {closed.actual_return_pct:.2f}%")
```

### Get Performance
```python
from ledger.trading_ledger import TradingLedger

ledger = TradingLedger()
summary = ledger.get_performance_summary()
print(f"Win rate: {summary['win_rate']:.2f}%")
```

### Export Data
```python
from ledger.reports import export_to_csv
from ledger import trade_logger

trades = trade_logger.get_all_trades()
export_to_csv(trades, "my_trades.csv")
```

## Key Metrics

| Metric | Description | Formula |
|--------|-------------|---------|
| **Win Rate** | % of winning trades | `(wins / total) × 100` |
| **Expectancy** | Avg profit per trade | `(Win% × AvgWin) - (Loss% × AvgLoss)` |
| **Return Accuracy** | Prediction accuracy | `max(0, 100 - error×10)` |
| **Entry Quality** | Entry execution quality | `max(0, 100 - slippage%×20)` |

## Exit Reasons

- `TARGET_HIT` - Target price reached
- `STOP_LOSS` - Stop loss triggered
- `TIME_LIMIT` - Time-based exit
- `MANUAL` - Manual exit decision

## Trade Types

- `SWING` - Multi-day trades (typically 3-30 days)
- `DAY` - Intraday trades (same-day entry/exit)

## File Locations

- **Ledger data:** `data/ledger/ledger.json`
- **Exports:** `data/ledger/` (with timestamps)

## Examples

See `ledger/example_usage.py` for complete examples:
```bash
python ledger/example_usage.py
```

## Tips

1. **Use consistent confidence levels** - Calibrate over time
2. **Always add notes** - Record your reasoning
3. **Track monitored trades** - Learn from opportunities you didn't take
4. **Review regularly** - Check accuracy and performance weekly
5. **Export backups** - Save your data periodically

## Integration Example

```python
# In your trading script
from ledger import trade_logger

# After finding a trade opportunity
for trade in opportunities:
    if should_execute(trade):
        entry = trade_logger.log_trade_entry(
            trade,
            executed=True,
            notes=f"Auto-executed: {trade.entry_strategy}"
        )

# When closing position
trade_logger.log_trade_exit(
    trade_id,
    exit_price=current_price,
    exit_reason='TARGET_HIT',
    lessons_learned='Strong follow-through'
)
```

## Troubleshooting

**Empty ledger after restart?**
- Check `data/ledger/ledger.json` exists
- Verify file permissions

**Import errors?**
- Run from project root directory
- Check Python path includes project

**Metrics showing 0?**
- Need closed executed trades for performance metrics
- Monitored trades don't count toward P&L

---

For full documentation, see `ledger/README.md`
