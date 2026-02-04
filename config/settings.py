"""
User settings and preferences
"""

# Trading parameters
CAPITAL_PER_TRADE = 1000
PRIMARY_RETURN_TARGET = 15.0  # 15%
FALLBACK_RETURN_TARGET = 8.0  # 8%
MAX_LOSS_PERCENT = 10.0  # -10% stop loss
MAX_HOLD_DAYS = 10
MIN_RISK_REWARD_RATIO = 1.5  # Risk $100 to make $150

# Screening filters
MIN_PRICE = 5.0
MAX_PRICE = 500.0  # Allow AAPL ($270), MSFT ($410), AMD ($238), TSLA ($416)
MIN_VOLUME = 500000  # 500K shares/day
MIN_MARKET_CAP = 500000000  # $500M
MIN_VOLATILITY = 3.0  # 3% daily ATR

# Technical scoring weights
MACD_WEIGHT = 0.25
RSI_WEIGHT = 0.20
VOLUME_WEIGHT = 0.20
BREAKOUT_WEIGHT = 0.20
MOMENTUM_WEIGHT = 0.15

# Confidence thresholds
TIER_1_MIN_RETURN = 15.0
TIER_1_MIN_CONFIDENCE = 75
TIER_2_MIN_RETURN = 8.0
TIER_2_MIN_CONFIDENCE = 60

# Caching
CACHE_DURATION_HOURS = 4  # Cache stock data for 4 hours

# Day Trading Parameters
DAY_TRADE_MODE = "MONITOR"  # "MONITOR" or "EXECUTE" (when capital > $7000)
DAY_TRADE_MIN_RETURN = 1.0  # 1% minimum
DAY_TRADE_TARGET_RETURN = 2.5  # 2.5% typical target
DAY_TRADE_MAX_RETURN = 5.0  # 5% maximum realistic
DAY_TRADE_MAX_LOSS = 2.0  # -2% stop loss (tighter than swing)
DAY_TRADE_MIN_CONFIDENCE = 85  # 85% minimum confidence
DAY_TRADE_CHECK_INTERVAL = 15  # Check every 15 minutes
DAY_TRADE_FORCE_EXIT_TIME = "15:45"  # Force exit by 3:45 PM
PDT_WEEKLY_LIMIT = 3  # Pattern Day Trader limit

# Capital Management
STARTING_CAPITAL = 4000.0
CURRENT_CAPITAL = 4000.0  # Updated manually or auto-synced
PAYCHECK_AMOUNT = 100.0
PAYCHECK_FREQUENCY_DAYS = 14
NEXT_PAYCHECK_DATE = "2026-02-15"

# Milestone thresholds
ENABLE_DAY_TRADING_THRESHOLD = 7000.0  # Switch to active day trading at $7k
ENABLE_AUTO_TRADING_THRESHOLD = 10000.0  # Enable broker API at $10k
