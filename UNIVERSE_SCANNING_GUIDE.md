# Universe Scanning & O Position Management - User Guide

## Overview

This update adds three major enhancements to the stock screener:

1. **Expanded Universe Scanning** - Scan 500-1000+ stocks across multiple universes
2. **Stage-by-Stage Filtering Visualization** - See exactly how stocks are filtered at each stage
3. **O Position Buy/Sell Signal Analysis** - Smart recommendations for O (Realty Income) position

---

## 1. Universe Scanning

### Available Universes

| Universe | Stocks | Description |
|----------|--------|-------------|
| `sp500` | ~580 | S&P 500 large-cap stocks |
| `nasdaq100` | ~100 | NASDAQ 100 tech-heavy stocks |
| `high_volume` | ~590 | Most liquid stocks (>1M volume/day) |
| `all_markets` | ~780 | Combined universe, deduplicated |

### Usage

```bash
# Scan S&P 500 with 5% minimum return, 60% minimum confidence
python console_scanner.py --universe sp500 --min-return 5 --min-confidence 60

# Scan all markets with 0% minimum return (see everything)
python console_scanner.py --universe all_markets --min-return 0 --min-confidence 0

# Scan high volume stocks for aggressive opportunities (15%/80%)
python console_scanner.py --universe high_volume --min-return 15 --min-confidence 80
```

---

## 2. Stage-by-Stage Filtering

### The 10-Stage Funnel

When scanning a universe, stocks go through 10 filtering stages:

1. **Initial Load** - Fetch stock data from API
2. **Price Filter** - $5-$500 range
3. **Volume Filter** - >500K shares/day average
4. **Market Cap Filter** - >$500M market cap
5. **Volatility Filter** - >3% ATR (daily volatility)
6. **Trend Filter** - Price above 50-day moving average
7. **Technical Scoring** - Calculate MACD, RSI, Volume scores
8. **Return Estimation** - Estimate return potential
9. **Return Threshold** - Filter by minimum return %
10. **Confidence Threshold** - Filter by minimum confidence %

### Sample Output

```
📊 FILTERING BREAKDOWN
======================================================================

Universe: sp500
Total Scanned: 581 stocks
Total Time: 245.3s

----------------------------------------------------------------------

Stage 1: Initial Load
  Fetch stock data
  Input:   581 stocks
  ✅ Passed: 520 stocks (89.5%)
  ❌ Failed: 61 stocks
  Time: 120.5s

Stage 2: Price Filter
  $5 - $500
  Input:   520 stocks
  ✅ Passed: 512 stocks (98.5%)
  ❌ Failed: 8 stocks
  Time: 15.2s

... (stages 3-10) ...

Stage 10: Confidence Threshold
  Confidence > 60%
  Input:   25 stocks
  ✅ Passed: 12 stocks (48.0%)
  ❌ Failed: 13 stocks

======================================================================
```

This breakdown shows:
- How many stocks pass each filter
- Where the biggest dropoffs occur
- Time spent at each stage
- Pass rates at each stage

---

## 3. O Position Management

### Position Status

The screener automatically displays your O (Realty Income) position status:

```
💼 O POSITION STATUS
======================================================================
Shares: 69.312
Avg Cost: $55.90
Current Price: $62.47
Position Value: $4,329.92
Unrealized Gain: +11.75%
Monthly Dividend: $19.15

BUY SIGNAL: WAIT
O at $62.47 is 11.8% above your average. Wait for pullback to $52-56 
range before buying more.
======================================================================
```

### Buy Signal Zones

| Price Range | Signal | Action |
|-------------|--------|--------|
| < $53.11 (-5% from avg) | **STRONG_BUY** | Excellent opportunity - buy with next paycheck |
| $53.11 - $55.90 | **GOOD_BUY** | Reasonable price near your average |
| $55.90 - $59.81 (+7% from avg) | **HOLD** | Don't add more, hold current position |
| > $59.81 | **WAIT** | Wait for pullback to $52-56 range |

### Sell Signal Analysis (15%/80% Rule)

When swing trades are found, the screener analyzes whether you should sell O:

**Criteria:**
- Swing trade must offer **15%+ return** with **80%+ confidence**
- Net profit advantage must exceed **$100** after accounting for:
  - Lost dividend (7-day estimate)
  - Short-term capital gains tax (30%)

