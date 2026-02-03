# 🎯 Intelligent Swing Trading Screener

An adaptive, cost-effective stock screener optimized for $1000 swing trades with intelligent return targeting (15% → 8% → wait). Features sector-focused scanning, comprehensive technical analysis, and zero API costs.

## ✨ Key Features

- **🆓 100% FREE**: Works entirely with yfinance (no API keys required)
- **🎯 Adaptive Targeting**: Intelligently adjusts between 15% → 8% → wait modes
- **📊 Multi-Tier System**: Clear guidance on trade quality (Aggressive/Moderate/Wait)
- **⚡ Fast Scanning**: Sector-based approach scans 20-45 stocks in minutes
- **📈 Technical Analysis**: RSI, MACD, volume, breakout, and momentum scoring
- **💰 Risk Management**: Automatic stop loss, position sizing, and R:R ratios
- **💼 Position Tracking**: Monitor active trades with real-time signals
- **📤 Export Ready**: Fidelity ATP CSV format + full analysis exports
- **🖥️ Dual Interface**: Streamlit GUI + Command-line tool

## 🚀 Quick Start (5 Minutes)

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/CWitteVera/stock_screener.git
cd stock_screener

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Screener

**Option A: Web Interface (Recommended)**
```bash
streamlit run main.py
```

**Option B: Command Line**
```bash
python console_scanner.py --sector Technology
```

That's it! No API keys needed. The screener works immediately with free yfinance data.

## 📊 Usage Guide

### Web Interface (Streamlit)

1. **Launch the app:**
   ```bash
   streamlit run main.py
   ```

2. **Select a sector** (Technology, Healthcare, Energy, etc.)

3. **Set your target return** (default: 15%)

4. **Click "Start Scan"** to find opportunities

5. **Review results:**
   - 🔥 **Tier 1**: High-confidence 15%+ trades → TRADE NOW
   - ⚠️ **Tier 2**: Moderate 8-14% trades → CONSIDER
   - 🛑 **Tier 3**: Weak conditions → HOLD CASH

6. **Export trades** to Fidelity CSV or full analysis

### Command Line Interface

**Scan a sector:**
```bash
python console_scanner.py --sector Technology
python console_scanner.py --sector Healthcare --min-return 8
```

**Scan custom watchlist:**
```bash
python console_scanner.py --watchlist watchlists/custom.txt
```

**Monitor active position:**
```bash
python console_scanner.py --monitor NVDA
```

**Export results:**
```bash
python console_scanner.py --sector Technology --export fidelity
python console_scanner.py --sector Healthcare --export csv
```

## 💡 Trading Strategy

### Position Parameters
- **Capital per trade:** $1000
- **Primary target:** 15% return in 5-10 days
- **Fallback target:** 8% if no 15% opportunities
- **Stop loss:** -10% maximum loss per trade
- **Maximum hold time:** 10 days
- **Risk/Reward ratio:** Minimum 1:1.5

### Three-Tier System

#### 🔥 Tier 1 - Aggressive (15%+ potential)
```
Found 5 stocks with 15%+ return potential
Risk Level: HIGH | Confidence: 75%+
Recommendation: TRADE NOW
```

#### ⚠️ Tier 2 - Moderate (8-14% potential)
```
Found 3 stocks with 8-12% return potential
Risk Level: MEDIUM | Confidence: 60%+
Recommendation: Consider smaller positions or wait
```

#### 🛑 Tier 3 - Wait (<8% potential)
```
No stocks meet 8%+ return criteria
Recommendation: HOLD CASH - Wait for better opportunities
```

## 🔧 Technical Details

### Screening Process

**Stage 1: Pre-Filter (using yfinance)**
- Price: $5-$200
- Volume: >500K shares/day
- Market cap: >$500M
- Volatility: ATR >3%
- Trend: Not in downtrend (above 50-day MA)

