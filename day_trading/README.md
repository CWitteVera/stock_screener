# Day Trading Monitoring System

Complete intraday trading system for 1-5% daily opportunities with 85%+ confidence.

## 📁 System Components

### 1. **intraday_strategy.py** - Technical Analysis Engine
Filters and scores stocks for day trading potential:
- ✅ Pre-market gap detection (>1%)
- ✅ Volume surge analysis (>2x average)
- ✅ High ATR calculation (>5% volatility)
- ✅ News catalyst detection
- ✅ Support/resistance levels
- ✅ Technical setup scoring (0-100)
- ✅ Momentum analysis (MACD, RSI, velocity)

### 2. **day_screener.py** - Morning Scanner
Pre-market scan at 8:45 AM to find opportunities:
- Scans all sectors from watchlists
- Applies intraday filters
- Estimates 1-5% intraday moves
- Calculates 85%+ confidence requirements
- Returns ranked DayTradeOpportunity objects
- Shows setup type (GAP_UP, MOMENTUM, BREAKOUT, etc.)

### 3. **live_monitor.py** - Position Tracking
Monitors positions every 15 minutes:
- Tracks executed AND educational (monitor-only) trades
- Real-time P&L calculations
- Automatic exit conditions:
  - 🎯 Target hit
  - 🛑 Stop loss triggered
  - ⏰ 3:45 PM force exit
- Persistent storage in JSON
- Historical tracking

### 4. **day_console.py** - Command-Line Interface
Easy-to-use CLI for all operations:
```bash
# Morning scan
python day_console.py --scan

# Scan specific symbol
python day_console.py --scan --symbol AAPL

# Monitor a stock
python day_console.py --monitor TSLA

# Check status
python day_console.py --status

# Custom check interval
python day_console.py --status --check-interval 10
```

## 🎯 Key Features

### Educational Mode (< $7,000 capital)
- 📚 **Monitor-only**: Tracks "would-be" P&L without executing
- 📊 **Real data**: Uses live market prices
- 📈 **Learn patterns**: Understand what works
- 💡 **No risk**: Practice before committing capital

### Active Trading Mode (≥ $7,000 capital)
- 💰 **Live execution**: Real trades with broker API
- ⚠️ **PDT tracking**: Monitors 3 trades/week limit
- 🔒 **Risk management**: 2% max loss per trade
- 📊 **Performance tracking**: Real P&L

### Safety Features
- ⏰ **Force exit at 3:45 PM** - Avoid overnight risk
- 🛑 **Automatic stop loss** - 2% max loss
- ⚠️ **PDT warnings** - Prevents rule violations
- 📊 **Capital tracking** - Prevents over-leveraging

## 📊 Confidence Scoring

Opportunities must score 85%+ confidence based on:
- **Setup Quality (30%)**: Trend, volume, pattern quality
- **Momentum (25%)**: MACD, ROC, price velocity  
- **Catalysts (20%)**: News events, earnings, announcements
- **Volatility (15%)**: ATR contribution for move potential
- **Volume (10%)**: Surge vs. average volume

## 🎯 Trade Selection Criteria

### Must Pass ALL Filters:
1. ✅ Pre-market gap > 1%
2. ✅ Volume surge > 2x average
3. ✅ ATR > 5% (volatility for intraday moves)
4. ✅ Overall confidence ≥ 85%
5. ✅ Price between $5-$500
6. ✅ Liquid stocks only (from curated watchlists)

### Return Estimates:
- Conservative: 40% of ATR as target
- Adjusted for momentum strength
- Capped at 1-5% realistic range
- Based on historical volatility patterns

## 📁 Data Storage

Monitored trades stored at:
```
/home/runner/work/stock_screener/stock_screener/data/day_trading/monitored_trades.json
```

JSON structure:
```json
{
  "last_updated": "2026-02-04T15:44:07",
  "trades": [
    {
      "symbol": "TSLA",
      "executed": false,
      "entry_price": 250.50,
      "current_price": 253.75,
      "current_pnl": 13.00,
      "status": "MONITORING",
      ...
    }
  ]
}
```

## 🚀 Quick Start

### 1. Morning Routine (8:45 AM)
```bash
# Scan for opportunities
python day_trading/day_console.py --scan

# Review top 5 opportunities
# System shows: setup type, confidence, catalyst, targets
```

### 2. Select & Monitor
```bash
# Add to monitoring (educational mode)
python day_trading/day_console.py --monitor AAPL

# Or execute if capital > $7k
python day_trading/day_console.py --monitor AAPL --execute
```

### 3. Check Progress
```bash
# Status check (every 15 min recommended)
python day_trading/day_console.py --status
```

### 4. End of Day
System auto-exits at 3:45 PM. Review results:
```bash
python day_trading/day_console.py --status
```

## 📈 Example Output

