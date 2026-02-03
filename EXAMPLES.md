# Usage Examples

This file contains real-world usage examples for the swing trading screener.

## Example 1: Monday Morning Scan

**Goal:** Find the best swing trade opportunities for the week

```bash
# Scan Technology sector (usually most volatile)
python console_scanner.py --sector Technology --export fidelity

# Review results:
# - Tier 1: Found 4 aggressive trades
# - Top pick: NVDA at $487, target $566 (+16.2%)
# - Second: AMD at $156, target $180 (+14.8%)

# Import fidelity_trades.csv into your broker
# Execute trade for NVDA (2 shares @ $487.23 = $974.46)
```

## Example 2: Lower Risk Scan

**Goal:** Find moderate opportunities in defensive sectors

```bash
# Scan Healthcare with 8% minimum target
python console_scanner.py --sector Healthcare --min-return 8 --export csv

# Review results:
# - Tier 2: Found 5 moderate trades
# - Lower risk but consistent returns
# - Good for cautious trading days
```

## Example 3: Custom Watchlist

**Goal:** Scan your own list of favorite stocks

```bash
# Edit watchlists/custom.txt with your symbols:
# AAPL,MSFT,GOOGL,AMZN,TSLA,NVDA

# Run scan
python console_scanner.py --watchlist watchlists/custom.txt --export json
```

## Example 4: Multi-Sector Search

**Goal:** Find the absolute best opportunities across sectors

```bash
# Monday: Scan Technology
python console_scanner.py --sector Technology > tech_results.txt

# Tuesday: Scan Energy
python console_scanner.py --sector Energy > energy_results.txt

# Wednesday: Scan Financials
python console_scanner.py --sector Financials > financials_results.txt

# Review all three, pick the highest scoring trades
```

## Example 5: Position Monitoring Workflow

**Goal:** Track your active $1000 position daily

```bash
# Day 1: Enter position (after finding trade)
# Bought NVDA: 2 shares @ $487.23

# Day 2: Morning check
python console_scanner.py --monitor NVDA
# Output: +3.0% | Status: HOLD | Signals: Bullish

# Day 3: Morning check
python console_scanner.py --monitor NVDA
# Output: +8.5% | Status: HOLD | Signals: Strong

# Day 7: Target reached!
python console_scanner.py --monitor NVDA
# Output: +16.2% | Status: TARGET REACHED | Action: EXIT
# Sell position, profit: $157.54 ✅
```

## Example 6: Bear Market Strategy

**Goal:** Protect capital when markets are weak

```bash
# Scan with standard 15% target
python console_scanner.py --sector Technology

# Result: Tier 3 - WEAK MARKET CONDITIONS
# Recommendation: HOLD CASH

# Try lower threshold
python console_scanner.py --sector Healthcare --min-return 8

# Result: Still Tier 3
# Action: Stay in cash, wait for better conditions
```

## Example 7: Streamlit Web Interface

**Goal:** Use visual interface for analysis

```bash
# Launch Streamlit app
streamlit run main.py

# In browser:
# 1. Select sector: "Technology"
# 2. Set min return: 15%
# 3. Click "Start Scan"
# 4. View detailed analysis with charts
# 5. Export trades directly from UI
```

## Example 8: Weekly Trading Routine

**Monday 9:00 AM - Market Open:**
```bash
# Quick scan of hottest sector
python console_scanner.py --sector Technology --min-return 15
```

**Monday 9:30 AM - Place Orders:**
- Review scan results
- Select top 1-2 trades
- Place limit orders at entry price or better
- Set stop loss orders

**Tuesday-Friday 9:00 AM - Monitor:**
```bash
# Check each position
python console_scanner.py --monitor NVDA
python console_scanner.py --monitor AMD
```

**Exit Conditions:**
- ✅ Target reached: Sell immediately
- 🛑 Stop loss hit: Sell immediately  
- ⏱️ Day 10: Sell regardless of P&L
- ⚠️ Technical signals turn bearish: Consider early exit

## Example 9: Paper Trading Practice

**Goal:** Test strategy without real money

```bash
# Week 1: Find and "paper trade" 3 positions
python console_scanner.py --sector Technology --export csv
# Record: NVDA @ $487, AMD @ $156, PLTR @ $78

# Track in spreadsheet:
# Symbol | Entry | Target | Current | P&L | Days
# NVDA   | $487  | $566   | $502    | +3% | 2
# AMD    | $156  | $180   | $158    | +1% | 2
# PLTR   | $78   | $90    | $79     | +1% | 2

# Monitor daily and record results
# After 4 weeks, calculate:
# - Win rate
# - Average return
# - Average hold time
```

## Example 10: Export and Analyze

**Goal:** Build historical database of opportunities

```bash
# Daily: Export JSON with date
DATE=$(date +%Y%m%d)
python console_scanner.py --sector Technology --export json --output "trades_$DATE"

# Creates: trades_20260203.json

# After 1 month, analyze patterns:
# - Which sectors had most Tier 1 opportunities?
# - What technical scores correlated with success?
# - Which stocks appeared multiple times?
```

## Example 11: Stop Loss Adjustment

**Goal:** Manually adjust stop based on market conditions

```bash
# Day 1: Enter NVDA @ $487, stop @ $438
# Trade going well...

# Day 5: Price at $535 (+10%)
# Manual adjustment: Move stop to $500 (breakeven)
# Now risk-free trade!

# Continue monitoring:
python console_scanner.py --monitor NVDA
```

## Example 12: Sector Rotation Strategy

**Goal:** Follow market sector rotation

```bash
# Bull market phase: Technology
python console_scanner.py --sector Technology

# Late cycle: Energy and Financials
python console_scanner.py --sector Energy
python console_scanner.py --sector Financials

# Defensive phase: Healthcare and Consumer
python console_scanner.py --sector Healthcare
python console_scanner.py --sector Consumer

# Adapt to market conditions
```

## Tips for Success

1. **Start Small:** Paper trade first, then use real money
2. **Be Selective:** Only take Tier 1 trades with 90+ scores
3. **Respect Stops:** Always exit at stop loss, no exceptions
4. **Time Limit:** Exit after 10 days regardless of P&L
5. **One at a Time:** Master one trade before adding more
6. **Keep Records:** Track every trade for learning
7. **Market Respect:** In Tier 3 conditions, hold cash
8. **No Chasing:** Don't buy above entry + 3%

## Common Mistakes to Avoid

❌ Ignoring stop losses  
❌ Trading in Tier 3 conditions  
❌ Holding past 10 days  
❌ Taking Tier 2 trades with score < 75  
❌ Over-diversifying (stick to 1-2 positions)  
❌ Revenge trading after losses  
❌ Not monitoring daily  

✅ Follow the system  
✅ Respect risk management  
✅ Take profits at targets  
✅ Learn from each trade  
✅ Stay disciplined  

Happy Trading! 📈