**Stage 2: Technical Scoring (0-100 points each)**
- **MACD Score (25%):** Crossovers, histogram, trend
- **RSI Score (20%):** Momentum zone (45-65 optimal)
- **Volume Score (20%):** 2x average = bullish
- **Breakout Score (20%):** 20-day highs, MA positions
- **Momentum Score (15%):** 5-day returns, acceleration

**Stage 3: Return Estimation**
- Historical volatility analysis
- Technical targets (resistance levels)
- Momentum projection
- Confidence calculation

**Stage 4: Adaptive Tiering**
- Categorize into Tier 1/2/3
- Rank by overall score
- Generate trade recommendations

### Technical Indicators Calculated

All indicators are calculated from yfinance historical data:

- **RSI (14-period):** Momentum indicator
- **MACD (12,26,9):** Trend and momentum
- **Moving Averages:** 20-day and 50-day SMA
- **ATR:** Average True Range for volatility
- **Bollinger Bands:** Volatility channels
- **Volume Analysis:** Volume trends and spikes
- **Support/Resistance:** Key price levels

## 📁 Project Structure

```
stock_screener/
├── main.py                    # Streamlit GUI
├── console_scanner.py         # CLI tool
├── requirements.txt           # Dependencies
├── .env.example              # API config template
│
├── config/                   # Configuration
│   ├── api_config.py        # Data fetching (yfinance + optional FMP)
│   ├── sectors.py           # Sector definitions
│   └── settings.py          # User preferences
│
├── core/                     # Core logic
│   ├── screener.py          # Main screening engine
│   ├── technical_analysis.py # Technical indicators
│   ├── return_estimator.py  # Return potential calculator
│   ├── risk_calculator.py   # Risk management
│   └── scoring_engine.py    # Composite scoring
│
├── models/                   # Data models
│   ├── stock.py             # Stock data
│   ├── trade.py             # Trade opportunity
│   └── position.py          # Position tracking
│
├── ui/                       # User interface
│   ├── dashboard.py         # Streamlit components
│   ├── charts.py            # Plotly charts
│   └── export.py            # CSV/JSON export
│
├── utils/                    # Utilities
│   ├── cache.py             # File-based caching
│   ├── logger.py            # Logging
│   └── helpers.py           # Helper functions
│
├── watchlists/              # Sector watchlists
│   ├── technology.txt       # 43 tech stocks
│   ├── healthcare.txt       # 35 healthcare stocks
│   ├── energy.txt           # 24 energy stocks
│   ├── financials.txt       # 25 financial stocks
│   ├── consumer.txt         # 22 consumer stocks
│   ├── communications.txt   # 20 communications stocks
│   └── custom.txt           # Your custom list
│
└── data/                     # Data storage
    ├── cache/               # Cached API responses
    ├── trades/              # Trade history
    └── positions/           # Active positions
```

## 🔑 Optional API Enhancement

While the screener works 100% FREE with yfinance, you can optionally enhance it with Financial Modeling Prep:

1. **Create `.env` file:**
   ```bash
   cp .env.example .env
   ```

2. **Add your FMP API key:**
   ```
   FMP_API_KEY=your_key_here
   ```

3. **Get free key:** https://financialmodelingprep.com/developer/docs/

**What FMP adds:**
- Enhanced fundamental data
- Earnings information
- Analyst targets
- Company news

**Without FMP:** Screener still works perfectly using yfinance fundamentals.

## 📤 Export Formats

### Fidelity ATP CSV
Direct import into Fidelity Active Trader Pro:
```csv
Symbol,Action,Quantity,OrderType,Price,TimeInForce,Notes
NVDA,BUY,2,LIMIT,487.23,DAY,"Target: $566, Stop: $438"
```

### Full Analysis CSV
Complete trade data for your records:
```csv
Symbol,Entry,Target,Stop,Return%,Confidence,Score,Sector,...
NVDA,487.23,566.00,438.00,16.2,78,94,Technology,...
```

