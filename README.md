# 🎯 Intelligent Trading System

A comprehensive, dual-mode trading platform combining swing trading (15%+ returns, 5-10 days) with day trading monitoring (1-5% intraday). Features adaptive return targeting, complete trade tracking with performance metrics, capital progression monitoring, and smart watchlist management - all with zero API costs.

## ✨ Key Features

### Core Trading
- **🆓 100% FREE**: Works entirely with yfinance (no API keys required)
- **🎯 Adaptive Targeting**: Intelligently adjusts between 15% → 8% → wait modes
- **📊 Multi-Tier System**: Clear guidance on trade quality (Aggressive/Moderate/Wait)
- **⚡ Fast Scanning**: Sector-based approach scans 20-45 stocks in minutes
- **📈 Technical Analysis**: RSI, MACD, volume, breakout, and momentum scoring
- **💰 Risk Management**: Automatic stop loss, position sizing, and R:R ratios
- **💼 Position Tracking**: Monitor active trades with real-time signals
- **📤 Export Ready**: Fidelity ATP CSV format + full analysis exports
- **🖥️ Dual Interface**: Streamlit GUI + Command-line tool

### Day Trading Monitor
- **⚡ Intraday Scanning**: 1-5% same-day return targets
- **🎯 High Confidence**: 85%+ confidence threshold for day trades
- **⏰ Time-Aware**: Automatic exit signals by 3:45 PM
- **🔒 PDT Protection**: Track weekly limits (3 trades/week under $25k)
- **👀 Monitor Mode**: Paper trade until $7k capital threshold

### Trading Ledger & Performance
- **📚 Complete History**: Track every trade with entry, exit, and performance
- **🎯 Accuracy Metrics**: Measure prediction accuracy, confidence calibration, ROI accuracy
- **📊 Performance Stats**: Win rate, total return, average per trade
- **📤 Export Everything**: CSV, JSON formats for external analysis
- **🔍 Trade Attribution**: Compare predicted vs. actual returns

### Capital Management
- **💵 Account Tracking**: Monitor capital progression from $4k → $7k → $10k
- **📈 Goal Projections**: Time-to-goal estimates (current pace, best case, conservative)
- **💰 Paycheck Integration**: Track biweekly deposits and compound growth
- **🎚️ Milestone Unlocks**: Day trading at $7k, auto-trading at $10k
- **📊 Visual Progress**: Real-time progress bars and metrics

### Smart Watchlist
- **🤖 Auto-Population**: Automatically adds stocks showing early momentum
- **📊 Momentum Tracking**: Track score, return, and confidence trends over time
- **🔔 Alert System**: Notifications when stocks reach trade criteria
- **📈 Trend Analysis**: Identify improving, declining, or stable stocks
- **⏰ Days-to-Ready**: Estimate when stocks will meet buy criteria

### Enhanced UI
- **📱 Dual Dashboard**: View swing and day trades side-by-side
- **📑 Multi-Tab Interface**: Opportunities, Positions, Ledger, Debug
- **🎨 Capital Sidebar**: Live capital tracking and progress indicators
- **🔄 Mode Switching**: Toggle between swing and day trading modes
- **🔧 Debug Tools**: Filtering pipeline analysis and stock analyzer

## 📑 Table of Contents