**Example Output:**

```
💰 SWAP ANALYSIS: O vs Swing Trade
======================================================================
✅ SELL O and enter swing trade. Net profit advantage: $725 
(after taxes and lost dividend)

Profit Breakdown:
  Swing Profit:     +$865.94
  Lost Dividend:    -$4.45
  Taxes on O:       -$135.59
  Net Advantage:    +$724.90
======================================================================
```

**Decision Logic:**
- ✅ **SELL** if net advantage > $100
- 🔴 **HOLD** if trade doesn't meet 15%/80% criteria
- 🔴 **HOLD** if net advantage too small

---

## Usage Examples

### Example 1: Daily Screening Routine

```bash
# Morning: Scan high volume universe for new opportunities
python console_scanner.py --universe high_volume --min-return 15 --min-confidence 80

# Check O position status and potential swaps
# Results automatically include O analysis
```

### Example 2: Exploring Lower-Return Opportunities

```bash
# Cast a wider net with lower thresholds
python console_scanner.py --universe all_markets --min-return 8 --min-confidence 60

# See more opportunities with stage breakdown
```

### Example 3: Aggressive High-Conviction Scan

```bash
# Only show 20%+ opportunities with 85%+ confidence
python console_scanner.py --universe sp500 --min-return 20 --min-confidence 85
```

---

## Configuration

### Adjusting O Position Parameters

Edit `console_scanner.py` to update your O position:

```python
# Current settings (as of Feb 5, 2026)
o_manager = OPositionManager(
    shares=69.312,      # Your current share count
    avg_cost=55.90      # Your average cost basis
)
```

### Universe Files

Universe files are located in `watchlists/universe/`:
- `sp500.txt`
- `nasdaq100.txt`
- `high_volume.txt`
- `all_markets.txt`

To add/remove stocks, edit these files directly. Format:
```
# Comments start with #
AAPL,MSFT,GOOGL,AMZN
META,TSLA,NFLX
```

---

## Tips & Best Practices

### When to Use Universe Scanning

1. **Daily Morning Scan** - Use `high_volume` with 15%/80% to find best opportunities
2. **Slow Market Days** - Use `all_markets` with 8%/60% to see more options
3. **Bull Market** - Use `sp500` with 20%/85% for aggressive plays
4. **Research Mode** - Use `all_markets` with 0%/0% to see entire funnel

### Understanding Stage Breakdown

- **High Stage 1 failures** → Network/API issues
- **High Stage 2 failures** → Penny stocks filtered out
- **High Stage 3 failures** → Low liquidity stocks filtered
- **High Stage 6 failures** → Market in downtrend
- **High Stage 10 failures** → Not enough high-confidence opportunities

### O Position Management Strategy

**Current Situation (Feb 5, 2026):**
- O at $62.47 (+11.75% above avg)
- Signal: WAIT
- Next paycheck: Feb 11, 2026 ($100)

**Strategy:**
1. **Wait for pullback** to $52-56 range (STRONG_BUY zone)
2. **Hold current position** - earning $19.15/month dividend
3. **Only sell O** if swing trade meets 15%/80% AND net advantage >$100
4. **Use paychecks** to buy O when in STRONG_BUY zone

---

## Troubleshooting

### No stocks found after Stage 1
→ Check internet connection or try smaller universe

### All stocks filtered at Stage 6 (Trend)
→ Market may be in downtrend, consider waiting

### O position shows wrong price
→ Fallback price ($62.47) used when API unavailable

### Stage breakdown not showing
→ Only shown for `--universe` scans, not `--sector` scans

---

## Technical Details

### Minimum Requirements
- Python 3.8+
- yfinance, pandas, pandas-ta
- Internet connection for live data

### Performance
- **sp500**: ~3-5 minutes
- **nasdaq100**: ~1-2 minutes
- **high_volume**: ~4-6 minutes
- **all_markets**: ~8-12 minutes

### API Rate Limits
- yfinance has no strict rate limits
- Recommended: Run universe scans 1-2 times per day
- Stage 1 is slowest (fetching data)

---

## Support

For issues or questions:
1. Check that universe files exist in `watchlists/universe/`
2. Verify internet connection for live data
3. Review logs for detailed error messages
4. Test with smaller watchlist first (`--watchlist` mode)
