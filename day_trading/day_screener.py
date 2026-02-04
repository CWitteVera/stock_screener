"""
Morning pre-market scanner for day trade opportunities (8:45 AM)
"""

import yfinance as yf
from datetime import datetime, time
from typing import List, Optional
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.day_trade_opportunity import DayTradeOpportunity
from config.settings import (
    DAY_TRADE_MIN_RETURN,
    DAY_TRADE_TARGET_RETURN,
    DAY_TRADE_MAX_RETURN,
    DAY_TRADE_MAX_LOSS,
    DAY_TRADE_MIN_CONFIDENCE,
    CAPITAL_PER_TRADE,
    MIN_PRICE,
    MAX_PRICE,
)
from config.sectors import SECTOR_TICKERS
from day_trading.intraday_strategy import IntradayStrategy


class DayScreener:
    """
    Morning pre-market scan for high-confidence day trading opportunities
    Target: 1-5% intraday moves with 85%+ confidence
    """
    
    def __init__(self, capital_per_trade: float = CAPITAL_PER_TRADE):
        self.capital_per_trade = capital_per_trade
        self.strategy = IntradayStrategy()
        self.min_confidence = DAY_TRADE_MIN_CONFIDENCE
        
    def scan_all_sectors(self) -> List[DayTradeOpportunity]:
        """
        Scan all sectors for day trade setups
        Returns ranked list of high-confidence opportunities
        """
        print("=" * 80)
        print("DAY TRADING MORNING SCAN - Pre-Market Analysis")
        print(f"Scan time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Minimum confidence: {self.min_confidence}%")
        print("=" * 80)
        print()
        
        opportunities = []
        
        # Scan each sector
        for sector_name, tickers in SECTOR_TICKERS.items():
            print(f"\n📊 Scanning {sector_name}...")
            print("-" * 60)
            
            for symbol in tickers:
                try:
                    opp = self.analyze_stock(symbol, sector_name)
                    if opp and opp.is_high_confidence(self.min_confidence):
                        opportunities.append(opp)
                        self._print_opportunity(opp)
                except Exception as e:
                    print(f"  ❌ {symbol}: Error - {str(e)[:50]}")
        
        # Sort by overall score
        opportunities.sort(key=lambda x: x.overall_score, reverse=True)
        
        print("\n" + "=" * 80)
        print(f"SCAN COMPLETE: Found {len(opportunities)} high-confidence opportunities")
        print("=" * 80)
        
        return opportunities
    
    def analyze_stock(self, symbol: str, sector: str) -> Optional[DayTradeOpportunity]:
        """
        Analyze a single stock for day trading opportunity
        Returns DayTradeOpportunity if it passes filters, None otherwise
        """
        # Get evaluation from strategy
        eval_data = self.strategy.evaluate_stock(symbol)
        
        # Check if passes basic filters
        if not eval_data['passes_filters']:
            return None
        
        # Check if overall score indicates confidence
        if eval_data['overall_score'] < self.min_confidence:
            return None
        
        # Get current price and stock info
        ticker = yf.Ticker(symbol)
        info = ticker.info
        current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
        
        if current_price < MIN_PRICE or current_price > MAX_PRICE:
            return None
        
        name = info.get('shortName', symbol)
        
        # Calculate position size
        shares = int(self.capital_per_trade / current_price)
        position_value = shares * current_price
        
        # Determine setup type based on gap and momentum
        setup_type = self._determine_setup_type(eval_data)
        
        # Calculate entry, target, and stop prices
        entry_price = current_price
        estimated_return_pct = self._estimate_return_pct(eval_data)
        target_price = entry_price * (1 + estimated_return_pct / 100)
        stop_price = entry_price * (1 - DAY_TRADE_MAX_LOSS / 100)
        
        # Calculate dollar returns
        estimated_return_dollars = position_value * (estimated_return_pct / 100)
        max_loss_dollars = position_value * (DAY_TRADE_MAX_LOSS / 100)
        
        # Estimate time to target (based on volatility)
        estimated_time = self._estimate_time_to_target(eval_data['atr_pct'])
        
        # Calculate confidence (same as overall score for simplicity)
        confidence = int(eval_data['overall_score'])
        
        # Create opportunity object
        opportunity = DayTradeOpportunity(
            symbol=symbol,
            name=name,
            current_price=current_price,
            sector=sector,
            entry_price=entry_price,
            target_price=target_price,
            stop_price=stop_price,
            estimated_return_pct=estimated_return_pct,
            estimated_return_dollars=estimated_return_dollars,
            estimated_time_minutes=estimated_time,
            confidence=confidence,
            shares=shares,
            position_value=position_value,
            premarket_gap_pct=eval_data['gap_pct'],
            premarket_volume_ratio=eval_data['volume_ratio'],
            atr_pct=eval_data['atr_pct'],
            current_volume_ratio=eval_data['volume_ratio'],
            setup_score=eval_data['setup_score'],
            catalyst_score=eval_data['catalyst_score'],
            momentum_score=eval_data['momentum_score'],
            overall_score=eval_data['overall_score'],
            setup_type=setup_type,
            catalyst=eval_data['catalyst'],
            support_levels=eval_data['support_levels'],
            resistance_levels=eval_data['resistance_levels'],
            max_loss_pct=DAY_TRADE_MAX_LOSS,
            max_loss_dollars=max_loss_dollars,
            current_time=datetime.now(),
        )
        
        return opportunity
    
    def _determine_setup_type(self, eval_data: dict) -> str:
        """Determine the type of setup based on evaluation data"""
        gap_pct = eval_data['gap_pct']
        momentum_score = eval_data['momentum_score']
        
        if gap_pct > 3:
            return "GAP_UP"
        elif gap_pct < -3:
            return "GAP_DOWN"
        elif momentum_score > 70:
            return "MOMENTUM"
        elif eval_data['setup_score'] > 70:
            return "BREAKOUT"
        else:
            return "REVERSAL"
    
    def _estimate_return_pct(self, eval_data: dict) -> float:
        """
        Estimate realistic return percentage (1-5%)
        Based on ATR and momentum
        """
        atr_pct = eval_data['atr_pct']
        momentum_score = eval_data['momentum_score']
        
        # Base estimate on ATR (conservative: use 40% of ATR as target)
        base_return = min(atr_pct * 0.4, DAY_TRADE_MAX_RETURN)
        
        # Adjust based on momentum
        if momentum_score > 80:
            base_return *= 1.2
        elif momentum_score < 50:
            base_return *= 0.8
        
        # Clamp to realistic range
        return max(DAY_TRADE_MIN_RETURN, min(base_return, DAY_TRADE_MAX_RETURN))
    
    def _estimate_time_to_target(self, atr_pct: float) -> int:
        """
        Estimate time to reach target in minutes
        Higher volatility = faster moves
        """
        if atr_pct > 10:
            return 60  # 1 hour
        elif atr_pct > 7:
            return 120  # 2 hours
        elif atr_pct > 5:
            return 180  # 3 hours
        else:
            return 240  # 4 hours
    
    def _print_opportunity(self, opp: DayTradeOpportunity):
        """Pretty print an opportunity"""
        print(f"\n  ✅ {opp.symbol} - {opp.name}")
        print(f"     Setup: {opp.setup_type} | Confidence: {opp.confidence}%")
        print(f"     Entry: ${opp.entry_price:.2f} → Target: ${opp.target_price:.2f} ({opp.estimated_return_pct:.1f}%)")
        print(f"     Stop: ${opp.stop_price:.2f} | Est. Time: {opp.estimated_time_minutes}min")
        print(f"     Gap: {opp.premarket_gap_pct:+.1f}% | Volume: {opp.current_volume_ratio:.1f}x | ATR: {opp.atr_pct:.1f}%")
        print(f"     Catalyst: {opp.catalyst[:60]}")
        print(f"     Position: {opp.shares} shares = ${opp.position_value:.2f}")
        print(f"     Est. Return: ${opp.estimated_return_dollars:+.2f} | Max Loss: ${opp.max_loss_dollars:.2f}")
        print(f"     Risk/Reward: {opp.risk_reward_ratio:.2f}:1")
    
    def scan_single_stock(self, symbol: str) -> Optional[DayTradeOpportunity]:
        """Scan a single stock and return opportunity if valid"""
        print(f"\n🔍 Analyzing {symbol} for day trading...")
        print("-" * 60)
        
        try:
            # Try to get sector from known tickers
            sector = "Unknown"
            for sector_name, tickers in SECTOR_TICKERS.items():
                if symbol in tickers:
                    sector = sector_name
                    break
            
            opp = self.analyze_stock(symbol, sector)
            
            if opp:
                if opp.is_high_confidence(self.min_confidence):
                    self._print_opportunity(opp)
                    return opp
                else:
                    print(f"  ⚠️  Confidence too low: {opp.confidence}% < {self.min_confidence}%")
            else:
                print(f"  ❌ Does not meet day trading filters")
            
            return None
            
        except Exception as e:
            print(f"  ❌ Error analyzing {symbol}: {e}")
            return None


if __name__ == "__main__":
    # Test the scanner
    screener = DayScreener()
    opportunities = screener.scan_all_sectors()
    
    print("\n" + "=" * 80)
    print("TOP OPPORTUNITIES")
    print("=" * 80)
    
    for i, opp in enumerate(opportunities[:5], 1):
        print(f"\n#{i} {opp.symbol} - Score: {opp.overall_score:.1f}")
        screener._print_opportunity(opp)