### Morning Scan:
```
================================================================================
DAY TRADING MORNING SCAN - Pre-Market Analysis
Scan time: 2026-02-04 08:45:00
Minimum confidence: 85%
================================================================================

📊 Scanning Technology...
------------------------------------------------------------
  ✅ NVDA - NVIDIA Corporation
     Setup: MOMENTUM | Confidence: 92%
     Entry: $850.25 → Target: $867.76 (2.1%)
     Stop: $833.45 | Est. Time: 120min
     Gap: +2.3% | Volume: 3.2x | ATR: 7.8%
     Catalyst: 3 news items in last 24h: "NVIDIA announces new AI chip"
     Position: 1 shares = $850.25
     Est. Return: +$17.51 | Max Loss: $16.80
     Risk/Reward: 1.04:1

🏆 TOP OPPORTUNITIES
#1 NVDA - Score: 92.0/100
```

### Position Monitoring:
```
📊 POSITION CHECK - 2026-02-04 10:30:00
================================================================================

📚 NVDA - NVIDIA Corporation
   Entry: $850.25 → Current: $859.40
   Target: $867.76 | Stop: $833.45
   📈 P&L: +$9.15 (+1.08%)
   Time in trade: 1h 45m

MONITORING SUMMARY
--------------------------------------------------------------------------------
📊 Active Positions: 1
   Total P&L: +$9.15
```

## ⚙️ Configuration

Settings in `config/settings.py`:
```python
DAY_TRADE_MIN_RETURN = 1.0          # 1% minimum
DAY_TRADE_TARGET_RETURN = 2.5       # 2.5% typical
DAY_TRADE_MAX_RETURN = 5.0          # 5% maximum
DAY_TRADE_MAX_LOSS = 2.0            # 2% stop loss
DAY_TRADE_MIN_CONFIDENCE = 85       # 85% minimum
DAY_TRADE_CHECK_INTERVAL = 15       # Check every 15 min
DAY_TRADE_FORCE_EXIT_TIME = "15:45" # Force exit time
PDT_WEEKLY_LIMIT = 3                # Pattern Day Trader limit
```

## 🔧 Advanced Usage

### Test Single Stock:
```python
from day_trading import DayScreener

screener = DayScreener()
opportunity = screener.scan_single_stock('AAPL')
if opportunity:
    print(f"Found: {opportunity.symbol} - {opportunity.confidence}%")
```

### Manual Strategy Testing:
```python
from day_trading import IntradayStrategy

strategy = IntradayStrategy()
eval_data = strategy.evaluate_stock('TSLA')
print(f"Overall score: {eval_data['overall_score']}")
print(f"Setup score: {eval_data['setup_score']}")
print(f"Momentum: {eval_data['momentum_score']}")
```

### Custom Monitoring:
```python
from day_trading import LiveMonitor
from models import DayTradeOpportunity

monitor = LiveMonitor()
# ... create opportunity ...
monitor.add_trade(opportunity, executed=False)
monitor.check_positions()
```

## 📊 Performance Tracking

The system tracks:
- ✅ Entry/exit prices and times
- ✅ Actual vs. predicted returns
- ✅ Win rate and average P&L
- ✅ Time in trade vs. estimates
- ✅ Which setup types perform best
- ✅ Educational vs. executed performance

## ⚠️ Risk Warnings

- **PDT Rules**: Limited to 3 day trades per week (< $25k account)
- **Slippage**: Actual fills may differ from targets
- **Gaps**: Pre-market gaps can reverse quickly
- **News Risk**: Catalysts can be positive or negative
- **Educational Mode**: Practice extensively before live trading
- **Capital Requirements**: Need $7k to enable execution

## 🎓 Learning Resources

Use educational mode to:
1. Understand setup patterns
2. Calibrate confidence scoring
3. Test timing strategies
4. Develop exit discipline
5. Build experience without risk

Track your "would-be" results over 30+ days before committing capital.

## 🔄 Integration

Works seamlessly with:
- ✅ Main stock screener (swing trades)
- ✅ Capital account tracking
- ✅ Ledger system
- ✅ Sector watchlists
- ✅ Settings configuration

## 📞 Support

For issues or questions:
1. Check configuration in `config/settings.py`
2. Verify watchlists in `watchlists/*.txt`
3. Review monitored trades JSON for data
4. Test with `--status` command first

## 🎯 Success Tips

1. **Scan Early**: 8:45 AM is optimal (pre-market info available)
2. **High Confidence Only**: Don't trade opportunities < 85%
3. **Respect Stops**: 2% loss is maximum - no exceptions
4. **Force Exit**: Always exit by 3:45 PM - no overnight holds
5. **Track Everything**: Review what worked and what didn't
6. **PDT Awareness**: Save your 3 trades for best opportunities
7. **Educational First**: Practice for 30+ days before executing

---

**Built for 1-5% daily moves with 85%+ confidence. Trade smart, trade safe.**
