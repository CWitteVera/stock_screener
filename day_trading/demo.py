#!/usr/bin/env python
"""
Day Trading System Demo
Shows key features and usage examples
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from day_trading.intraday_strategy import IntradayStrategy
from day_trading.day_screener import DayScreener
from day_trading.live_monitor import LiveMonitor
from models.day_trade_opportunity import DayTradeOpportunity
from config.settings import CURRENT_CAPITAL, ENABLE_DAY_TRADING_THRESHOLD

def demo_strategy():
    """Demo the intraday strategy analysis"""
    print("=" * 80)
    print("DEMO 1: Intraday Strategy Analysis")
    print("=" * 80)
    print()
    
    strategy = IntradayStrategy()
    print("Strategy Configuration:")
    print(f"  • Minimum gap: {strategy.min_gap_pct}%")
    print(f"  • Minimum volume ratio: {strategy.min_volume_ratio}x")
    print(f"  • Minimum ATR: {strategy.min_atr_pct}%")
    print()
    
    print("This strategy filters stocks for day trading by:")
    print("  1. Pre-market gap detection (>1%)")
    print("  2. Volume surge analysis (>2x average)")
    print("  3. High volatility check (ATR >5%)")
    print("  4. News catalyst scoring")
    print("  5. Technical setup quality (0-100)")
    print("  6. Momentum indicators (MACD, RSI)")
    print()

def demo_screener():
    """Demo the day screener"""
    print("=" * 80)
    print("DEMO 2: Day Trading Scanner")
    print("=" * 80)
    print()
    
    screener = DayScreener()
    print("Scanner Configuration:")
    print(f"  • Capital per trade: ${screener.capital_per_trade}")
    print(f"  • Minimum confidence: {screener.min_confidence}%")
    print()
    
    print("Morning Scan Process:")
    print("  1. 8:45 AM - Run pre-market scan")
    print("  2. Evaluate stocks across all sectors")
    print("  3. Apply filters and confidence scoring")
    print("  4. Rank by overall score")
    print("  5. Present top 5 opportunities")
    print()
    
    print("Usage:")
    print("  python day_trading/day_console.py --scan")
    print()

def demo_monitor():
    """Demo the live monitor"""
    print("=" * 80)
    print("DEMO 3: Position Monitoring")
    print("=" * 80)
    print()
    
    monitor = LiveMonitor()
    print("Monitor Configuration:")
    print(f"  • Check interval: {monitor.check_interval} minutes")
    print(f"  • Force exit time: {monitor.force_exit_time}")
    print(f"  • Data file: {os.path.basename(monitor.data_file)}")
    print()
    
    print("Monitoring Features:")
    print("  • Real-time P&L tracking")
    print("  • Automatic exit conditions:")
    print("    - 🎯 Target hit")
    print("    - 🛑 Stop loss triggered")
    print("    - ⏰ 3:45 PM force exit")
    print("  • Educational mode (< $7k capital)")
    print("  • Persistent storage in JSON")
    print()
    
    print("Usage:")
    print("  python day_trading/day_console.py --monitor AAPL")
    print("  python day_trading/day_console.py --status")
    print()

def demo_educational_mode():
    """Demo educational mode"""
    print("=" * 80)
    print("DEMO 4: Educational Mode")
    print("=" * 80)
    print()
    
    print(f"Current Capital: ${CURRENT_CAPITAL:,.2f}")
    print(f"Day Trading Threshold: ${ENABLE_DAY_TRADING_THRESHOLD:,.2f}")
    print()
    
    if CURRENT_CAPITAL < ENABLE_DAY_TRADING_THRESHOLD:
        needed = ENABLE_DAY_TRADING_THRESHOLD - CURRENT_CAPITAL
        print(f"📚 EDUCATIONAL MODE ACTIVE")
        print(f"   Need ${needed:,.2f} more to enable execution")
        print()
        print("In educational mode, you can:")
        print("  ✅ Scan for opportunities")
        print("  ✅ Monitor positions (track 'would-be' P&L)")
        print("  ✅ Learn patterns and strategies")
        print("  ✅ Build confidence without risk")
        print()
        print("Trades are NOT executed - you practice first!")
    else:
        print(f"💰 ACTIVE DAY TRADING MODE")
        print(f"   Trades can be executed (PDT rules apply)")
    print()

def demo_workflow():
    """Demo typical daily workflow"""
    print("=" * 80)
    print("DEMO 5: Typical Daily Workflow")
    print("=" * 80)
    print()
    
    print("Morning Routine (8:45 AM):")
    print("  1. Run morning scan:")
    print("     python day_trading/day_console.py --scan")
    print()
    print("  2. Review opportunities:")
    print("     - Check confidence scores (need 85%+)")
    print("     - Review catalysts (news, earnings)")
    print("     - Check setup types (GAP_UP, MOMENTUM, etc.)")
    print("     - Verify risk/reward ratios")
    print()
    print("  3. Select and monitor:")
    print("     python day_trading/day_console.py --monitor NVDA")
    print()
    
    print("\nIntraday Monitoring:")
    print("  4. Check positions every 15 minutes:")
    print("     python day_trading/day_console.py --status")
    print()
    print("  5. System automatically:")
    print("     - Tracks real-time prices")
    print("     - Calculates P&L")
    print("     - Checks exit conditions")
    print("     - Warns at 3:30 PM (15 min before force exit)")
    print()
    
    print("\nEnd of Day (3:45 PM):")
    print("  6. System force-exits all positions")
    print("  7. Review results:")
    print("     python day_trading/day_console.py --status")
    print()
    print("  8. Track what worked for tomorrow's scan")
    print()

def demo_example_opportunity():
    """Show example of what an opportunity looks like"""
    print("=" * 80)
    print("DEMO 6: Example Day Trade Opportunity")
    print("=" * 80)
    print()
    
    # Create example opportunity
    opp = DayTradeOpportunity(
        symbol="NVDA",
        name="NVIDIA Corporation",
        current_price=850.25,
        sector="Technology",
        entry_price=850.25,
        target_price=867.76,
        stop_price=833.45,
        estimated_return_pct=2.1,
        estimated_return_dollars=17.51,
        estimated_time_minutes=120,
        confidence=92,
        shares=1,
        position_value=850.25,
        premarket_gap_pct=2.3,
        premarket_volume_ratio=3.2,
        atr_pct=7.8,
        current_volume_ratio=3.2,
        setup_score=88.0,
        catalyst_score=85.0,
        momentum_score=90.0,
        overall_score=92.0,
        setup_type="MOMENTUM",
        catalyst="3 news items: NVIDIA announces new AI chip",
    )
    
    print("Example High-Confidence Opportunity:")
    print()
    print(f"  Symbol: {opp.symbol} - {opp.name}")
    print(f"  Sector: {opp.sector}")
    print()
    print(f"  Setup Type: {opp.setup_type}")
    print(f"  Confidence: {opp.confidence}%")
    print()
    print(f"  Entry: ${opp.entry_price:.2f}")
    print(f"  Target: ${opp.target_price:.2f} ({opp.estimated_return_pct:+.1f}%)")
    print(f"  Stop: ${opp.stop_price:.2f} (-{opp.max_loss_pct:.1f}%)")
    print()
    print(f"  Pre-market Gap: {opp.premarket_gap_pct:+.1f}%")
    print(f"  Volume Ratio: {opp.current_volume_ratio:.1f}x")
    print(f"  ATR: {opp.atr_pct:.1f}%")
    print()
    print(f"  Catalyst: {opp.catalyst}")
    print()
    print(f"  Position: {opp.shares} shares = ${opp.position_value:.2f}")
    print(f"  Est. Return: ${opp.estimated_return_dollars:+.2f}")
    print(f"  Max Loss: ${opp.max_loss_dollars:.2f}")
    print(f"  Risk/Reward: {opp.risk_reward_ratio:.2f}:1")
    print()
    print(f"  Scores:")
    print(f"    • Setup Quality: {opp.setup_score:.0f}/100")
    print(f"    • Momentum: {opp.momentum_score:.0f}/100")
    print(f"    • Catalyst: {opp.catalyst_score:.0f}/100")
    print(f"    • Overall: {opp.overall_score:.0f}/100")
    print()

def main():
    """Run all demos"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "DAY TRADING SYSTEM DEMO" + " " * 35 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    print("This demo shows the key features of the day trading monitoring system")
    print("for finding and tracking 1-5% intraday opportunities.")
    print()
    
    demos = [
        demo_strategy,
        demo_screener,
        demo_monitor,
        demo_educational_mode,
        demo_workflow,
        demo_example_opportunity,
    ]
    
    for demo_func in demos:
        demo_func()
        input("Press Enter to continue...")
        print("\n")
    
    print("=" * 80)
    print("DEMO COMPLETE")
    print("=" * 80)
    print()
    print("Ready to start? Run:")
    print("  python day_trading/day_console.py --scan")
    print()
    print("Or read the documentation:")
    print("  cat day_trading/README.md")
    print()

if __name__ == "__main__":
    main()
