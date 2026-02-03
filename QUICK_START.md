# Quick Reference Guide

## 🚀 Getting Started in 60 Seconds

### Installation
```bash
pip install -r requirements.txt
```

### Run the Screener

**Web Interface:**
```bash
streamlit run main.py
```

**Command Line:**
```bash
python console_scanner.py --sector Technology
```

## 📖 Common Commands

### Scanning

```bash
# Scan specific sector for 15%+ opportunities
python console_scanner.py --sector Technology

# Scan with lower 8% threshold
python console_scanner.py --sector Healthcare --min-return 8

# Scan custom watchlist
python console_scanner.py --watchlist watchlists/custom.txt
```

### Exporting

```bash
# Export to Fidelity CSV
python console_scanner.py --sector Energy --export fidelity

# Export full analysis
python console_scanner.py --sector Financials --export csv

# Export to JSON
python console_scanner.py --sector Consumer --export json
```

### Monitoring Positions

```bash
# Monitor active position
python console_scanner.py --monitor NVDA

# Check position status
python console_scanner.py --monitor AAPL
```

## 🎯 Understanding Results

### Tier 1 - Aggressive (15%+)
```
🔥 AGGRESSIVE OPPORTUNITIES
5 high-confidence trades with 15%+ potential
Action: TRADE NOW
```

### Tier 2 - Moderate (8-14%)
```
⚠️ MODERATE OPPORTUNITIES
3 trades with 8-14% potential
Action: Consider smaller positions
```

### Tier 3 - Wait (<8%)
```
🛑 WEAK MARKET CONDITIONS
No stocks meet criteria
Action: HOLD CASH
```

## 📊 Reading Trade Cards

```
🥇 RANK #1: NVDA - NVIDIA Corp
Current Price: $487.23
Score: 94/100 ⭐⭐⭐⭐⭐

📈 RETURN POTENTIAL: 16.2% in 7 days
   Confidence: 78% ●●●●●●●●○○

💰 TRADE SETUP:
   BUY:    2 shares @ $487.23 = $974.46
   TARGET: $566 (+16.2% = +$157 profit)
   STOP:   $438 (-10.1% = -$99 max loss)

📊 TECHNICAL SIGNALS:
   ✅ MACD: 92/100
   ✅ RSI: 58 (momentum zone)
   ✅ Volume: 96/100
   ✅ Breakout: 90/100
   ✅ Momentum: 95/100
```

## 🛡️ Risk Management

Every trade includes:
- **Entry Price:** Optimal buy price
- **Target Price:** 15% or 8% return goal
- **Stop Loss:** -10% maximum loss
- **Position Size:** Calculated for $1000
- **Risk/Reward:** Minimum 1:1.5 ratio
- **Time Limit:** Exit after 10 days

## 📁 Sector Watchlists

Pre-built watchlists available:

| Sector | Stocks | File |
|--------|--------|------|
| Technology | 43 | `watchlists/technology.txt` |
| Healthcare | 35 | `watchlists/healthcare.txt` |
| Energy | 24 | `watchlists/energy.txt` |
| Financials | 25 | `watchlists/financials.txt` |
| Consumer | 22 | `watchlists/consumer.txt` |
| Communications | 20 | `watchlists/communications.txt` |

## 🔧 Configuration

### Optional: Add FMP API Key

1. Copy example: `cp .env.example .env`
2. Edit `.env` and add your key
3. Get free key: https://financialmodelingprep.com/developer/docs/

**Note:** Screener works 100% FREE without API key!

## 💡 Tips & Best Practices

### When to Trade
- ✅ **Tier 1** with 3+ opportunities → Pick best 1-2
- ⚠️ **Tier 2** with good technical signals → Consider carefully
- 🛑 **Tier 3** → Wait for better conditions

### Position Management
1. **Enter:** At or below entry price
2. **Monitor:** Daily using `--monitor`
3. **Exit:** At target, stop, or 10 days

### Risk Control
- Never risk more than $100 per trade
- Always set stop loss orders
- Exit at 10 days regardless of P&L
- Don't chase prices above entry + 3%

## 🆘 Troubleshooting

### "No symbols found in watchlist"
- Check file path is correct
- Ensure watchlist file exists
- Verify symbols are comma or newline separated

### "Could not fetch data"
- Check internet connection
- Try again in a few minutes
- Some symbols may be delisted

### "No opportunities found"
- Normal in weak markets
- Try different sector
- Lower min-return threshold (--min-return 8)

## 📞 Support

- **Documentation:** See README.md
- **Issues:** Create GitHub issue
- **Questions:** Check examples in README

## 🎓 Example Workflow

```bash
# Morning: Find trades
python console_scanner.py --sector Technology --export fidelity

# Review results, select top 1-2 trades
# Import fidelity_trades.csv into Fidelity ATP

# Daily: Monitor positions
python console_scanner.py --monitor NVDA
python console_scanner.py --monitor AMD

# When exit signal appears:
# - Target reached: Sell and take profit
# - Stop hit: Sell and limit loss
# - 10 days passed: Sell regardless
```

Happy Trading! 📈