### JSON Export
Machine-readable format for custom tools:
```json
[
  {
    "symbol": "NVDA",
    "entry_price": 487.23,
    "target_price": 566.00,
    ...
  }
]
```

## 💼 Position Tracking

Track active $1000 positions with real-time monitoring:

```bash
# CLI
python console_scanner.py --monitor NVDA

# Web interface: Switch to "Monitor Position" mode
```

**Monitoring includes:**
- Current P&L and progress to target
- Technical signal updates (RSI, MACD, Volume, MA)
- Exit signals (target reached, stop hit, max time)
- Days remaining in trade

## 🎓 Example Workflow

### Day 1: Find a Trade
```bash
# Scan Technology sector
python console_scanner.py --sector Technology --export fidelity

# Results: Tier 1 - Found 5 aggressive opportunities
# Top pick: NVDA - 16% potential, 78% confidence
```

### Day 2-10: Monitor Position
```bash
# Check position daily
python console_scanner.py --monitor NVDA

# Position update:
# Entry: $487.23 | Current: $502.15 | P&L: +$29.84 (+3.0%)
# Status: HOLD - Thesis intact
```

### Day 7: Exit Signal
```
# Target reached: $566 (+16.2%)
# Profit: $157.54
# STATUS: TARGET REACHED - Exit trade ✅
```

## 📈 Sector Watchlists

Pre-built watchlists for rapid scanning:

- **Technology:** 43 stocks (AAPL, MSFT, NVDA, AMD, PLTR...)
- **Healthcare:** 35 stocks (UNH, JNJ, LLY, ABBV, TMO...)
- **Energy:** 24 stocks (XOM, CVX, COP, EOG, SLB...)
- **Financials:** 25 stocks (JPM, BAC, GS, V, MA...)
- **Consumer:** 22 stocks (AMZN, TSLA, HD, NKE, SBUX...)
- **Communications:** 20 stocks (GOOGL, META, NFLX, DIS...)

**Custom watchlists:** Edit `watchlists/custom.txt` with your own symbols.

## 🛡️ Risk Management

Built-in risk controls for every trade:

- **Automatic stop loss:** -10% maximum loss per trade
- **Position sizing:** Calculate exact shares for $1000 position
- **Risk/Reward ratio:** Minimum 1:1.5 required
- **Support-based stops:** Adjust stops based on support levels
- **Maximum hold time:** Exit after 10 days regardless
- **Profit targets:** Clear exit targets based on technical analysis

## 🔍 Scanning Performance

**Quick Scan (Single Sector):**
- Stocks: 20-45 symbols
- Time: 2-5 minutes
- API Calls: 0 FMP calls (100% yfinance)
- Cost: FREE

**Multi-Sector Scan:**
- Stocks: 60-135 symbols
- Time: 6-15 minutes
- API Calls: 0 FMP calls (100% yfinance)
- Cost: FREE

**With FMP Enhancement:**
- Additional calls: 5-50 per scan
- Enhanced data: Fundamentals, earnings, analyst targets
- Still under free tier limit (250 calls/day)

## 🤝 Contributing

Contributions welcome! This is a practical tool for swing traders.

**Areas for contribution:**
- Additional technical indicators
- More export formats
- Broker API integrations
- Machine learning return predictions
- Backtesting capabilities

## 📝 License

MIT License - Free to use for personal trading

## ⚠️ Disclaimer

This tool is for informational and educational purposes only. It does NOT constitute financial advice. All trading involves risk. Past performance does not guarantee future results. Always do your own research and consider consulting with a financial advisor.

## 🙏 Acknowledgments

- **yfinance:** Free, reliable market data
- **pandas-ta:** Technical analysis library
- **Streamlit:** Modern web UI framework
- **Plotly:** Interactive charting

---

Made with ❤️ for swing traders. Trade smart, not hard! 📈