- [Quick Start](#-quick-start-5-minutes) - Get running in 5 minutes
- [Feature Guides](#-feature-guides) - Day Trading, Ledger, Capital, Watchlist, UI
- [Usage Guide](#-usage-guide) - Web and CLI interfaces
- [Trading Strategy](#-trading-strategy) - Swing, day trading, capital progression
- [Technical Details](#-technical-details) - Screening process and indicators
- [Project Structure](#-project-structure) - Directory and file organization
- [API Enhancement](#-optional-api-enhancement) - Optional FMP integration
- [Export Formats](#-export-formats) - Fidelity, CSV, JSON
- [Position Tracking](#-position-tracking) - Monitor active trades
- [Example Workflows](#-example-workflows) - 5 complete workflow examples
- [Sector Watchlists](#-sector-watchlists) - Pre-built sector lists
- [Risk Management](#-risk-management) - Built-in risk controls
- [Configuration](#%EF%B8%8F-configuration) - All configurable settings
- [Scanning Performance](#-scanning-performance) - Speed and cost metrics
- [Contributing](#-contributing) - How to contribute
- [Additional Docs](#-additional-documentation) - Link to all documentation

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
# Swing trading scan
python console_scanner.py --sector Technology

# Day trading monitor
python day_trading/day_console.py --watch AAPL MSFT NVDA

# View trading ledger
python ledger/ledger_console.py --view

# Manage watchlist
python core/watchlist_console.py --update
```

That's it! No API keys needed. The screener works immediately with free yfinance data.

## 🚀 Feature Guides

### ⚡ Day Trading Monitor

The day trading monitor identifies high-confidence intraday opportunities with 1-5% return potential within market hours.

**Key Features:**
- 1-5% same-day return targets
- 85%+ confidence threshold
- Automatic exit signals by 3:45 PM
- PDT-aware (tracks 3 trades/week limit)
- Two modes: MONITOR (< $7k capital) and EXECUTE (≥ $7k capital)

**CLI Usage:**
```bash
# Watch specific stocks for intraday setups
python day_trading/day_console.py --watch AAPL MSFT NVDA AMD

# Scan sector for day trade opportunities
python day_trading/day_console.py --scan Technology

# Live monitoring (updates every 15 min)
python day_trading/live_monitor.py --symbols AAPL,MSFT,NVDA
```

**Parameters:**
- **Minimum Return:** 1.0% (configurable)
- **Target Return:** 2.5% typical
- **Max Loss:** -2.0% (tighter than swing)
- **Min Confidence:** 85%
- **Force Exit:** 3:45 PM ET

**Example Output:**
```
⚡ DAY TRADE OPPORTUNITIES - 2025-02-10

🥇 NVDA - NVIDIA Corp | Score: 88
   Entry: $487.50 → Target: $502.50 (+3.1%)
   Stop: $477.63 (-2.0%) | R:R 1.5:1
   Confidence: 87% | Entry: NOW (9:45 AM)
   Exit By: 3:45 PM | Mode: MONITOR ONLY
```

### 📚 Trading Ledger

Track every trade with complete performance analytics and accuracy metrics.

**Features:**
- Complete trade history (entry, exit, P&L)
- Prediction accuracy tracking
- Confidence calibration metrics
- Win rate and return statistics
- Export to CSV/JSON

**CLI Usage:**
```bash
# View complete ledger
python ledger/ledger_console.py --view

# View performance metrics
python ledger/ledger_console.py --metrics

# Log a new trade
python ledger/ledger_console.py --add \
  --type swing \
  --symbol NVDA \
  --entry 487.50 \
  --target 566.00 \
  --stop 438.75 \
  --predicted-return 16.2 \
  --confidence 78

# Update trade with exit
python ledger/ledger_console.py --exit \
  --symbol NVDA \
  --exit-price 552.00 \
  --reason "Target nearly reached"

# Export ledger
python ledger/ledger_console.py --export csv
python ledger/ledger_console.py --export json
```

**Performance Metrics:**
- **Win Rate:** Percentage of profitable trades
- **Prediction Accuracy:** How often predictions matched reality
- **Confidence Calibration:** How well confidence scores predict success
- **ROI Accuracy:** How close actual returns match predictions
- **Average Return:** Mean return per trade

**Example Output:**
```
📚 TRADING LEDGER

📊 PERFORMANCE METRICS
Total Trades:  25
Win Rate:      68.0%
Total Return:  +$2,450 (+61.3%)
Avg/Trade:     +$98 (+2.5%)

🎯 ACCURACY METRICS
Prediction Accuracy:    72.0%
Confidence Calibration: 78.5%
ROI Accuracy:           85.2%

RECENT TRADES
Date       Type   Symbol  Entry    Exit     P&L      Predicted  Actual
----------------------------------------------------------------------
2025-02-08 Swing  NVDA    $487.50  $552.00  +$129    +16.2%     +13.2%
2025-02-05 Day    AAPL    $182.50  $187.25  +$26     +2.6%      +2.6%
2025-02-03 Swing  AMD     $147.00  $142.50  -$91     +15.0%     -3.1%
```

### 💵 Capital Management

Track your capital progression from starting balance through milestone thresholds with automated projections.

**Features:**
- Real-time capital tracking
- Progress to milestone goals ($7k, $10k)
- Paycheck integration
- Time-to-goal projections (3 scenarios)
- Visual progress indicators

**Milestones:**
- **$4,000:** Starting capital (swing trading only)
- **$7,000:** Enable day trading (PDT threshold)
- **$10,000:** Enable automated trading
- **$25,000:** Unlimited day trading

**CLI Usage:**
```bash
# View capital status
python -c "from models.capital_account import CapitalAccount; \
  ca = CapitalAccount(); ca.load(); print(ca.summary())"

# Add paycheck
python -c "from models.capital_account import CapitalAccount; \
  ca = CapitalAccount(); ca.load(); \
  ca.add_paycheck(100); ca.save()"

# Update capital after trade
python -c "from models.capital_account import CapitalAccount; \
  ca = CapitalAccount(); ca.load(); \
  ca.record_trade_profit(129); ca.save()"
```

**Example Display (Streamlit Sidebar):**
```
💵 CAPITAL ACCOUNT

Current Capital: $5,240
Progress to $7k: ▓▓▓▓▓▓▓▓░░ 75%

📊 Trading Stats
Total Trades:  18
Win Rate:      72%
Total Profit:  +$1,240
Return:        +31.0%

⏰ Time to $7k Goal
Current Pace:   45 days
Best Case:      28 days
Conservative:   68 days

💰 Next Paycheck: $100 in 6 days
```

### 🎯 Smart Watchlist

Automatically track stocks showing early momentum signals before they reach full buy criteria.

**Auto-Add Criteria (2+ signals):**
1. Score improving (60-79 range)
2. Near threshold (10-14% return OR 70-79% confidence)
3. MACD crossover (last 3 days)
4. RSI momentum (45-65 zone)
5. Volume surge (3+ days increasing)

**Alert Triggers:**
- Return ≥ 15% AND Confidence ≥ 80%

**CLI Usage:**
```bash
# View watchlist
python core/watchlist_console.py --view

# Add stock manually
python core/watchlist_console.py --add AAPL --notes "Breakout setup"

# Update all stocks
python core/watchlist_console.py --update

# Check alerts (ready to trade)
python core/watchlist_console.py --alerts

# View trending stocks
python core/watchlist_console.py --trending

# Auto-scan for candidates
python core/watchlist_console.py --auto-scan AAPL MSFT GOOGL NVDA
```

**Example Output:**
```
📋 SMART WATCHLIST

Symbol  Days  Reason           Score  Return  Conf   Trend         Days to  Alert
                                                                   Criteria
--------------------------------------------------------------------------------
AAPL    5     NEAR_THRESHOLD   72.0   13.0%   75%    📈 IMPROVING  7        
MSFT    3     MACD_CROSSOVER   68.0   11.5%   72%    ➡️ STABLE     -        
GOOGL   8     IMPROVING_TREND  85.0   16.0%   82%    📈 IMPROVING  0        🔔
NVDA    2     VOLUME_SURGE     74.0   12.5%   76%    📈 IMPROVING  5        

Total: 4 | Improving: 3 | Declining: 0 | Stable: 1 | Alerts: 1
```

### 🖥️ Enhanced Dashboard UI

The Streamlit interface features a comprehensive dual-mode dashboard with capital tracking and complete trade management.

**Sidebar:**
- **Capital Account:** Real-time balance, progress bars, stats
- **Trading Mode:** Toggle swing/day trading, execution controls
- **Configuration:** Sector selection, return targets, risk settings

**Main Tabs:**

#### 📊 Today's Opportunities (Dual Dashboard)
Split-screen view showing both trading modes:

**Left Column - Swing Trades:**
- Top 5 swing opportunities
- 15%+ return targets, 5-10 day holds
- Full technical analysis and risk metrics

**Right Column - Day Trades:**
- Top 5 intraday setups
- 1-5% same-day targets
- Mode indicator (MONITOR/EXECUTE)
- Time-to-exit countdown

#### 💼 Active Positions
- Monitor open positions
- Real-time P&L and progress
- Exit signals and recommendations
- Technical indicator updates

#### 📚 Trading Ledger
- Complete trade history table
- Performance and accuracy metrics
- Win rate, returns, prediction accuracy
- Export to CSV/JSON

#### 🔧 Debug & Analysis
- Filtering pipeline visualization
- Rejection reason breakdown
- Individual stock analyzer
- Technical score details

**Usage:**
```bash
# Launch enhanced dashboard
streamlit run main.py

# Navigate using tabs at top
# Toggle modes in sidebar
# View capital progress in sidebar
# Export data from each tab
```

## 📊 Usage Guide

### Web Interface (Streamlit)

1. **Launch the app:**
   ```bash
   streamlit run main.py
   ```

2. **Configure trading modes in sidebar:**
   - ✅ Enable **📊 Swing Trading** (15%+ returns)
   - ✅ Enable **⚡ Day Trade Monitor** (1-5% intraday)
   - ⚠️ **🔴 Execute Day Trades** (unlocked at $7k capital)

3. **Select a sector** (Technology, Healthcare, Energy, etc.)

4. **Set your target return** (default: 15%)

5. **Click "Start Scan"** to find opportunities

6. **Review results in dual dashboard:**
   - 🔥 **Left Column**: Swing trades (5-10 days)
   - ⚡ **Right Column**: Day trades (same-day)
   
7. **Switch tabs for additional features:**
   - **💼 Active Positions**: Monitor open trades
   - **📚 Trading Ledger**: View performance and history
   - **🔧 Debug**: Analyze filtering and individual stocks

8. **Export trades** to Fidelity CSV or full analysis

9. **Track capital progress** in sidebar

### Command Line Interface

**Swing Trading:**
```bash
# Scan specific sector
python console_scanner.py --sector Technology

# Scan with lower 8% threshold
python console_scanner.py --sector Healthcare --min-return 8

# Scan custom watchlist
python console_scanner.py --watchlist watchlists/custom.txt

# Monitor active position
python console_scanner.py --monitor NVDA

# Export results
python console_scanner.py --sector Technology --export fidelity
python console_scanner.py --sector Healthcare --export csv
```

**Day Trading:**
```bash
# Watch specific stocks
python day_trading/day_console.py --watch AAPL MSFT NVDA

# Scan sector for day trades
python day_trading/day_console.py --scan Technology

# Live monitoring (auto-refresh)
python day_trading/live_monitor.py --symbols AAPL,MSFT,NVDA

# Check PDT status
python day_trading/day_console.py --pdt-status
```

**Trading Ledger:**
```bash
# View complete ledger
python ledger/ledger_console.py --view

# View performance metrics only
python ledger/ledger_console.py --metrics

# Log new trade
python ledger/ledger_console.py --add --type swing --symbol NVDA \
  --entry 487.50 --target 566.00 --stop 438.75 \
  --predicted-return 16.2 --confidence 78

# Update with exit
python ledger/ledger_console.py --exit --symbol NVDA \
  --exit-price 552.00 --reason "Target reached"

# Export ledger
python ledger/ledger_console.py --export csv
```

**Smart Watchlist:**
```bash
# View watchlist
python core/watchlist_console.py --view

# Update all stocks
python core/watchlist_console.py --update

# Check alerts
python core/watchlist_console.py --alerts

# View trending
python core/watchlist_console.py --trending

# Add stock manually
python core/watchlist_console.py --add AAPL --notes "Breakout setup"

# Auto-scan for candidates
python core/watchlist_console.py --auto-scan AAPL MSFT GOOGL NVDA
```

## 💡 Trading Strategy

### Swing Trading Parameters
- **Capital per trade:** $1000
- **Primary target:** 15% return in 5-10 days
- **Fallback target:** 8% if no 15% opportunities
- **Stop loss:** -10% maximum loss per trade
- **Maximum hold time:** 10 days
- **Risk/Reward ratio:** Minimum 1:1.5

### Day Trading Parameters
- **Capital per trade:** $1000
- **Target range:** 1-5% same-day return
- **Minimum confidence:** 85%
- **Stop loss:** -2% maximum (tighter than swing)
- **Force exit:** 3:45 PM ET (15 min before close)
- **PDT limit:** 3 trades/week (under $25k account)
- **Mode:** MONITOR (< $7k) or EXECUTE (≥ $7k)

### Three-Tier System (Swing Trading)

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

### Capital Progression Strategy

**Phase 1: $4,000 - $7,000 (Swing Trading Only)**
- Focus on 15%+ swing trades
- Monitor day trades (no execution)
- Add $100 biweekly paychecks
- Target: Reach $7k for day trading

**Phase 2: $7,000 - $10,000 (Swing + Day Trading)**
- Continue swing trading as primary
- Execute up to 3 day trades/week
- Combine strategies for faster growth
- Target: Reach $10k for automation

**Phase 3: $10,000 - $25,000 (Advanced)**
- Full swing + day trading access
- Consider broker API integration
- Advanced position sizing
- Target: $25k for unlimited day trading

**Phase 4: $25,000+ (Professional)**
- Unlimited day trading
- Portfolio diversification
- Scale position sizes
- Consider options strategies

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
├── main.py                    # Streamlit GUI with dual dashboard
├── console_scanner.py         # CLI tool for swing trading
├── requirements.txt           # Dependencies
├── .env.example              # API config template
│
├── config/                   # Configuration
│   ├── api_config.py        # Data fetching (yfinance + optional FMP)
│   ├── sectors.py           # Sector definitions
│   └── settings.py          # User preferences (swing + day trading settings)
│
├── core/                     # Core logic
│   ├── screener.py          # Main screening engine
│   ├── technical_analysis.py # Technical indicators
│   ├── return_estimator.py  # Return potential calculator
│   ├── risk_calculator.py   # Risk management
│   ├── scoring_engine.py    # Composite scoring
│   ├── watchlist_manager.py # Smart watchlist system
│   ├── auto_watchlist.py    # Auto-population logic
│   └── watchlist_console.py # Watchlist CLI tool
│
├── models/                   # Data models
│   ├── stock.py             # Stock data
│   ├── trade.py             # Trade opportunity
│   ├── position.py          # Position tracking
│   ├── ledger_entry.py      # Ledger trade entry
│   ├── capital_account.py   # Capital tracking and milestones
│   ├── day_trade_opportunity.py  # Intraday opportunity
│   └── watchlist_stock.py   # Watchlist item with momentum tracking
│
├── day_trading/             # Day trading system
│   ├── day_screener.py      # Intraday screener
│   ├── day_console.py       # Day trading CLI
│   ├── live_monitor.py      # Real-time monitoring
│   ├── intraday_strategy.py # Day trading strategy logic
│   └── README.md            # Day trading documentation
│
├── ledger/                   # Trading ledger system
│   ├── trading_ledger.py    # Ledger management
│   ├── ledger_console.py    # Ledger CLI tool
│   ├── accuracy_calculator.py # Prediction accuracy metrics
│   ├── performance_metrics.py # Win rate, returns, stats
│   ├── reports.py           # Report generation
│   └── README.md            # Ledger documentation
│
├── ui/                       # User interface
│   ├── dashboard.py         # Streamlit components
│   ├── enhanced_dashboard.py # Dual-mode dashboard
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
    ├── positions/           # Active positions
    ├── ledger/              # Trading ledger JSON
    ├── watchlist/           # Smart watchlist data
    └── capital/             # Capital account data
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

## 🎓 Example Workflows

### Workflow 1: New Trader (Starting with $4,000)

**Day 1: Initial Setup**
```bash
# Launch dashboard
streamlit run main.py

# Enable swing trading mode only
# Capital: $4,000 (day trading locked)
# Select Technology sector
# Start scan
```

**Day 1: Execute First Trade**
```bash
# Export top swing trade to Fidelity
python console_scanner.py --sector Technology --export fidelity

# Results: NVDA - 16% potential, 78% confidence
# Import fidelity_trades.csv into Fidelity ATP
# Execute: Buy 2 shares @ $487.23

# Log trade in ledger
python ledger/ledger_console.py --add \
  --type swing --symbol NVDA \
  --entry 487.50 --target 566.00 --stop 438.75 \
  --predicted-return 16.2 --confidence 78
```

**Days 2-7: Monitor Position**
```bash
# Daily monitoring
python console_scanner.py --monitor NVDA

# Position update:
# Entry: $487.23 | Current: $502.15 | P&L: +$29.84 (+3.0%)
# Status: HOLD - Thesis intact
# Technical signals: All green
```

**Day 7: Exit Trade**
```bash
# Target reached: $552 (+13.2%)
# Profit: $129.54

# Log exit in ledger
python ledger/ledger_console.py --exit \
  --symbol NVDA --exit-price 552.00 \
  --reason "Target nearly reached"

# New capital: $4,129.54
```

**Day 8: Review Performance**
```bash
# Check ledger stats
python ledger/ledger_console.py --metrics

# Stats: 1 trade, 100% win rate, +$129 profit
# Prediction accuracy: 81% (predicted 16.2%, actual 13.2%)
```

### Workflow 2: Day Trading Monitor (Capital < $7k)

**Morning Routine**
```bash
# Check swing opportunities
python console_scanner.py --sector Technology

# Monitor day trade setups (no execution)
python day_trading/day_console.py --watch AAPL MSFT NVDA AMD

# Check watchlist alerts
python core/watchlist_console.py --alerts
```

**9:30 AM - Market Open**
```bash
# Review day trade opportunities
# AAPL: 2.8% intraday potential, 88% confidence
# Mode: MONITOR ONLY (capital $5,200 < $7k)

# Log the opportunity for practice tracking
python ledger/ledger_console.py --add \
  --type day --symbol AAPL \
  --entry 182.50 --target 187.61 --stop 178.85 \
  --predicted-return 2.8 --confidence 88 \
  --executed false
```

**Track Throughout Day**
```bash
# Check progress at noon
python day_trading/day_console.py --watch AAPL

# AAPL moved to $187.25 (+2.6%)
# Virtual profit: +$26 (if executed)
```

**End of Day**
```bash
# Log hypothetical result
python ledger/ledger_console.py --exit \
  --symbol AAPL --exit-price 187.25 \
  --reason "Paper trade tracking"

# Accuracy: 93% (predicted 2.8%, actual 2.6%)
# Build confidence for real day trading at $7k
```

### Workflow 3: Dual Trading Mode (Capital ≥ $7k)

**Morning: Scan Both Modes**
```bash
streamlit run main.py

# Enable both modes in sidebar:
# ✅ Swing Trading
# ✅ Day Trade Monitor  
# ✅ Execute Day Trades (unlocked!)

# Dual dashboard shows:
# Left: 5 swing trades (15%+ returns)
# Right: 5 day trades (2-5% intraday)
```

**Execute Swing Trade**
```bash
# Swing: MSFT - 17% potential, 5-10 day hold
python console_scanner.py --monitor MSFT --export fidelity

# Log in ledger
python ledger/ledger_console.py --add \
  --type swing --symbol MSFT --entry 410.00 \
  --target 479.70 --stop 369.00 \
  --predicted-return 17.0 --confidence 81
```

**Execute Day Trade (1 of 3 this week)**
```bash
# Day: NVDA - 3.2% intraday, 89% confidence
python day_trading/day_console.py --watch NVDA

# Execute at market open
# Entry: $487.50, Target: $503.09, Stop: $477.63

# Log in ledger
python ledger/ledger_console.py --add \
  --type day --symbol NVDA --entry 487.50 \
  --target 503.09 --stop 477.63 \
  --predicted-return 3.2 --confidence 89
```

**3:00 PM: Monitor Day Trade**
```bash
# NVDA at $500.50 (+2.7%)
# Close to target, take profit now or wait until 3:45 PM

# Exit at $500.50
python ledger/ledger_console.py --exit \
  --symbol NVDA --exit-price 500.50 \
  --reason "3:00 PM exit, near target"

# Profit: +$26 (+2.7%)
# 1 of 3 day trades used this week
```

**End of Week: Review**
```bash
# View complete performance
python ledger/ledger_console.py --view

# Weekly stats:
# Swing: 2 trades, $287 profit
# Day: 3 trades, $74 profit
# Total: +$361 (+5.2% weekly)
# New capital: $7,361
```

### Workflow 4: Smart Watchlist Integration

**Morning: Update Watchlist**
```bash
# Update all tracked stocks
python core/watchlist_console.py --update

# Check for alerts
python core/watchlist_console.py --alerts

# Alert: GOOGL now 16% potential, 82% confidence
# Days on watchlist: 8
# Status: READY TO TRADE 🔔
```

**Add to Watchlist from Scan**
```bash
# Scan Technology sector
python console_scanner.py --sector Technology

# Results show AAPL at 13% (not quite 15%)
# Auto-add to watchlist for tracking

python core/watchlist_console.py --add AAPL \
  --notes "Near threshold, MACD crossover"
```

**Daily Tracking**
```bash
# View trending stocks
python core/watchlist_console.py --trending

# AAPL: 📈 IMPROVING (5 days)
# Score: 68 → 72 → 76 (rising)
# Return: 11% → 12% → 13.5% (rising)
# Estimated days to criteria: 3-4 days
```

**Execute When Ready**
```bash
# Day 4: AAPL reaches 15.2% / 80% confidence
python core/watchlist_console.py --alerts

# Alert triggered! Execute trade
python console_scanner.py --monitor AAPL --export fidelity

# Remove from watchlist (now in active positions)
python core/watchlist_console.py --remove AAPL
```

### Workflow 5: Complete Daily Routine

**Pre-Market (8:00 AM)**
```bash
# Update capital account (paycheck day?)
# Check: Next paycheck in 0 days!

# Launch dashboard
streamlit run main.py

# Add paycheck in sidebar: $100
# New capital: $7,461 → $7,561
```

**Market Open (9:30 AM)**
```bash
# Update watchlist
python core/watchlist_console.py --update

# Check alerts
python core/watchlist_console.py --alerts
# Alert: 2 stocks ready

# Scan for new opportunities
python console_scanner.py --sector Technology --export fidelity
python day_trading/day_console.py --scan Technology

# Select best opportunities
# Swing: 1 trade (MSFT)
# Day: 1 trade if strong setup
```

**Mid-Day (12:00 PM)**
```bash
# Monitor active positions
python console_scanner.py --monitor MSFT  # Swing position
python day_trading/day_console.py --watch NVDA  # Day trade
```

**End of Day (3:45 PM)**
```bash
# Force exit day trades (if any open)
# Update ledger with exits
python ledger/ledger_console.py --exit --symbol NVDA \
  --exit-price 501.50 --reason "EOD forced exit"

# View daily performance
python ledger/ledger_console.py --metrics
```

**After Market (5:00 PM)**
```bash
# Export ledger for records
python ledger/ledger_console.py --export csv

# Review capital progress
# Check time to next milestone
# Plan tomorrow's scans
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

## ⚙️ Configuration

All settings are configured in `config/settings.py`. Key parameters:

### Swing Trading Settings
```python
# Trading parameters
CAPITAL_PER_TRADE = 1000           # $1000 per position
PRIMARY_RETURN_TARGET = 15.0       # 15% primary target
FALLBACK_RETURN_TARGET = 8.0       # 8% fallback target
MAX_LOSS_PERCENT = 10.0            # -10% stop loss
MAX_HOLD_DAYS = 10                 # Maximum hold time
MIN_RISK_REWARD_RATIO = 1.5        # Minimum 1.5:1 R:R

# Screening filters
MIN_PRICE = 5.0                    # Minimum stock price
MAX_PRICE = 500.0                  # Maximum price (allows AAPL, MSFT, etc.)
MIN_VOLUME = 500000                # 500K shares/day minimum
MIN_MARKET_CAP = 500000000         # $500M minimum market cap
MIN_VOLATILITY = 3.0               # 3% minimum daily ATR

# Confidence thresholds
TIER_1_MIN_RETURN = 15.0           # Tier 1: 15%+ return
TIER_1_MIN_CONFIDENCE = 75         # Tier 1: 75%+ confidence
TIER_2_MIN_RETURN = 8.0            # Tier 2: 8%+ return
TIER_2_MIN_CONFIDENCE = 60         # Tier 2: 60%+ confidence
```

### Day Trading Settings
```python
# Day trading parameters
DAY_TRADE_MODE = "MONITOR"         # "MONITOR" or "EXECUTE"
DAY_TRADE_MIN_RETURN = 1.0         # 1% minimum return
DAY_TRADE_TARGET_RETURN = 2.5      # 2.5% typical target
DAY_TRADE_MAX_RETURN = 5.0         # 5% maximum realistic
DAY_TRADE_MAX_LOSS = 2.0           # -2% stop loss (tighter)
DAY_TRADE_MIN_CONFIDENCE = 85      # 85% minimum confidence
DAY_TRADE_CHECK_INTERVAL = 15      # Check every 15 minutes
DAY_TRADE_FORCE_EXIT_TIME = "15:45"  # Force exit by 3:45 PM
PDT_WEEKLY_LIMIT = 3               # Pattern Day Trader limit (< $25k)
```

### Capital Management Settings
```python
# Capital tracking
STARTING_CAPITAL = 4000.0          # Initial capital
CURRENT_CAPITAL = 4000.0           # Current balance (auto-updated)
PAYCHECK_AMOUNT = 100.0            # Biweekly deposit amount
PAYCHECK_FREQUENCY_DAYS = 14       # Every 2 weeks
NEXT_PAYCHECK_DATE = "2026-02-15"  # Next deposit date

# Milestone thresholds
ENABLE_DAY_TRADING_THRESHOLD = 7000.0    # Unlock day trading at $7k
ENABLE_AUTO_TRADING_THRESHOLD = 10000.0  # Unlock automation at $10k
```

### Technical Scoring Weights
```python
# Indicator weights (must sum to 1.0)
MACD_WEIGHT = 0.25       # 25% - Trend and momentum
RSI_WEIGHT = 0.20        # 20% - Momentum zone
VOLUME_WEIGHT = 0.20     # 20% - Volume confirmation
BREAKOUT_WEIGHT = 0.20   # 20% - Breakout signals
MOMENTUM_WEIGHT = 0.15   # 15% - Price momentum
```

### Caching Settings
```python
CACHE_DURATION_HOURS = 4  # Cache stock data for 4 hours
```

### Customization Examples

**Lower the entry barrier for more opportunities:**
```python
TIER_1_MIN_RETURN = 12.0      # Accept 12%+ instead of 15%
TIER_1_MIN_CONFIDENCE = 70    # Accept 70%+ instead of 75%
```

**Tighter risk management:**
```python
MAX_LOSS_PERCENT = 7.0        # Reduce stop loss to -7%
MIN_RISK_REWARD_RATIO = 2.0   # Require 2:1 R:R ratio
```

**Enable higher-priced stocks:**
```python
MAX_PRICE = 1000.0            # Allow stocks up to $1000
```

**More aggressive day trading:**
```python
DAY_TRADE_MAX_LOSS = 3.0      # Allow -3% day trade stops
DAY_TRADE_MIN_CONFIDENCE = 80 # Accept 80%+ confidence
```

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

Contributions welcome! This is a comprehensive trading platform with multiple systems.

**Areas for contribution:**
- Additional technical indicators
- More export formats (TradingView, ThinkorSwim, etc.)
- Broker API integrations (Alpaca, Interactive Brokers, etc.)
- Machine learning return predictions
- Backtesting capabilities
- Real-time alert system (SMS, email, push notifications)
- Mobile app or responsive web design
- Advanced charting and pattern recognition
- Options strategy screening
- Portfolio optimization algorithms
- Tax reporting and P&L exports

## 📝 License

MIT License - Free to use for personal trading

## ⚠️ Disclaimer

This tool is for informational and educational purposes only. It does NOT constitute financial advice. All trading involves risk. Past performance does not guarantee future results. Always do your own research and consider consulting with a financial advisor.

## 🙏 Acknowledgments

- **yfinance:** Free, reliable market data
- **pandas-ta:** Technical analysis library
- **Streamlit:** Modern web UI framework
- **Plotly:** Interactive charting
- **Python community:** For excellent financial libraries

---

## 📚 Additional Documentation

- **[QUICK_START.md](QUICK_START.md)** - 60-second quick start guide
- **[EXAMPLES.md](EXAMPLES.md)** - 12 detailed usage scenarios
- **[FEATURES.md](FEATURES.md)** - Complete feature checklist
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Deployment and hosting guide
- **[UI_ENHANCEMENTS.md](UI_ENHANCEMENTS.md)** - Dual dashboard documentation
- **[WATCHLIST_QUICKSTART.md](WATCHLIST_QUICKSTART.md)** - Smart watchlist guide
- **[day_trading/README.md](day_trading/README.md)** - Day trading system docs
- **[ledger/README.md](ledger/README.md)** - Trading ledger documentation

---

Made with ❤️ for active traders. Trade smart, not hard! 📈💰

**Current Status:** Feature-complete dual-mode trading platform with 150+ implemented features.