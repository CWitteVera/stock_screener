# core/o_position_manager.py

import yfinance as yf
import pandas_ta as ta
from typing import Dict

class OPositionManager:
    """Analyze O (Realty Income) position for buy/sell signals"""
    
    def __init__(self, shares: float = 69.312, avg_cost: float = 55.90):
        self.shares = shares
        self.avg_cost = avg_cost
        self.symbol = "O"
    
    def get_current_price(self) -> float:
        """Fetch current O price"""
        try:
            ticker = yf.Ticker(self.symbol)
            data = ticker.history(period="1d")
            if len(data) > 0:
                return float(data['Close'].iloc[-1])
        except:
            pass
        return 62.47  # Fallback
    
    def analyze_buy_signal(self) -> Dict:
        """
        Determine if now is good time to buy more O
        
        Returns:
            {
                'signal': 'STRONG_BUY' | 'GOOD_BUY' | 'HOLD' | 'WAIT',
                'current_price': float,
                'vs_avg_pct': float,
                'recommendation': str
            }
        """
        current_price = self.get_current_price()
        
        # Calculate zones
        strong_buy_low = self.avg_cost * 0.93   # -7% from avg
        strong_buy_high = self.avg_cost * 0.95  # -5% from avg
        good_buy_high = self.avg_cost * 1.00    # At avg cost
        hold_high = self.avg_cost * 1.07        # +7% from avg
        
        vs_avg_pct = (current_price - self.avg_cost) / self.avg_cost * 100
        
        # Determine signal
        if current_price <= strong_buy_high:
            signal = 'STRONG_BUY'
            recommendation = (f"Excellent buy opportunity! O at ${current_price:.2f} is "
                            f"{abs(vs_avg_pct):.1f}% below your ${self.avg_cost:.2f} average. "
                            f"Consider buying with next paycheck ($100).")
        elif current_price <= good_buy_high:
            signal = 'GOOD_BUY'
            recommendation = (f"Good buy price. O at ${current_price:.2f} is near your "
                            f"${self.avg_cost:.2f} average cost. Reasonable opportunity.")
        elif current_price <= hold_high:
            signal = 'HOLD'
            recommendation = (f"O at ${current_price:.2f} is {vs_avg_pct:.1f}% above your average. "
                            f"Hold current position, don't add more now.")
        else:
            signal = 'WAIT'
            recommendation = (f"O at ${current_price:.2f} is {vs_avg_pct:.1f}% above your average. "
                            f"Wait for pullback to $52-56 range before buying more.")
        
        # Get RSI
        try:
            ticker = yf.Ticker(self.symbol)
            hist = ticker.history(period="3mo")
            hist['RSI'] = ta.rsi(hist['Close'], length=14)
            current_rsi = float(hist['RSI'].iloc[-1])
        except:
            current_rsi = None
        
        return {
            'signal': signal,
            'current_price': current_price,
            'avg_cost': self.avg_cost,
            'vs_avg_pct': vs_avg_pct,
            'rsi': current_rsi,
            'zones': {
                'strong_buy': (strong_buy_low, strong_buy_high),
                'good_buy': (strong_buy_high, good_buy_high),
                'hold': (good_buy_high, hold_high)
            },
            'recommendation': recommendation
        }
    
    def analyze_sell_signal(self, swing_return: float = None, swing_confidence: int = None) -> Dict:
        """
        Determine if should sell O for swing trade
        
        Args:
            swing_return: Expected return % from swing trade
            swing_confidence: Confidence % of swing trade
        
        Returns:
            {
                'should_sell': bool,
                'reason': str,
                'analysis': dict (profit comparison)
            }
        """
        if swing_return is None or swing_confidence is None:
            return {
                'should_sell': False,
                'reason': 'No swing trade opportunity available',
                'recommendation': 'Hold O. Earning $19.15/month dividend while waiting.'
            }
        
        # Check 15%/80% criteria
        if swing_return < 15.0 or swing_confidence < 80:
            return {
                'should_sell': False,
                'reason': f"Trade doesn't meet 15%/80% criteria ({swing_return:.1f}%/{swing_confidence}%)",
                'recommendation': 'Hold O. Swing trade not strong enough.'
            }
        
        # Calculate profit comparison
        position_value = self.shares * self.get_current_price()
        cost_basis = self.shares * self.avg_cost
        unrealized_gain = position_value - cost_basis
        
        swing_profit = position_value * (swing_return / 100)
        # O monthly dividend: $0.2765 per share, pro-rated for 7-day holding period
        o_monthly_dividend_per_share = 0.2765
        o_dividend_7days = (self.shares * o_monthly_dividend_per_share) / 30 * 7
        tax_on_o_gains = unrealized_gain * 0.30  # 30% short-term capital gains
        
        net_advantage = swing_profit - o_dividend_7days - tax_on_o_gains
        
        if net_advantage > 100:
            return {
                'should_sell': True,
                'reason': f"Swing trade offers ${net_advantage:.0f} net advantage",
                'analysis': {
                    'position_value': position_value,
                    'swing_profit': swing_profit,
                    'lost_dividend': o_dividend_7days,
                    'o_taxes': tax_on_o_gains,
                    'net_advantage': net_advantage
                },
                'recommendation': (f"SELL O and enter swing trade. "
                                 f"Net profit advantage: ${net_advantage:.0f} "
                                 f"(after taxes and lost dividend)")
            }
        else:
            return {
                'should_sell': False,
                'reason': f"Net advantage too small (${net_advantage:.0f})",
                'recommendation': 'Hold O. Swing trade margin not worth taxes/hassle.'
            }
    
    def get_summary(self) -> str:
        """Get quick summary for console display"""
        buy_analysis = self.analyze_buy_signal()
        
        summary = [
            "\n" + "="*70,
            "💼 O POSITION STATUS",
            "="*70,
            f"Shares: {self.shares:.3f}",
            f"Avg Cost: ${self.avg_cost:.2f}",
            f"Current Price: ${buy_analysis['current_price']:.2f}",
            f"Position Value: ${self.shares * buy_analysis['current_price']:,.2f}",
            f"Unrealized Gain: {buy_analysis['vs_avg_pct']:+.2f}%",
            f"Monthly Dividend: $19.15",
            "",
            f"BUY SIGNAL: {buy_analysis['signal']}",
            f"{buy_analysis['recommendation']}",
            "="*70
        ]
        
        return "\n".join(summary)
